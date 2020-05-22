from physicscontests import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(UserMixin, db.Model):
	id = db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	image_file = db.Column(db.String(100), nullable=False, default="default.jpg")
	password = db.Column(db.String(60), nullable=False)

	def __repr__(self):
		return f"User('{self.username}', '{self.email}', '{self.image_file}'"


class Task(db.Model):
	visible = db.Column(db.Boolean,nullable=False,default=True)
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(200), nullable=False)
	story = db.Column(db.Text, nullable=False)
	task = db.Column(db.Text, nullable=False)
	solution = db.Column(db.String(300), nullable=False)
	writeup = db.Column(db.Text, default="See the attached document for an explanation.")
	writeup2 = db.Column(db.String(400))
	difficulty = db.Column(db.Integer, nullable=False)
	author = db.Column(db.String(100), nullable=False)

	def __repr__(self):
		return f"Task('{self.title}', ID: '{self.id}')"


