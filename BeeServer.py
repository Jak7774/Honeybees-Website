from flask import Flask, render_template, send_from_directory, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy

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

# Function to calculate summary statistics for a given set of data
def calculate_summary(data, time_ranges):
    summary = {period: {'mean': None, 'min': None, 'max': None, 'count': 0} for period in time_ranges.keys()}
    for entry in data:
        timestamp_str = entry['timestamp']
        timestamp = datetime.strptime(timestamp_str, '%d/%m/%YT%H:%M:%S')
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
        'Evening': (time(18, 0), time(0, 0)),
        'Night': (time(0, 0), time(6, 0))
    }

    temp_data = [{'timestamp': entry['timestamp'], 'values': [entry['values'][i] for i in [0, 1, 3, 5]]} for entry in timestamps_data if len(entry['values']) > 5]
    humidity_data = [{'timestamp': entry['timestamp'], 'values': [entry['values'][i] for i in [2, 4]]} for entry in timestamps_data if len(entry['values']) > 4]
    weight_data = [{'timestamp': entry['timestamp'], 'values': [entry['values'][6]]} for entry in timestamps_data if len(entry['values']) > 6]

    temp_summary = calculate_summary(temp_data, time_ranges)
    humidity_summary = calculate_summary(humidity_data, time_ranges)
    weight_summary = calculate_summary(weight_data, time_ranges)

    return temp_summary, humidity_summary, weight_summary

@app.route('/')
def landing_page():
    latest_readings = get_latest_readings()
    print(latest_readings)
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

    # Get summary statistics
    temp_summary, humidity_summary, weight_summary = get_summary_statistics(timestamps_data)

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
                           weight=weight,
                           temp_summary=temp_summary,
                           humidity_summary=humidity_summary,
                           weight_summary=weight_summary)

@app.route('/temperature')
def temperature_page():
    # Set default start_date and end_date to last 7 days
    end_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    if 'start_date' in request.args:
        start_date = request.args['start_date']
    if 'end_date' in request.args:
        end_date = request.args['end_date']

    timestamps_data = get_timestamps_with_values()

    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        timestamps_data = [entry for entry in timestamps_data if start_datetime <= datetime.strptime(entry['timestamp'], '%d/%m/%YT%H:%M:%S') <= end_datetime]

    all_timestamps = [entry['timestamp'] for entry in timestamps_data]
    all_temp1 = [entry['values'][0] if len(entry['values']) > 0 else None for entry in timestamps_data]
    all_temp2 = [entry['values'][1] if len(entry['values']) > 1 else None for entry in timestamps_data]
    all_temp3 = [entry['values'][3] if len(entry['values']) > 3 else None for entry in timestamps_data]
    all_temp4 = [entry['values'][5] if len(entry['values']) > 5 else None for entry in timestamps_data]

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
                           temp4=all_temp4)

@app.route('/humidity')
def humidity_page():
    end_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    if 'start_date' in request.args:
        start_date = request.args['start_date']
    if 'end_date' in request.args:
        end_date = request.args['end_date']

    timestamps_data = get_timestamps_with_values()

    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        timestamps_data = [entry for entry in timestamps_data if start_datetime <= datetime.strptime(entry['timestamp'], '%d/%m/%YT%H:%M:%S') <= end_datetime]

    all_timestamps = [entry['timestamp'] for entry in timestamps_data]
    all_humidity1 = [entry['values'][2] if len(entry['values']) > 2 else None for entry in timestamps_data]
    all_humidity2 = [entry['values'][4] if len(entry['values']) > 4 else None for entry in timestamps_data]

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
                           humidity2=all_humidity2)

@app.route('/weight')
def weight_page():
    end_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    if 'start_date' in request.args:
        start_date = request.args['start_date']
    if 'end_date' in request.args:
        end_date = request.args['end_date']

    timestamps_data = get_timestamps_with_values()

    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        timestamps_data = [entry for entry in timestamps_data if start_datetime <= datetime.strptime(entry['timestamp'], '%d/%m/%YT%H:%M:%S') <= end_datetime]

    all_timestamps = [entry['timestamp'] for entry in timestamps_data]
    all_weight = [entry['values'][6] if len(entry['values']) > 6 else None for entry in timestamps_data]

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
                           weight=all_weight)

@app.route('/export_temperature', methods=['GET'])
def export_temperature():
    # Fetch the filtered data (same logic as in the temperature route)
    timestamps_data = get_timestamps_with_values()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        timestamps_data = [entry for entry in timestamps_data if start_datetime <= datetime.strptime(entry['timestamp'], '%d/%m/%YT%H:%M:%S') <= end_datetime]

    all_timestamps = [entry['timestamp'] for entry in timestamps_data]
    all_temp1 = [entry['values'][0] if len(entry['values']) > 0 else None for entry in timestamps_data]
    all_temp2 = [entry['values'][1] if len(entry['values']) > 1 else None for entry in timestamps_data]
    all_temp3 = [entry['values'][3] if len(entry['values']) > 3 else None for entry in timestamps_data]
    all_temp4 = [entry['values'][5] if len(entry['values']) > 5 else None for entry in timestamps_data]

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
    # Fetch the filtered data (same logic as in the humidity route)
    timestamps_data = get_timestamps_with_values()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        timestamps_data = [entry for entry in timestamps_data if start_datetime <= datetime.strptime(entry['timestamp'], '%d/%m/%YT%H:%M:%S') <= end_datetime]

    all_timestamps = [entry['timestamp'] for entry in timestamps_data]
    all_humidity1 = [entry['values'][2] if len(entry['values']) > 2 else None for entry in timestamps_data]
    all_humidity2 = [entry['values'][4] if len(entry['values']) > 4 else None for entry in timestamps_data]

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
    # Fetch the filtered data (same logic as in the weight route)
    timestamps_data = get_timestamps_with_values()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        timestamps_data = [entry for entry in timestamps_data if start_datetime <= datetime.strptime(entry['timestamp'], '%d/%m/%YT%H:%M:%S') <= end_datetime]

    all_timestamps = [entry['timestamp'] for entry in timestamps_data]
    all_weight = [entry['values'][6] if len(entry['values']) > 6 else None for entry in timestamps_data]

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
