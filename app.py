import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from urllib.parse import quote_plus

app = Flask(__name__)

# Secret key for session - set as environment variable or fallback
app.secret_key = os.getenv('FLASKSECRETKEY', 'secretkey')

# MongoDB credentials - use environment variable or hardcode here for testing
MONGO_USER = 'kavidharan02'
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', 'Kavi@211')  # Make sure this is URL encoded if special chars

# URL encode the password
encoded_password = quote_plus(MONGO_PASSWORD)

# Construct the URI with encoded password
mongo_uri = f"mongodb+srv://{MONGO_USER}:{encoded_password}@heart-disease-db.rvvhg4q.mongodb.net/heart_disease_db?retryWrites=true&w=majority"

# Initialize bcrypt and MongoDB client
bcrypt = Bcrypt(app)
client = MongoClient(mongo_uri)
db = client["heart_disease_db"]

# Collections
users_collection = db["users"]
patients_collection = db["patients"]
predictions_collection = db["predictions"]

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        if users_collection.find_one({"email": email}):
            flash("Email already registered, please log in.", "danger")
            return redirect(url_for('login'))

        users_collection.insert_one({"username": username, "email": email, "password": password})
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({"email": email})

        if user and bcrypt.check_password_hash(user['password'], password):
            session['user'] = user['email']
            flash("Login successful!", "success")
            return redirect(url_for('patient_details'))
        else:
            flash("Invalid credentials, try again.", "danger")
    
    return render_template('login.html')

@app.route('/patient_details', methods=['GET', 'POST'])
def patient_details():
    if 'user' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    return render_template('patient_details.html')

@app.route('/submit_patient_details', methods=['POST'])
def submit_patient_details():
    if 'user' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    patient_name = request.form.get('patient_name')
    age = request.form.get('age')
    gender = request.form.get('gender')

    if not patient_name or not age or not gender:
        flash("All fields are required!", "danger")
        return redirect(url_for('patient_details'))

    patient_data = {
        "user_email": session['user'],
        "patient_name": patient_name,
        "age": int(age),
        "gender": gender
    }

    patients_collection.insert_one(patient_data)
    flash("Patient details submitted successfully!", "success")
    
    return redirect(url_for('report_input'))

@app.route('/report_input', methods=['GET', 'POST'])
def report_input():
    if 'user' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))
    
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'user' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    form_data = request.form.to_dict()
    
    try:
        age = int(form_data.get("age", 0))
        cholesterol = float(form_data.get("serum_cholesterol", 0.0))
        blood_pressure = float(form_data.get("restingbp", 0.0))
        oldpeak = float(form_data.get("oldpeak", 0.0))
        num_major_vessels = int(form_data.get("num_major_vessels", 0))
        chest_pain_type = form_data.get("chest_pain_type", "").strip()

        # Basic risk assessment logic
        if (cholesterol > 220 or blood_pressure > 150 or oldpeak > 2 or num_major_vessels > 1 or chest_pain_type in ["Typical Angina", "Asymptomatic"]):
            prediction = "High Risk of Heart Disease"
            confidence = 85
        else:
            prediction = "Low Risk of Heart Disease"
            confidence = 60

        # Store prediction in MongoDB
        prediction_data = {
            "user_email": session['user'],
            "age": age,
            "cholesterol": cholesterol,
            "blood_pressure": blood_pressure,
            "oldpeak": oldpeak,
            "num_major_vessels": num_major_vessels,
            "chest_pain_type": chest_pain_type,
            "prediction": prediction,
            "confidence": confidence
        }
        predictions_collection.insert_one(prediction_data)
        
        return render_template('result.html', prediction=prediction, confidence=confidence)

    except Exception as e:
        flash(f"Error in prediction: {e}", "danger")
        return redirect(url_for('report_input'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

@app.route('/test')
def test():
    return "Flask is working!"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
