from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from datetime import datetime
from login import login_required


app = Flask(__name__, static_url_path='/static')


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL('sqlite:///users.db')

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/average')
@login_required
def average():
    return render_template('average.html')


# Route to display the TODO list for the logged-in user
@app.route('/todo')
@login_required
def todo_list():
    user_id = session['user_id']

    # Retrieve TODOs for the current user from the database (sorted by date_added in ascending order)
    todos = db.execute("SELECT * FROM todos WHERE user_id = :user_id ORDER BY date_added ASC", user_id=user_id)

    return render_template('todo.html', todos=todos)

# Route to handle adding a new TODO for the logged-in user
@app.route('/add_todo', methods=['POST'])
@login_required
def add_todo():
    user_id = session['user_id']
    description = request.form.get('description')

    if description:
        # Add the new TODO to the database with the current date/time
        db.execute("INSERT INTO todos (user_id, description, date_added) VALUES (:user_id, :description, :date_added)",
                   user_id=user_id, description=description, date_added=datetime.now())

        flash('TODO added successfully!', 'success')
    else:
        flash('Please enter a valid TODO description.', 'danger')

    return redirect('/todo')

# Route to handle removing a TODO for the logged-in user
@app.route('/remove_todo', methods=['POST'])
@login_required
def remove_todo():
    user_id = session['user_id']
    todo_id = request.form.get('todo_id')

    # Make sure the logged-in user owns the todo_id before removing it
    todo = db.execute("SELECT * FROM todos WHERE id = :todo_id AND user_id = :user_id", todo_id=todo_id, user_id=user_id)

    if todo:
        # Remove the TODO from the database
        db.execute("DELETE FROM todos WHERE id = :todo_id", todo_id=todo_id)
        flash('TODO removed successfully!', 'success')
    else:
        flash('Failed to remove TODO.', 'danger')

    return redirect('/todo')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        if len(rows) > 0:
            flash('Username already taken', 'danger')
            return redirect('/register')

        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", username=username, password=password)

        flash('Registration successful! Please log in.', 'success')
        return redirect('/login')

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        rows = db.execute("SELECT * FROM users WHERE username = :username AND password = :password",
                           username=username, password=password)
        if len(rows) != 1:
            flash('Invalid username or password', 'danger')
            return redirect('/login')
        session['user_id'] = rows[0]['id']

        flash('Login successful!', 'success')
        return redirect('/')

    return render_template('login.html')


@app.route('/logout')
def logout():
    # Clear the user session to log out the user
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect('/login')
