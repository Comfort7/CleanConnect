import os
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
mail = Mail(app)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default_key_if_not_set')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # Token expiration time

jwt = JWTManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)
    phone_number = db.Column(db.String(20))
    location = db.Column(db.String(200), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='client')  # 'client' or 'cleaner'
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.phone_number}', '{self.role}', '{self.date_created}', '{self.last_login}')"

class CleanerRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    service = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='Pending')
    cleaner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cleaner = db.relationship('User', foreign_keys=[cleaner_id])
    
class CleanerService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service = db.Column(db.String(100), nullable=False)

    user = db.relationship('User', backref=db.backref('services', lazy=True))

    def __repr__(self):
        return f"CleanerService('{self.user.username}', '{self.service}')"
    
# Seeding Function
def seed_data():
    # Clean up the existing data
    db.drop_all()
    db.create_all()

    # Seed data for cleaners
    cleaners = [
        {
            "username": "cleaner1",
            "email": "cleaner1@example.com",
            "phone_number": "+12345678901",
            "location": "Kenya",
            "password": "password1",
            "role": "cleaner",
            "services": ["General House Cleaning", "Laundry"]
        },
        {
            "username": "cleaner2",
            "email": "cleaner2@example.com",
            "phone_number": "+12345678902",
            "location": "Kenya",
            "password": "password2",
            "role": "cleaner",
            "services": ["House Cleaning with Laundry"]
        },
        {
            "username": "cleaner3",
            "email": "cleaner3@example.com",
            "phone_number": "+12345678903",
            "location": "Kenya",
            "password": "password3",
            "role": "cleaner",
            "services": ["General House Cleaning", "Laundry", "House Cleaning with Laundry"]
        },
    ]

    # Insert data into the database
    for cleaner_data in cleaners:
        cleaner = User(
            username=cleaner_data['username'],
            email=cleaner_data['email'],
            phone_number=cleaner_data['phone_number'],
            location=cleaner_data['location'],
            role=cleaner_data['role']
        )
        cleaner.set_password(cleaner_data['password'])
        db.session.add(cleaner)
        db.session.commit()

        for service in cleaner_data['services']:
            cleaner_service = CleanerService(user_id=cleaner.id, service=service)
            db.session.add(cleaner_service)
        
        db.session.commit()

    print("Database has been seeded successfully!")

# Route to trigger seeding
@app.route('/api/seed', methods=['POST'])
def seed():
    try:
        seed_data()
        return jsonify({'message': 'Database seeded successfully!'}), 200
    except Exception as e:
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

@app.route('/api/test', methods=['POST'])
def test():
    if request.content_type != 'application/json':
        return jsonify({'message': 'Unsupported Media Type. Please send JSON data.'}), 415
    
    data = request.get_json()
    return jsonify({'received': data}), 200

@app.route('/api/login', methods=['POST'])
def login():
    if request.content_type != 'application/json':
        return jsonify({'message': 'Unsupported Media Type. Please send JSON data.'}), 415
    
    data = request.get_json()
    identifier = data.get('identifier')  # This can be either email or phone number
    password = data.get('password')

    if not identifier or not password:
        return jsonify({'message': 'Please fill out all required fields.'}), 400

    user = User.query.filter((User.email == identifier) | (User.phone_number == identifier)).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify({'message': 'Login successful!', 'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid credentials. Please try again.'}), 401

@app.route('/api/register', methods=['POST'])
def register():
    if request.content_type != 'application/json':
        return jsonify({'message': 'Unsupported Media Type. Please send JSON data.'}), 415
    
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    phone_number = data.get('phone_number')
    password = data.get('password')
    role = data.get('role')
    services = data.get('services') if role == 'cleaner' else None
    country = data.get('country')

    if not username or not email or not password or not country:
        return jsonify({'message': 'Please fill out all required fields.'}), 400

    try:
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'message': 'A user with this email already exists.'}), 400

        new_user = User(username=username, email=email, phone_number=phone_number, 
                        location=country, role=role)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        if role == 'cleaner' and services:
            services_list = services.split(',')
            for service in services_list:
                cleaner_service = CleanerService(user_id=new_user.id, service=service.strip())
                db.session.add(cleaner_service)
            db.session.commit()

        return jsonify({'message': 'Registration successful!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500
    
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/api/connect_with_cleaner', methods=['POST'])
@jwt_required()
def connect_with_cleaner():
    if request.content_type != 'application/json':
        return jsonify({'message': 'Unsupported Media Type. Please send JSON data.'}), 415
    
    data = request.get_json()
    location = data.get('location')
    service = data.get('service')

    if not location or not service:
        return jsonify({'message': 'Location and service are required.'}), 400

    cleaner_request = CleanerRequest(location=location, service=service)
    db.session.add(cleaner_request)
    db.session.commit()

    cleaners = User.query.filter_by(role='cleaner').all()
    cleaner_profiles = [
        {
            'id': cleaner.id,
            'username': cleaner.username,
            'email': cleaner.email,
            'phone_number': cleaner.phone_number,
            'location': cleaner.location,
            'services': [service.service for service in cleaner.services]
        } for cleaner in cleaners
    ]

    return jsonify({
        'message': 'Your request has been submitted!',
        'available_cleaners': cleaner_profiles
    }), 201

@app.route('/api/select_cleaner', methods=['POST'])
@jwt_required()
def select_cleaner():
    if request.content_type != 'application/json':
        return jsonify({'message': 'Unsupported Media Type. Please send JSON data.'}), 415
    
    data = request.get_json()
    cleaner_id = data.get('cleaner_id')
    request_id = data.get('request_id')

    if not cleaner_id or not request_id:
        return jsonify({'error': 'Cleaner ID and Request ID are required.'}), 400

    cleaner = User.query.get(int(cleaner_id))
    cleaner_request = CleanerRequest.query.get(int(request_id))

    if not cleaner or not cleaner_request:
        return jsonify({'error': 'Cleaner or request not found.'}), 404

    if cleaner_request.cleaner_id:
        return jsonify({'message': 'This request has already been assigned to a cleaner.'}), 400

    cleaner_request.cleaner_id = cleaner.id
    cleaner_request.status = 'Assigned'
    db.session.commit()

    return jsonify({'message': f'Cleaner {cleaner.username} has been successfully assigned to the request.'}), 200

@app.route('/requests/<int:request_id>/update_status', methods=['PUT'])
@jwt_required()
def update_status(request_id):
    current_user = get_jwt_identity()
    cleaning_request = CleanerRequest.query.get_or_404(request_id)

    if current_user['role'] == 'client' and cleaning_request.client_id != current_user['id']:
        return jsonify({'message': 'Unauthorized access'}), 403
    if current_user['role'] == 'cleaner' and cleaning_request.cleaner_id != current_user['id']:
        return jsonify({'message': 'Unauthorized access'}), 403

    data = request.get_json()
    cleaning_request.status = data['status']
    db.session.commit()
    return jsonify({'message': 'Status updated successfully'}), 200

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found.'}), 404

    profile_data = {
        'username': user.username,
        'email': user.email,
        'phone_number': user.phone_number,
        'location': user.location,
        'role': user.role
    }

    if user.role == 'client':
        requests = CleanerRequest.query.filter_by(location=user.location, status='Assigned').all()
        assigned_cleaners = [
            {
                'cleaner_id': req.cleaner_id,
                'cleaner_name': User.query.get(req.cleaner_id).username,
                'service': req.service
            } for req in requests
        ]
        profile_data['assigned_cleaners'] = assigned_cleaners

    elif user.role == 'cleaner':
        cleaner_requests = CleanerRequest.query.filter_by(cleaner_id=user.id).all()
        assigned_clients = [
            {
                'request_id': req.id,
                'client_name': User.query.get(req.cleaner_id).username,
                'service': req.service
            } for req in cleaner_requests
        ]
        profile_data['assigned_clients'] = assigned_clients

    return jsonify(profile_data), 200

@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'message': 'You have been logged out.'}), 200

@app.route('/api/contact', methods=['GET'])
def contact():
    return jsonify({'email': 'contact@example.com', 'phone_number': '+123456789'}), 200

@app.route('/api/update_profile', methods=['PUT'])
@jwt_required()  # Ensure the user is authenticated
def update_profile():
    current_user_id = get_jwt_identity()  # Get the current user's ID from the token
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found.'}), 404

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    phone_number = data.get('phone_number')
    location = data.get('location')

    if username:
        user.username = username
    if email:
        user.email = email
    if phone_number:
        user.phone_number = phone_number
    if location:
        user.location = location

    try:
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500
    
@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [
        {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone_number': user.phone_number,
            'location': user.location,
            'role': user.role
        } for user in users
    ]
    return jsonify(user_list), 200

@app.route('/api/cleaner_services', methods=['GET'])
def get_cleaner_services():
    services = CleanerService.query.all()
    service_list = [
        {
            'user_id': service.user_id,
            'service': service.service
        } for service in services
    ]
    return jsonify(service_list), 200

if __name__ == '__main__':
    app.run(debug=True)
