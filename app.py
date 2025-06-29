from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this to a secure key

# ---------------- Helper Functions ----------------

def load_feedback():
    if os.path.exists('feedback.json'):
        with open('feedback.json', 'r') as f:
            return json.load(f)
    return []

def save_feedback(data):
    with open('feedback.json', 'w') as f:
        json.dump(data, f, indent=2)

def load_admin_password():
    if os.path.exists('admin.json'):
        with open('admin.json', 'r') as f:
            return json.load(f).get('password', 'admin')
    return 'admin'

def save_admin_password(new_password):
    with open('admin.json', 'w') as f:
        json.dump({'password': new_password}, f)

# ---------------- Routes ----------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        feedback = {
            "member": request.form['member'],
            "project": request.form['project'],
            "task": request.form['task'],
            "difficulty": request.form['difficulty'],
            "comments": request.form['comments']
        }
        data = load_feedback()
        data.append(feedback)
        save_feedback(data)
        return redirect(url_for('success'))
    return render_template('feedback.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form['password']
        if password == load_admin_password():
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error="Wrong password")
    return render_template('admin_login.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    feedbacks = load_feedback()
    return render_template('admin_dashboard.html', feedbacks=feedbacks)

@app.route('/delete/<int:index>')
def delete_feedback(index):
    if not session.get('admin'):
        return redirect(url_for('admin'))
    data = load_feedback()
    if 0 <= index < len(data):
        del data[index]
        save_feedback(data)
    return redirect(url_for('admin_dashboard'))

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    if request.method == 'POST':
        new_password = request.form['new_password']
        save_admin_password(new_password)
        return redirect(url_for('admin_dashboard'))
    return render_template('change_password.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

# ---------------- Run ----------------

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)