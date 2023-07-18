import sqlite3

from flask import Flask, request, app, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from flask_jwt_extended import create_access_token, JWTManager
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'secret-key'
app.config['JWT_DEFAULT_REALM'] = 'jwt-realm'
jwt = JWTManager(app)

@app.route('/create-user', methods=['POST'])
def create_user():
    username = request.json.get('username')
    password = request.json.get('password')

    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()

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


def authenticate(username, password):
    print('####')


@app.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    print('####')


@app.route('/create-task', methods=['POST'])
@jwt_required()
def create_task():
    print('####')


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    print('####')


if __name__ == '__main__':
    app.run()
