from flask import render_template, request, redirect, flash, url_for, Response, Flask
from flask.ext.login import login_required, login_user, logout_user, current_user
from simplecrypt import decrypt
from datetime import datetime as dt
from models import User, get_user
from config import SECRET_KEY, CREATE_PIN
from app import app, db
import os, json

#####################################
# Regular pages
#####################################

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', user=current_user)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user, target=current_user)

@app.route('/profile/<user_id>')
@login_required
def profile_id(user_id):
    user = get_user(id=user_id)
    if not user:
        flash("Invalid page.")
        return redirect(url_for('index'))
    return render_template('profile.html', user=current_user, target=user)

#####################################
# public API
#####################################

def generate_json_response(file, index):
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "dummy_data", file)
    data = json.load(open(json_url))[index]
    resp = Response(response=json.dumps(data),
        status=200, \
        mimetype="application/json")
    return resp

@app.route('/event/<event_id>', methods=["GET", "PUT"])
@login_required
def event(event_id):
    if request.method == "PUT":
        # update event
        pass

    elif request.method == "GET":
        # get info for event
        resp = generate_json_response("events.json", int(event_id))
        return (resp)


@app.route('/task/<task_id>', methods=["GET", "PUT"])
@login_required
def task(task_id):
    if request.method == "PUT":
        # update task
        pass

    elif request.method == "GET":
        # get info for task
        resp = generate_json_response("tasks.json", int(task_id))
        return (resp)


@app.route('/user/<user_id>', methods=["GET", "PUT"])
@login_required
def user(user_id):
    if request.method == "PUT":
        # update event
        pass

    elif request.method == "GET":
        # get info for event
        pass


#####################################
# User login stuff
#####################################

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = get_user(email=request.form["email"])
        if user:
            password = request.form["password"]
            if password == decrypt(SECRET_KEY, user.password).decode('utf8'):
                remember = request.form.get("remember", "no") == "yes"
                if login_user(user, remember=remember):
                    flash("Logged in!")
                    return redirect(request.args.get("next") or url_for("index"))
                else:
                    flash("Sorry, but you could not log in.")
            else:
                flash("Sorry, wrong password.")
        else:
            flash("Invalid username.")
    return render_template('login.html')

@app.route("/register-user", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        if check_valid_new_account(request.form["email"]):
            new_user = User(request.form["name"], request.form["password"], request.form["email"])
            db.session.add(new_user)
            db.session.commit()
            flash("User "+new_user.name+" registered.")
            return redirect(url_for("index"))
    return render_template('create.html')

# Checks whether a new account is allowed to be created, and flashes a failure message if not
def check_valid_new_account(email):
    for user in User.query.all():
        if user.email == email:
            flash("That email address has already been used.")
            return False
    return True

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("login"))

@app.route('/admin', methods=["GET", "POST"])
@login_required
def admin():
    return require_permission("a", # only admins can do this
                              lambda :admin_internal())

def admin_internal():
    if request.method == "POST":
        new_admins = [get_user(id=int(n)) for n in request.form.getlist('new-admins')]
        new_losers = [get_user(id=int(n)) for n in request.form.getlist('new-losers')]
        for u in new_admins:
            u.permissions = request.form["permissions"]
        for u in new_losers:
            u.permissions = ""

        db.session.commit()
        flash("Permissions updated.")
        return redirect(url_for("index"))

    return render_template('admin.html', user=current_user,
                                         user_list=User.query.all())

# Requires some amount of privileges to view page
def require_permission(permission_options, viewfun):
    for perm in permission_options:
        if perm in current_user.permissions:
            return viewfun()
    return render_template('permission-denied.html', user=current_user)
