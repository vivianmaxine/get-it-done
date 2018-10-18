from flask import Flask, request, redirect, render_template

app = Flask(__name__)
app.config['DEBUG'] = True

tasks = []


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task = request.form['task']  # connects to name in html form
        tasks.append(task)  # appends each task to tasks list
    return render_template('todos.html', title="Get It Done!", tasks=tasks)

app.run()
