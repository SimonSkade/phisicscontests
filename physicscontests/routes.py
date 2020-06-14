import secrets
import os
from PIL import Image, ImageOps
from flask import render_template, url_for, flash, redirect, request, make_response
from physicscontests import app, db, bcrypt, login_manager, scheduler
from physicscontests.models import User, Task, Contest, Solved_by
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime, timedelta
from sqlalchemy import or_
from physicscontests.forms import RegistrationForm, LoginForm, UpdateAccountForm, TaskForm, AnswerForm, ContestForm, RegisterContestForm, ModifyTaskForm
from wtforms import SelectMultipleField
from flask_wtf import FlaskForm

@app.route("/")
@app.route("/home")
def home():
	contest = Contest.query.filter(Contest.end > datetime.now()).order_by(Contest.start).first()
	return render_template("index.html", contest=contest)
 

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
		flash(f"Account created for {form.username.data}! You were logged in!", "success")
		login_user(user)
		next_page = request.args.get("next")
		return redirect(next_page) if next_page else redirect(url_for("home"))
	return render_template("register.html", form=form)


@app.route("/login", methods=["GET","POST"])
def login():
	if current_user.is_authenticated:
		return redirect(url_for("home"))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user)
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
	shrink_factor = min(min(orig_width,500)/orig_width, min(orig_height,450)/orig_height)
	output_size = (int(orig_width*shrink_factor),int(orig_height*shrink_factor))
	i.thumbnail(output_size, Image.ANTIALIAS)
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
		task = Task(title=form.title.data, story=form.story.data, image_file=image_file, task=form.task.data, solution=form.solution.data, writeup=form.writeup.data, writeup2=writeup_file, difficulty=form.difficulty.data, visible=form.visible.data, author=current_user)
		db.session.add(task)
		db.session.commit()
		flash("Task was created successfully!", "success")
		return redirect(url_for("home"))
	return render_template("create_task.html", form=form)


@app.route("/modify-task/<int:taskID>", methods=["GET","POST"])
@login_required
def modify_task(taskID):
	task = Task.query.filter_by(id=taskID).first()
	if current_user != task.author:
		return not_found(404)
	form = ModifyTaskForm()
	form.title.data = task.title
	#form.story.data = task.story
	#form.image.data = task.image_file
	#form.task.data = task.task
	#form.solution.data = task.solution
	form.writeup.data = task.writeup
	#form.writeup2.data = task.writeup2
	form.difficulty.data = task.difficulty
	form.visible.data = task.visible
	#form.modifying.data = True
	if form.validate_on_submit():
		image_file = None
		if form.image.data:
			image_file = save_explanation_picture(form.image.data)
		writeup_file = None
		if form.writeup2.data:
			writeup_file = save_writeup_file(form.writeup2.data)
		#task = Task(title=form.title.data, story=form.story.data, image_file=image_file, task=form.task.data, solution=form.solution.data, writeup=form.writeup.data, writeup2=writeup_file, difficulty=form.difficulty.data, visible=form.visible.data, author=current_user)
		task.title = form.title.data
		task.story = form.story.data
		task.image_file = image_file
		task.task = form.task.data
		task.solution = form.solution.data
		task.writeup = form.writeup.data
		task.writeup2 = writeup_file
		task.difficulty = form.difficulty.data
		task.visible = form.visible.data
		db.session.commit()
		flash("Task was updated successfully!", "success")
		return redirect(url_for("home"))
	return render_template("modify_task.html", form=form)



@app.route("/practice/exercises/<int:taskID>", methods=["GET","POST"])
def view_task(taskID):
	task = Task.query.filter_by(id=taskID).first()
	if task:
		form = AnswerForm()
		if current_user.is_authenticated and Solved_by.query.filter_by(solved=task).filter_by(solved_by_users=current_user).all():
			form.answer.data = task.solution
		if form.validate_on_submit():
			if abs(form.answer.data-task.solution)/abs(task.solution) <= 0.01 and current_user.is_authenticated and not Solved_by.query.filter_by(solved=task).filter_by(solved_by_users=current_user).all():
				assoc = Solved_by(solved_by_users=current_user, solved=task, timestamp=datetime.now())
				task.solved_by_users.append(assoc)
				db.session.commit()
			image_file = None
			if task.image_file:
				image_file = url_for("static",filename="explanation_images/" + task.image_file)
			return render_template("view_task.html", task=task, form=form, image_file=image_file, is_author=(current_user==task.author))
			#return redirect(url_for('exercises') + "/" + str(taskID))
		image_file = None
		if task.image_file:
			image_file = url_for("static",filename="explanation_images/" + task.image_file)
		return render_template("view_task.html", task=task, form=form, image_file=image_file, is_author=(current_user==task.author))
	else:
		return not_found(1)

@app.route("/contests/<int:contestID>")
def view_contest(contestID):
	contest = Contest.query.filter_by(id=contestID).first()
	return render_template("view_contest.html", contest=contest)
	if contest.end < datetime.now() or current_user == contest.creator:
		return render_template("view_contest.html", contest=contest)
	elif not current_user.is_authenticated:
		flash(f"Log in to participate in the contest!", "success")
		return redirect(url_for("login"))
	elif current_user not in contest.participants:
		return redirect(url_for("register_contest", contestID=contestID))
	elif contest.start > datetime.now():
		flash("The contest has not started yet. You can access this page when the contest has started.")
		return redirect(url_for("home"))
	else:
		return render_template("view_contest.html", contest=contest)

@app.route("/contests/register/<int:contestID>", methods=["GET", "POST"])
@login_required
def register_contest(contestID):
	contest = Contest.query.filter_by(id=contestID).first()
	form = RegisterContestForm()
	if form.validate_on_submit():
		if current_user == contest.creator:
			flash("You cannot participate in a contest you created!")
		elif current_user not in contest.participants:
			contest.participants.append(current_user)
			db.session.commit()
		if contest.start <= datetime.now():
			return redirect(url_for("view_contest", contestID=contestID))
		else:
			return redirect(url_for("home"))
	return render_template("register_contest.html", form=form, contest=contest)



@app.route("/contests/scoreboard/<int:contestID>")
def contest_scoreboard(contestID):#inefficient, must be changed if there are many participants in one contest
	contest = Contest.query.filter_by(id=contestID).first()
	#if datetime.now() > contest.end:
	#calculate scoreboard
	task_ids = [task.id for task in contest.tasks]
	#participation = len(contest.participants)
	scores = []
	participants = User.query.filter(User.participated_in.any(Contest.id == contest.id)).all()
	for participant in participants:
		contest_tasks_solved = []
		solves = Solved_by.query.filter_by(solved_by_users=participant).all()
		for i in range(len(solves)):
			task = solves[i].solved
			if task.id in task_ids and solves[i].timestamp < contest.end:
				contest_tasks_solved.append((task,solves[i].timestamp))
		score = 0
		latest_answer = timedelta(0)
		for task,time in contest_tasks_solved:
			score += task.difficulty
			latest_answer = max(latest_answer, time - contest.start)
		scores.append((score, latest_answer, participant.username))
	scores.sort(key=lambda k: (-k[0], k[1]))
	rank = 1
	scoreboard = []
	for i, score_user in enumerate(scores):
		scoreboard.append((rank, score_user[2], score_user[0], score_user[1]))
		rank += 1
	return render_template("scoreboard.html", contest=contest, scoreboard=scoreboard)
	#else:
	#	flash("Contest is not over yet.")
	#	return redirect(url_for("home"))


@app.route("/practice/exercises")
def exercises():
	if current_user.is_authenticated:
		tasks = Task.query.filter(or_(Task.visible == True, Task.author == current_user)).all()
	else:
		tasks = Task.query.filter_by(visible=True).all()
	tasks = Task.query.all()#temporary
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
	contests = Contest.query.filter(Contest.end > datetime.now()).order_by(Contest.start).all()
	return render_template("upcoming_contests.html", contests=contests, current_user=current_user)


@app.route("/contribute")
def contribute():
	return render_template("contribute.html")



def contest_start_notification(contestID):#does not work, as it requires a user request
	contest = Contest.query.filter_by(id=contestID).first()
	for task in contest.tasks:
		task.visible = True
		db.session.commit()
	#flash(f"Contest {contest.name} has started. You can now access the contest site, if you are registered.")


def end_contest_process(contestID):
	#publish contest tasks
	contest = Contest.query.filter_by(id=contestID).first()
	for task in contest.tasks:
		task.visible = True
		db.session.commit()
	



@app.route("/create_contest", methods=["GET", "POST"])
@login_required
def create_contest():
	form = ContestForm()
	#users_tasks= Task.query.filter(or_(Task.visible == True, Task.author == current_user)).all()
	#form2 = FlaskForm()
	#form2.tasks = SelectMultipleField(label="Add Tasks", choices=[(task.id,task.title) for task in users_tasks], coerce=int)
	if form.validate_on_submit():
		contest = Contest(name=form.name.data, description=form.description.data, start=form.start.data, end=form.end.data, creator=current_user)
		for taskID in form.tasks.data:
			contest.tasks.append(Task.query.filter_by(id=taskID).first())
		db.session.add(contest)
		db.session.commit()
		#scheduler.add_job(contest_start_notification, "date", run_date=contest.start, args=[contest.id])
		scheduler.add_job(end_contest_process, "date", run_date=contest.end, args=[contest.id])
		flash("Contest created successfully!")
	return render_template("create_contest.html", form=form)#, contests_running=Contest.query.filter(Contest.start <= datetime.now()).filter(Contest.end > datetime.now()).all())






@app.errorhandler(404)
def not_found(trash):#somehow only works with an unneeded argument
	return make_response(render_template("404.html"),404)

