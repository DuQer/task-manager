from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, create_refresh_token
from werkzeug.security import generate_password_hash
from datetime import timedelta
import secrets

from app import create_app, db
from models import User, Task

app = create_app()


secret_key = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/DuQer/Desktop/task-manager-master/database/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = secret_key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)


migrate = Migrate(app, db)
jwt = JWTManager(app)


@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)


@app.route('/create-user', methods=['POST'])
def create_user():
    with app.app_context():
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
        users = User.query.all()
        user_list = [{'id': user.id, 'username': user.username} for user in users]
        return jsonify(user_list), 200
    except Exception as e:
        return {'message': f'An error occurred: {str(e)}'}, 500


@app.route('/create-task', methods=['POST'])
@jwt_required()
def create_task():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if user is None:
            return {'message': 'User not found or your account has been deleted'}, 403

        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        due_date = data.get('due_date')
        priority = data.get('priority')

        new_task = Task(user_id=user_id, title=title, description=description, due_date=due_date, priority=priority)
        db.session.add(new_task)
        db.session.commit()

        return jsonify({'task_id': new_task.id, 'message': 'Task created successfully'}), 201

    except Exception as e:
        return {'message': f'An error occurred: {str(e)}'}, 500


@app.route('/tasks/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_tasks(user_id):
    try:
        tasks = Task.query.filter_by(user_id=user_id).all()
        task_list = [{'id': task.id, 'title': task.title, 'description': task.description, 'due_date': task.due_date, 'priority': task.priority} for task in tasks]
        return jsonify(task_list), 200
    except Exception as e:
        return {'message': f'An error occurred: {str(e)}'}, 500


@app.route('/update-task/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    try:
        user_id = get_jwt_identity()
        task = Task.query.get(task_id)

        if task is None:
            return {'message': 'Task not found'}, 404

        if task.user_id != user_id:
            return {'message': 'You do not have permission to update this task'}, 403

        data = request.get_json()
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.due_date = data.get('due_date', task.due_date)
        task.priority = data.get('priority', task.priority)

        db.session.commit()

        return {'message': 'Task updated successfully'}, 200

    except Exception as e:
        return {'message': f'An error occurred: {str(e)}'}, 500


@app.route('/delete-task/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    try:
        user_id = get_jwt_identity()
        task = Task.query.get(task_id)

        if task is None:
            return {'message': 'Task not found'}, 404

        if task.user_id != user_id:
            return {'message': 'You do not have permission to delete this task'}, 403

        db.session.delete(task)
        db.session.commit()

        return {'message': 'Task deleted successfully'}, 200

    except Exception as e:
        return {'message': f'An error occurred: {str(e)}'}, 500


@app.route('/all-tasks', methods=['GET'])
@jwt_required()
def get_all_tasks():
    try:
        tasks = Task.query.all()
        task_list = [
            {
                'id': task.id,
                'user_id': task.user_id,
                'title': task.title,
                'description': task.description,
                'creation_time': task.creation_time,
                'due_date': task.due_date,
                'priority': task.priority
            }
            for task in tasks
        ]
        return jsonify(task_list), 200
    except Exception as e:
        return {'message': f'An error occurred: {str(e)}'}, 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
