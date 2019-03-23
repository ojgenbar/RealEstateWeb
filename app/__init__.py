from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
from app import views
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
