from flask import Flask, request, render_template
import mysql.connector
import boto3
import json

app = Flask(__name__)

def get_gcp_credentials_from_s3():
    s3 = boto3.client('s3')
    bucket_name = 'gcp-creds-enhub'  
    object_key = 'sturdy-tuner-459209-e3-227b9a1d4a29.json'  

    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    content = response['Body'].read()
    credentials = json.loads(content)
    
    # Optionally, you can set these creds in environment variables or return them
    return credentials

def get_gcp_sql_connection():
    # Get the GCP service account credentials (not used in this MySQL connection directly)
    credentials = get_gcp_credentials_from_s3()

    # MySQL connection — using DB IP, user, password (replace with your values)
    conn = mysql.connector.connect(
        host='34.66.32.63',     
        user='enhubtask',                
        password='enhub123',        
        database='root-enhub'            
    )
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        conn = get_gcp_sql_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
        conn.commit()
        cursor.close()
        conn.close()
        return "Data submitted!"
    return render_template('form.html')
