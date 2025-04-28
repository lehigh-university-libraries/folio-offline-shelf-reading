from configparser import ConfigParser
from datetime import datetime
from flask import Flask, g, render_template, request #pip install flask
from folioclient import FolioClient #pip install folioclient
import re

config = None
inventoried_statistical_code = None
inventoried_item_note_type = None

def create_app():
  global config
  app = Flask(__name__)

  config = ConfigParser()
  config.read_file(open('config/config.properties'))

  init_folio()

  return app

def run_with_folio_client(fn):
  folio_config = config['FOLIO']

  with FolioClient(
    folio_config['base_url'], 
    folio_config['tenant'],
    folio_config['username'],
    folio_config['password']) as folio:

    return fn(folio)

def init_folio():

  def init_folio_internal(folio):
    init_statistical_codes(folio)
    init_item_note_types(folio)

  run_with_folio_client(init_folio_internal)


def init_statistical_codes(folio):
  result = folio.folio_get(
    path = '/statistical-codes',
    key = 'statisticalCodes',
    query_params = 'limit=1000',
  )
  statistical_codes = {statistical_code['code']: statistical_code for statistical_code in result}

  inventoried_code = config['FOLIO']['inventoried_statistical_code']
  global inventoried_statistical_code
  inventoried_statistical_code = statistical_codes[inventoried_code]['id']

def init_item_note_types(folio):
  result = folio.folio_get(
    path = '/item-note-types',
    key = 'itemNoteTypes',
    query_params = {
      'limit': 1000,
    }
  )
  item_note_types = {item_note_type['name']: item_note_type for item_note_type in result}

  note_type = config['FOLIO']['inventoried_item_note_type']
  global inventoried_item_note_type
  inventoried_item_note_type = item_note_types[note_type]['id']

app = create_app()

@app.route('/', methods=['GET'])
def home():
  return render_template('index.html', test = eval(config['Testing']['enabled']))

@app.route('/load-items', methods=['GET'])
def load_items():
  start_barcode = request.args.get('start_barcode')
  if not validate_barcode(start_barcode):
    return f'Invalid start barcode: {start_barcode}', 400

  end_barcode = request.args.get('end_barcode')
  if not validate_barcode(end_barcode):
    return f'Invalid end barcode: {end_barcode}', 400

  def load_items_internal(folio):
    result = folio.folio_post(
      path = '/ldp/db/reports', 
      payload = {
        'url': config['MetaDB']['items_query_url'],
        'params': {
            'start_barcode': start_barcode,
            'end_barcode': end_barcode,
        },
        'limit': 1000
      }
    )
    return result['records']
  
  return run_with_folio_client(load_items_internal)
  
@app.route('/save-items', methods=['POST'])
def save_items():
  items_input = request.json

  def save_items_internal(folio):
    for item_input in items_input:
      barcode = item_input['barcode']
      if not validate_barcode(barcode):
        return f'Invalid barcode: {barcode}', 400

      shelf_status = item_input['shelf_status']
      if not shelf_status:
        continue
      if not validate_shelf_status(shelf_status):
        return f'Invalid shelf status: {shelf_status}', 400

      result = folio.folio_get(
        path = '/inventory/items',
        key = 'items',
        query = f"barcode={barcode}",
      )
      item = result[0]

      item['statisticalCodeIds'].append(inventoried_statistical_code)
      timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      username = 'abc123' # TODO real username
      item['notes'].append({
        'itemNoteTypeId': inventoried_item_note_type,
        'note': f"Inventoried at {timestamp} by {username}.  Shelf status: {shelf_status}.",
        'staffOnly': True,
      })

      result = folio.folio_put(
        path = f"/inventory/items/{item['id']}",
        payload = item,
      )

    return "Saved items"
  
  return run_with_folio_client(save_items_internal)

def validate_barcode(barcode):
  return re.match('^[0-9]*$', barcode)

def validate_shelf_status(shelf_status):
  return re.match('^[A-Za-z ]*$', shelf_status)
