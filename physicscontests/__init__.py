from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import os

app = Flask(__name__)

if os.environ.get("ENV") == "production":
	app.config["DEBUG"] = False
	app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
	app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
else:
	app.config["DEBUG"] = True
	app.config["SECRET_KEY"] = "2vt8q98bfwbfb28vgfzu25cfjsghfgv4t"
	app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"
scheduler = BackgroundScheduler()
scheduler.start()


from physicscontests import routes
from physicscontests.models import Contest

def get_important_announcements():#should only be triggered once if there is something important
	announcements = []
	#for c in get_finished_contests():
	#	announcements.append(f"Contest {c.name} is over. I hope all participants had much fun! The solutions will be published tomorrow here: https://drive.google.com/drive/folders/1tjkZkgJCgY_ttnxcxglH2GyXKpj_NcT7?usp=sharing")
	return announcements

def get_running_contests():
	contests_running = Contest.query.filter(Contest.start <= datetime.now()).filter(Contest.end > datetime.now()).all()
	return contests_running

def get_finished_contests():
	contests_finished = Contest.query.filter(Contest.end <= datetime.now()).filter(Contest.end > datetime.now() - timedelta(hours=2)).all()
	return contests_finished

app.jinja_env.globals.update(get_running_contests=get_running_contests)
app.jinja_env.globals.update(get_finished_contests=get_finished_contests)
app.jinja_env.globals.update(get_important_announcements=get_important_announcements)

from physicscontests.commands import create_tables

