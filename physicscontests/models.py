from physicscontests import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

solved_by = db.Table("solved_by",
	db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
	db.Column("task_id", db.Integer, db.ForeignKey("task.id"))
	)

class User(UserMixin, db.Model):
	id = db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	image_file = db.Column(db.String(100), nullable=False, default="default.jpg")
	password = db.Column(db.String(60), nullable=False)
	created = db.relationship('Task', backref='author')
	solved = db.relationship("Task", secondary=solved_by, backref=db.backref("solved_by_users", lazy="dynamic"))

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
	#author = db.Column(db.Integer, nullable=False)
	author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	contest_id = db.Column(db.Integer, db.ForeignKey('contest.id'))

	def __repr__(self):
		return f"Task('{self.title}', ID: '{self.id}')"


class Contest(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(40), unique=True, nullable=False, default=f"Physicscontest #{id}")
	description = db.Column(db.Text)
	start = db.Column(db.DateTime, nullable=False)
	end = db.Column(db.DateTime, nullable=False)
	tasks = db.relationship('Task', backref='contest')





