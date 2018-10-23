from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
# above imports SQLAlchemy class from flask_sqlalchemy module

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'mysql+pymysql://get-it-done:getitdone@localhost:8889/get-it-done'
# above tells app how to connect to database
# connection string used to connect to database
app.config['SQLALCHEMY_ECHO'] = True
# above lets you see actual SQL queries in command line by SQLAlchemy

db = SQLAlchemy(app)  # creates db object by binding app w/ db

# create persistent class representing the app-specific data
# instead of using just a simple list like tasks = []

# set secret key up below for session
app.secret_key = 'Za8-eX=$fdQE!^Wr'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    # specify that a user as many tasks (connect to task class)
    tasks = db.relationship('Task', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password


class Task(db.Model):
    # every class has an id (primary key)
    id = db.Column(db.Integer, primary_key=True)
    # above extends db.Model class, db is the object created above (db)
    # helps store app-specific data
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean)
    # above uses Boolean to show whether task is completed or not

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # make owner an actual user object by connecting to User() with ID

    # provide constuctor below
    # create owner in constructor for each instance of a task
    def __init__(self, name, owner):
        self.name = name  # name from input is the default
        self.completed = False  # False if NOT completed (default)
        self.owner = owner


@app.before_request
def require_login():
    # check for existence of user email in session
    # allowed routes allows people to view page even when not in session
    allowed_routes = ['register', 'login']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/', methods=['POST', 'GET'])
def index():

    # helps create task using the owner whose info was retreived
    # using the email from the current session
    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        # task = request.form['task']; connects to name in html form
        # tasks.append(task) - appends each task to simple tasks list

        task_name = request.form['task']  # pulls input from form
        # get the user/owner and then apply task to user (below)

        new_task = Task(task_name, owner)  # converts to a new task object
        db.session.add(new_task)  # puts new task object in db
        db.session.commit()

    # tasks = Task.query.all()  # gathers all list

    # make sure you specify that owner of given task is the same as
    # the owner you're currently working with in the session who
    # made the request
    # left is querying for tasks based on value of owner property
    # right is based on owner retrieved from session information

    tasks = Task.query.filter_by(completed=False, owner=owner).all()
    # above shows all tasks where completed = False

    completed_tasks = Task.query.filter_by(completed=True, owner=owner).all()

    # add additional filter of who owns the task (below)

    return render_template(
        'todos.html', title="Get It Done!",
        tasks=tasks, completed_tasks=completed_tasks)
    # todos.html is a positional argument
    # tasks=tasks is a key word argument

# refers to form in todos.html where you select a task to delete it


@app.route('/delete-task', methods=['POST'])
def delete_task():
    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    # instead of deleting, will change completed property to True or 1
    task.completed = True  # True is 1 (completed), False is 0 (not completed)
    db.session.add(task)
    db.session.commit()
    # db.session.delete(task)
    # db.session.commit()

    return redirect('/')


# REGISTER HANDLER
@app.route('/register', methods=['GET', 'POST'])
def register():
    entered_email = ''
    existing_user_error = ''
    password_mismatch = ''
    password_length_error = ''
    email_format_error = ''

    if request.method == 'POST':
        new_email = request.form['email']
        entered_email = new_email

        new_password = request.form['password']
        new_password_verify = request.form['verify']

        existing_user = User.query.filter_by(email=new_email).first()
        print(existing_user)

        if not existing_user:

            if new_password == new_password_verify:
                new_user = User(new_email, new_password)
                if '@' in new_email and '.' in new_email:
                    if len(new_password) <= 5 or len(new_password) > 20:
                        password_length_error = "Your password should be \
                        5-20 characters long."
                    else:
                        db.session.add(new_user)
                        db.session.commit()
                    # TODO: REMEMBER THE USER AS LOGGED IN (BELOW)
                        session['email'] = new_email
                        flash(
                            "You have successfully registered for Get It\
                             Done!", 'flash_success')
                        return redirect('/')
                else:
                    email_format_error = "Please enter a valid email."

            else:
                password_mismatch = "Please make sure your passwords match."
                # return '<h1 style="color: red">Please make sure \
                # your passwords match.</h1>'
        else:
            existing_user_error = "This user already exists."
            # return '<h1 style="color: red">This user already exists.</h1>'

    return render_template(
        'register.html',
        existing_user_error=existing_user_error,
        password_mismatch=password_mismatch,
        entered_email=entered_email,
        email_format_error=email_format_error,
        password_length_error=password_length_error)


# LOGIN HANDLER
@app.route('/login', methods=['GET', 'POST'])
def login():
    # first, check for request type;
    # GET just return form, POST needs to get data
    if request.method == 'POST':
        login_email = request.form['email']
        login_password = request.form['password']

        # verify password by retrieving user with given email from db
        # and seeing if it equals the enteres password
        user = User.query.filter_by(email=login_email).first()

        # below, "if user" checks to see if above condition met
        # below, "user.password == password" checks to see if
        # entered pw = db pw
        if user and user.password == login_password:
            # TODO - REMEMBER THAT USER HAS LOGGED IN (BELOW)
            session['email'] = login_email
            # flash message to verify they logged in (below)
            flash("You have successfully logged in.", 'flash_success')
            return redirect('/')
        else:
            # TODO - ERROR MESSAGES EXPLAINING WHY LOGIN FAILED
            flash(
                "User does not exist or password is incorrect.", 'flash_fail')
    return render_template('login.html')


@app.route('/logout')
def logout():
    del session['email']
    flash("You have successfully logged out.", 'flash_success')
    return redirect('/')

if __name__ == "__main__":
    app.run()
