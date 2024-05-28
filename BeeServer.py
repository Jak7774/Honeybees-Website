from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import os
#import psycopg2
from datetime import datetime, timedelta

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
        return data

@app.route('/')
def index():
    # Set default start_date and end_date to last 7 days
    end_date = datetime.now().strftime('%Y-%m-%d')
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
    
    # Extracting data
    timestamps = [entry['timestamp'] for entry in timestamps_data]
    temp1 = [entry['values'][0] for entry in timestamps_data]
    temp2 = [entry['values'][1] for entry in timestamps_data]
    temp3 = [entry['values'][3] for entry in timestamps_data]
    temp4 = [entry['values'][5] for entry in timestamps_data]
    humidity1 = [entry['values'][2] for entry in timestamps_data]
    humidity2 = [entry['values'][4] for entry in timestamps_data]
    weight = [entry['values'][6] for entry in timestamps_data]

    # Plotting
    plt.figure(figsize=(12, 6))

    # Temperature plot
    plt.plot(timestamps, temp1, color='red', label='Brood')
    plt.plot(timestamps, temp2, color='blue', label='Super')
    plt.plot(timestamps, temp3, color='green', label='Outside')
    plt.plot(timestamps, temp4, color='orange', label='Roof')

    plt.title('Temperature Readings')
    plt.xlabel('Timestamp')
    plt.ylabel('Temperature (°C)')
    plt.legend()
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
    plt.plot(timestamps, humidity1, color='cyan', label='Outside')
    plt.plot(timestamps, humidity2, color='magenta', label='Roof')
    plt.title('Humidity Readings')
    plt.xlabel('Timestamp')
    plt.ylabel('Humidity (%)')
    plt.legend()
    plt.tight_layout()

    # Saving humidity plot to a file
    humidity_plot_path = os.path.join(static_dir, 'humidity_plot.png')
    plt.savefig(humidity_plot_path)
    plt.close()

    # Plotting Weight
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, weight, color='black', label='Weight')
    plt.title('Weight Readings')
    plt.xlabel('Timestamp')
    plt.ylabel('Weight (kg)')
    plt.legend()
    plt.tight_layout()

    # Saving weight plot to a file
    weight_plot_path = os.path.join(static_dir, 'weight_plot.png')
    plt.savefig(weight_plot_path)
    plt.close()

    # Rendering template with the plot paths
    return render_template('index.html', temp_plot_path='/static/temperature_plot.png', 
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
    app.run(debug=False)
