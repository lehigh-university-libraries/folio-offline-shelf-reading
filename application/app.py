from configparser import ConfigParser
from datetime import datetime
from flask import (
    Flask,
    g,
    make_response,
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

SHELF_STATUS = {
    "PRESENT": "Present",
    "MISSING": "Missing",
    "UNAVAILABLE_BUT_ON_SHELF": "Unavailable item is on shelf",
    "UNAVAILABLE_AS_EXPECTED": "Unavailable as expected",
    "IGNORE_INVENTORIED": "Ignoring: Already inventoried",
}

custom_condition_name = "<custom>"

config = None
inventoried_statistical_code = None
inventoried_item_note_type = None
inventoried_item_condition_note_type = None
item_damage_status = None
conditions_by_name = None
location_to_service_point = None

reporter = None


def create_app():
    app = Flask(__name__)

    init_config()

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


def init_config():
    global config
    config = ConfigParser()
    config.read_file(open("config/config.properties"))
    dir = os.path.dirname(__file__)
    dir = os.path.dirname(dir)
    config_path = os.path.join(dir, "config", "config.properties")
    with open(config_path, "r", encoding="utf-8") as f:
        config.read_file(f)


def init_conditions():
    global conditions_by_name
    conditions_by_name = dict(map(reversed, config.items("Conditions")))


def init_folio():

    def init_folio_internal(folio):
        init_statistical_codes(folio)
        init_item_note_types(folio)
        init_item_damaged_statuses(folio)
        init_locations(folio)

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


def init_locations(folio):
    result = folio.folio_get(
        path="/locations",
        key="locations",
        query_params="limit=1000",
    )
    global location_to_service_point
    location_to_service_point = {
        location["id"]: location["primaryServicePoint"] for location in result
    }


app = create_app()


@app.route("/", methods=["GET"])
def default():
    return home("default")


@app.route("/individual", methods=["GET"])
def individual():
    return home("individual")


@app.route("/condition-fix", methods=["GET"])
def condition_fix():
    return home("condition-fix")


def home(mode):
    if "username" not in session:
        username = request.headers.get("X-Remote-User", None)
        if not username:
            return "Log in first", 401
        session["username"] = username

    return render_template(
        mode + ".html",
        mode=mode,
        cycle=inventoried_statistical_code["name"],
        username=session["username"],
        test=dict(config["Testing"]) if eval(config["Testing"]["enabled"]) else False,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if not config.has_option("Testing", "password"):
        return "Local testing is not enabled.", 400

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


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    response = make_response("Logged out", 401)
    response.delete_cookie("ldapAuth_session_token", path=url_for("home")[:-1])
    return response


@app.route("/done/logout", methods=["GET"])
def done_logout():
    return render_template("logged_out.html", home=url_for("home"))


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

            item_id = item_input["id"] if id in item_input else None
            barcode = item_input["barcode"]
            shelf_status = item_input["shelf_status"]
            shelf_condition = (
                item_input["shelf_condition"].strip()
                if "shelf_condition" in item_input
                else None
            )
            item = load_item(folio, item_id, barcode)
            if not item:
                result = build_error(barcode, f"Unknown barcode: {barcode}")
            else:
                item = modify_item(item, shelf_status, shelf_condition)
                result = save_item(folio, item)
                if (
                    item_input.get("shelf_status")
                    == SHELF_STATUS["UNAVAILABLE_BUT_ON_SHELF"]  # range mode
                    or item_input.get("shelf_status")
                    == SHELF_STATUS["PRESENT"]  # individual mode
                ) and (
                    item.get("status").get("name") == "Checked out"
                    or item.get("status").get("name") == "Missing"
                ):
                    result = mark_item_checked_in(folio, item)
                if item_input.get("shelf_status") == SHELF_STATUS["MISSING"]:
                    result = mark_item_missing(folio, item)
            results.append(result)
        return results

    return run_with_folio_client(save_items_internal)


@app.route("/fix-items-condition", methods=["POST"])
def fix_items_condition():
    items_input = request.json

    def fix_items_condition_internal(folio):
        results = []
        for item_input in items_input:
            validation_error = validate_item_input(item_input, shelf_status=False)
            if validation_error:
                results.append(validation_error)
                continue

            barcode = item_input["barcode"]
            item = load_item(folio, None, barcode)
            if not item:
                result = build_error(barcode, f"Unknown barcode: {barcode}")
            else:
                if item.get("itemDamagedStatusId", None) == item_damage_status:
                    result = build_error(
                        barcode,
                        "Cannot remove condition note, item damaged status is set.",
                    )
                else:
                    item["notes"] = [
                        note
                        for note in item["notes"]
                        if note["itemNoteTypeId"]
                        != inventoried_item_condition_note_type
                    ]
                    result = save_item(folio, item)
            results.append(result)
        return results

    return run_with_folio_client(fix_items_condition_internal)


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
    barcode = items_input[0]["barcode"]

    def enrich_report_load_item(folio):
        item = load_item(folio, item_id, barcode)
        return item

    item = run_with_folio_client(enrich_report_load_item)
    location_name = item["effectiveLocation"]["name"]
    results["locationName"] = location_name


def validate_item_input(item_input, shelf_status=True):
    error = None
    barcode = item_input.get("barcode")
    if not validate_barcode(barcode):
        return build_error(barcode, f"Invalid barcode: {barcode}")
    if not validate_item_id(item_input.get("id")):
        return build_error(barcode, f'Invalid item id: {item_input.get("id")}')
    if shelf_status and not validate_shelf_status(item_input.get("shelf_status")):
        return build_error(
            barcode, f'Invalid shelf status: {item_input.get("shelf_status")}'
        )
    if not validate_shelf_condition(item_input.get("shelf_condition")):
        return build_error(
            barcode, f'Invalid shelf condition: {item_input.get("shelf_condition")}'
        )
    return None


def build_error(barcode, message):
    return {
        "barcode": barcode,
        "text": message,
        "success": False,
    }


def load_item(folio, item_id, barcode):
    if item_id:
        item = folio.folio_get(path=f"/inventory/items/{item_id}")
    else:
        response = folio.folio_get(
            path=f"/inventory/items", query_params={"query": f"barcode=={barcode}"}
        )
        items = response["items"]
        if not len(items):
            return None
        item = items[0]
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


def mark_item_checked_in(folio, item):
    location = item["effectiveLocation"]["id"]
    service_point = location_to_service_point.get(location)
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    try:
        folio.folio_post(
            path=f"/circulation/check-in-by-barcode",
            payload={
                "itemBarcode": item.get("barcode"),
                "servicePointId": service_point,
                "checkInDate": current_time,
            },
        )
        return {
            "barcode": item.get("barcode"),
            "text": "Checked in",
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
    return barcode and re.match(config.get("Validation", "BARCODE"), barcode)


def validate_item_id(item_id):
    return not item_id or re.match(config.get("Validation", "ITEM_ID"), item_id)


def validate_shelf_status(shelf_status):
    return shelf_status and re.match(
        config.get("Validation", "SHELF_STATUS"), shelf_status
    )


def validate_shelf_condition(shelf_condition):
    return not shelf_condition or re.match(
        config.get("Validation", "SHELF_CONDITION"), shelf_condition
    )


@app.route("/constants.js")
def serve_constants():
    js_content = ""
    for prefix, values in {
        "SHELF_STATUS": SHELF_STATUS,
        "VALIDATION": dict(config.items("Validation")),
    }.items():
        js_content += "\n"
        for key, value in values.items():
            js_content += f"{prefix}_{key.upper()} = '{value}';\n"
    response = make_response(js_content)
    response.mimetype = "application/javascript"
    return response


@app.route("/healthcheck")
def healthcheck():
    return "OK"


class HealthCheckFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.healthcheck_path = os.environ.get("SCRIPT_NAME", "/") + "healthcheck"

    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find(self.healthcheck_path) == -1


# Remove /healthcheck from application server logs
logging.getLogger("gunicorn.access").addFilter(HealthCheckFilter())

logger = logging.getLogger(__name__)
