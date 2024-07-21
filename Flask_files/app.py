from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB Atlas connection
client = MongoClient('mongodb+srv://roni5604:Dani1996!@blockchainvote.lbmcrlj.mongodb.net/')
db = client.get_database('BlockchainVote')
users_collection = db.users
votes_collection = db.votes

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users_collection.find_one({"email": email})
        if user and user['password'] == password:
            session['user'] = email
            session['role'] = user.get('role', 'user')
            session['first_name'] = user['first_name']
            if session['role'] == 'manager':
                return redirect(url_for('manager_home'))
            else:
                return redirect(url_for('user_home'))
        else:
            error = "Invalid email or password."
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user_id = request.form['user_id']
        phone_number = request.form['phone_number']
        gender = request.form['gender']
        party = request.form['party']
        agree_terms = request.form.get('agree_terms')

        # Simple validation for first name, last name, phone number, and ID
        if not re.match(r"^[a-zA-Z]+$", first_name):
            error = "Invalid first name."
            return render_template('register.html', error=error)
        if not re.match(r"^[a-zA-Z]+$", last_name):
            error = "Invalid last name."
            return render_template('register.html', error=error)
        if not re.match(r"^\d{10}$", phone_number):
            error = "Invalid phone number. Must be 10 digits."
            return render_template('register.html', error=error)
        if not re.match(r"^\d{9}$", user_id):
            error = "Invalid ID. Must be 9 digits."
            return render_template('register.html', error=error)
        if password != confirm_password:
            error = "Passwords do not match."
            return render_template('register.html', error=error)
        if not agree_terms:
            error = "You must agree to the terms of use."
            return render_template('register.html', error=error)

        # Insert user into MongoDB with default role 'user'
        users_collection.insert_one({
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,
            "user_id": user_id,
            "phone_number": phone_number,
            "gender": gender,
            "party": party,
            "role": "user"
        })

        return redirect(url_for('login_page'))
    return render_template('register.html')

@app.route('/user_home')
def user_home():
    if 'user' in session and session.get('role') == 'user':
        return render_template('user_home.html', first_name=session.get('first_name'))
    return redirect(url_for('login_page'))

@app.route('/manager_home')
def manager_home():
    if 'user' in session and session.get('role') == 'manager':
        return render_template('manager_home.html', first_name=session.get('first_name'))
    return redirect(url_for('login_page'))

@app.route('/user_votes')
def user_votes():
    if 'user' in session and session.get('role') == 'user':
        return render_template('user_votes.html', first_name=session.get('first_name'))
    return redirect(url_for('login_page'))

@app.route('/manager_votes')
def manager_votes():
    if 'user' in session and session.get('role') == 'manager':
        return render_template('manager_votes.html', first_name=session.get('first_name'))
    return redirect(url_for('login_page'))

@app.route('/user_settings', methods=['GET', 'POST'])
def user_settings():
    if 'user' in session and session.get('role') == 'user':
        user = users_collection.find_one({"email": session.get('user')})
        if request.method == 'POST':
            # Update user settings logic here
            updated_data = {
                "first_name": request.form['first_name'],
                "last_name": request.form['last_name'],
                "email": request.form['email'],
                "user_id": request.form['user_id'],
                "phone_number": request.form['phone_number'],
                "gender": request.form['gender'],
                "party": request.form['party']
            }

            # Validate the updated data
            if not re.match(r"^[a-zA-Z]+$", updated_data['first_name']):
                error = "Invalid first name."
                return render_template('user_settings.html', user=user, error=error)
            if not re.match(r"^[a-zA-Z]+$", updated_data['last_name']):
                error = "Invalid last name."
                return render_template('user_settings.html', user=user, error=error)
            if not re.match(r"^\d{10}$", updated_data['phone_number']):
                error = "Invalid phone number. Must be 10 digits."
                return render_template('user_settings.html', user=user, error=error)
            if not re.match(r"^\d{9}$", updated_data['user_id']):
                error = "Invalid ID. Must be 9 digits."
                return render_template('user_settings.html', user=user, error=error)

            users_collection.update_one({"email": session.get('user')}, {"$set": updated_data})
            return redirect(url_for('user_home'))

        return render_template('user_settings.html', user=user)
    return redirect(url_for('login_page'))

@app.route('/manager_settings', methods=['GET', 'POST'])
def manager_settings():
    if 'user' in session and session.get('role') == 'manager':
        users = list(users_collection.find())
        return render_template('manager_settings.html', first_name=session.get('first_name'), users=users)
    return redirect(url_for('login_page'))

@app.route('/edit_user/<user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user' in session and session.get('role') == 'manager':
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if request.method == 'POST':
            updated_data = {
                "first_name": request.form['first_name'],
                "last_name": request.form['last_name'],
                "email": request.form['email'],
                "user_id": request.form['user_id'],
                "phone_number": request.form['phone_number'],
                "gender": request.form['gender'],
                "party": request.form['party'],
                "role": request.form['role']
            }

            # Validate the updated data
            if not re.match(r"^[a-zA-Z]+$", updated_data['first_name']):
                error = "Invalid first name."
                return render_template('edit_user.html', user=user, error=error)
            if not re.match(r"^[a-zA-Z]+$", updated_data['last_name']):
                error = "Invalid last name."
                return render_template('edit_user.html', user=user, error=error)
            if not re.match(r"^\d{10}$", updated_data['phone_number']):
                error = "Invalid phone number. Must be 10 digits."
                return render_template('edit_user.html', user=user, error=error)
            if not re.match(r"^\d{9}$", updated_data['user_id']):
                error = "Invalid ID. Must be 9 digits."
                return render_template('edit_user.html', user=user, error=error)

            users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": updated_data})
            return redirect(url_for('manager_settings'))

        return render_template('edit_user.html', user=user)
    return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    session.pop('first_name', None)
    return redirect(url_for('login_page'))

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/validate_password', methods=['POST'])
def validate_password():
    password = request.form['password']
    strength = 'Weak'
    if len(password) >= 8 and re.search(r"[a-z]", password) and re.search(r"[A-Z]", password) and re.search(r"[0-9]", password) and re.search(r"[!@#$%^&*]", password):
        strength = 'Strong'
    elif len(password) >= 6:
        strength = 'Medium'
    return jsonify({'strength': strength})

if __name__ == '__main__':
    app.run(debug=True)
