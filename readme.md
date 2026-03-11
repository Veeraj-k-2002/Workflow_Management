# Workflow Management API

A Workflow Management System built with FastAPI and PostgreSQL where users can sign up, log in, log out, and manage tasks securely. The project implements authentication, CRUD operations, and JWT-based token management.

## Table of Contents
- [Features](#features)
- [Database Schema](#database-schema)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Future Enhancements](#future-enhancements)

## Features
- **User Authentication:** Sign up, login, logout, and refresh token functionality.
- **User Management:** Get user details.
- **Workflow Management:** Create, read, update, and delete tasks.
- **JWT Authentication:** Secure routes with JWT tokens.
- **Task Assignment:** Each task is associated with a user (`owner_id`).

## Database Schema

### Users Table
| Column | Type | Description |
|--------|------|------------|
| id     | UUID | Primary key |
| name   | varchar | User full name |
| email  | varchar | Unique user email |
| country_code | varchar | Country code for phone |
| phone | varchar | User phone number |
| year_of_birth | int | Year of birth |
| gender | varchar | Gender |

### User Credentials Table
| Column               | Type      | Description                  |
|----------------------|-----------|------------------------------|
| user_id              | UUID      | Foreign key to users.id      |
| username             | varchar   | Login username               |
| password_hash        | varchar   | Hashed password              |
| refresh_token        | UUID      | Refresh token for JWT        |
| refresh_token_expiry | int       | Expiry time for refresh token|
| created_at           | timestamp | Account creation timestamp   |
| updated_at           | timestamp | Last update timestamp        |

### Tasks Table
| Column          | Type       | Description                     |
|-----------------|------------|---------------------------------|
| id              | UUID       | Primary key                     |
| title           | varchar    | Task title                      |
| description     | text       | Task description                |
| status          | varchar    | Task status (e.g., Pending/Done)|
| priority        | varchar    | Task priority (High/Medium/Low) |
| due_date        | timestamp  | Task due date                   |
| owner_id        | UUID       | Foreign key to users.id         |
| created_at      | timestamp  | Task creation timestamp         |
| updated_at      | timestamp  | Last update timestamp           |


## Tech Stack
- **Backend:** Python, FastAPI  
- **Database:** PostgreSQL  
- **Authentication:** JWT Tokens  
- **ORM:** SQLAlchemy / asyncpg  



## Installation
cd task-management

Create a virtual environment and activate it:
python -m venv venv
# Windows
venv\Scripts\activate



Install dependencies:- 
pip install -r requirements.txt


Running the Project:- 
uvicorn main:app --reload


Visit http://127.0.0.1:8000/api/v1/docs to see the Swagger UI and test my API endpoints.


API Endpoints


Auth Endpoints -->

| Method | Endpoint       | Description         |
| ------ | -------------- | ------------------- |
| POST   | /signup_user   | Register a new user |
| POST   | /login_user    | Login user          |
| POST   | /logout_user   | Logout user         |
| GET    | /get_user/{id} | Get user details    |


Task Endpoints -->

| Method | Endpoint          | Description       |
| ------ | ----------------- | ----------------- |
| POST   | /create_task      | Create a new task |
| GET    | /tasks/{id}       | Get task by ID    |
| GET    | /tasks/           | Get all tasks     |
| PUT    | /update_task/{id} | Update task by ID |
| DELETE | /delete_task/{id} | Delete task by ID |


Authentication-->
-JWT Token: Required for all task operations.
-Refresh Token: Implemented to refresh access tokens securely.

Future Enhancements -->
-Add role-based access (admin, regular user).
-Implement task notifications / reminders.
-Add task comments or attachments.
-Include filtering and sorting tasks by priority, due date, etc.
