import os
import time

# Reset Bluetooth adapter
os.system('sudo hciconfig hci0 down')
os.system('sudo hciconfig hci0 up')

# Set device name to be discoverable by Web Bluetooth
os.system('sudo hciconfig hci0 name "OIRD_Sensor"')

# Make it discoverable
os.system('sudo hciconfig hci0 piscan')

# Stop any ongoing advertisements
os.system('sudo hciconfig hci0 noleadv')

# Configure as non-connectable to avoid pairing issues
# Just focus on being discoverable first
os.system('sudo hcitool -i hci0 cmd 0x08 0x0008 0E 0D 09 4F 49 52 44 5F 53 65 6E 73 6F 72')

# Start advertising - using mode 3 for non-connectable
os.system('sudo hciconfig hci0 leadv 3')

print("Running simple advertisement as 'OIRD_Sensor'")
print("Press Ctrl+C to stop")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    os.system('sudo hciconfig hci0 noleadv')
    print("Advertisement stopped")
