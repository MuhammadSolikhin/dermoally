from flask import Flask, request, jsonify
import numpy as np
import tensorflow as tf
from PIL import Image
import mysql.connector
import os
import logging
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

# Load the trained model
model = tf.keras.models.load_model('dermoally-modelv7.h5', compile=False)

# Labels should match those used in your training
labels = ['Acne', 'ActinicKeratosis', 'Blackheads', 'Herpes', 'Keloid', 'KeratosisSeborrheic', 'Milia', 'Pityriasis versicolor', 'Ringworm']

# Function to connect to MySQL database
def get_mysql_connection():
    return mysql.connector.connect(
        host='34.128.126.40',
        user='khin',
        password='khin123',
        database='capstone'
    )

def authenticate_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token is None:
            return jsonify({'error': 'Unauthorized'}), 401

        try:
            decoded_token = jwt.decode(token.split(' ')[1], app.config['SECRET_KEY'], algorithms=['HS256'])
            id_user = decoded_token['id_user']
            request.id_user = id_user
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 401
        except (jwt.InvalidTokenError, jwt.DecodeError):
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)

    return decorated_function

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and check_password_hash(user['password'], password):
        token = jwt.encode({'id_user': user['id_user'], 'exp': datetime.utcnow() + timedelta(hours=24)}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})

    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    name = data.get('name')

    hashed_password = generate_password_hash(password)

    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password, email, name) VALUES (%s, %s, %s, %s)', (username, hashed_password, email, name))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'User registered successfully'})

@app.route('/predict/recent', methods=['GET'])
@authenticate_user
def recent_predict():
    user_id = request.id_user

    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM skin_analyze WHERE id_useranalyze = %s ORDER BY date_analyze DESC LIMIT 5', (user_id,))
    recent_predictions = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(recent_predictions)

@app.route('/disease/<int:id>/medications', methods=['GET'])
def select_medication_ingredients(id):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM medication_ingredients WHERE id_disease_medication = %s', (id,))
    medications = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(medications)

@app.route('/history', methods=['GET'])
@authenticate_user
def history():
    user_id = request.id_user

    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT sa.date_analyze, sa.id_imageanalyze, sa.acne, sa.actinickeratosis, sa.blackheads, sa.herpes, 
               sa.keloid, sa.keratosisseborrheic, sa.milia, sa.pityriasis_versicolor, sa.ringworm, sa.skin_health,
               i.image_url
        FROM skin_analyze sa
        JOIN images i ON sa.id_imageanalyze = i.id_image
        WHERE sa.id_useranalyze = %s
        ORDER BY sa.date_analyze DESC
    ''', (user_id,))

    history_data = cursor.fetchall()
    cursor.close()
    conn.close()

    result = []
    for row in history_data:
        analyze_values = {
            'Acne': row['acne'],
            'ActinicKeratosis': row['actinickeratosis'],
            'Blackheads': row['blackheads'],
            'Herpes': row['herpes'],
            'Keloid': row['keloid'],
            'KeratosisSeborrheic': row['keratosisseborrheic'],
            'Milia': row['milia'],
            'Pityriasis versicolor': row['pityriasis_versicolor'],
            'Ringworm': row['ringworm']
        }
        history_item = {
            'date': row['date_analyze'].strftime('%Y-%m-%d %H:%M:%S'),
            'image_url': row['image_url'],
            'result_analyze': analyze_values,
            'skin_health': row['skin_health']
        }
        result.append(history_item)

    return jsonify(result)

@app.route('/favorites', methods=['GET'])
@authenticate_user
def select_favorite():
    user_id = request.id_user

    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM skin_analyze WHERE id_useranalyze = %s AND favorite = TRUE', (user_id,))
    favorite_predictions = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(favorite_predictions)

@app.route('/user', methods=['GET'])
@authenticate_user
def get_user():
    user_id = request.id_user

    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT username, email, name, profile_image_url FROM users WHERE id_user = %s', (user_id,))
    user_info = cursor.fetchone()
    cursor.close()
    conn.close()

    return jsonify(user_info)

@app.route('/predict', methods=['POST'])
@authenticate_user
def predict():
    user_id = request.id_user

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    image = Image.open(file)

    if image.mode != 'RGB':
        image = image.convert('RGB')

    image = image.resize((224, 224))
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)

    try:
        # Perform prediction
        prediction = model.predict(image)[0]  # Assume model output is 1D array
        analyze_values = prediction.tolist()  # Convert numpy array to Python list

        # Generate unique filename using timestamp and user ID
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        unique_filename = f"image_{timestamp}_{user_id}.jpg"

        # Save image locally (optional)
        save_path = os.path.join('static', unique_filename)
        image_pil = Image.fromarray((image[0] * 255).astype(np.uint8))
        image_pil.save(save_path)
        image_url = f'http://localhost:9000/static/{unique_filename}'

        current_time = datetime.now()

        # Save image URL to database and get the newly inserted id_image
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO images (id_userimage, image_url, date) VALUES (%s, %s, %s)', (user_id, image_url, current_time))
        conn.commit()

        cursor.execute('SELECT LAST_INSERT_ID()')
        id_image = cursor.fetchone()[0]

        # Analyze predictions to compute skin_health score
        above_threshold = sum(value > 0.5 for value in analyze_values)
        if above_threshold == 0:
            skin_health = 100
        elif above_threshold == 1:
            skin_health = random.randint(90, 95)
        elif above_threshold in [2, 3]:
            skin_health = random.randint(85, 89)
        elif above_threshold == 4:
            skin_health = random.randint(80, 84)
        else:
            skin_health = random.randint(75, 79)

        # Round confidence values to 3 decimal places
        analyze_values_rounded = {label: round(confidence, 3) for label, confidence in zip(labels, analyze_values)}

        # Save analysis results to database
        cursor.execute('INSERT INTO skin_analyze (id_useranalyze, id_imageanalyze, acne, actinickeratosis, blackheads, herpes, keloid, keratosisseborrheic, milia, pityriasis_versicolor, ringworm, date_analyze, skin_health) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                       (user_id, id_image, *analyze_values, current_time, skin_health))
        conn.commit()

        cursor.close()
        conn.close()

        prediction_results = {
            'date': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'image_url': image_url,
            'result_analyze': analyze_values_rounded,
            'skin_health': skin_health
        }

        return jsonify(prediction_results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_id_disease', methods=['GET'])
def get_id_disease():
    disease_name = request.args.get('disease_name')

    if not disease_name:
        return jsonify({'error': 'Parameter disease_name is required.'}), 400

    conn = get_mysql_connection()
    cursor = conn.cursor()

    query = 'SELECT id_disease FROM disease WHERE name = %s'
    cursor.execute(query, (disease_name,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        return jsonify({'id_disease': result[0]})
    else:
        return jsonify({'error': f'Disease with name "{disease_name}" not found.'}), 404

@app.route('/disease/info/<int:id>', methods=['GET'])
@authenticate_user
def get_disease_info(id):
    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM disease WHERE id_disease = %s', (id,))
    disease_info = cursor.fetchone()

    cursor.close()
    conn.close()

    if not disease_info:
        return jsonify({'error': f'Disease with ID {id} not found'}), 404

    # Adjust the response as needed based on your database schema
    disease_data = {
        'id_disease': disease_info[0],
        'name': disease_info[1],
        'overview': disease_info[2],
        'image_url': disease_info[3]
        # Add more fields as necessary
    }

    return jsonify(disease_data)


@app.route('/favorites/<int:id>', methods=['PUT'])
@authenticate_user
def update_favorite(id):
    user_id = request.id_user
    data = request.get_json()
    favorite_status = data.get('favorite')

    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE skin_analyze SET favorite = %s WHERE id_useranalyze = %s AND id_imageanalyze = %s', (favorite_status, user_id, id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Favorite status updated successfully'})

@app.route('/profile', methods=['PUT'])
@authenticate_user
def update_profile():
    user_id = request.id_user
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    profile_image_url = data.get('profile_image_url')

    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET email = %s, name = %s, profile_image_url = %s WHERE id_user = %s', (email, name, profile_image_url, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Profile updated successfully'})

@app.route('/process/<int:id>', methods=['GET'])
@authenticate_user
def select_process_by_id(id):
    user_id = request.id_user

    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM skin_analyze WHERE id_useranalyze = %s AND id_imageanalyze = %s', (user_id, id))
    process = cursor.fetchone()
    cursor.close()
    conn.close()

    return jsonify(process)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
