from configparser import ConfigParser
from flask import Flask, render_template, request #pip install flask
from folioclient import FolioClient #pip install folioclient

config = ConfigParser()
config.read_file(open('config/config.properties'))

app = Flask(__name__)

@app.route("/", methods=['GET'])
def home():
  return render_template('index.html', test = eval(config['Testing']['enabled']))

@app.route("/load-items", methods=['GET'])
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
        "url": config['MetaDB']['items_query_url'],
        "params": {
            "start_barcode": start_barcode,
            "end_barcode": end_barcode,
        },
        "limit": 1000
      }
    )
    return result['records']
