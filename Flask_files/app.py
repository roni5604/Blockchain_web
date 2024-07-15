from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Here you can handle the form submission and registration logic
        username = request.form['username']
        password = request.form['password']
        # Add your registration logic here (e.g., save to database)
        return redirect(url_for('home'))
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
