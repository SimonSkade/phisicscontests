import secrets
import os
from PIL import Image, ImageOps
from flask import render_template, url_for, flash, redirect, request, make_response
from physicscontests import app, db, bcrypt
from physicscontests.forms import RegistrationForm, LoginForm, UpdateAccountForm, TaskForm, AnswerForm, ContestForm
from physicscontests.models import User, Task, Contest
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime

@app.route("/")
@app.route("/home")
def home():
	return render_template("index.html")
 

@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/register", methods=["GET","POST"])
def register():
	if current_user.is_authenticated:
		return redirect(url_for("home"))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash(f"Account created for {form.username.data}!", "success")
		return redirect(url_for("login"))
	return render_template("register.html", form=form)

@app.route("/login", methods=["GET","POST"])
def login():
	if current_user.is_authenticated:
		return redirect(url_for("home"))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get("next")
			return redirect(next_page) if next_page else redirect(url_for("home"))
		else:
			flash("Login unsuccessful. Please check username and password", "danger")
	return render_template("login.html", form=form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for("home"))

def save_profile_picture(form_picture):
	print(form_picture.filename, "\n", form_picture,"\n", dir(form_picture),"\n")
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, "static/profile_pics", picture_fn)
	
	output_size = (150,150)
	i = Image.open(form_picture)
	i = ImageOps.fit(i,output_size, Image.ANTIALIAS)
	i.save(picture_path)
	return picture_fn

def save_explanation_picture(form_picture):
	print(form_picture.filename)
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, "static/explanation_images", picture_fn)
	
	i = Image.open(form_picture)
	orig_width, orig_height = i.size
	output_size = (min(orig_width,350),min(orig_height,300))
	i = ImageOps.fit(i,output_size, Image.ANTIALIAS)
	i.save(picture_path)
	return picture_fn

def save_writeup_file(file):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(file.filename)
	fname = random_hex + f_ext
	file_path = os.path.join(app.root_path, "static/writeup_files", fname)
	file.save(file_path)
	return fname

@app.route("/account", methods=["GET","POST"])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			print(form.picture, "  pictureform\n")
			picture_file = save_profile_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash("Your account has been updated!", "success")
		return redirect(url_for("account"))
	elif request.method == "GET":
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for("static",filename="profile_pics/" + current_user.image_file)
	return render_template("account.html", image_file=image_file, form=form)


@app.route("/create-task", methods=["GET","POST"])
@login_required
def create_task():
	form = TaskForm()
	if form.validate_on_submit():
		image_file = None
		if form.image.data:
			image_file = save_explanation_picture(form.image.data)
		writeup_file = None
		if form.writeup2.data:
			writeup_file = save_writeup_file(form.writeup2.data)
		task = Task(title=form.title.data, story=form.story.data, image_file=image_file, task=form.task.data, solution=form.solution.data, writeup=form.writeup.data, writeup2=writeup_file, difficulty=form.difficulty.data, author=current_user)
		db.session.add(task)
		db.session.commit()
		flash("Thanks for creating this task! We will check it and probably use it in a contest or upload it as a practice example.", "success")
		return redirect(url_for("home"))
	return render_template("create_task.html", form=form)


@app.route("/practice/exercises/<int:taskID>", methods=["GET","POST"])
def view_task(taskID):
	task = Task.query.filter_by(id=taskID).first()
	if task:
		form = AnswerForm()
		if task in current_user.solved:
			form.answer.data = task.solution
		if form.validate_on_submit():
			if form.answer.data == task.solution and current_user.is_authenticated:
				task.solved_by_users.append(current_user)
				db.session.commit()
			return render_template("view_task.html", task=task, form=form)
			#return redirect(url_for('exercises') + "/" + str(taskID))
		image_file = None
		if task.image_file:
			image_file = url_for("static",filename="explanation_images/" + task.image_file)
		return render_template("view_task.html", task=task, form=form, image_file=image_file)
	else:
		return not_found(1)

@app.route("/contests/<int:contestID>")
def view_contest(contestID):
	contest = Contest.query.filter_by(id=contestID).first()
	return render_template("view_contest.html", contest=contest)


@app.route("/practice/exercises")
def exercises():
	tasks = Task.query.filter_by(visible=True).all()
	return render_template("exercises.html", tasks=tasks)

@app.route("/practice")
def practice():
	return render_template("practice.html")

@app.route("/past_contests")
def past_contests():
	contests = Contest.query.filter(Contest.end <= datetime.now()).all()
	return render_template("past_contests.html", contests=contests)

@app.route("/upcoming_contests")
def upcoming_contests():
	contests = Contest.query.filter(Contest.end > datetime.now()).all()
	return render_template("upcoming_contests.html", contests=contests)


@app.route("/contribute")
def contribute():
	return render_template("contribute.html")


@app.route("/create_contest", methods=["GET", "POST"])
@login_required
def create_contest():
	form = ContestForm()
	if form.validate_on_submit():
		contest = Contest(name=form.name.data, description=form.description.data, start=form.start.data, end=form.end.data)
		for taskID in form.tasks.data:
			contest.tasks.append(Task.query.filter_by(id=taskID).first())
		db.session.add(contest)
		db.session.commit()
		flash("Contest created! You can now add exercises to your contest.")
		#should redirect to modify contest page
	return render_template("create_contest.html", form=form)





@app.errorhandler(404)
def not_found(trash):#somehow only works with an unneeded argument
	return make_response(render_template("404.html"),404)

