class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


class Task(object):
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description


users = [
    User(1, 'user1', 'password1'),
    User(2, 'user2', 'password2')
]

tasks = {}