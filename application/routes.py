#  Copyright (c) 2023. Andrii Malchyk, All rights reserved.

from flask import render_template, request, Response, json, redirect, flash, url_for

from application import app
from application.forms import LoginForm, RegisterForm
from application.models import User, Course, Enrollment

course_data = [{"courseID": "1111", "title": "PHP 101", "description": "Intro to PHP", "credits": 3,
                "term": "Fall, Spring"},
               {"courseID": "2222", "title": "Java 1", "description": "Intro to Java Programming", "credits": 4,
                "term": "Spring"},
               {"courseID": "3333", "title": "Adv PHP 201", "description": "Advanced PHP Programming", "credits": 3,
                "term": "Fall"},
               {"courseID": "4444", "title": "Angular 1", "description": "Intro to Angular", "credits": 3,
                "term": "Fall, Spring"},
               {"courseID": "5555", "title": "Java 2", "description": "Advanced Java Programming", "credits": 4,
                "term": "Fall"}]


@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html", index=True)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.objects(email=email).first()
        if user and user.get_password(password):
            flash(f"{user.first_name}, you are successfully logged in!", "success")
            return redirect("/index")
        else:
            flash("Sorry, something went wrong", "danger")
    return render_template("login.html", title="Login", form=form, login=True)


@app.route("/courses/")
@app.route("/courses/<term>")
def courses(term=None):
    if term is None:
        term = "Spring 2023"

    classes = Course.objects.order_by("+courseID")
    return render_template("courses.html", course_data=classes, courses=True, term=term)


@app.route("/register", methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user_id = User.objects.count()
        user_id += 1
        email = form.email.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User(user_id=user_id, email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()
        flash("You are successfully registered!", "success")
        return redirect(url_for("index"))
    return render_template("register.html", title="Register", form=form, register=True)


@app.route("/enrollment", methods=["GET", "POST"])
def enrollment():
    courseID = request.form.get('courseID')
    course_title = request.form.get('title')
    user_id = 1
    if courseID:
        if Enrollment.objects(user_id=user_id, courseID=courseID):
            flash(f"Oops! You are already registered in this course {course_title}!", "danger")
            return redirect(url_for("courses"))
        else:
            Enrollment(user_id=user_id, courseID=courseID)
            flash(f"You are enrolled in {course_title}!", "success")

    classes = None
    term = request.form.get('term')
    return render_template("enrollment.html", enrollment=True, title="Enrollment", classes=classes)


@app.route("/api/")
@app.route("/api/<idx>")
def api(idx=None):
    if idx is None:
        jdata = course_data
    else:
        jdata = course_data[int(idx)]
    return Response(json.dumps(jdata), mimetype="application/json")


@app.route("/user")
def user():
    users = User.objects.all()
    return render_template("user.html", users=users)
