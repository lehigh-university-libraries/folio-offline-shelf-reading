from configparser import ConfigParser
from datetime import datetime
from flask import (
    Flask,
    g,
    render_template,
    redirect,
    request,
    session,
    url_for,
)  # pip install flask

# pip install pyopenssl
from folioclient import FolioClient  # pip install folioclient
from httpx import HTTPStatusError
import json
import re
import os
import logging

from application.reporter import Reporter

custom_condition_name = "<custom>"

config = None
inventoried_statistical_code = None
inventoried_item_note_type = None
inventoried_item_condition_note_type = None
item_damage_status = None
conditions_by_name = None

reporter = None


def create_app():
    global config
    app = Flask(__name__)

    config = ConfigParser()
    config.read_file(open("config/config.properties"))
    dir = os.path.dirname(__file__)
    dir = os.path.dirname(dir)
    config_path = os.path.join(dir, "config", "config.properties")
    with open(config_path, "r", encoding="utf-8") as f:
        config.read_file(f)

    app.secret_key = config["Testing"]["secret_key"]

    global reporter
    reporter = Reporter(config)

    init_conditions()
    init_folio()

    return app


def run_with_folio_client(fn):
    folio_config = config["FOLIO"]

    with FolioClient(
        folio_config["base_url"],
        folio_config["tenant"],
        folio_config["username"],
        folio_config["password"],
    ) as folio:

        return fn(folio)


def init_conditions():
    global conditions_by_name
    conditions_by_name = dict(map(reversed, config.items("Conditions")))


def init_folio():

    def init_folio_internal(folio):
        init_statistical_codes(folio)
        init_item_note_types(folio)
        init_item_damaged_statuses(folio)

    run_with_folio_client(init_folio_internal)


def init_statistical_codes(folio):
    result = folio.folio_get(
        path="/statistical-codes",
        key="statisticalCodes",
        query_params="limit=1000",
    )
    statistical_codes = {
        statistical_code["code"]: statistical_code for statistical_code in result
    }

    inventoried_code = config["FOLIO"]["inventoried_statistical_code"]
    global inventoried_statistical_code
    inventoried_statistical_code = statistical_codes[inventoried_code]


def init_item_note_types(folio):
    result = folio.folio_get(
        path="/item-note-types",
        key="itemNoteTypes",
        query_params={
            "limit": 1000,
        },
    )
    item_note_types = {
        item_note_type["name"]: item_note_type for item_note_type in result
    }

    global inventoried_item_note_type
    note_type = config["FOLIO"]["inventoried_item_note_type"]
    inventoried_item_note_type = item_note_types[note_type]["id"]

    note_type = config["FOLIO"]["inventoried_item_condition_note_type"]
    global inventoried_item_condition_note_type
    inventoried_item_condition_note_type = item_note_types[note_type]["id"]


def init_item_damaged_statuses(folio):
    result = folio.folio_get(
        path="/item-damaged-statuses",
        key="itemDamageStatuses",
        query_params="limit=1000",
    )
    item_damage_statuses = {
        item_damage_status["name"]: item_damage_status for item_damage_status in result
    }

    damage_status_code = config["FOLIO"]["item_damage_status"]
    global item_damage_status
    item_damage_status = item_damage_statuses[damage_status_code]["id"]


app = create_app()


@app.route("/", methods=["GET"])
def home():
    if "username" not in session:
        return "Log in first", 401

    return render_template(
        "index.html",
        cycle=inventoried_statistical_code["name"],
        username=session["username"],
        test=dict(config["Testing"]) if eval(config["Testing"]["enabled"]) else False,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not request.form["password"] == config["Testing"]["password"]:
            return "Nope", 401
        session["username"] = request.form["username"]
        return redirect(url_for("home"))
    return """
      <form method="post">
          <p><input type=text name=username>
          <p><input type=text name=password>
          <p><input type=submit value=Login>
      </form>
  """


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("home"), code=301)


@app.route("/load-conditions", methods=["GET"])
def load_conditions():
    return config.items("Conditions")


@app.route("/load-items", methods=["GET"])
def load_items():
    start_barcode = request.args.get("start_barcode")
    if not validate_barcode(start_barcode):
        return f"Invalid start barcode: {start_barcode}", 400

    end_barcode = request.args.get("end_barcode")
    if not validate_barcode(end_barcode):
        return f"Invalid end barcode: {end_barcode}", 400

    def load_items_internal(folio):
        result = folio.folio_post(
            path="/ldp/db/reports",
            payload={
                "url": config["MetaDB"]["items_query_url"],
                "params": {
                    "start_barcode": start_barcode,
                    "end_barcode": end_barcode,
                },
                "limit": 1000,
            },
        )
        records = result["records"]
        for record in records:
            record = enrich_record(record)
        return records

    return run_with_folio_client(load_items_internal)


@app.route("/save-items", methods=["POST"])
def save_items():
    items_input = request.json

    def save_items_internal(folio):
        results = []
        for item_input in items_input:
            validation_error = validate_item_input(item_input)
            if validation_error:
                results.append(validation_error)
                continue

            item_id = item_input["id"]
            shelf_status = item_input["shelf_status"]
            shelf_condition = (
                item_input["shelf_condition"].strip()
                if "shelf_condition" in item_input
                else None
            )
            item = load_item(folio, item_id)
            item = modify_item(item, shelf_status, shelf_condition)
            result = save_item(folio, item)
            if item_input.get("shelf_status") == "Missing":
                result = mark_item_missing(folio, item)
            results.append(result)
        return results

    return run_with_folio_client(save_items_internal)


@app.route("/report-results", methods=["POST"])
def report_results():
    results = request.json
    enrich_report_location(results)
    reporter.report_results(results)
    return "OK"


def enrich_report_location(results):
    items_input = results["itemsInput"]
    if not len(items_input):
        return
    item_id = items_input[0]["id"]

    def enrich_report_load_item(folio):
        item = load_item(folio, item_id)
        return item

    item = run_with_folio_client(enrich_report_load_item)
    location_name = item["effectiveLocation"]["name"]
    results["locationName"] = location_name


def validate_item_input(item_input):
    error = None
    barcode = item_input.get("barcode")
    if not validate_barcode(barcode):
        return validation_error(barcode, f"Invalid barcode: {barcode}")
    if not validate_item_id(item_input.get("id")):
        return validation_error(barcode, f'Invalid item id: {item_input.get("id")}')
    if not validate_shelf_status(item_input.get("shelf_status")):
        return validation_error(
            barcode, f'Invalid shelf status: {item_input.get("shelf_status")}'
        )
    if not validate_shelf_condition(item_input.get("shelf_condition")):
        return validation_error(
            barcode, f'Invalid shelf condition: {item_input.get("shelf_condition")}'
        )
    return None


def validation_error(barcode, message):
    return {
        "barcode": barcode,
        "text": message,
        "success": False,
    }


def load_item(folio, item_id):
    item = folio.folio_get(path=f"/inventory/items/{item_id}")
    return item


def modify_item(item, shelf_status, shelf_condition):
    item["statisticalCodeIds"].append(inventoried_statistical_code["id"])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    item["notes"].append(
        {
            "itemNoteTypeId": inventoried_item_note_type,
            "note": f"Shelf status: {shelf_status}. Inventoried at {timestamp} by {session['username']}.",
            "staffOnly": True,
        }
    )
    if shelf_condition:
        item["notes"].append(
            {
                "itemNoteTypeId": inventoried_item_condition_note_type,
                "note": f"{shelf_condition}. Inventoried at {timestamp} by {session['username']}.",
                "staffOnly": True,
            }
        )

        condition_barcode = conditions_by_name.get(
            shelf_condition, conditions_by_name.get(custom_condition_name)
        )
        if eval(config["ConditionsDamageFlag"][condition_barcode]):
            item["itemDamagedStatusId"] = item_damage_status
            item["itemDamagedStatusDate"] = timestamp

    return item


def save_item(folio, item):
    try:
        folio.folio_put(
            path=f"/inventory/items/{item['id']}",
            payload=item,
        )
        return {
            "barcode": item.get("barcode"),
            "text": "Saved",
            "success": True,
        }
    except HTTPStatusError as error:
        return {
            "barcode": item.get("barcode"),
            "text": str(error),
            "success": False,
        }


def mark_item_missing(folio, item):
    try:
        folio.folio_post(
            path=f"/inventory/items/{item['id']}/mark-missing",
            payload=None,
        )
        return {
            "barcode": item.get("barcode"),
            "text": "Marked as missing",
            "success": True,
        }
    except HTTPStatusError as error:
        return {
            "barcode": item.get("barcode"),
            "text": str(error),
            "success": False,
        }


def enrich_record(record):
    statistical_codes = json.loads(record["statistical_codes"])
    record["local_inventoried"] = (
        inventoried_statistical_code["id"] in statistical_codes
    )
    return record


def validate_barcode(barcode):
    return barcode and re.match("^[0-9]*$", barcode)


def validate_item_id(item_id):
    return item_id and re.match("^[a-f0-9-]*$", item_id)


def validate_shelf_status(shelf_status):
    return shelf_status and re.match("^[A-Za-z ]*$", shelf_status)


def validate_shelf_condition(shelf_condition):
    return not shelf_condition or re.match("^[A-Za-z ]*$", shelf_condition)


@app.route("/healthcheck")
def healthcheck():
    return "OK"


class HealthCheckFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("/healthcheck") == -1


# Remove /healthcheck from application server logs
logging.getLogger("gunicorn.access").addFilter(HealthCheckFilter())

logger = logging.getLogger(__name__)
