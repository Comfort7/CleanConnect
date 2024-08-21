CleanConnect

Owner: Comfort Ehachi

Project Overview
CleanConnect is a web application designed to bridge the gap between clients and professional cleaners within their country. The platform allows clients to register, request cleaning services, and connect with available cleaners. Cleaners can register their services, receive requests from clients, and manage their cleaning assignments through the platform.

Features
User Registration and Login: Clients and cleaners can register and log in securely.
JWT Authentication: Secure endpoints with JWT-based authentication.
Profile Management: Users can update their profile details such as username, email, phone number, and location.
Request Cleaning Services: Clients can create and manage requests for cleaning services.
Assign Cleaners: Clients can select and assign cleaners to their service requests.
Service Management: Cleaners can manage their service offerings and view requests assigned to them.
Admin Access: Special endpoints for admin operations.

Installation
Clone the repository:

bash

git clone https://github.com/yourusername/cleanconnect.git
cd cleanconnect
Create a virtual environment:

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

bash

pip install -r requirements.txt
Set up environment variables:
Create a .env file in the project root and add the following variables:

makefile
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
Initialize the database:

bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
Run the application:

bash
flask run

API Endpoints
Authentication
POST /api/register: Register a new user.
POST /api/login: Authenticate a user and retrieve a JWT token.
User Profile
GET /api/profile: Get the current user's profile details.
PUT /api/update_profile: Update the current user's profile.
Service Requests
POST /requests: Create a new cleaning request.
GET /requests: Retrieve a list of requests for the current user.
Cleaners
POST /api/connect_with_cleaner: Submit a request to connect with a cleaner.
POST /api/select_cleaner: Assign a cleaner to a specific request.
Admin
GET /api/admin: Access the admin panel.
Technologies Used
Flask: Micro web framework for building the API.
SQLAlchemy: ORM for managing database interactions.
Flask-Migrate: Database migrations.
Flask-Mail: Email notifications (if needed).
Flask-JWT-Extended: JWT-based authentication.
Contribution
Feel free to fork this repository and make your own contributions. Pull requests are welcome!

License
This project is licensed under the MIT License.
