from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from models import db, User, Pet
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
CORS(app)

# Configure SQLite DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///petconnect.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)

@app.route('/')
def home():
    return "Welcome to the PetConnect Flask Backend!"

# Registration Route
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print("📥 Register data:", data)

    try:
        hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(
            name=data['name'],
            email=data['email'],
            password=hashed_pw,
            role=data['role']
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully!"}), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Email already registered."}), 409

    except Exception as e:
        print("Error during registration:", e)
        return jsonify({"message": "Registration failed due to server error."}), 500

# Login Route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if user and bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({"message": "Login successful!", "role": user.role})

    return jsonify({"message": "Invalid credentials"}), 401

# Add Pet Route
@app.route('/add_pet', methods=['POST'])
def add_pet():
    data = request.get_json()

    try:
        new_pet = Pet(
            name=data['name'],
            breed=data['breed'],
            age=data['age'],
            description=data.get('description', ''),
            image_url=data.get('image_url', ''),
            pet_type=data['pet_type'],
            shelter_id=data['shelter_id']
        )
        db.session.add(new_pet)
        db.session.commit()
        return jsonify({"message": "Pet added successfully!"}), 201

    except Exception as e:
        print("Error adding pet:", e)
        return jsonify({"message": "Failed to add pet."}), 500

# Get All Pets Route
@app.route('/pets', methods=['GET'])
def get_pets():
    pets = Pet.query.all()
    pet_list = [
        {
            "id": pet.id,
            "name": pet.name,
            "breed": pet.breed,
            "age": pet.age,
            "description": pet.description,
            "image_url": pet.image_url,
            "pet_type": pet.pet_type,
            "shelter_id": pet.shelter_id
        }
        for pet in pets
    ]
    return jsonify(pet_list)

# DB create and run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)





