from flask import Flask, request, redirect, render_template
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


class Task(db.Model):
    # every class has an id (primary key)
    id = db.Column(db.Integer, primary_key=True)
    # above extends db.Model class, db is the object created above (db)
    # helps store app-specific data
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean)
    # above uses Boolean to show whether task is completed or not

    # provide constuctor below

    def __init__(self, name):
        self.name = name  # name from input is the default
        self.completed = False  # False if NOT completed (default)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        # task = request.form['task']; connects to name in html form
        # tasks.append(task) - appends each task to simple tasks list

        task_name = request.form['task']  # pulls input from form
        new_task = Task(task_name)  # converts to a new task object
        db.session.add(new_task)  # puts new task object in db
        db.session.commit()

    # tasks = Task.query.all()  # gathers all list
    tasks = Task.query.filter_by(completed=False).all()
    # above shows all tasks where completed = False

    completed_tasks = Task.query.filter_by(completed=True).all()

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
    if request.method == 'POST':
        new_email = request.form['email']
        new_password = request.form['password']
        new_password_verify = request.form['verify']

        existing_user = User.query.filter_by(email=new_email).first()

        if not existing_user:

            if new_password == new_password_verify:
                new_user = User(new_email, new_password)

                db.session.add(new_user)
                db.session.commit()

                # TODO: REMEMBER THE USER AS LOGGED IN
                return redirect('/')
            else:
                return '<h1 style="color: red">Please make sure \
                your passwords match.</h1>'
        else:
            return '<h1 style="color: red">This user already exists.</h1>'

    return render_template('register.html')


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
            # TODO - REMEMBER THAT USER HAS LOGGED IN
            return redirect('/')
        else:
            # TODO - ERROR MESSAGES EXPLAINING WHY LOGIN FAILED
            return '<h1 style="color:red">ERROR ALERT!<br> \
            Email or Password Incorrect! :(</h1>'
    return render_template('login.html')


if __name__ == "__main__":
    app.run()
