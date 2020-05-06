from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from physicscontests.models import User, Task

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
	title = StringField("Title", validators=[DataRequired()])
	story = TextAreaField("Story or Background", validators=[DataRequired()])
	task = TextAreaField("Task", validators=[DataRequired()])
	solution = StringField("Solution", validators=[DataRequired()])
	writeup = TextAreaField("Writeup / Explanation of solution")
	writeup2 = FileField("Writeup / Explanation of solution", validators=[FileAllowed(["jpg","png","pdf","docx","odt","odp","pptx","txt","md"])])
	submit = SubmitField("Create Task")


class AnswerForm(FlaskForm):
	answer = StringField("Your answer", validators=[DataRequired()])
	submit = SubmitField("Submit Answer")

