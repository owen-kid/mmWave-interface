
import socket
import time
import json
import struct
import threading
import numpy as np
# Import your existing BoardInterface class and other dependencies
# from board_interface import BoardInterface

# Function to connect to the server via TCP
def connect_to_server(server_addr, port=5025):
    """Connect to the server via TCP"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server_addr, port))
        print(f"Connected to server at {server_addr}:{port}")
        return sock
    except Exception as e:
        print(f"Failed to connect to server: {e}")
        return None

# Function to send data to the server
def send_data(sock, hr, br, patient_detected):
    """Send heart rate and breath rate data to the server"""
    if not sock:
        return False
    
    try:
        # Create a JSON payload
        data = json.dumps({
            "heartRate": hr,
            "breathRate": br,
            "pd": patient_detected, 
            "timestamp": time.time() * 1000
        })
        
        # Send the data with a newline delimiter
        sock.send((data + '\n').encode('utf-8'))
        return True
    except Exception as e:
        print(f"Error sending data: {e}")
        return False

# Simulation function to generate test data (replace with your sensor data)
def simulate_sensor_data():
    """Simulate sensor data for testing"""
    hr_base = 70
    br_base = 16
    time_elapsed = 0
    
    while True:
        # Simulate some variation in the heart rate and breath rate
        time_elapsed += 1
        hr = hr_base + 5 * (0.5 - (time_elapsed % 10) / 10)
        br = br_base + 2 * (0.5 - (time_elapsed % 15) / 15)
        
        yield hr, br
        time.sleep(1)

# Function to integrate with your actual mmWave radar sensor
def read_from_mmwave_sensor():
    """Read data from the mmWave radar sensor"""
    try:
        # Initialize your sensor interface
        from board_interface import BoardInterface
        from parser import UARTParser
        
        bi = BoardInterface()
        bi.setup_ports()
        #bi.send_config(bi.config, bi.config_file)
        
        parser = UARTParser(type="DoubleCOMPort")
        parser.dataCom = bi.data
        patient_detected = 0 
        br = 0
        hr = 0
    except Exception as e:
        print(f"Failed to setup")

    while True:
        try:
            output = parser.readAndParseUartDoubleCOMPort()
            # print("\n\n" + str(output) + "\n\n")

            point_cloud = output.get('pointCloud', np.array([]))

            # print(f"Point cloud shape: {point_cloud.shape}")

            if point_cloud.shape[0] == 0:  # No points detected
                #  print("-")
                if patient_detected > -30:
                    patient_detected = patient_detected - 1
                continue
            else:
                # print("+")
                if patient_detected < 10:
                    patient_detected = patient_detected + 1

            if patient_detected < 0:
                print("patient not detected")
                yield hr, br, patient_detected
            else: 
                print("patient detected")
                yield hr, br, patient_detected

            if 'vitals' in output:
                hr = output['vitals']['heartRate']
                br = output['vitals']['breathRate']
                yield hr, br, patient_detected
            time.sleep(0.1)

        except Exception as e:
            print(f"Failed to while running")

           # Fall back to simulation if sensor fails
        # for hr, br in simulate_sensor_data():
           #  yield hr, br

# Main function to read from your radar sensor and send data to server
def main():
    # Replace with your server's IP address
    SERVER_ADDR = "172.20.10.3"  # Replace with your server's IP address
    SERVER_PORT = 5025
    
    # Connect to the server
    sock = connect_to_server(SERVER_ADDR, SERVER_PORT)
    if not sock:
        print("Could not connect to server. Exiting.")
        return
    
    try:
        # Choose which data source to use
        USE_REAL_SENSOR = True  # Set to True to use the actual mmWave sensor
        
        if USE_REAL_SENSOR:
            # Use real data from your mmWave sensor
            data_source = read_from_mmwave_sensor()
        else:
            # Use simulated data for testing
            data_source = simulate_sensor_data()
        
        # Process data and send to server
        for hr, br, patient_detected in data_source:
            print(f"Sending data - HR: {hr:.1f}, BR: {br:.1f}, PD: {patient_detected}")
            if not send_data(sock, hr, br, patient_detected):
                print("Connection lost. Attempting to reconnect...")
                sock = connect_to_server(SERVER_ADDR, SERVER_PORT)
                if not sock:
                    print("Reconnection failed. Exiting.")
                    break
    
    except KeyboardInterrupt:
        print("Interrupted. Closing connection.")
    finally:
        if sock:
            sock.close()

if __name__ == "__main__":
    main()
