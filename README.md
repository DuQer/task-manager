# Task manager
Task Manager is a straightforward, RESTful application designed for efficient task management. It allows users to create their accounts and effectively manage their tasks.
The application needs a Postman to work. The task manager uses the JWT token for authorization, which is returned in Postman when creating a new user. The user sends JSON with the necessary information and access token (in header) to a given endpoint and receives a response from the API.
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
- SQLAlchemy
- Werkzeug
- Postman


## API Reference

#### Create new user

  ```json
POST /create-user/
```

| Parameter | Type | Description
| --- | --- | --- | 
| `username` | string | **Required.** Name of user  |
| `password` | string | **Required.** Password of user |

#### Update user

  ```json
PUT /update-user/{id}
```

| Parameter | Type | Description
| --- | --- | --- | 
| `id` | int | **Required.** ID of user  |
| `username` | string | **Required.** New name of user  |

#### Delete user

  ```json
DELETE /users/{id}
```
| Parameter | Type | Description
| --- | --- | --- | 
| `id` | int | **Required.** ID of user  |
#### Create new task

  ```json
POST /create-task/
```

| Parameter | Type | Description
| --- | --- | --- | 
| `title` | string | **Required.** Title of task |
| `description` | string | **Required.** Description of task |
| `due_date` | date | **Required.** Time limit of task |
| `priority` | integer | **Required.** Priority of task |

#### Get all user's tasks

```json
GET /tasks/
```

#### Update task

  ```json
PUT /update-task/{id}
```

| Parameter | Type | Description
| --- | --- | --- | 
| `title` | string | **Optional.** Title of task |
| `description` | string | **Optional.** Description of task |
| `due_date` | date | **Optional.** Time limit of task |
| `priority` | integer | **Optional.** Priority of task |

#### Delete task

```json
DELETE /tasks/{id}
```
| Parameter | Type | Description
| --- | --- | --- | 
| `id` | int | **Required.** ID of task  |

## System requirements
To run this application you need:
* Python 3.11.0 (or higher)
* Postman
* Docker

## Installation
To run this project use this command:
  ```
docker-compose up
```
