import os
import time

print("Starting BLE advertisement for Web Bluetooth...")

# First reset and configure the controller
os.system('sudo hciconfig hci0 down')
os.system('sudo hciconfig hci0 up')
os.system('sudo hciconfig hci0 reset')

# Set the device name
os.system('sudo hciconfig hci0 name "OIRD_Sensor"')

# Make it discoverable
os.system('sudo hciconfig hci0 piscan')

# Configure advertisement to be more Web Bluetooth friendly
# This creates an advertisement with several key elements:
# 1. Sets it as a BLE device (LE General Discoverable Mode)
# 2. Includes the complete name
# 3. Advertises a service UUID

# First, stop any ongoing advertisements
os.system('sudo hciconfig hci0 noleadv')

# Create advertisement with flags, complete name and a health service UUID
os.system("""
sudo hcitool -i hci0 cmd 0x08 0x0008 1E 02 01 06 0B 09 4F 49 52 44 5F 53 65 6E 73 6F 72 05 03 18 0D 18 0F
""")

# Start advertising
os.system('sudo hciconfig hci0 leadv 0')

print("Advertisement started. BLE device should now be discoverable as 'OIRD_Sensor'.")
print("Running... Press CTRL+C to stop.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    os.system('sudo hciconfig hci0 noleadv')
    print("Stopped advertisement")
