API Documentation for CleanConnect
Overview
The CleanConnect API allows users to register, log in, request cleaning services, and manage connections between clients and cleaners. Below is the detailed documentation of the available API endpoints, including the request methods, request bodies, response formats, and descriptions.

Authentication
All API endpoints require authentication via JSON Web Tokens (JWT). To access the endpoints, include the JWT in the Authorization header as a Bearer token:

makefile
Authorization: Bearer <token>

Endpoints

1. User Registration
URL: /api/register

Method: POST

Description: Registers a new user (either a client or cleaner).

Request Body:

json
{
    "username": "user123",
    "email": "user@example.com",
    "password": "password123",
    "user_type": "cleaner",
    "service": "general house cleaning"
}
username: (String) The desired username.
email: (String) The user's email address.
password: (String) The user's password.
user_type: (String) Either client or cleaner.
service: (String, optional) Required if the user is a cleaner. Examples: general house cleaning, laundry.
Response:

json
{
    "message": "User registered successfully",
    "user_id": 1
}

2. User Login
URL: /api/login

Method: POST

Description: Authenticates a user and returns a JWT.

Request Body:

json
{
    "email": "user@example.com",
    "password": "password123"
}
email: (String) The user's email address.
password: (String) The user's password.
Response:

json
{
    "access_token": "your.jwt.token"
}

3. Connect with a Cleaner
URL: /api/connect

Method: POST

Description: Allows clients to connect with cleaners by specifying location and service type.

Request Body:

json
{
    "location": "Umoja",
    "service": "general house cleaning"
}
location: (String) The client's location.
service: (String) The type of cleaning service required.
Response:

json
{
    "message": "Request submitted successfully",
    "request_id": 10,
    "available_cleaners": [
        {
            "cleaner_id": 2,
            "name": "Cleaner Name",
            "service": "general house cleaning"
        },
        ...
    ]
}

4. Select a Cleaner
URL: /api/select_cleaner

Method: POST

Description: Allows clients to select a specific cleaner from the available options.

Request Body:

json
{
    "request_id": 10,
    "cleaner_id": 2
}
request_id: (Integer) The ID of the cleaning request.
cleaner_id: (Integer) The ID of the selected cleaner.
Response:

json
{
    "message": "Cleaner selected successfully",
    "status": "Connected",
    "cleaner_details": {
        "cleaner_id": 2,
        "name": "Cleaner Name",
        "service": "general house cleaning"
    }
}

5. Get User Profile
URL: /api/profile

Method: GET

Description: Retrieves the profile information of the logged-in user.

Response:

json
{
    "user_id": 1,
    "username": "user123",
    "email": "user@example.com",
    "user_type": "client",
    "requests": [
        {
            "request_id": 10,
            "location": "Umoja",
            "service": "general house cleaning",
            "status": "Connected"
        },
        ...
    ]
}
Error Handling
All API responses will follow a standard error format when an error occurs:

Response Format:

json
{
    "error": "Error message here"
}

Notes

Authentication: Make sure to authenticate users using JWT for secured access to the endpoints.
Data Validation: Proper validation should be performed on input data to prevent SQL injection, XSS, and other vulnerabilities.
Status Codes: Use appropriate HTTP status codes, such as 200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 404 Not Found, etc.