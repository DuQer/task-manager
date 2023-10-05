import sqlite3
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, create_refresh_token
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import secrets

from models import User, Task

secret_key = secrets.token_hex(16)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = secret_key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

jwt = JWTManager(app)
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)

@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)


@app.route('/create-user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        username = data.get('username')
        password = generate_password_hash(data.get('password'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return {'message': 'Username already exists'}, 409

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        user_id = new_user.id
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)

        return jsonify(access_token=access_token, refresh_token=refresh_token), 201

    except Exception as e:
        return {'message': f'An error occurred: {str(e)}'}, 500


@app.route('/update-user/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    try:
        new_username = request.json.get('new_username')
        if not new_username:
            return {'message': 'New username is required'}, 400

        user = User.query.get(user_id)
        if not user:
            return {'message': 'User not found'}, 404

        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user:
            return {'message': 'Username already exists'}, 409

        user.username = new_username
        db.session.commit()

        return {'message': 'Username updated successfully'}, 200

    except Exception as e:
        return {'message': f'An error occurred: {str(e)}'}, 500


@app.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return {'message': 'User not found'}, 404

        if current_user_id == user_id:
            return {'message': 'You do not have permission to delete this user'}, 403

        db.session.delete(user)
        db.session.commit()

        return {'message': 'User deleted successfully'}, 200

    except Exception as e:
        return {'message': f'An error occurred: {str(e)}'}, 500


@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    try:
        conn = sqlite3.connect('database/database.db')
        c = conn.cursor()

        c.execute('SELECT * FROM users')
        users = c.fetchall()

        conn.close()

        user_list = []
        for user in users:
            user_data = {
                'id': user[0],
                'username': user[1]
            }
            user_list.append(user_data)

        return jsonify(user_list), 200

    except Exception as e:
        return {'message': f'An error occurred: {str(e)}'}, 500


@app.route('/create-task', methods=['POST'])
@jwt_required()
def create_task():
    try:
        user_id = get_jwt_identity()

        conn = sqlite3.connect('database/database.db')
        c = conn.cursor()

        c.execute('SELECT * FROM users WHERE id=?', (user_id,))
        user = c.fetchone()

        if user is None:
            return {'message': 'User not found or your account has been deleted'}, 403

        title = request.json.get('title')
        description = request.json.get('description')
        creation_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        due_date = request.json.get('due_date')
        priority = request.json.get('priority')

        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
        table_exists = c.fetchone()

        if not table_exists:
            c.execute('''
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    creation_time TEXT,
                    due_date TEXT,
                    priority INTEGER
                )
            ''')

            conn.commit()

        c.execute('INSERT INTO tasks (user_id, title, description, creation_time, due_date, priority) VALUES (?, ?, ?, ?, ?, ?)',
                  (user_id, title, description, creation_time, due_date, priority))
        task_id = c.lastrowid

        conn.commit()
        conn.close()

        return jsonify({'task_id': task_id, 'message': 'Task created successfully'}), 201

    except Exception as e:
        return {'message': f'An error occurred: {str(e)}'}, 500


@app.route('/tasks/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_tasks(user_id):
    try:
        conn = sqlite3.connect('database/database.db')
        c = conn.cursor()

        c.execute('SELECT * FROM tasks WHERE user_id=?', (user_id,))
        tasks = c.fetchall()

        conn.close()

        task_list = []
        for task in tasks:
            task_dict = {
                'id': task[0],
                'user_id': task[1],
                'title': task[2],
                'description': task[3],
                'creation_time': task[4],
                'due_date': task[5],
                'priority': task[6]
            }
            task_list.append(task_dict)

        return jsonify(task_list), 200

    except Exception as e:
        return {'message': f'An error occurred: {str(e)}'}, 500


@app.route('/update-task/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    try:
        user_id = get_jwt_identity()

        conn = sqlite3.connect('database/database.db')
        c = conn.cursor()

        c.execute('SELECT * FROM users WHERE id=?', (user_id,))
        user = c.fetchone()

        if user is None:
            conn.close()
            return {'message': 'User not found or your account has been deleted'}, 403

        title = request.json.get('title')
        description = request.json.get('description')
        due_date = request.json.get('due_date')
        priority = request.json.get('priority')

        c.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
        task = c.fetchone()

        if not task:
            conn.close()
            return {'message': 'Task not found'}, 404

        if task[1] != user_id:
            conn.close()
            return {'message': 'You do not have permission to update this task'}, 403

        c.execute('UPDATE tasks SET title=?, description=?, due_date=?, priority=? WHERE id=?',
                  (title, description, due_date, priority, task_id))

        conn.commit()
        conn.close()

        return {'message': 'Task updated successfully'}, 200

    except Exception as e:
        return {'message': f'An error occurred: {str(e)}'}, 500


@app.route('/delete-task/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    try:
        current_user_id = get_jwt_identity()

        conn = sqlite3.connect('database/database.db')
        c = conn.cursor()

        c.execute('SELECT * FROM tasks WHERE id=? AND user_id=?', (task_id, current_user_id))
        task = c.fetchone()

        if not task:
            conn.close()
            return {'message': 'Task not found'}, 404

        c.execute('DELETE FROM tasks WHERE id=? AND user_id=?', (task_id, current_user_id))
        conn.commit()
        conn.close()

        return {'message': 'Task deleted successfully'}, 200

    except Exception as e:
        return {'message': f'An error occurred: {str(e)}'}, 500


@app.route('/all-tasks', methods=['GET'])
@jwt_required()
def get_all_tasks():
    try:
        conn = sqlite3.connect('database/database.db')
        c = conn.cursor()

        c.execute('SELECT * FROM tasks')
        tasks = c.fetchall()

        conn.close()

        task_list = []
        for task in tasks:
            task_data = {
                'id': task[0],
                'user_id': task[1],
                'title': task[2],
                'description': task[3],
                'creation_time': task[4],
                'due_date': task[5],
                'priority': task[6]
            }
            task_list.append(task_data)

        return jsonify(task_list), 200

    except Exception as e:
        return {'message': f'An error occurred: {str(e)}'}, 500


if __name__ == '__main__':
    app.run()
