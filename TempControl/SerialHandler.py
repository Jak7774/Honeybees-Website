# SerialHandler.py
import serial
import time

class ArduinoSerialHandler:
    def __init__(self, port, baud_rate):
        self.port = port
        self.baud_rate = baud_rate
        self.serial = None

    def open_connection(self):
        self.serial = serial.Serial(self.port, self.baud_rate)

    def close_connection(self):
        if self.serial:
            self.serial.close()
    
    # In SerialHandler.py, modify the read_temperatures method
    def read_temperatures(self, max_retries=3):
        for _ in range(max_retries):
            try:
                self.serial.flush()
                data = self.serial.readline().decode('utf-8').rstrip()
                temperatures = [float(temp) for temp in data.split(",") if temp]
                return temperatures[0], temperatures[3]  # Return the first two values
            except ValueError:
                return [40, 30]
            except serial.SerialException as e:
                print(f"Error reading temperatures: {e}")
                print("Retrying...")
                time.sleep(1)  # Add a delay between retries
        else:
            print("Max retries reached. Returning placeholder values.")
            return [40, 30]  # Return placeholder values or handle the error as needed

