import serial
import time

from parser import *


# Update with your new COM ports and baud rates
CONFIG_PORT = "COM5"  # Replace with your configuration COM port
DATA_PORT = "COM10"    # Replace with your data COM port
BAUD_RATE_CONFIG = 115200
BAUD_RATE_DATA = 921600
TIMEOUT = 2
          
#self.cliCom = serial.Serial(cliCom, 115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0.6)
#self.dataCom = serial.Serial(dataCom, 921600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0.6)

vitals_patient_data = []

def send_command(serial_port, command):
    """Send a single command to the board."""
    try:
        serial_port.write(command.encode() + b'\n')  # Send the command
        time.sleep(0.1)  # Delay for command processing
        response = serial_port.readlines()  # Read the response
        for line in response:
            print(f"Response: {line.decode('utf-8', errors='ignore').strip()}")
    except Exception as e:
        print(f"Error sending command: {e}")

def send_config(serial_port, config_file_path):
    """Send a configuration file to the board."""
    try:
        with open(config_file_path, 'r') as config_file:
            for line in config_file:
                if line.strip() and not line.startswith('%'):  # Skip comments and blank lines
                    print(f"Sending: {line.strip()}")
                    send_command(serial_port, line.strip())
        print("Configuration completed.")
    except Exception as e:
        print(f"Error sending configuration: {e}")



def main():
    config_file = "vital_signs_ISK_2m.cfg"  # Replace with your .cfg file path

    try:
        # Open configuration and data ports
        with serial.Serial(CONFIG_PORT, BAUD_RATE_CONFIG, timeout=TIMEOUT) as config_port, \
             serial.Serial(DATA_PORT, 
                           BAUD_RATE_DATA,  
                           bytesize=serial.EIGHTBITS,
                           parity=serial.PARITY_NONE,
                           stopbits=serial.STOPBITS_ONE,
                           timeout=TIMEOUT) as data_port:
            
            # Send the configuration file
            print("Sending configuration...")
            send_config(config_port, config_file)

            parser = UARTParser(type="DoubleCOMPort")
            parser.dataCom = data_port

            while (1):
                output = parser.readAndParseUartDoubleCOMPort()
                print(output)
    
    except serial.SerialException as e:
        print(f"Serial error: {e}")

if __name__ == "__main__":
    main()
