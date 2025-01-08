from flask import Flask, request, jsonify, make_response, render_template, session, abort, current_app
import jwt
import json
import re
import openai
import face_recognition
from flask import Flask, request, jsonify
import os
import boto3
from flask_cors import CORS
import cv2
from io import BytesIO
import io
from PIL import Image
import base64
from botocore.exceptions import NoCredentialsError
import logging

# Authorization Key
auth_key = "replace with user specific key"

api_key = "replace with your key"
openai.api_key = api_key
app = Flask(__name__)
CORS(app)

########### FUNCTION TO DELETE FILES ################
def delete_img_files(username):
    instant_path = fr"instant_input_img/{username}.jpg"
    real_path = fr"real_input_img/{username}.jpg"
    try:
        os.remove(instant_path)
        os.remove(real_path)
    except FileNotFoundError:
        print(f"File {instant_path} not found")
    except Exception as e :
        print(f"Error in deleting: {e}")

# ########## FACE VERIFICATION ##############

# AWS S3 configuration
AWS_ACCESS_KEY = ''
AWS_SECRET_KEY = ''
AWS_BUCKET_NAME = ''
AWS_REGION = ''

def save_to_s3(image_data, username):
    try:
        AWS_IMAGE_KEY = f'images/{username}.jpg'
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

        image_parts = image_data.split(',')
        if len(image_parts) < 2:
            raise ValueError('Invalid image data format')

        image_bytes = image_parts[1].encode()

        s3.upload_fileobj(
            Fileobj=io.BytesIO(base64.b64decode(image_bytes)),
            Bucket=AWS_BUCKET_NAME,
            Key=AWS_IMAGE_KEY,
        )

        return True

    except NoCredentialsError:
        print('Credentials not available')
        return False

    except Exception as e:
        print(f'Error in save_to_s3: {e}')
        return False

# route
@app.route('/capture_image', methods=['POST'])
def capture_image():
    try:

        image_data = request.json.get('image_data')
        username = request.json.get('username')

        # Save the image to AWS S3
        if save_to_s3(image_data, username):
            return jsonify({'message': 'Image captured and saved to S3 successfully'}), 200
        else:
            return jsonify({'error': 'Failed to save image to S3'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

################## VERIFICATION PART ##############

UPLOAD_FOLDER = 'instant_input_img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to download image from s3
def download_images_from_s3(username):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    object_key = f'images/{username}.jpg'
    local_path = fr"real_input_img/{object_key.split('/')[-1]}"
    s3.download_file(AWS_BUCKET_NAME, object_key, local_path)
    return jsonify({'success': 'Images obtained successfully'}), 200

# Flask route for face verification
@app.route('/verify_faces', methods=['POST'])
def verify_face_route():
    data = request.get_json()
    if 'username' not in data:
        return jsonify({'error': 'Invalid request format'}), 400

    username = data['username']
    live_image_data = data['image_data']

    known_image_path = None  # Initialize known_image_path (s3)

    try:
        image_bytes = base64.b64decode(live_image_data)

        image = Image.open(BytesIO(image_bytes)).convert("RGB")

        img_name = f'{username}.jpg'

        input_image_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)

        image.save(input_image_path, 'JPEG')

        live_image = face_recognition.load_image_file(input_image_path)

        input_face_encodings = face_recognition.face_encodings(live_image)


        download_images_from_s3(username)

        # Load the known face image
        known_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{username}.jpg')
        known_image = face_recognition.load_image_file(known_image_path)
        known_face_encodings = face_recognition.face_encodings(known_image)

        # Verify faces using multiple encodings
        for known_encoding in known_face_encodings:
            for input_encoding in input_face_encodings:
                results = face_recognition.compare_faces([known_encoding], input_encoding)
                if any(results):
                    return jsonify({'status': 'True'})
        return jsonify({'status': 'False'})

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500

    finally:
        delete_img_files(username)

@app.route('/')
def default_route():
    return ("Hello route working! you got this !")
