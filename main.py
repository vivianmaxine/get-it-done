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

    return render_template('todos.html', title="Get It Done!",
            tasks=tasks, completed_tasks=completed_tasks)

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

if __name__ == "__main__":
    app.run()
