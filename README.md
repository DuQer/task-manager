# Task manager
Task Manager is a straightforward, RESTful application designed for efficient task management. It allows users to create their accounts and effectively manage their tasks.
The application needs a Postman to work. The task manager uses the JWT token for authorization, which is returned in Postman when creating a new user. The user sends JSON with the necessary information to a given endpoint and receives a response from the API. 
For example, the JSON for the task creation process should look like this:

  ```json
{
  "title": "Example Task",
  "description": "This is an example task",
  "due_date": "2023-07-31",
  "priority": 1
}
```

## Technology stack
- Python
- Flask
- JWT token
- SQLite
- Werkzeug
- Postman


## API Reference

#### Create new user

  ```json
POST /create-user/
```

| Parameter | Type | Description
| --- | --- | --- | 
| `username` | string | Name of user  |
| `password` | string | Password of user |

#### Create new task

  ```json
POST /create-task/
```

| Parameter | Type | Description
| --- | --- | --- | 
| `title` | string | Title of task |
| `description` | string | Description of task |
| `due_date` | date | Time limit of task |
| `priority` | integer | Priority of task |

## System requirements
To run this application you need:
* Python 3.11.0 (or higher)
* Postman
