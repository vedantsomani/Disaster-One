from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os

app = Flask(__name__)
app.secret_key = 'vedant'

DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
REQUESTS_FILE = os.path.join(DATA_DIR, 'requests.json')
RESOURCES_FILE = os.path.join(DATA_DIR, 'resources.json')

os.makedirs(DATA_DIR, exist_ok=True)
for file_path in [USERS_FILE, REQUESTS_FILE, RESOURCES_FILE]:
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump([], f)

def load_data(filepath):
    with open(filepath, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_data(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    if 'user' in session:
        role = session['user']['role']
        return redirect(url_for(f'{role}_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_data(USERS_FILE)
        email = request.form['email']
        password = request.form['password']
        for user in users:
            if user['email'] == email and user['password'] == password:
                session['user'] = user
                return redirect(url_for('index'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_data(USERS_FILE)
        new_user = {
            'email': request.form['email'],
            'password': request.form['password'],
            'role': request.form['role']
        }
        users.append(new_user)
        save_data(USERS_FILE, users)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    users = load_data(USERS_FILE)
    requests_data = load_data(REQUESTS_FILE)
    resources = load_data(RESOURCES_FILE)
    volunteers = [u for u in users if u['role'] == 'volunteer']
    ngos = [u for u in users if u['role'] == 'ngo']

    if request.method == 'POST':
        task_index = int(request.form['task_index'])
        volunteer_email = request.form['volunteer_email']
        requests_data[task_index]['assigned_volunteer'] = volunteer_email
        requests_data[task_index]['status'] = 'Assigned'
        save_data(REQUESTS_FILE, requests_data)
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_dashboard.html', users=users, requests=requests_data, resources=resources, volunteers=volunteers, ngos=ngos, enumerate=enumerate)

@app.route('/ngo', methods=['GET', 'POST'])
def ngo_dashboard():
    resources = load_data(RESOURCES_FILE)
    if request.method == 'POST':
        new_resource = {
            'name': request.form['resource_name'],
            'quantity': request.form['quantity'],
            'approved': False
        }
        resources.append(new_resource)
        save_data(RESOURCES_FILE, resources)
        return redirect(url_for('ngo_dashboard'))
    return render_template('ngo_dashboard.html', resources=resources)

@app.route('/volunteer', methods=['GET', 'POST'])
def volunteer_dashboard():
    requests_data = load_data(REQUESTS_FILE)
    if request.method == 'POST':
        task_index = int(request.form['task_index'])
        status = request.form['status']
        requests_data[task_index]['status'] = status
        save_data(REQUESTS_FILE, requests_data)
        return redirect(url_for('volunteer_dashboard'))

    return render_template('volunteer_dashboard.html', requests=requests_data, enumerate=enumerate)

@app.route('/survivor', methods=['GET', 'POST'])
def survivor_dashboard():
    requests_data = load_data(REQUESTS_FILE)
    if request.method == 'POST':
        new_request = {
            'type': request.form['help_type'],
            'details': request.form['details'],
            'status': 'Pending',
            'survivor': session['user']['email'],
            'assigned_volunteer': None
        }
        requests_data.append(new_request)
        save_data(REQUESTS_FILE, requests_data)
        return redirect(url_for('survivor_dashboard'))
    return render_template('survivor_dashboard.html', requests=requests_data)

@app.route('/approve_resource', methods=['POST'])
def approve_resource():
    resources = load_data(RESOURCES_FILE)
    resource_id = int(request.form['resource_id'])
    resources[resource_id]['approved'] = True
    save_data(RESOURCES_FILE, resources)
    return redirect(url_for('admin_dashboard'))

@app.route('/data')
def data():
    requests_data = load_data(REQUESTS_FILE)
    resources = load_data(RESOURCES_FILE)
    return jsonify({'requests': requests_data, 'resources': resources})

@app.route('/notify_sos')
def notify_sos():
    return jsonify({"message": "Admin notified of SOS!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
