from physicscontests import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

#needs to be changed to class model to use the timestamp
class Solved_by(db.Model):
	#id = db.Column(db.Integer, primary_key=True)
	__table_args__ = (db.PrimaryKeyConstraint("user_id","task_id"),)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
	task_id = db.Column(db.Integer, db.ForeignKey("task.id"), primary_key=True)
	timestamp = db.Column(db.TIMESTAMP(timezone=False), nullable=False, default=datetime.now())
	solved_by_users = db.relationship("User", back_populates="solved")
	solved = db.relationship("Task", back_populates="solved_by_users")


participation = db.Table("participation",
	db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
	db.Column("contest_id", db.Integer, db.ForeignKey("contest.id"))
	)

placement = db.Table("placement",
	db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
	db.Column("contest_id", db.Integer, db.ForeignKey("contest.id")),
	db.Column("placement", db.Integer)
	)

class User(UserMixin, db.Model):
	id = db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	image_file = db.Column(db.String(200), nullable=False, default="default.jpg")
	password = db.Column(db.String(60), nullable=False)
	contests_created = db.relationship('Contest', backref='creator')
	created = db.relationship('Task', backref='author')
	solved = db.relationship('Solved_by', back_populates="solved_by_users")
	participated_in = db.relationship('Contest', secondary=participation, backref=db.backref("participants", lazy="dynamic"))
	placements = db.relationship('Contest', secondary=placement, backref=db.backref("standings", lazy="dynamic"))

	def __repr__(self):
		return f"User('{self.username}', '{self.email}', '{self.image_file})'"


class Task(db.Model):
	visible = db.Column(db.Boolean,nullable=False,default=False)
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(200), unique=True, nullable=False)
	story = db.Column(db.Text, nullable=False)
	image_file = db.Column(db.String(200))
	task = db.Column(db.Text, nullable=False)
	solution = db.Column(db.Numeric, nullable=False)
	writeup = db.Column(db.Text, default="See the attached document for an explanation.")
	writeup2 = db.Column(db.String(400))
	difficulty = db.Column(db.Integer, nullable=False)
	author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	contest_id = db.Column(db.Integer, db.ForeignKey('contest.id'))
	solved_by_users = db.relationship("Solved_by", back_populates="solved")

	def __repr__(self):
		return f"Task('{self.title}', ID: '{self.id}')"


class Contest(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(40), unique=True, nullable=False, default=f"Physicscontest #{id}")
	description = db.Column(db.Text)
	start = db.Column(db.DateTime, nullable=False)
	end = db.Column(db.DateTime, nullable=False)
	tasks = db.relationship('Task', backref='contest')
	creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))

"""
class Scoreboard(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	contest_id = db.Column(db.Integer, db.ForeignKey("contest.id"))
	contest = relationship("Contest", uselist=False, backref=db.backref("scoreboard", uselist=False))
	rank = db.Column(db.Integer, nullable=False)
	username = db.Column(db.Integer, nullable=False)
	score = db.Column(db.Integer, nullable=False)
"""


##########DANGER ZONE##########################
db.drop_all()
db.create_all()

## if you uncomment the above the complete database will be deleted and recreated
###############################################
