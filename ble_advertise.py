import time
import subprocess
import sys
import struct

# Device name
DEVICE_NAME = "OIRD_Sensor"

def setup_ble():
    """Initialize the BLE adapter"""
    try:
        # Reset the adapter
        subprocess.call(['sudo', 'hciconfig', 'hci0', 'reset'])
        # Set device name
        subprocess.call(['sudo', 'hciconfig', 'hci0', 'name', DEVICE_NAME])
        # Make it discoverable
        subprocess.call(['sudo', 'hciconfig', 'hci0', 'piscan'])
        print("BLE adapter initialized")
        return True
    except Exception as e:
        print(f"Error setting up BLE: {e}")
        return False

def advertise_data(hr, br):
    """Advertise heart rate and breath rate data"""
    try:
        # Stop any ongoing advertisements
        subprocess.call(['sudo', 'hciconfig', 'hci0', 'noleadv'])
        
        # Start a new advertisement with manufacturer data
        # First two bytes are company ID (using a fake one)
        # Next bytes are heart rate (2 bytes) and breath rate (2 bytes)
        hr_bytes = struct.pack('<H', int(hr * 10))  # Multiply by 10 to preserve decimal
        br_bytes = struct.pack('<H', int(br * 10))
        
        # Convert to hex string for command
        hr_hex = hr_bytes.hex()
        br_hex = br_bytes.hex()
        
        # Manufacturer data command
        cmd = [
            'sudo', 'hcitool', 'cmd', '0x08', '0x0008',
            # Length (13 bytes), type (0x09 for complete local name)
            '13', '09',
            # Name as hex values (ASCII "OIRD_Sensor")
            '4F', '49', '52', '44', '5F', '53', '65', '6E', '73', '6F', '72',
            # Manufacturer specific data
            '05', 'FF',  # Length (5), type (0xFF for manufacturer data)
            'A1', 'B2',  # Company identifier (made up)
            hr_hex[:2], hr_hex[2:],  # Heart rate
            br_hex[:2], br_hex[2:]   # Breath rate
        ]
        
        # Execute the command
        subprocess.call(cmd)
        
        # Start advertising
        subprocess.call(['sudo', 'hciconfig', 'hci0', 'leadv', '0'])
        return True
    except Exception as e:
        print(f"Error advertising data: {e}")
        return False

def main():
    """Main function to demonstrate advertising"""
    if not setup_ble():
        print("Failed to set up BLE. Exiting.")
        sys.exit(1)
        
    print(f"Starting BLE advertisement as '{DEVICE_NAME}'")
    print("Press Ctrl+C to stop")
    
    try:
        # Generate sample data
        hr = 70.0
        br = 16.0
        
        while True:
            # Advertise the current data
            if advertise_data(hr, br):
                print(f"Advertising HR: {hr:.1f}, BR: {br:.1f}")
            else:
                print("Failed to advertise data")
                
            # Wait a bit
            time.sleep(1)
            
            # Simulate changing values
            hr = max(50, min(100, hr + (0.5 - 1.0 * (hr > 75))))
            br = max(10, min(25, br + (0.2 - 0.4 * (br > 18))))
            
    except KeyboardInterrupt:
        print("\nStopping advertisement")
        subprocess.call(['sudo', 'hciconfig', 'hci0', 'noleadv'])
        print("Advertisement stopped")

if __name__ == "__main__":
    main()
