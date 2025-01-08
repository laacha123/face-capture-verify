Flask Face Verification App
Overview
This is a Flask-based web application designed for face verification using the face_recognition library. The app integrates with AWS S3 for storing and retrieving images, supports CORS for cross-origin requests, and provides endpoints for capturing and verifying facial images.

Features
Image Capture and Upload: Accepts base64-encoded images from clients and uploads them to an S3 bucket.
Face Verification: Compares a live-captured image with a known image stored on AWS S3 to verify identity.
Image Cleanup: Deletes temporary image files locally after use.
Cross-Origin Support: Allows secure requests from multiple origins using Flask-CORS.

Prerequisites
To run this application, ensure you have the following:
1. Python 3.7+
2. Flask and Required Libraries mentioned in the app :
The following Python libraries are required:
Flask
Flask-CORS
boto3
face_recognition
Pillow
opencv-python
base64
jwt
openai

3. AWS S3 Bucket Credentials:
AWS_ACCESS_KEY
AWS_SECRET_KEY
AWS_BUCKET_NAME

4. OpenAI API key 

5. Local folders:
instant_input_img/
real_input_img/
