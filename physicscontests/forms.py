from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, DateTimeField, SelectMultipleField, MultipleFileField, FileField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from physicscontests.models import User, Task
from sqlalchemy import or_

class RegistrationForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired(), Length(min=2,max=20)])
	email = StringField("Email", validators=[DataRequired(),Email()])
	password = PasswordField("Password", validators=[DataRequired()])
	confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
	submit = SubmitField("Sign Up")
	def validate_username(self,username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError("username already exists")

	def validate_email(self,email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError("email already registered")


class LoginForm(FlaskForm):
	email = StringField("Email", validators=[DataRequired(),Email()])
	password = PasswordField("Password", validators=[DataRequired()])
	remember = BooleanField("Remember Me")
	submit = SubmitField("Log In")


class UpdateAccountForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired(), Length(min=2,max=20)])
	email = StringField("Email", validators=[DataRequired(),Email()])
	picture = FileField("Update Profile Picture", validators=[FileAllowed(["jpg","png"])])
	submit = SubmitField("Update")
	def validate_username(self,username):
		if username.data != current_user.username:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError("username already exists")

	def validate_email(self,email):
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError("email already registered")


class TaskForm(FlaskForm):
	#enctype="multipart/form-data"
	title = StringField("Title", validators=[DataRequired()])
	story = TextAreaField("Story or Background", validators=[DataRequired()])
	image = FileField("Upload Clarification Image", validators=[FileAllowed(["jpg","png"])])
	task = TextAreaField("Task", validators=[DataRequired()])
	solution = DecimalField("Solution", validators=[DataRequired()])
	writeup = TextAreaField("Writeup / Explanation of solution")
	writeup2 = FileField("Writeup / Explanation of solution", validators=[FileAllowed(["jpg","png","pdf","docx","odt","odp","pptx","txt","md"])])
	difficulty = SelectField("Difficulty", choices=[(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10)], coerce=int)
	submit = SubmitField("Create Task")
	def validate_title(self,title):
		if Task.query.filter_by(title=title.data).first():
			raise ValidationError("task title already exists")


class AnswerForm(FlaskForm):
	answer = DecimalField("Your answer", validators=[DataRequired()])
	submit = SubmitField("Submit Answer")



class ContestForm(FlaskForm):
	name = StringField("Contest name", validators=[DataRequired()])
	description = TextAreaField("Contest description")
	start = DateTimeField("Start (format: yyyy-mm-dd HH:MM:SS)", validators=[DataRequired()])
	end = DateTimeField("End (format: yyyy-mm-dd HH:MM:SS)", validators=[DataRequired()])
	if current_user:
		users_tasks = Task.query.filter(or_(Task.visible == True, Task.author == current_user)).all()
	else:
		users_tasks = Task.query.filter_by(visible=True).all()
	tasks = SelectMultipleField("Add Tasks", choices=[(task.id,task.title) for task in users_tasks], coerce=int)
	submit = SubmitField("Create Contest")
	def validate_title(self,name):
		if Contest.query.filter_by(name=name.data).first():
			raise ValidationError("Contest name already exists")




