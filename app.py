from flask import Flask, request, render_template
import mysql.connector
import boto3
import json
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Function to fetch GCP credentials from S3
def get_gcp_credentials_from_s3():
    s3 = boto3.client('s3')
    bucket_name = 'gcp-creds-enhub'  
    object_key = 'sturdy-tuner-459209-e3-227b9a1d4a29.json' 
    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        content = response['Body'].read()
        credentials = json.loads(content)
        logging.info("GCP credentials successfully retrieved from S3")
        return credentials
    except Exception as e:
        logging.error(f"Error retrieving credentials from S3: {e}")
        return None

# Function to connect to Cloud SQL
def get_gcp_sql_connection():
    credentials = get_gcp_credentials_from_s3()
    

    try:
        conn = mysql.connector.connect(
            host='34.66.32.63',     # GCP Cloud SQL public IP
            user='sohit',       # Your DB user
            password='enhub123',    # Your DB password
            database='root-enhub'   # Your DB name
        )
        logging.info("Connected to Cloud SQL successfully")
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        conn = get_gcp_sql_connection()
        if conn is None:
            return "Database connection failed."

        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
            conn.commit()
            cursor.close()
            conn.close()
            logging.info("User data inserted successfully")
            return "Data submitted successfully!"
        except Exception as e:
            logging.error(f"Error inserting data: {e}")
            return "Failed to insert data."

    return render_template('form.html')

# Ensure Flask runs on all interfaces (for EC2 public access)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
