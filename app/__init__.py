from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from sqlalchemy import create_engine

app = Flask(__name__)
app.config.from_object(Config)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
db = SQLAlchemy(app)

from app import routes, prototype_routes, models
