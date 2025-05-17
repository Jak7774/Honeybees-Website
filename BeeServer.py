from flask import Flask, render_template, send_from_directory, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload # For Faster Loading Database
from sqlalchemy import distinct

#from flask import Flask, redirect, url_for, flash
#from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
#from flask_bcrypt import Bcrypt
#from flask_migrate import Migrate

import matplotlib
matplotlib.use('Agg')
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt

import os
from datetime import datetime, timedelta, time
from statistics import mean

app = Flask(__name__)

# Use the DATABASE_URL environment variable provided by Heroku
database_url = os.environ.get('DATABASE_URL')

# Update the connection string if it starts with 'postgres://'
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql+psycopg2://', 1)

# Configure SQLAlchemy with the database URL
app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'postgresql+psycopg2://postgres:raspberry@localhost:5433/SensorReadings'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SECRET_KEY'] = 'yoursecretkey'

db = SQLAlchemy(app)

#migrate = Migrate(app, db)  # Initialize Flask-Migrate
#bcrypt = Bcrypt(app)
#login_manager = LoginManager(app)
#login_manager.login_view = 'login'  # Route to redirect for login
#login_manager.login_message = "Please log in to access this page."

class Timestamp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(20), unique=True, nullable=False)
    beehive_id = db.Column(db.Integer, nullable=False)
    
    temperature = db.relationship('Temperature', backref='timestamp', lazy=True)
    humidity = db.relationship('Humidity', backref='timestamp', lazy=True)
    weight = db.relationship('Weight', backref='timestamp', lazy=True)

# Define Temperature Table (4 columns)
class Temperature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp_id = db.Column(db.Integer, db.ForeignKey('timestamp.id'), nullable=False)
    temp1 = db.Column(db.Float, nullable=False)
    temp2 = db.Column(db.Float, nullable=False)
    temp3 = db.Column(db.Float, nullable=False)
    temp4 = db.Column(db.Float, nullable=False)

# Define Humidity Table (2 columns)
class Humidity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp_id = db.Column(db.Integer, db.ForeignKey('timestamp.id'), nullable=False)
    humid1 = db.Column(db.Float, nullable=False)
    humid2 = db.Column(db.Float, nullable=False)

# Define Weight Table (1 column)
class Weight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp_id = db.Column(db.Integer, db.ForeignKey('timestamp.id'), nullable=False)
    weight = db.Column(db.Float, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
#     password = db.Column(db.String(150), nullable=False)
    beehive_id = db.Column(db.Integer, nullable=False)

# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

# # Registration route (optional)
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
#         new_user = User(username=username, password=hashed_password)
#         db.session.add(new_user)
#         db.session.commit()
#         flash('Account created successfully! Please log in.', 'success')
#         return redirect(url_for('login'))
#     return render_template('register.html')

# # Login route
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         user = User.query.filter_by(username=username).first()
#         if user and bcrypt.check_password_hash(user.password, password):
#             login_user(user)
#             return redirect(url_for('index'))
#         else:
#             flash('Login failed. Check your credentials', 'danger')
#     return render_template('login.html')

# # Logout route
# @app.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('login'))

# ---------------------------------------------------------
# Helper Functions (optionally filter by bee_hive_id)
# ---------------------------------------------------------

def get_timestamps_with_values(beehive_id=None):
    with app.app_context():
        query = Timestamp.query.options(
                joinedload(Timestamp.temperature),
                joinedload(Timestamp.humidity),
                joinedload(Timestamp.weight)
        ).order_by(Timestamp.timestamp)
        if beehive_id:
            query = query.filter_by(beehive_id=beehive_id)
        timestamps = query.all()
        
        data = []
        for timestamp in timestamps:
            temperature = timestamp.temperature[0] if timestamp.temperature else None
            humidity = timestamp.humidity[0] if timestamp.humidity else None
            weight = timestamp.weight[0] if timestamp.weight else None

            if temperature and humidity and weight:
                data.append({
                    'timestamp': timestamp.timestamp,
                    'beehive_id': timestamp.beehive_id,
                    'temp1': temperature.temp1,
                    'temp2': temperature.temp2,
                    'temp3': temperature.temp3,
                    'temp4': temperature.temp4,
                    'humid1': humidity.humid1,
                    'humid2': humidity.humid2,
                    'weight': weight.weight
                })
        return data



# Function to filter data points for specific time ranges of the day
def filter_data_for_times(timestamps_data):
    filtered_data = []
    time_ranges = [
        (time(0, 0), time(0, 30)),
        (time(6, 0), time(6, 30)),
        (time(12, 0), time(12, 30)),
        (time(18, 0), time(18, 30))
    ]
    for entry in timestamps_data:
        timestamp_str = entry['timestamp']
        timestamp = datetime.strptime(timestamp_str, '%d/%m/%YT%H:%M:%S.%f')
        entry_time = timestamp.time()
        if any(start <= entry_time <= end for start, end in time_ranges):
            filtered_data.append(entry)
    return filtered_data

# Function to get the most recent sensor readings
def get_latest_readings(beehive_id=None):
    with app.app_context():
        query = Timestamp.query.order_by(Timestamp.id.desc())
        if beehive_id:
            query = query.filter_by(beehive_id=beehive_id)
        latest_timestamp = query.first()
        if latest_timestamp:
            temperature = Temperature.query.filter_by(timestamp_id=latest_timestamp.id).first()
            humidity = Humidity.query.filter_by(timestamp_id=latest_timestamp.id).first()
            weight = Weight.query.filter_by(timestamp_id=latest_timestamp.id).first()
            if temperature and humidity and weight:
                return {
                    'timestamp': latest_timestamp.timestamp,
                    'beehive_id': latest_timestamp.beehive_id,
                    'temp1': temperature.temp1,
                    'temp2': temperature.temp2,
                    'temp3': temperature.temp3,
                    'temp4': temperature.temp4,
                    'humid1': humidity.humid1,
                    'humid2': humidity.humid2,
                    'weight': weight.weight
                }
        return None

# Function to calculate summary statistics for a given set of data
def calculate_summary(data, time_ranges):
    summary = {period: {'mean': None, 'min': None, 'max': None, 'count': 0} for period in time_ranges.keys()}
    for entry in data:
        timestamp_str = entry['timestamp']
        timestamp = datetime.strptime(timestamp_str, '%d/%m/%YT%H:%M:%S.%f')
        entry_time = timestamp.time()
        for period, (start, end) in time_ranges.items():
            if start <= entry_time < end:
                values = entry['values']
                if values:
                    if summary[period]['count'] == 0:
                        summary[period]['mean'] = mean(values)
                        summary[period]['min'] = min(values)
                        summary[period]['max'] = max(values)
                    else:
                        summary[period]['mean'] = (summary[period]['mean'] * summary[period]['count'] + sum(values)) / (summary[period]['count'] + len(values))
                        summary[period]['min'] = min(summary[period]['min'], min(values))
                        summary[period]['max'] = max(summary[period]['max'], max(values))
                    summary[period]['count'] += len(values)
    return summary

# Function to get the summary statistics for each category (temperature, humidity, weight)
def get_summary_statistics(timestamps_data):
    time_ranges = {
        'Morning': (time(6, 0), time(12, 0)),
        'Afternoon': (time(12, 0), time(18, 0)),
        'Evening': (time(18, 0), time(23, 59)),
        'Night': (time(0, 0), time(6, 0))
    }

    # temp_data = [{'timestamp': entry['timestamp'], 'values': [entry['values'][i] for i in sensor_positions['temperature']]} for entry in timestamps_data if len(entry['values']) > max(sensor_positions['temperature'])]
    # humidity_data = [{'timestamp': entry['timestamp'], 'values': [entry['values'][i] for i in sensor_positions['humidity']]} for entry in timestamps_data if len(entry['values']) > max(sensor_positions['humidity'])]
    # weight_data = [{'timestamp': entry['timestamp'], 'values': [entry['values'][i] for i in sensor_positions['weight']]} for entry in timestamps_data if len(entry['values']) > max(sensor_positions['weight'])]

    temp_data = [{'timestamp': entry['timestamp'], 'values': [entry['temp1'], entry['temp2'], entry['temp3'], entry['temp4']]} for entry in timestamps_data]
    humidity_data = [{'timestamp': entry['timestamp'], 'values': [entry['humid1'], entry['humid2']]} for entry in timestamps_data]
    weight_data = [{'timestamp': entry['timestamp'], 'values': [entry['weight']]} for entry in timestamps_data]

    temp_summary = calculate_summary(temp_data, time_ranges)
    humidity_summary = calculate_summary(humidity_data, time_ranges)
    weight_summary = calculate_summary(weight_data, time_ranges)

    return temp_summary, humidity_summary, weight_summary

# ---------------------------------------------------------
# Webserver Routes
# ---------------------------------------------------------

@app.context_processor
def inject_hives():
    # 1. Grab all the distinct hive IDs
    hive_list = [row[0] for row in db.session.query(distinct(Timestamp.beehive_id)).order_by(Timestamp.beehive_id.asc()).all()]
    # 2. Read current hive from query (fallback to first hive if none)
    current = request.args.get('beehive_id', type=int)

    # Check if it's the landing page, and set current to None if so
    if current is None and hive_list:
        current = hive_list[0]
    if request.endpoint == 'landing_page':
        current = None  # This will prevent hive tabs from being shown on the landing page

    return {
        'hive_list': hive_list,
        'current_beehive_id': current
    }

@app.route('/')
def landing_page():
    # Get all distinct hive IDs
    hive_ids = [row[0] for row in db.session.query(distinct(Timestamp.beehive_id)).order_by(Timestamp.beehive_id).all()]

    # Get latest readings for each hive
    latest_readings_list = []
    for hive_id in hive_ids:
        latest = get_latest_readings(hive_id)
        if latest:
            latest_readings_list.append(latest)

    return render_template('landing_page.html', latest_readings_list=latest_readings_list)

@app.route('/all_data', endpoint='all_data')
#@login_required
def index():
    # Retrieve beehive_id from request
    beehive_id = request.args.get('beehive_id', type=int)

    # If none provided, pull the very first hive_id in the DB
    if beehive_id is None:
        first_row = (
            db.session.query(Timestamp.beehive_id)
            .distinct()
            .order_by(Timestamp.beehive_id.asc()) # Order so lowest ID is first
            .first()
        )
        if first_row:
            beehive_id = first_row[0]
        else:
            return "No beehives found in the database", 404

    # Set default start_date and end_date to last 7 days
    end_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    # Override defaults if provided in the request arguments
    if 'start_date' in request.args:
        start_date = request.args['start_date']
    if 'end_date' in request.args:
        end_date = request.args['end_date']

    timestamps_data = get_timestamps_with_values(beehive_id)

    # Fetch all distinct hive IDs for the tabs
    hive_list = [row[0] for row in db.session.query(distinct(Timestamp.beehive_id)).order_by(Timestamp.beehive_id.asc()).all()]

    # Filter data by date range if start_date and end_date are provided
    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        timestamps_data = [entry for entry in timestamps_data 
                           if start_datetime <= datetime.strptime(entry['timestamp'], '%d/%m/%YT%H:%M:%S.%f') <= end_datetime]

    # Extracting data for plots with length checks
    all_timestamps = [entry['timestamp'] for entry in timestamps_data]
    all_temp1 = [entry['temp1'] for entry in timestamps_data]
    all_temp2 = [entry['temp2'] for entry in timestamps_data]
    all_temp3 = [entry['temp3'] for entry in timestamps_data]
    all_temp4 = [entry['temp4'] for entry in timestamps_data]
    all_humidity1 = [entry['humid1'] for entry in timestamps_data]
    all_humidity2 = [entry['humid2'] for entry in timestamps_data]
    all_weight = [entry['weight'] for entry in timestamps_data]

    # Filter data for specific time ranges
    filtered_data = filter_data_for_times(timestamps_data)

    # Extracting data for table with length checks
    timestamps = [entry['timestamp'] for entry in filtered_data]

    temp1 = [entry['temp1'] for entry in filtered_data]
    temp2 = [entry['temp2'] for entry in filtered_data]
    temp3 = [entry['temp3'] for entry in filtered_data]
    temp4 = [entry['temp4'] for entry in filtered_data]
    humidity1 = [entry['humid1'] for entry in filtered_data]
    humidity2 = [entry['humid2'] for entry in filtered_data]
    weight = [entry['weight'] for entry in filtered_data]

    # Debug: Print the filtered data
    #print("Filtered Data for Table:", filtered_data)

    # Calculate summary statistics
    temp_summary, humidity_summary, weight_summary = get_summary_statistics(timestamps_data)

    # Plotting
    maxtick = 6
    plt.figure(figsize=(12, 6))

    # --------------------
    # Temperature plot
    # --------------------

    plt.plot(all_timestamps, all_temp1, color='red', label='Brood')
    plt.plot(all_timestamps, all_temp2, color='blue', label='Super')
    plt.plot(all_timestamps, all_temp3, color='green', label='Outside')
    plt.plot(all_timestamps, all_temp4, color='orange', label='Roof')

    plt.title('Temperature Readings')
    plt.xlabel('Timestamp')
    plt.ylabel('Temperature (°C)')
    plt.legend()
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=maxtick))  # Reduce the number of ticks
    plt.tight_layout()

    # Ensure the directory for saving the plot exists
    static_dir = os.path.join(app.root_path, 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    # Saving temperature plot to a file
    temp_plot_path = os.path.join(static_dir, 'temperature_plot.png')
    plt.savefig(temp_plot_path)
    plt.close()

    # --------------------
    # Plotting Humidity
    # --------------------

    plt.figure(figsize=(12, 6))
    plt.plot(all_timestamps, all_humidity1, color='cyan', label='Outside')
    plt.plot(all_timestamps, all_humidity2, color='magenta', label='Roof')

    plt.title('Humidity Readings')
    plt.xlabel('Timestamp')
    plt.ylabel('Humidity (%)')
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=maxtick))  # Reduce the number of ticks 
    plt.legend()
    plt.tight_layout()

    # Saving humidity plot to a file
    humidity_plot_path = os.path.join(static_dir, 'humidity_plot.png')
    plt.savefig(humidity_plot_path)
    plt.close()

    # --------------------
    # Plotting Weight
    # --------------------

    plt.figure(figsize=(12, 6))
    plt.plot(all_timestamps, all_weight, color='black', label='Weight')

    plt.title('Weight Readings')
    plt.xlabel('Timestamp')
    plt.ylabel('Weight (kg)')
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=maxtick))  # Reduce the number of ticks
    plt.legend()
    plt.tight_layout()

    # Saving weight plot to a file
    weight_plot_path = os.path.join(static_dir, 'weight_plot.png')
    plt.savefig(weight_plot_path)
    plt.close()

    # Rendering template with the plot paths and table data
    return render_template('index.html', 
                           temp_plot_path='/static/temperature_plot.png', 
                           humidity_plot_path='/static/humidity_plot.png', 
                           weight_plot_path='/static/weight_plot.png',
                           timestamps=timestamps,
                           temp1=temp1,
                           temp2=temp2,
                           temp3=temp3,
                           temp4=temp4,
                           humidity1=humidity1,
                           humidity2=humidity2,
                           weight=weight,
                           temp_summary=temp_summary,
                           humidity_summary=humidity_summary,
                           weight_summary=weight_summary,
                           beehive_id=beehive_id,
                           hive_list=hive_list,
)

@app.route('/temperature')
def temperature_page():
    beehive_id = request.args.get('beehive_id', type=int)
    # If none provided, pull the very first hive_id in the DB
    if beehive_id is None:
        first_row = (
            db.session.query(Timestamp.beehive_id)
            .distinct()
            .order_by(Timestamp.beehive_id.asc()) # Order so lowest ID is first
            .first()
        )
        if first_row:
            beehive_id = first_row[0]
        else:
            return "No beehives found in the database", 404

    # Set default start_date and end_date to last 7 days
    end_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    if 'start_date' in request.args:
        start_date = request.args['start_date']
    if 'end_date' in request.args:
        end_date = request.args['end_date']

    timestamps_data = get_timestamps_with_values(beehive_id)

    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        timestamps_data = [entry for entry in timestamps_data if start_datetime <= datetime.strptime(entry['timestamp'], '%d/%m/%YT%H:%M:%S.%f') <= end_datetime]

    all_timestamps = [entry['timestamp'] for entry in timestamps_data]
    all_temp1 = [entry['temp1'] for entry in timestamps_data]
    all_temp2 = [entry['temp2'] for entry in timestamps_data]
    all_temp3 = [entry['temp3'] for entry in timestamps_data]
    all_temp4 = [entry['temp4'] for entry in timestamps_data]

    # -------------------
    # Generate Plot
    # -------------------

    maxtick = 6
    plt.figure(figsize=(12, 6))
    plt.plot(all_timestamps, all_temp1, color='red', label='Brood')
    plt.plot(all_timestamps, all_temp2, color='blue', label='Super')
    plt.plot(all_timestamps, all_temp3, color='green', label='Outside')
    plt.plot(all_timestamps, all_temp4, color='orange', label='Roof')
    plt.title('Temperature Readings')
    plt.xlabel('Timestamp')
    plt.ylabel('Temperature (°C)')
    plt.legend()
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=maxtick))
    plt.tight_layout()

    static_dir = os.path.join(app.root_path, 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    temp_plot_path = os.path.join(static_dir, 'temperature_plot.png')
    plt.savefig(temp_plot_path)
    plt.close()

    return render_template('temperature.html',
                           temp_plot_path='/static/temperature_plot.png',
                           timestamps=all_timestamps,
                           temp1=all_temp1,
                           temp2=all_temp2,
                           temp3=all_temp3,
                           temp4=all_temp4,
                           beehive_id=beehive_id)

@app.route('/humidity')
def humidity_page():
    beehive_id = request.args.get('beehive_id', type=int)
    # If none provided, pull the very first hive_id in the DB
    if beehive_id is None:
        first_row = (
            db.session.query(Timestamp.beehive_id)
            .distinct()
            .order_by(Timestamp.beehive_id.asc()) # Order so lowest ID is first
            .first()
        )
        if first_row:
            beehive_id = first_row[0]
        else:
            return "No beehives found in the database", 404
            
    end_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    if 'start_date' in request.args:
        start_date = request.args['start_date']
    if 'end_date' in request.args:
        end_date = request.args['end_date']

    timestamps_data = get_timestamps_with_values(beehive_id)

    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        timestamps_data = [entry for entry in timestamps_data if start_datetime <= datetime.strptime(entry['timestamp'], '%d/%m/%YT%H:%M:%S.%f') <= end_datetime]

    all_timestamps = [entry['timestamp'] for entry in timestamps_data]
    all_humidity1 = [entry['humid1'] for entry in timestamps_data]
    all_humidity2 = [entry['humid2'] for entry in timestamps_data]

    # -------------------
    # Generate Plot
    # -------------------
    
    maxtick = 6
    plt.figure(figsize=(12, 6))
    plt.plot(all_timestamps, all_humidity1, color='cyan', label='Outside')
    plt.plot(all_timestamps, all_humidity2, color='magenta', label='Roof')
    plt.title('Humidity Readings')
    plt.xlabel('Timestamp')
    plt.ylabel('Humidity (%)')
    plt.legend()
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=maxtick))
    plt.tight_layout()

    static_dir = os.path.join(app.root_path, 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    humidity_plot_path = os.path.join(static_dir, 'humidity_plot.png')
    plt.savefig(humidity_plot_path)
    plt.close()

    return render_template('humidity.html',
                           humidity_plot_path='/static/humidity_plot.png',
                           timestamps=all_timestamps,
                           humidity1=all_humidity1,
                           humidity2=all_humidity2,
                           beehive_id=beehive_id)

@app.route('/weight')
def weight_page():
    beehive_id = request.args.get('beehive_id', type=int)
    # If none provided, pull the very first hive_id in the DB
    if beehive_id is None:
        first_row = (
            db.session.query(Timestamp.beehive_id)
            .distinct()
            .order_by(Timestamp.beehive_id.asc()) # Order so lowest ID is first
            .first()
        )
        if first_row:
            beehive_id = first_row[0]
        else:
            return "No beehives found in the database", 404

    end_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    if 'start_date' in request.args:
        start_date = request.args['start_date']
    if 'end_date' in request.args:
        end_date = request.args['end_date']

    timestamps_data = get_timestamps_with_values(beehive_id)

    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        timestamps_data = [entry for entry in timestamps_data if start_datetime <= datetime.strptime(entry['timestamp'], '%d/%m/%YT%H:%M:%S.%f') <= end_datetime]

    all_timestamps = [entry['timestamp'] for entry in timestamps_data]
    all_weight = [entry['weight'] for entry in timestamps_data]

    # -------------------
    # Generate Plot
    # -------------------

    maxtick = 6
    plt.figure(figsize=(12, 6))
    plt.plot(all_timestamps, all_weight, color='brown', label='Weight')
    plt.title('Weight Readings')
    plt.xlabel('Timestamp')
    plt.ylabel('Weight (kg)')
    plt.legend()
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=maxtick))
    plt.tight_layout()

    static_dir = os.path.join(app.root_path, 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    weight_plot_path = os.path.join(static_dir, 'weight_plot.png')
    plt.savefig(weight_plot_path)
    plt.close()

    return render_template('weight.html',
                           weight_plot_path='/static/weight_plot.png',
                           timestamps=all_timestamps,
                           weight=all_weight,
                           beehive_id=beehive_id)

@app.route('/export_temperature', methods=['GET'])
def export_temperature():
    beehive_id = request.args.get('beehive_id', type=int)

    # Fetch the filtered data (same logic as in the temperature route)
    timestamps_data = get_timestamps_with_values(beehive_id)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        timestamps_data = [entry for entry in timestamps_data if start_datetime <= datetime.strptime(entry['timestamp'], '%d/%m/%YT%H:%M:%S.%f') <= end_datetime]

    all_timestamps = [entry['timestamp'] for entry in timestamps_data]
    all_temp1 = [entry['temp1'] for entry in timestamps_data]
    all_temp2 = [entry['temp2'] for entry in timestamps_data]
    all_temp3 = [entry['temp3'] for entry in timestamps_data]
    all_temp4 = [entry['temp4'] for entry in timestamps_data]

    # Create a CSV string
    csv_data = 'Timestamp,Brood Temp,Super Temp,Outside Temp,Roof Temp\n'
    for i in range(len(all_timestamps)):
        csv_data += f'{all_timestamps[i]},{all_temp1[i]},{all_temp2[i]},{all_temp3[i]},{all_temp4[i]}\n'

    # Create a response with the CSV string
    response = make_response(csv_data)
    response.headers['Content-Disposition'] = 'attachment; filename=temperature_readings.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

@app.route('/export_humidity', methods=['GET'])
def export_humidity():
    beehive_id = request.args.get('beehive_id', type=int)

    # Fetch the filtered data (same logic as in the humidity route)
    timestamps_data = get_timestamps_with_values(beehive_id)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        timestamps_data = [entry for entry in timestamps_data if start_datetime <= datetime.strptime(entry['timestamp'], '%d/%m/%YT%H:%M:%S.%f') <= end_datetime]

    all_timestamps = [entry['timestamp'] for entry in timestamps_data]
    all_humidity1 = [entry['humid1'] for entry in timestamps_data]
    all_humidity2 = [entry['humid2'] for entry in timestamps_data]

    # Create a CSV string
    csv_data = 'Timestamp,Outside Humidity,Roof Humidity\n'
    for i in range(len(all_timestamps)):
        csv_data += f'{all_timestamps[i]},{all_humidity1[i]},{all_humidity2[i]}\n'

    # Create a response with the CSV string
    response = make_response(csv_data)
    response.headers['Content-Disposition'] = 'attachment; filename=humidity_readings.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

@app.route('/export_weight', methods=['GET'])
def export_weight():
    beehive_id = request.args.get('beehive_id', type=int)

    # Fetch the filtered data (same logic as in the weight route)
    timestamps_data = get_timestamps_with_values(beehive_id)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        timestamps_data = [entry for entry in timestamps_data if start_datetime <= datetime.strptime(entry['timestamp'], '%d/%m/%YT%H:%M:%S.%f') <= end_datetime]

    all_timestamps = [entry['timestamp'] for entry in timestamps_data]
    all_weight = [entry['weight'] for entry in timestamps_data]

    # Create a CSV string
    csv_data = 'Timestamp,Weight\n'
    for i in range(len(all_timestamps)):
        csv_data += f'{all_timestamps[i]},{all_weight[i]}\n'

    # Create a response with the CSV string
    response = make_response(csv_data)
    response.headers['Content-Disposition'] = 'attachment; filename=weight_readings.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

# Route to serve favicon.ico
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Function to process and store incoming sensor data
@app.route('/post_endpoint', methods=['POST'])
def post_endpoint():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON"}), 400

            # Extract timestamp and sensor values
            timestamp_str = data.get('timestamp')
            beehive_id = data.get('beehive_id')
            if not timestamp_str:
                return jsonify({"error": "Missing timestamp"}), 400
            if beehive_id is None:
                return jsonify({"error": "Missing Beehive ID"}), 400

            required_keys = ["temp1", "temp2", "humid1", "temp3", "humid2", "temp4", "weight"]
            if any(key not in data for key in required_keys):
                return jsonify({"error": "Missing sensor values"}), 400

            # Store timestamp
            timestamp = Timestamp(timestamp=timestamp_str, beehive_id=beehive_id)
            db.session.add(timestamp)
            db.session.commit()

            # Store temperature readings
            temperature_entry = Temperature(
                timestamp_id=timestamp.id,
                temp1=data["temp1"],
                temp2=data["temp2"],
                temp3=data["temp3"],
                temp4=data["temp4"]
            )
            db.session.add(temperature_entry)

            # Store humidity readings
            humidity_entry = Humidity(
                timestamp_id=timestamp.id,
                humid1=data["humid1"],
                humid2=data["humid2"]
            )
            db.session.add(humidity_entry)

            # Store weight reading
            weight_entry = Weight(
                timestamp_id=timestamp.id,
                weight=data["weight"]
            )
            db.session.add(weight_entry)

            db.session.commit()
            return jsonify({"message": "Data added successfully"}), 200

        except Exception as e:
            db.session.rollback()  # Roll back changes on error
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
