import serial
import time

from parser import *

class BoardInterface:
    # Update with your new COM ports and baud rates
    CONFIG_PORT = "COM5"  # Replace with your configuration COM port
    DATA_PORT = "COM10"    # Replace with your data COM port
    BAUD_RATE_CONFIG = 115200
    BAUD_RATE_DATA = 921600
    TIMEOUT = 2
    config_file = "vital_signs_ISK_2m.cfg"
    config = None
    data = None
    
    vitals_patient_data = []

    def setup_ports(self):
        self.config = serial.Serial(self.CONFIG_PORT, self.BAUD_RATE_CONFIG, timeout=self.TIMEOUT)
        self.data = serial.Serial(self.DATA_PORT, self.BAUD_RATE_DATA,  
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=self.TIMEOUT)


    def send_command(self, serial_port, command):
        """Send a single command to the board."""
        try:
            serial_port.write(command.encode() + b'\n')  # Send the command
            time.sleep(0.1)  # Delay for command processing
            response = serial_port.readlines()  # Read the response
            for line in response:
                print(f"Response: {line.decode('utf-8', errors='ignore').strip()}")
        except Exception as e:
            print(f"Error sending command: {e}")

    def send_config(self, serial_port, config_file_path):
        """Send a configuration file to the board."""
        try:
            with open(config_file_path, 'r') as config_file:
                for line in config_file:
                    if line.strip() and not line.startswith('%'):  # Skip comments and blank lines
                        print(f"Sending: {line.strip()}")
                        self.send_command(serial_port, line.strip())
            print("Configuration completed.")
        except Exception as e:
            print(f"Error sending configuration: {e}")

    def print_nice_vitals(self, sensorOutput):
        if 'vitals' in sensorOutput:
            hr = sensorOutput['vitals']['heartRate']
            br = sensorOutput['vitals']['breathRate']
            hrWF = sensorOutput['vitals']['heartWaveform']
            brWF = sensorOutput['vitals']['breathWaveform']
            print("Heart rate: " + str(hr))
            print("Breath rate: " + str(br))
            #print("Heart rate waveform: " + hrWF)
            #print("Breath rate waveform: " + brWF)

    def get_nice_vitals(self, sensorOutput):
        if 'vitals' in sensorOutput:
            hr = sensorOutput['vitals']['heartRate']
            br = sensorOutput['vitals']['breathRate']
            hrWF = sensorOutput['vitals']['heartWaveform']
            brWF = sensorOutput['vitals']['breathWaveform']
            print("HERE")
            return hr, br
            #print("Heart rate waveform: " + hrWF)
            #print("Breath rate waveform: " + brWF)

    def parse_output(self):
        parser = UARTParser(type="DoubleCOMPort")
        parser.dataCom = self.data

        while (1):
            output = parser.readAndParseUartDoubleCOMPort()
            self.print_nice_vitals(output)

    def parse_output_2(self):
        parser = UARTParser(type="DoubleCOMPort")
        parser.dataCom = self.data

        while (1):
            output = parser.readAndParseUartDoubleCOMPort()
            return self.get_nice_vitals(output)


def main():
    bi = BoardInterface()
      # Replace with your .cfg file path

    try:
        # Open confguration and data ports
        bi.setup_ports()
            
        # Send the configuration file
        print("Sending configuration...")
        bi.send_config(bi.config, bi.config_file)

        bi.parse_output()
    
    except serial.SerialException as e:
        print(f"Serial error: {e}")

if __name__ == "__main__":
    main()
