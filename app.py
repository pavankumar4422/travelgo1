from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
import os

# Flask App Setup
app = Flask(__name__)
app.secret_key = 'e0d15ae2faa18025f4e2a0c7dc5a7b8a830791cc83ad7538667ce14ca2ad8bc0'

# MongoDB Atlas Setup
client = MongoClient("mongodb+srv://kvssmidhun:QStk6eMbUrhNUCY8@cluster0.ckzmfyj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['Travelgo']
users_collection = db['users']
bookings_collection = db['bookings']

@app.route('/')
def home():
    return render_template('index.html', logged_in='user' in session)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        if users_collection.find_one({"email": email}):
            return render_template('register.html', message="User already exists.")
        users_collection.insert_one({
            "email": email,
            "name": request.form['name'],
            "password": request.form['password'],
            "logins": 0
        })
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({"email": email})
        if user and user['password'] == password:
            session['user'] = email
            return redirect('/dashboard')
            users_collection.update_one({"email": email}, {"$inc": {"logins": 1}})
            return '''
                <script>
                    localStorage.setItem("loggedIn", "true");
                    window.location.href = "/";
                </script>
            '''
        return render_template('login.html', message="Invalid credentials.")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    email = session['user']
    user = users_collection.find_one({"email": email})
    bookings = list(bookings_collection.find({'user_email':email}))
    return render_template('dashboard.html', name =user['name'], bookings=bookings)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
