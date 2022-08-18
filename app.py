from distutils.log import error
from flask import Flask, render_template, redirect, url_for, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flask_admin:flask@localhost:5432/todoapp'
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todoLists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo ID:{self.id}, Description: {self.description}, Completed: {self.completed}, List: {self.list_id} >'

class Todo_List(db.Model):
    __tablename__ = 'todoLists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref='list', lazy=True)

    def __repr__(self):
        return f'<Todo_List ID: {self.id}, name: {self.name}, todos: {self.todos}>'

db.create_all()

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    # Using 'form' to receive data
    # description = request.form.get('description', '')

    #Using AJAX to receive data
    try:
        description = request.get_json()['description']
        list_id = request.get_json()['list_id']
        todo = Todo(description=description)
        active_list = Todo_List.query.get(list_id)
        todo.list = active_list
        db.session.add(todo)
        db.session.commit()
        body['id'] = todo.id
        body['completed'] = todo.completed
        body['description'] = todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort (500)
    else:

    # Using 'form' to send data
    # return redirect(url_for('index'))

        return jsonify(body)

# Controller for set completed
@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def update_todo(todo_id):
    error = False
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return redirect(url_for('index'))

# Controller for delete
@app.route('/todos/<todo_id>/delete', methods=['DELETE'])
def delete_todo(todo_id):
    error = False
    try:
        todo = Todo.query.get(todo_id)
        db.session.delete(todo)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify({ 'success': True})

@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    lists=Todo_List.query.all(),
    active_list=Todo_List.query.get(list_id),
    todos=Todo.query.filter_by(list_id=list_id).order_by('id').all()
    return render_template('index.html', lists=lists, active_lists=active_list, todos=todos)

@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)