from configparser import ConfigParser
from datetime import datetime
from flask import Flask, g, render_template, request #pip install flask
from folioclient import FolioClient #pip install folioclient

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

def init_folio():
  folio_config = config['FOLIO']

  with FolioClient(
    folio_config['base_url'], 
    folio_config['tenant'],
    folio_config['username'],
    folio_config['password']) as folio:

    init_statistical_codes(folio)
    init_item_note_types(folio)

    pass

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
  end_barcode = request.args.get('end_barcode')

  folio_config = config['FOLIO']

  with FolioClient(
    folio_config['base_url'], 
    folio_config['tenant'],
    folio_config['username'],
    folio_config['password']) as folio:

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

@app.route('/save-items', methods=['POST'])
def save_items():
  pass
  items_input = request.json

  # TODO refactor constructing FolioClient
  # with app.app_context():
  folio_config = config['FOLIO']
  with FolioClient(
    folio_config['base_url'], 
    folio_config['tenant'],
    folio_config['username'],
    folio_config['password']) as folio:

    for item_input in items_input:
      # TODO: Validate / secure all input
      barcode = item_input['barcode']
      if not item_input['shelf_status']:
        continue

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
        'note': f"Inventoried at {timestamp} by {username}.  Shelf status: {item_input['shelf_status']}.",
        'staffOnly': True,
      })

      result = folio.folio_put(
        path = f"/inventory/items/{item['id']}",
        payload = item,
      )

  return "Saved items"
