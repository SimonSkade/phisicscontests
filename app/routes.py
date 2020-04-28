from flask import render_template, url_for, flash, redirect
from app import app
from app.models import User
from app.forms import RegistrationForm, LoginForm


@app.route("/")
@app.route("/home")
def home():
	return render_template("index.html")
 

@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/register", methods=["GET","POST"])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		flash(f"Account created for {form.username.data}!", "success")
		return redirect(url_for("home"))
	return render_template("register.html", form=form)

@app.route("/login", methods=["GET","POST"])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		#here is an placeholder
		redirect("home")
	return render_template("login.html", form=form)
