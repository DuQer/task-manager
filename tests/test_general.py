import sqlite3
import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import app


def setup_module(module):
    app.config['ENV'] = 'test'

def create_test_users_table():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database/test_database.db"))
    print(f"Creating test database at: {db_path}")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_database.db'

    create_test_users_table()

    with app.test_client() as client:
        yield client


def create_user_and_get_token(client, username, password, db_path):
    data = {
        'username': username,
        'password': password
    }
    response = client.post('/create-user', json=data)

    assert response.status_code == 201

    access_token = response.json.get('access_token')

    return access_token


def test_update_user(client):

    access_token = create_user_and_get_token(client, 'testuser', 'testpassword', 'C:\\Users\\DuQer\\Desktop\\task-manager-master\\database\\test_database.db')

    data = {
        'new_username': 'new_testuser'
    }

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = client.put('/update-user/1', json=data, headers=headers)


    assert response.status_code == 200
    assert response.json['message'] == 'Username updated successfully'

    conn = sqlite3.connect("C:\\Users\\DuQer\\Desktop\\task-manager-master\\database\\test_database.db")
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=?', ('new_testuser',))
    updated_user = c.fetchone()
    conn.close()

    assert updated_user is not None


def test_delete_user(client):

    access_token = create_user_and_get_token(client, 'testuser', 'testpassword', 'C:\\Users\\DuQer\\Desktop\\task-manager-master\\database\\test_database.db')

    data = {
        'username': 'testuser',
        'password': 'testpassword'
    }

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = client.delete('/users/1', json=data, headers=headers)  # Zakładam, że usunięto użytkownika o ID=1

    assert response.status_code == 200
    assert response.json['message'] == 'User deleted successfully'

    conn = sqlite3.connect("C:\\Users\\DuQer\\Desktop\\task-manager-master\\database\\test_database.db")
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id=?', (1,))
    user = c.fetchone()
    conn.close()

    assert user is None


def test_get_users(client):

    conn = sqlite3.connect("C:\\Users\\DuQer\\Desktop\\task-manager-master\\database\\test_database.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('user1', 'password1'))
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('user2', 'password2'))
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('user3', 'password3'))
    conn.commit()
    conn.close()

    response = client.get('/users')

    assert response.status_code == 200
    users = response.json
