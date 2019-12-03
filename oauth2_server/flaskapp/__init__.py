import os

from flask import Flask
from flask_jsonschema import JsonSchema
from config import BASE_DIR

app = Flask(__name__)
app.config['JSONSCHEMA_DIR'] = os.path.join(BASE_DIR, 'json_schemas')
setattr(app, 'jsonschema', JsonSchema(app))

import flaskapp.views
