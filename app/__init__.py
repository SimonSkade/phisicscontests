from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SECRET_KEY"] = "bb31594820cb0ee8d7e0dc07bd156619"
app.config["SCLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)



from app import routes

