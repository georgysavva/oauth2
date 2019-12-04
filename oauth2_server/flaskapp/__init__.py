from flask import Flask
from flask_jsonschema import JsonSchema

from config import JSON_SCHEMAS_DIR

app = Flask(__name__)
app.config['JSONSCHEMA_DIR'] = JSON_SCHEMAS_DIR
setattr(app, 'jsonschema', JsonSchema(app))

import flaskapp.views
