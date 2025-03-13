import os
import time

# Basic advertisement just to test if devices can see the Pi
os.system('sudo hciconfig hci0 up')
os.system('sudo hciconfig hci0 piscan')
os.system('sudo hciconfig hci0 name "OIRD_Test"')
os.system('sudo hciconfig hci0 leadv 3')

print("Started basic advertisement. Press Ctrl+C to stop.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    os.system('sudo hciconfig hci0 noleadv')
    print("Stopped advertisement")
