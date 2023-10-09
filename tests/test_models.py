import sys
import os
import pytest
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

from app import db, create_app
from models import User, Task


@pytest.fixture(scope='module')
def test_client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_create_and_retrieve_user(test_client):
    with test_client.application.app_context():
        db.session.query(User).delete()
        new_user = User(username="test_user", password="test_pass")
        db.session.add(new_user)
        db.session.commit()

        retrieved_user = User.query.filter_by(username="test_user").first()
        assert retrieved_user is not None
        assert retrieved_user.username == "test_user"


def test_create_and_retrieve_task(test_client):
    with test_client.application.app_context():
        db.session.query(Task).delete()
        db.session.query(User).delete()

        new_user = User(username="test_user", password="test_pass")
        db.session.add(new_user)
        db.session.commit()

        new_task = Task(user_id=new_user.id, title="Test task", description="This is a test", priority=1)
        db.session.add(new_task)
        db.session.commit()

        retrieved_task = Task.query.filter_by(title="Test task").first()
        assert retrieved_task is not None
        assert retrieved_task.title == "Test task"
        assert retrieved_task.user_id == new_user.id
