from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import matplotlib
matplotlib.use('Agg')
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt

import os
from datetime import datetime, timedelta, time

app = Flask(__name__)

# Use the DATABASE_URL environment variable provided by Heroku
database_url = os.environ.get('DATABASE_URL')

# Update the connection string if it starts with 'postgres://'
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql+psycopg2://', 1)

# Configure SQLAlchemy with the database URL
app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'postgresql+psycopg2://postgres:raspberry@localhost/SensorReadings'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Timestamp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(20))
    values = db.relationship('Value', backref='timestamp', lazy=True)

class Value(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp_id = db.Column(db.Integer, db.ForeignKey('timestamp.id'), nullable=False)
    value = db.Column(db.Float)

# Function to retrieve all timestamps with their corresponding values
def get_timestamps_with_values():
    with app.app_context():
        timestamps = Timestamp.query.all()
        data = []
        for timestamp in timestamps:
            values = [value.value for value in timestamp.values]
            data.append({'timestamp': timestamp.timestamp, 'values': values})
        # Sort the data by timestamps
        data.sort(key=lambda x: datetime.strptime(x['timestamp'], '%d/%m/%YT%H:%M:%S'))
        
        # Debug: Print the fetched data
        #print("Fetched Data:", data)
        
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
        timestamp = datetime.strptime(timestamp_str, '%d/%m/%YT%H:%M:%S')
        entry_time = timestamp.time()
        if any(start <= entry_time <= end for start, end in time_ranges):
            filtered_data.append(entry)
    return filtered_data

# Function to get the most recent sensor readings
def get_latest_readings():
    with app.app_context():
        latest_timestamp = Timestamp.query.order_by(Timestamp.id.desc()).first()
        if latest_timestamp:
            latest_values = [value.value for value in latest_timestamp.values]
            return {'timestamp': latest_timestamp.timestamp, 'values': latest_values}
        return None

@app.route('/')
def landing_page():
    latest_readings = get_latest_readings()
    return render_template('landing_page.html', latest_readings=latest_readings)

@app.route('/all_data')
def index():
    # Set default start_date and end_date to last 7 days
    end_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    # Override defaults if provided in the request arguments
    if 'start_date' in request.args:
        start_date = request.args['start_date']
    if 'end_date' in request.args:
        end_date = request.args['end_date']

    timestamps_data = get_timestamps_with_values()

    # Filter data by date range if start_date and end_date are provided
    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        timestamps_data = [entry for entry in timestamps_data if start_datetime <= datetime.strptime(entry['timestamp'], '%d/%m/%YT%H:%M:%S') <= end_datetime]

     # Extracting data for plots with length checks
    all_timestamps = [entry['timestamp'] for entry in timestamps_data]
    all_temp1 = [entry['values'][0] if len(entry['values']) > 0 else None for entry in timestamps_data]
    all_temp2 = [entry['values'][1] if len(entry['values']) > 1 else None for entry in timestamps_data]
    all_temp3 = [entry['values'][3] if len(entry['values']) > 3 else None for entry in timestamps_data]
    all_temp4 = [entry['values'][5] if len(entry['values']) > 5 else None for entry in timestamps_data]
    all_humidity1 = [entry['values'][2] if len(entry['values']) > 2 else None for entry in timestamps_data]
    all_humidity2 = [entry['values'][4] if len(entry['values']) > 4 else None for entry in timestamps_data]
    all_weight = [entry['values'][6] if len(entry['values']) > 6 else None for entry in timestamps_data]

    # Filter data for specific time ranges
    filtered_data = filter_data_for_times(timestamps_data)

    # Extracting data for table with length checks
    timestamps = [entry['timestamp'] for entry in filtered_data]
    temp1 = [entry['values'][0] if len(entry['values']) > 0 else None for entry in filtered_data]
    temp2 = [entry['values'][1] if len(entry['values']) > 1 else None for entry in filtered_data]
    temp3 = [entry['values'][3] if len(entry['values']) > 3 else None for entry in filtered_data]
    temp4 = [entry['values'][5] if len(entry['values']) > 5 else None for entry in filtered_data]
    humidity1 = [entry['values'][2] if len(entry['values']) > 2 else None for entry in filtered_data]
    humidity2 = [entry['values'][4] if len(entry['values']) > 4 else None for entry in filtered_data]
    weight = [entry['values'][6] if len(entry['values']) > 6 else None for entry in filtered_data]

    # Debug: Print the filtered data
    print("Filtered Data for Table:", filtered_data)

    # Plotting
    maxtick = 6
    plt.figure(figsize=(12, 6))

    # Temperature plot
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

    # Plotting Humidity
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

    # Plotting Weight
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
                           weight=weight)

# Route to serve favicon.ico
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/post_endpoint', methods=['POST'])
def post_endpoint():
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            timestamp_str = data.get('timestamp')
            values_str = data.get('values')
            
            if not timestamp_str or not values_str:
                return jsonify({"error": "Missing timestamp or values"}), 400

            timestamp = Timestamp(timestamp=timestamp_str)
            db.session.add(timestamp)
            db.session.commit()

            values_list = [float(val) for val in values_str.split(',')]
            for val in values_list:
                value = Value(timestamp_id=timestamp.id, value=val)
                db.session.add(value)
            
            db.session.commit()
            return jsonify({"message": "Data added successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
