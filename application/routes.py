#  Copyright (c) 2023. Andrii Malchyk, All rights reserved.

from flask import render_template, request, redirect, flash, url_for, session, jsonify
from flask_restx import Resource

from application import app, api
from application.course_list import course_list
from application.forms import LoginForm, RegisterForm
from application.models import User, Course, Enrollment


########################################
@api.route('/api', '/api/')
class GetAndPost(Resource):
    # GET all
    def get(self):
        return jsonify(User.objects.all())

    # POST
    def post(self):
        data = api.payload
        user = User(user_id=data['user_id'], email=data['email'], first_name=data['first_name'],
                    last_name=data['last_name'])
        user.set_password(data['password'])
        user.save()
        return jsonify(User.objects(user_id=data['user_id']))


@api.route('/api/<idx>')
class GetUpdateDelete(Resource):
    # GET one
    def get(self, idx):
        return jsonify(User.objects(user_id=idx))

    # PUT
    def put(self, idx):
        data = api.payload
        User.objects(user_id=idx).update(**data)
        return jsonify(User.objects(user_id=idx))

    # DELETE
    def delete(self, idx):
        User.objects(user_id=idx).delete()
        return jsonify("User is deleted!")


########################################

@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html", index=True)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if session.get('user_name'):
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.objects(email=email).first()
        if user and user.get_password(password):
            flash(f"{user.first_name}, you are successfully logged in!", "success")
            session['user_id'] = user.user_id
            session['user_name'] = user.first_name
            return redirect("/index")
        else:
            flash("Sorry, something went wrong", "danger")
    return render_template("login.html", title="Login", form=form, login=True)


@app.route("/logout")
def logout():
    session['user_id'] = False
    session.pop('user_name', None)
    return redirect(url_for('index'))


@app.route("/courses/")
@app.route("/courses/<term>")
def courses(term=None):
    if term is None:
        term = "Spring 2023"

    classes = Course.objects.order_by("+courseID")
    return render_template("courses.html", course_data=classes, courses=True, term=term)


@app.route("/register", methods=['POST', 'GET'])
def register():
    if session.get('user_name'):
        return redirect(url_for('index'))
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
    if not session.get('user_name'):
        return redirect(url_for('login'))

    courseID = request.form.get('courseID')
    course_title = request.form.get('title')
    user_id = session.get('user_id')

    if courseID:
        if Enrollment.objects(user_id=user_id, courseID=courseID):
            flash(f"Oops! You are already registered in this course {course_title}!", "danger")
            return redirect(url_for("courses"))
        else:
            Enrollment(user_id=user_id, courseID=courseID).save()
            flash(f"You are enrolled in {course_title}!", "success")

    classes = course_list()

    return render_template("enrollment.html", enrollment=True, title="Enrollment", classes=classes)


@app.route("/user")
def user():
    users = User.objects.all()
    return render_template("user.html", users=users)
