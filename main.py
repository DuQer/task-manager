import sqlite3
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash
from datetime import datetime
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'secret-key'
jwt = JWTManager(app)

refresh_tokens = {}


@app.route('/create-user', methods=['POST'])
def create_user():
    username = request.json.get('username')
    password = request.json.get('password')

    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()

    c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')

    c.execute('SELECT * FROM users WHERE username=?', (username,))
    existing_user = c.fetchone()
    if existing_user:
        return {'message': 'Username already exists'}, 409

    password_hash = generate_password_hash(password)

    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password_hash))

    conn.commit()
    conn.close()

    access_token = create_access_token(identity=username)

    return {'access_token': access_token}, 201


@app.route('/update-user/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user_id = get_jwt_identity()
    new_username = request.json.get('new_username')
    print(current_user_id)
    print(user_id)
    if not new_username:
        return {'message': 'New username is required'}, 400

    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()

    c.execute('SELECT * FROM users WHERE id=?', (user_id,))
    user = c.fetchone()

    if not user:
        return {'message': 'User not found'}, 404

    c.execute('SELECT * FROM users WHERE username=?', (new_username,))
    existing_user = c.fetchone()
    if existing_user:
        return {'message': 'Username already exists'}, 409

    c.execute('UPDATE users SET username=? WHERE id=?', (new_username, user_id))
    conn.commit()
    conn.close()

    return {'message': 'Username updated successfully'}, 200


@app.route('/refresh-token', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    print('lol')


@app.route('/create-task', methods=['POST'])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    title = request.json.get('title')
    description = request.json.get('description')
    creation_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    due_date = request.json.get('due_date')
    priority = request.json.get('priority')

    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()

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


@app.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    current_user_id = get_jwt_identity()

    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()

    c.execute('SELECT * FROM tasks WHERE user_id=?', (current_user_id,))
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


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    current_user_id = get_jwt_identity()

    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()

    c.execute('SELECT * FROM tasks WHERE id=? AND user_id=?', (task_id, current_user_id))
    task = c.fetchone()

    if not task:
        return {'message': 'Task not found'}, 404

    c.execute('DELETE FROM tasks WHERE id=? AND user_id=?', (task_id, current_user_id))
    conn.commit()
    conn.close()

    return {'message': 'Task deleted successfully'}, 200


if __name__ == '__main__':
    app.run()
