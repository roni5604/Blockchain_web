from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
import re
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB Atlas connection
client = MongoClient(
    'mongodb+srv://roniRoyAvia:Gilli2106!@webblockchain.jmrzy.mongodb.net/'
)

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
            session['user_id'] = user['user_id']
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

        # Store user ID in session
        session['user_id'] = user_id
        session['first_name'] = first_name
        session['role'] = 'user'

        return redirect(url_for('login_page'))
    return render_template('register.html')


@app.route('/user_home')
def user_home():
    if 'user' in session and session.get('role') == 'user':
        user_id = session.get('user_id').strip().lower()
        ongoing_votes = list(votes_collection.find({
            "stage": {"$ne": "Closed"},
            "voted_users": {"$ne": user_id}
        }))
        voted_votes = list(votes_collection.find({
            "voted_users": user_id,
            "stage": {"$ne": "Closed"}
        }))
        closed_votes = list(votes_collection.find({
            "voting_status": "Closed",
            "voted_users": user_id
        }))

        return render_template('user_home.html', first_name=session.get('first_name'), votes=ongoing_votes,
                               voted_votes=voted_votes, closed_votes=closed_votes, user_id=user_id)
    return redirect(url_for('login_page'))


@app.route('/manager_home')
def manager_home():
    if 'user' in session and session.get('role') == 'manager':
        return render_template('manager_home.html', first_name=session.get('first_name'))
    return redirect(url_for('login_page'))


@app.route('/user_votes', methods=['GET', 'POST'])
def user_votes():
    if 'user' in session and session.get('role') == 'user':
        if request.method == 'POST':
            search_query = request.form.get('search_query', '').strip().lower()
            search_stage = request.form.get('search_stage', '').strip()
            query = {"voting_status": "closed"}
            if search_query:
                query["title"] = {"$regex": search_query, "$options": "i"}
            if search_stage:
                query["stage"] = {"$regex": search_stage, "$options": "i"}

            closed_votes = list(votes_collection.find(query))
        else:
            closed_votes = list(votes_collection.find({"voting_status": "closed"}))

        return render_template('user_votes.html', closed_votes=closed_votes, first_name=session.get('first_name'))
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
                return render_template('user_settings.html', user=user, first_name=session.get('first_name'),
                                       error=error)
            if not re.match(r"^[a-zA-Z]+$", updated_data['last_name']):
                error = "Invalid last name."
                return render_template('user_settings.html', user=user, first_name=session.get('first_name'),
                                       error=error)
            if not re.match(r"^\d{10}$", updated_data['phone_number']):
                error = "Invalid phone number. Must be 10 digits."
                return render_template('user_settings.html', user=user, first_name=session.get('first_name'),
                                       error=error)
            if not re.match(r"^\d{9}$", updated_data['user_id']):
                error = "Invalid ID. Must be 9 digits."
                return render_template('user_settings.html', user=user, first_name=session.get('first_name'),
                                       error=error)

            users_collection.update_one({"email": session.get('user')}, {"$set": updated_data})
            return redirect(url_for('user_home'))

        return render_template('user_settings.html', user=user, first_name=session.get('first_name'))
    return redirect(url_for('login_page'))


@app.route('/manager_votes')
def manager_votes():
    if 'user' in session and session.get('role') == 'manager':
        return render_template('manager_votes.html', first_name=session.get('first_name'))
    return redirect(url_for('login_page'))


@app.route('/manager_settings', methods=['GET'])
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
                return render_template('edit_user.html', user=user, first_name=session.get('first_name'), error=error)
            if not re.match(r"^[a-zA-Z]+$", updated_data['last_name']):
                error = "Invalid last name."
                return render_template('edit_user.html', user=user, first_name=session.get('first_name'), error=error)
            if not re.match(r"^\d{10}$", updated_data['phone_number']):
                error = "Invalid phone number. Must be 10 digits."
                return render_template('edit_user.html', user=user, first_name=session.get('first_name'), error=error)
            if not re.match(r"^\d{9}$", updated_data['user_id']):
                error = "Invalid ID. Must be 9 digits."
                return render_template('edit_user.html', user=user, first_name=session.get('first_name'), error=error)

            users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": updated_data})
            return redirect(url_for('manager_settings'))

        return render_template('edit_user.html', user=user, first_name=session.get('first_name'))
    return redirect(url_for('login_page'))


@app.route('/request_manager')
def request_manager():
    if 'user' in session and session.get('role') == 'user':
        users_collection.update_one({"email": session.get('user')}, {"$set": {"role": "manager"}})
        session['role'] = 'manager'
        return redirect(url_for('manager_home'))
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
    print(f"Received password: {password}")  # Debug print
    strength = 'Weak'
    if len(password) >= 8 and re.search(r"[a-z]", password) and re.search(r"[A-Z]", password) and re.search(r"[0-9]", password) and re.search(r"[!@#$%^&*]", password):
        strength = 'Strong'
    elif len(password) >= 6:
        strength = 'Medium'
    print(f"Password strength calculated: {strength}")  # Debug print
    return jsonify({'strength': strength})


@app.route('/search_users')
def search_users():
    if 'user' in session and session.get('role') == 'manager':
        query = request.args.get('q', '')
        users = users_collection.find({
            "$or": [
                {"first_name": {"$regex": query, "$options": "i"}},
                {"last_name": {"$regex": query, "$options": "i"}},
                {"user_id": {"$regex": query, "$options": "i"}},
                {"party": {"$regex": query, "$options": "i"}}
            ]
        })
        return jsonify([user for user in users])
    return jsonify([])


@app.route('/create_vote', methods=['GET', 'POST'])
def create_vote():
    if 'user' in session and session.get('role') == 'manager':
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            stage = request.form['stage']

            votes_collection.insert_one({
                "title": title,
                "description": description,
                "stage": stage,
                "voting_status": "inprocess",  # New field for voting status
                "created_by": session.get('user')
            })

            return redirect(url_for('manage_votes'))

        return render_template('create_vote.html', first_name=session.get('first_name'))
    return redirect(url_for('login_page'))


@app.route('/manage_votes')
def manage_votes():
    if 'user' in session and session.get('role') == 'manager':
        votes = list(votes_collection.find())
        return render_template('manage_votes.html', votes=votes, first_name=session.get('first_name'))
    return redirect(url_for('login_page'))


@app.route('/edit_vote/<vote_id>', methods=['GET', 'POST'])
def edit_vote(vote_id):
    if 'user' in session and session.get('role') == 'manager':
        vote = votes_collection.find_one({"_id": ObjectId(vote_id)})
        if request.method == 'POST':
            updated_data = {
                "title": request.form['title'],
                "description": request.form['description'],
                "stage": request.form['stage']
            }
            votes_collection.update_one({"_id": ObjectId(vote_id)}, {"$set": updated_data})
            return redirect(url_for('manage_votes'))

        return render_template('edit_vote.html', vote=vote, first_name=session.get('first_name'))
    return redirect(url_for('login_page'))


def normalize_votes():
    votes = votes_collection.find()
    for vote in votes:
        if 'votes' in vote:
            new_votes = {}
            for key, value in vote['votes'].items():
                normalized_key = key.strip().lower() + ".com"
                new_votes[normalized_key] = value
            votes_collection.update_one({"_id": vote["_id"]}, {"$set": {"votes": new_votes}})


@app.route('/delete_vote/<vote_id>', methods=['POST'])
def delete_vote(vote_id):
    if 'user' in session and session.get('role') == 'manager':
        votes_collection.delete_one({"_id": ObjectId(vote_id)})
        return redirect(url_for('manage_votes'))
    return redirect(url_for('login_page'))


@app.route('/vote/<vote_id>', methods=['GET', 'POST'])
def vote(vote_id):
    if 'user' in session and session.get('role') == 'user':
        user_id = session.get('user_id').strip().lower()
        vote = votes_collection.find_one({"_id": ObjectId(vote_id)})

        if request.method == 'POST':
            vote_choice = request.form['vote_choice']
            if user_id in vote.get('voted_users', []):
                return redirect(url_for('user_home'))

            votes_collection.update_one(
                {"_id": ObjectId(vote_id)},
                {
                    "$push": {"voted_users": user_id},
                    "$set": {f"votes.{user_id}": vote_choice},
                    "$inc": {vote_choice: 1}
                }
            )
            return redirect(url_for('user_home'))

        return render_template('vote.html', vote=vote, first_name=session.get('first_name'))
    return redirect(url_for('login_page'))


@app.route('/close_vote/<vote_id>', methods=['POST'])
def close_vote(vote_id):
    if 'user' in session and session.get('role') == 'manager':
        vote = votes_collection.find_one({"_id": ObjectId(vote_id)})
        yes_count = sum(1 for v in vote['votes'].values() if v == 'yes')
        no_count = sum(1 for v in vote['votes'].values() if v == 'no')
        votes_collection.update_one(
            {"_id": ObjectId(vote_id)},
            {
                "$set": {"voting_status": "closed", "yes": yes_count, "no": no_count}  # Change voting status to closed
            }
        )
        return redirect(url_for('manage_votes'))
    return redirect(url_for('login_page'))


@app.route('/closed_votes')
def closed_votes():
    if 'user' in session and session.get('role') == 'user':
        closed_votes = list(votes_collection.find({"voting_status": "closed"}))
        return render_template('closed_votes.html', closed_votes=closed_votes)
    return redirect(url_for('login_page'))


@app.route('/vote_results/<vote_id>')
def vote_results(vote_id):
    if 'user' in session and session.get('role') == 'user':
        vote = votes_collection.find_one({"_id": ObjectId(vote_id)})
        yes_votes = vote.get("yes", 0)
        no_votes = vote.get("no", 0)
        return render_template('vote_results.html', vote=vote, yes_votes=yes_votes, no_votes=no_votes,
                               first_name=session.get('first_name'))
    return redirect(url_for('login_page'))


if __name__ == '__main__':
    app.run(debug=True)
