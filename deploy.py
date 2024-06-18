from flask import Flask, request, jsonify
import numpy as np
import tensorflow as tf
from PIL import Image
import mysql.connector
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

# Load the trained model (adjust the path as needed)
model = tf.keras.models.load_model('dermoally-modelv7.h5', compile=False)

# Labels should match those used in your training
labels = ['Acne', 'ActinicKeratosis', 'Blackheads', 'Herpes', 'Keloid', 'KeratosisSeborrheic', 'Milia', 'Pityriasis versicolor', 'Ringworm']

# Function to connect to MySQL database
def get_mysql_connection():
    return mysql.connector.connect(
        host='34.128.126.40',
        user='root',
        password='myCpastone1234',
        database='capstone'
    )

def authenticate_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token is None:
            return jsonify({'message': 'Unauthorized'}), 401

        try:
            decoded_token = jwt.decode(token.split(' ')[1], app.config['SECRET_KEY'], algorithms=['HS256'])
            id_user = decoded_token['id_user']
            request.id_user = id_user
        except jwt.ExpiredSignatureError:
            return jsonify({'error': True, 'message': 'Expired token'}), 401
        except (jwt.InvalidTokenError, jwt.DecodeError):
            return jsonify({'error': True, 'message': 'Invalid token'}), 401

        return f(*args, **kwargs)

    return decorated_function

@app.route('/', methods=['GET'])
def get_message():
    return jsonify(message='Hey, your app is working')

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

    if not user:
        return jsonify({'error': True, 'message': 'Username not registered'}), 400

    if user and not check_password_hash(user['password'], password):
        return jsonify({'error': True, 'message': 'Incorrect password'}), 400

    if user and check_password_hash(user['password'], password):
        token = jwt.encode({'id_user': user['id_user'], 'exp': datetime.utcnow() + timedelta(hours=24)}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'error': False, 'message': 'Login successfully', 'token': token})

    return jsonify({'error': True, 'message': 'Invalid credentials'}), 400


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

    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': True, 'message': 'Username already exists'}), 400

    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': True, 'message': 'Email already exists'}), 400

    cursor.execute('INSERT INTO users (username, password, email, name) VALUES (%s, %s, %s, %s)', (username, hashed_password, email, name))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'error': False, 'message': 'User registered successfully'})


@app.route('/predict/recent', methods=['GET'])
@authenticate_user
def recent_predict():
    user_id = request.id_user

    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('''
            SELECT sa.id_analyze, sa.favorite, sa.date_analyze, sa.id_imageanalyze, sa.acne, sa.actinickeratosis, sa.blackheads, sa.herpes, 
                    sa.keloid, sa.keratosisseborrheic, sa.milia, sa.pityriasis_versicolor, sa.ringworm, sa.skin_health,
                    i.image_url
            FROM skin_analyze sa
            JOIN images i ON sa.id_imageanalyze = i.id_image
            WHERE sa.id_useranalyze = %s
            ORDER BY sa.date_analyze DESC
            LIMIT 5
        ''', (user_id,))

        recent_predictions = cursor.fetchall()

        result = []
        for row in recent_predictions:
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

            # Find the disease with the highest confidence
            disease_detection_label = max(analyze_values, key=analyze_values.get)
            disease_detection_confidence = analyze_values[disease_detection_label]

            # Get the id_disease from the database based on the disease name
            cursor.execute('SELECT id_disease, image_url, overview FROM disease WHERE name = %s', (disease_detection_label,))
            id_disease_result = cursor.fetchone()

            if id_disease_result:
                id_disease = id_disease_result['id_disease']
                disease_image_url = id_disease_result['image_url']
                disease_overview = id_disease_result['overview']
            else:
                id_disease = None
                disease_image_url = None
                disease_overview = None

            # Get medication ingredients for the detected disease
            medication_ingredients = []
            if id_disease:
                cursor.execute('SELECT * FROM medication_ingredients WHERE id_disease_medication = %s', (id_disease,))
                medication_ingredients = cursor.fetchall()

            # Log the medication ingredients for debugging
            logging.debug(f"Medication ingredients for disease {disease_detection_label}: {medication_ingredients}")

            recent_item = {
                'id_analyze': row['id_analyze'],  
                'favorite': row['favorite'], 
                'date': row['date_analyze'].strftime('%Y-%m-%d %H:%M:%S'),
                'image_url': row['image_url'],
                'result_analyze': analyze_values,
                'skin_health': row['skin_health'],
                'disease_detection': {
                    'id_disease': id_disease,
                    'disease': disease_detection_label,
                    'confidence': disease_detection_confidence,
                    'image_url': disease_image_url,
                    'overview': disease_overview,
                    'medication_ingredients': [
                        {
                            'id_medication': ingredient['id_medication'],
                            'id_disease_medication': ingredient['id_disease_medication'],
                            'name': ingredient['name'],
                            'image_url': ingredient['image_url'],
                            'link_tokopedia': ingredient['link_tokopedia']
                        } for ingredient in medication_ingredients
                    ]
                }
            }
            result.append(recent_item)

        cursor.close()
        conn.close()

        return jsonify(result)

    except mysql.connector.Error as err:
        logging.error(f"MySQL Error: {err}")
        return jsonify({'message': str(err)}), 500

    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({'message': str(e)}), 500

@app.route('/disease/<int:id>/medications', methods=['GET'])
def select_medication_ingredients(id):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM medication_ingredients WHERE id_disease_medication = %s', (id,))
    medications = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(medications)

import logging

@app.route('/history', methods=['GET'])
@authenticate_user
def history():
    user_id = request.id_user

    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('''
            SELECT sa.id_analyze, sa.favorite, sa.date_analyze, sa.id_imageanalyze, sa.acne, sa.actinickeratosis, sa.blackheads, sa.herpes, 
                    sa.keloid, sa.keratosisseborrheic, sa.milia, sa.pityriasis_versicolor, sa.ringworm, sa.skin_health,
                    i.image_url
            FROM skin_analyze sa
            JOIN images i ON sa.id_imageanalyze = i.id_image
            WHERE sa.id_useranalyze = %s
            ORDER BY sa.date_analyze DESC
        ''', (user_id,))

        history_data = cursor.fetchall()

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

            # Find the disease with the highest confidence
            disease_detection_label = max(analyze_values, key=analyze_values.get)
            disease_detection_confidence = analyze_values[disease_detection_label]

            # Get the id_disease from the database based on the disease name
            cursor.execute('SELECT id_disease, image_url, overview FROM disease WHERE name = %s', (disease_detection_label,))
            id_disease_result = cursor.fetchone()

            if id_disease_result:
                id_disease = id_disease_result['id_disease']
                disease_image_url = id_disease_result['image_url']
                disease_overview = id_disease_result['overview']
            else:
                id_disease = None
                disease_image_url = None
                disease_overview = None

            # Get medication ingredients for the detected disease
            medication_ingredients = []
            if id_disease:
                cursor.execute('SELECT * FROM medication_ingredients WHERE id_disease_medication = %s', (id_disease,))
                medication_ingredients = cursor.fetchall()

            # Log the medication ingredients for debugging
            logging.debug(f"Medication ingredients for disease {disease_detection_label}: {medication_ingredients}")

            history_item = {
                'id_analyze': row['id_analyze'],
                'favorite': row['favorite'],  
                'date': row['date_analyze'].strftime('%Y-%m-%d %H:%M:%S'),
                'image_url': row['image_url'],
                'result_analyze': analyze_values,
                'skin_health': row['skin_health'],
                'disease_detection': {
                    'id_disease': id_disease,
                    'disease': disease_detection_label,
                    'confidence': disease_detection_confidence,
                    'image_url': disease_image_url,
                    'overview': disease_overview,
                    'medication_ingredients': [
                        {
                            'id_medication': ingredient['id_medication'],
                            'id_disease_medication': ingredient['id_disease_medication'],
                            'name': ingredient['name'],
                            'image_url': ingredient['image_url'],
                            'link_tokopedia': ingredient['link_tokopedia']
                        } for ingredient in medication_ingredients
                    ]
                }
            }
            result.append(history_item)

        cursor.close()
        conn.close()

        return jsonify(result)

    except mysql.connector.Error as err:
        logging.error(f"MySQL Error: {err}")
        return jsonify({'message': str(err)}), 500

    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({'message': str(e)}), 500

@app.route('/analyzeById', methods=['GET'])
@authenticate_user
def select_analyzeById():
    analyze_id = request.args.get('id_analyze')
    if not analyze_id:
        return jsonify({'error': True, 'message': "id_analyze parameter is required" }), 400

    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('''
            SELECT sa.date_analyze, sa.id_imageanalyze, sa.acne, sa.actinickeratosis, sa.blackheads, sa.herpes, 
                    sa.keloid, sa.keratosisseborrheic, sa.milia, sa.pityriasis_versicolor, sa.ringworm, sa.skin_health,
                    i.image_url
            FROM skin_analyze sa
            JOIN images i ON sa.id_imageanalyze = i.id_image
            WHERE sa.id_analyze = %s
        ''', (analyze_id,))

        analyze_data = cursor.fetchone()
        if not analyze_data:
            return jsonify({'message': 'No analyze data found for the provided id'}), 404

        analyze_values = {
            'Acne': analyze_data['acne'],
            'ActinicKeratosis': analyze_data['actinickeratosis'],
            'Blackheads': analyze_data['blackheads'],
            'Herpes': analyze_data['herpes'],
            'Keloid': analyze_data['keloid'],
            'KeratosisSeborrheic': analyze_data['keratosisseborrheic'],
            'Milia': analyze_data['milia'],
            'Pityriasis versicolor': analyze_data['pityriasis_versicolor'],
            'Ringworm': analyze_data['ringworm']
        }

        # Find the disease with the highest confidence
        disease_detection_label = max(analyze_values, key=analyze_values.get)
        disease_detection_confidence = analyze_values[disease_detection_label]

        # Get the id_disease from the database based on the disease name
        cursor.execute('SELECT id_disease, image_url, overview FROM disease WHERE name = %s', (disease_detection_label,))
        id_disease_result = cursor.fetchone()

        if id_disease_result:
            id_disease = id_disease_result['id_disease']
            disease_image_url = id_disease_result['image_url']
            disease_overview = id_disease_result['overview']
        else:
            id_disease = None
            disease_image_url = None
            disease_overview = None

        # Get medication ingredients for the detected disease
        medication_ingredients = []
        if id_disease:
            cursor.execute('SELECT * FROM medication_ingredients WHERE id_disease_medication = %s', (id_disease,))
            medication_ingredients = cursor.fetchall()

        # Log the medication ingredients for debugging
        logging.debug(f"Medication ingredients for disease {disease_detection_label}: {medication_ingredients}")

        analyze_item = {
            'date': analyze_data['date_analyze'].strftime('%Y-%m-%d %H:%M:%S'),
            'image_url': analyze_data['image_url'],
            'result_analyze': analyze_values,
            'skin_health': analyze_data['skin_health'],
            'disease_detection': {
                'id_disease': id_disease,
                'disease': disease_detection_label,
                'confidence': disease_detection_confidence,
                'image_url': disease_image_url,
                'overview': disease_overview,
                'medication_ingredients': [
                    {
                        'id_medication': ingredient['id_medication'],
                        'id_disease_medication': ingredient['id_disease_medication'],
                        'name': ingredient['name'],
                        'image_url': ingredient['image_url'],
                        'link_tokopedia': ingredient['link_tokopedia']
                    } for ingredient in medication_ingredients
                ]
            }
        }

        cursor.close()
        conn.close()

        return jsonify(analyze_item)

    except mysql.connector.Error as err:
        logging.error(f"MySQL Error: {err}")
        return jsonify({'message': str(err)}), 500

    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({'message': str(e)}), 500

@app.route('/getFavorite', methods=['GET'])
@authenticate_user
def get_favorite():
    user_id = request.id_user

    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('''
            SELECT sa.id_analyze, sa.favorite, sa.date_analyze, sa.id_imageanalyze, sa.acne, sa.actinickeratosis, sa.blackheads, sa.herpes, 
                    sa.keloid, sa.keratosisseborrheic, sa.milia, sa.pityriasis_versicolor, sa.ringworm, sa.skin_health,
                    i.image_url
            FROM skin_analyze sa
            JOIN images i ON sa.id_imageanalyze = i.id_image
            WHERE sa.id_useranalyze = %s AND sa.favorite = 1
            ORDER BY sa.date_analyze DESC
        ''', (user_id,))

        favorite_data = cursor.fetchall()

        result = []
        for row in favorite_data:
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

            # Find the disease with the highest confidence
            disease_detection_label = max(analyze_values, key=analyze_values.get)
            disease_detection_confidence = analyze_values[disease_detection_label]

            # Get the id_disease from the database based on the disease name
            cursor.execute('SELECT id_disease, image_url, overview FROM disease WHERE name = %s', (disease_detection_label,))
            id_disease_result = cursor.fetchone()

            if id_disease_result:
                id_disease = id_disease_result['id_disease']
                disease_image_url = id_disease_result['image_url']
                disease_overview = id_disease_result['overview']
            else:
                id_disease = None
                disease_image_url = None
                disease_overview = None

            # Get medication ingredients for the detected disease
            medication_ingredients = []
            if id_disease:
                cursor.execute('SELECT * FROM medication_ingredients WHERE id_disease_medication = %s', (id_disease,))
                medication_ingredients = cursor.fetchall()

            # Log the medication ingredients for debugging
            logging.debug(f"Medication ingredients for disease {disease_detection_label}: {medication_ingredients}")

            history_item = {
                'id_analyze': row['id_analyze'],  
                'favorite': row['favorite'],  
                'date': row['date_analyze'].strftime('%Y-%m-%d %H:%M:%S'),
                'image_url': row['image_url'],
                'result_analyze': analyze_values,
                'skin_health': row['skin_health'],
                'disease_detection': {
                    'id_disease': id_disease,
                    'disease': disease_detection_label,
                    'confidence': disease_detection_confidence,
                    'image_url': disease_image_url,
                    'overview': disease_overview,
                    'medication_ingredients': [
                        {
                            'id_medication': ingredient['id_medication'],
                            'id_disease_medication': ingredient['id_disease_medication'],
                            'name': ingredient['name'],
                            'image_url': ingredient['image_url'],
                            'link_tokopedia': ingredient['link_tokopedia']
                        } for ingredient in medication_ingredients
                    ]
                }
            }
            result.append(history_item)

        cursor.close()
        conn.close()

        return jsonify(result)

    except mysql.connector.Error as err:
        logging.error(f"MySQL Error: {err}")
        return jsonify({'message': str(err)}), 500

    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({'message': str(e)}), 500

@app.route('/medications', methods=['GET'])
@authenticate_user
def get_medications():
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('''
            SELECT mi.id_medication, mi.id_disease_medication, mi.name as medication_name, mi.image_url as medication_image_url, mi.link_tokopedia, 
                    d.name as disease_name
            FROM medication_ingredients mi
            JOIN disease d ON mi.id_disease_medication = d.id_disease
        ''')

        medication_data = cursor.fetchall()

        result = [
            {
                'id_medication': item['id_medication'],
                'id_disease_medication': item['id_disease_medication'],
                'medication_name': item['medication_name'],
                'medication_image_url': item['medication_image_url'],
                'link_tokopedia': item['link_tokopedia'],
                'disease_name': item['disease_name']
            } for item in medication_data
        ]

        cursor.close()
        conn.close()

        return jsonify(result)

    except mysql.connector.Error as err:
        logging.error(f"MySQL Error: {err}")
        return jsonify({'message': str(err)}), 500

    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({'message': str(e)}), 500


@app.route('/updateFavorite', methods=['POST'])
@authenticate_user
def update_favorite():
    try:
        data = request.get_json()
        id_analyze = data.get('id_analyze')
        value = data.get('value')

        if id_analyze is None or value is None:
            return jsonify({'error': True, 'message': 'id_analyze and value are required'}), 400

        if value not in [0, 1]:
            return jsonify({'error': True, 'message': 'value must be 0 or 1'}), 400

        conn = get_mysql_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE skin_analyze
            SET favorite = %s
            WHERE id_analyze = %s
        ''', (value, id_analyze))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'error': False, 'message': 'Favorite status updated successfully'})

    except mysql.connector.Error as err:
        logging.error(f"MySQL Error: {err}")
        return jsonify({'message': str(err)}), 500

    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({'message': str(e)}), 500

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

def normalize_disease_name(name):
    import re
    return re.sub(r'(?<!^)(?=[A-Z])', ' ', name)

import logging

logging.basicConfig(level=logging.DEBUG)
@app.route('/predict', methods=['POST'])
@authenticate_user
def predict():
    user_id = request.id_user

    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400

    file = request.files['file']

    try:
        image = Image.open(file)
    except Exception as e:
        return jsonify({'message': 'Invalid image file'}), 400


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
        image_url = f'static/{unique_filename}'

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

        disease_detection_label = max(analyze_values_rounded, key=analyze_values_rounded.get)
        disease_detection_confidence = analyze_values_rounded[disease_detection_label]

        normalized_disease_name = normalize_disease_name(disease_detection_label)

        # Get the disease details from the database
        cursor.execute('SELECT id_disease, image_url, overview FROM disease WHERE name = %s', (normalized_disease_name,))
        disease_details = cursor.fetchone()

        if disease_details is None:
            conn.rollback()  
            conn.close()
            return jsonify({'error': True, 'message': f'Skin disease {normalized_disease_name} not found'}), 404

        
        id_disease = disease_details[0]
        disease_image_url = disease_details[1]
        disease_overview = disease_details[2]

        # Get medication ingredients for the detected disease
        cursor.execute('SELECT * FROM medication_ingredients WHERE id_disease_medication = %s', (id_disease,))
        medication_ingredients = cursor.fetchall()

        # Save analysis results to database
        cursor.execute('INSERT INTO skin_analyze (id_useranalyze, id_imageanalyze, acne, actinickeratosis, blackheads, herpes, keloid, keratosisseborrheic, milia, pityriasis_versicolor, ringworm, date_analyze, skin_health) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                       (user_id, id_image, *analyze_values, current_time, skin_health))
        conn.commit()

        cursor.close()
        conn.close()

        prediction_results = {
            'id_analyze': cursor.lastrowid,
            'favorite': 0,
            'date': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'image_url': image_url,
            'result_analyze': analyze_values_rounded,
            'skin_health': skin_health,
            'disease_detection': {
                'id_disease': id_disease,
                'disease': disease_detection_label,
                'confidence': disease_detection_confidence,
                'image_url': disease_image_url,
                'overview': disease_overview,
                'medication_ingredients': [
                    {
                        'id_medication': ingredient[0],
                        'id_disease_medication': ingredient[1],
                        'name': ingredient[2],
                        'image_url': ingredient[3],
                        'link_tokopedia': ingredient[4]
                    } for ingredient in medication_ingredients
                ]
            }
        }

        return jsonify({'error' : False, 'data' : prediction_results})

    except Exception as e:
        logging.error('Error during prediction', exc_info=e)
        return jsonify({'error': True, 'message': str(e)})

@app.route('/get_id_disease', methods=['GET'])
def get_id_disease():
    disease_name = request.args.get('disease_name')

    if not disease_name:
        return jsonify({'message': 'Parameter disease_name is required.'}), 400

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
        return jsonify({'message': f'Disease with name "{disease_name}" not found.'}), 404

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
        return jsonify({'message': f'Disease with ID {id} not found'}), 404

    # Adjust the response as needed based on your database schema
    disease_data = {
        'id_disease': disease_info[0],
        'name': disease_info[1],
        'overview': disease_info[2],
        'image_url': disease_info[3]
        # Add more fields as necessary
    }

    return jsonify(disease_data)


# @app.route('/favorites/<int:id>', methods=['PUT'])
# @authenticate_user
# def update_favorite(id):
#     user_id = request.id_user
#     data = request.get_json()
#     favorite_status = data.get('favorite')

#     conn = get_mysql_connection()
#     cursor = conn.cursor()
#     cursor.execute('UPDATE skin_analyze SET favorite = %s WHERE id_useranalyze = %s AND id_imageanalyze = %s', (favorite_status, user_id, id))
#     conn.commit()
#     cursor.close()
#     conn.close()

#     return jsonify({'message': 'Favorite status updated successfully'})

@app.route('/profile', methods=['PUT'])
@authenticate_user
def update_profile():
    user_id = request.id_user
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    # profile_image_url = data.get('profile_image_url')

    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET email = %s, name = %s WHERE id_user = %s', (email, name, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'error': False, 'message': 'Profile updated successfully'})

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
