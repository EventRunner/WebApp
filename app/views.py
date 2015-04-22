from flask import render_template, request, redirect, flash, url_for, Response, Flask
from flask.ext.login import login_required, login_user, logout_user, current_user
from simplecrypt import decrypt
from datetime import datetime as dt
from models import User, get_user, Event, Task
from config import SECRET_KEY, CREATE_PIN
from app import app, db
import os, json

#####################################
# Regular pages
#####################################

@app.route('/')
@app.route('/main')
@app.route('/index')
@login_required
def index():
    return render_template('main.html', user=current_user)

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

# test routes
#####################################
@app.route('/test-task')
@login_required
def test_task():
	return render_template('test-task.html', user=current_user)

#####################################
# public API 
#####################################

""" helper function for loading dummy data from a file """
def generate_json_response(file, index):
	SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
	json_url = os.path.join(SITE_ROOT, "dummy_data", file)
	data = json.load(open(json_url))[index]
	resp = Response(response=json.dumps(data),
		status=200, \
		mimetype="application/json")
	return resp


def json_out(s):
    return Response(json.dumps(s), mimetype="application/json")

@app.route('/debug/dummy', methods=["GET"])
def dummy():
    event = Event.query.first()
    if not event:
        event = Event(name="Key Signing Party", is_private=False,
                      manager_id=current_user.id)
        db.session.add(event)

    users = User.query.all()
    if len(users) < 5:
        users = [User(name=u, password=u, email=u+"@example.com")
                 for u in ["user%d" % n for n in xrange(5)]]
        for u in users:
            db.session.add(u)
    else:
        users = users[1:]  # the first user is logged in and not dummy

    if len(event.volunteers) < 3:
        event.volunteers = users[:3]

    tasks = Task.query.all()
    if len(tasks) < 3:
        tasks = [Task(name=s, event_id=event.id, volunteers=[users[n]])
                 for n, s in enumerate(["Comb Eckhardt's beard",
                                        "Troll Kesden", "Surprise Cortina"])]
        for t in tasks:
            db.session.add(t)

    db.session.commit()

    return "Dummy data successfully created/verified"


def check_valid_new_event(form):
    str = ""
    # if 'is_private' not in form:
    #     str+="Event not added , you need to specify privacy!\n"
    if 'name' not in form:
        str+="Event not added , you need to specify the name!\n"
    if 'start_time' not in form or 'end_time' not in form:
        str+="Event not added , you need to specify the time!\n"
    start_time = form['start_time']
    end_time = form['end_time']
    if start_time > end_time:
        str+="Event not added , start time after end time!\n"
    if 'manager_id' not in form:
        str+="Event not added , no manager id!\n"
    if not User.query.filter_by(id=form['manager_id']).first():
        str+="Event not added , manager does not exist!\n"
    if 'user_list' not in form:
        str+="Event not added , no user list!\n"
    if 'task_list' not in form:
        str+="Event not added , no task list!\n"
    if str != "":
        return str
    return None





@app.route('/event', methods=["GET", "POST"])
def event_list():
    if request.method == "GET":
        events = [{"id": e.id, "name": e.name}
                for e in Event.query.order_by(Event.start_time.desc()).all()]
        return json_out({"status_code": 0, "events": events})
    if request.method == "POST":
        status = check_valid_new_event(request.form)
        if not status:
            return json_out({"status_code": 2,"status_msg":status})
        form = request.form
        is_private = True if 'is_private' in form else False
        e = Event(is_private=is_private,description=form['description']
                  ,name=form['name'],start_time=form['start_time']
                  ,end_time = form['end_time'],manager_id=current_user.id
                  ,user_list=[], task_list =[])
        db.session.add(e)
        db.session.commit()
        flash("Event "+e.name+" registered.")
        return json_out({"status_code": 0})




@app.route('/event/<event_id>', methods=["GET", "PUT"])
@login_required
def event(event_id):
    if request.method == "GET":
        e = Event.query.filter_by(id=event_id).first()
        if not e:
            return json_out({"status_code": 2})  # event doesn't exist
        result = {"status_code": 0,
                  "id": e.id,
                  "name": e.name,
                  "start_time": e.start_time,
                  "end_time": e.end_time,
                  "is_private": e.is_private,
                  "manager_id": e.manager_id,
                  "task_list": map(lambda t: t.id, e.tasks),
                  "user_list": map(lambda u: u.id, e.volunteers)
                 }
        return json_out(result)


    elif request.method == "PUT":
        pass


def check_valid_new_task(form):
    if 'name' not in form:
        flash("Task not added , you need to specify the name!")
        return False
    if 'start_time' not in form or 'end_time' not in form:
        flash("Task not added , you need to specify the time!")
        return False
    start_time = form['start_time']
    end_time = form['end_time']
    if start_time > end_time:
        flash("Task not added , start time after end time!")
        return False
    if 'event_id' not in form:
        flash("Task not added , no event id!")
        return False
    if not Event.query.filter_by(id=form['Event_id']).first():
        flash("Task not added , event does not exist!")
        return False
    if 'volunteers' not in form:
        flash("Task not added , no volunteers list!")
        return False
    return True


# @app.route('/task/<event_id>', methods=["GET", "POST"])
# def task_list(event_id):
#     if request.method == "GET":
#         tasks = [{"id": t.id, "name": t.name}
#                 for t in Task.query.filter_by(event_id=event_id).order_by(Event.start_time.desc()).all()]
#         return json_out({"status_code": 0, "events": tasks})
#     if request.method == "POST":
#         if not check_valid_new_task(request.form):
#             return json_out({"status_code": 2})
#         form = request.form
#         t = Task(description=form['description'],location=form['location']
#                   ,name=form['name'],start_time=form['start_time']
#                   ,end_time = form['end_time'],event_id=form['event_id']
#                   ,volunteers =form['volunteers'])
#         db.session.add(t)
#         db.session.commit()
#         flash("Task "+t.name+" Added.")
#         return json_out({"status_code": 0})

 


@app.route('/task/<task_id>', methods=["GET", "PUT"])
@login_required
def task(task_id):
    if request.method == "GET":
        t = Task.query.filter_by(id=task_id).first()
        if not t:
            return json_out({"status_code": 2})  # event doesn't exist
        result = {"status_code": 0,
                  "id": t.id,
                  "name": t.name,
                  "start_time": t.start_time,
                  "end_time": t.end_time,
                  "location": t.location,
                  "description": t.description,
                  "event_id": t.event_id,
                  "user_list": map(lambda u: u.id, t.volunteers)
                 }
        return json_out(result)

    elif request.method == "PUT":
        pass

def get_user_info(user_id):
    u = User.query.filter_by(id=user_id).first()
    if not u:
        return json_out({"status_code": 2})  # user doesn't exist
    result = {"status_code": 0,
              "id": u.id,
              "username": u.name,
              "managing_events": map(lambda e: e.id, u.managing_events if u.managing_events else []),
              "volunteering_events": map(lambda e: e.id, u.volunteering_events if u.managing_events else [])
             }
    return json_out(result)

@app.route('/me', methods=["GET"])
@login_required
def me():
    print "AsdfASDFASDFASDF"
    return get_user_info(current_user.id)


@app.route('/user/<user_id>', methods=["GET", "PUT"])
@login_required
def user(user_id):
    if request.method == "PUT":
        pass

    elif request.method == "GET":
        return get_user_info(user_id)


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
