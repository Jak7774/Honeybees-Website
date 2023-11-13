# TriggerScript.py
import subprocess
import time
from SerialHandler import ArduinoSerialHandler

def read_temperatures(serial_handler):
    serial_handler.open_connection()
    temp_brood, temp_outside = serial_handler.read_temperatures()
    serial_handler.close_connection()
    return temp_brood, temp_outside

def start_heating_control():
    print("Activating HeatingControl.py...")
    subprocess.Popen(["python3", "HeatingControl.py"])  # Run HeatingControl.py as a subprocess

def stop_heating_control():
    print("Stopping HeatingControl.py...")
    subprocess.run(["pkill", "-f", "HeatingControl.py"])  # Stop HeatingControl.py subprocess

def main():
    # Instance of ArduinoSerialHandler
    arduino_serial = ArduinoSerialHandler(port='/dev/ttyACM0', baud_rate=9600)

    heating_control_running = False

    try:
        temp_brood, temp_outside = read_temperatures(arduino_serial)
        print(f"Outside temperature: {temp_outside}°C")
        
        if temp_outside < 10 and temp_outside > -50 and not heating_control_running:
            # Start HeatingControl.py if outside temperature is below 10°C and it's not already running
            arduino_serial.close_connection()
            time.sleep(5)
            start_heating_control()
            heating_control_running = True

        elif temp_outside >= 10 and heating_control_running:
            # Stop HeatingControl.py if outside temperature is 10°C or above and it's currently running
            stop_heating_control()
            heating_control_running = False
        arduino_serial.close_connection()
        #time.sleep(1)  # Adjust the sleep duration as needed

    except KeyboardInterrupt:
        print("Program terminated by user.")
        if heating_control_running:
            stop_heating_control()

if __name__ == "__main__":
    main()
    