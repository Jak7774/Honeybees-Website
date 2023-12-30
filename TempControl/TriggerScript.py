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
    process = subprocess.Popen(["python3", "HeatingControl.py"])
    return_code = process.wait()
    if return_code == 0:
        print("HeatingControl.py has finished successfully.")
    else:
        print(f"HeatingControl.py exited with return code {return_code}.")

def stop_heating_control():
    print("Stopping HeatingControl.py...")
    subprocess.run(["pkill", "-f", "HeatingControl.py"])  # Stop HeatingControl.py subprocesss
    
def main():
    # Instance of ArduinoSerialHandler
    arduino_serial = ArduinoSerialHandler(port='/dev/ttyACM0', baud_rate=9600)

    #heating_control_running = False

    try:
        temp_brood, temp_outside = read_temperatures(arduino_serial)
        arduino_serial.close_connection()
        #temp_outside = 0 # For Debugging
        print(f"Outside temperature: {temp_outside}°C")     
        if temp_outside < 10: #and not heating_control_running:
            # Start HeatingControl.py if outside temperature is below 10°C and it's not already running
            arduino_serial.close_connection()
            time.sleep(5)
            start_heating_control()
            #heating_control_running = True

        elif temp_outside >= 10: #and heating_control_running:
            arduino_serial.close_connection()
            # Stop HeatingControl.py if outside temperature is 10°C or above and it's currently running
            time.sleep(5)
            stop_heating_control()
            #heating_control_running = False
        #time.sleep(1)  # Adjust the sleep duration as needed

    except KeyboardInterrupt:
        arduino_serial.close_connection()
        print("Program terminated by user.")
        if heating_control_running:
            stop_heating_control()
            
    finally:
        arduino_serial.close_connection()
        
if __name__ == "__main__":
    main()
    
