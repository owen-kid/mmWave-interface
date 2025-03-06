import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import asyncio
import threading
from board_interface import BoardInterface

class VitalsMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Vitals Monitor")
        self.geometry("800x600")
        self.configure(bg='#4C3575')

        # Initialize last known values
        self.last_hr = None
        self.last_br = None

        # Create main container
        self.container = tk.Frame(self, bg='#4C3575')
        self.container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create vitals display
        self.create_vitals_display()
        
        # Initialize board interface
        self.board_interface = BoardInterface()
        print("BoardInterface initialized")
        
        # Start asyncio event loop in a separate thread
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.run_async_loop, daemon=True)
        self.thread.start()
        print("Async loop started in separate thread")

    def create_vitals_display(self):
        # Heart Rate Display
        self.hr_frame = tk.Frame(self.container, bg='#7C6992', relief=tk.RAISED, bd=2)
        self.hr_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        # Fixed width for the frames
        self.hr_frame.pack_propagate(False)  # Prevent frame from resizing
        self.hr_frame.configure(width=300, height=200)  # Set fixed size
        
        tk.Label(self.hr_frame, text="Heart Rate", font=("Helvetica", 16, "bold"), 
                bg='#7C6992', fg='white').pack(pady=10)
        
        # Create a fixed-width frame for the value
        hr_value_frame = tk.Frame(self.hr_frame, bg='#7C6992', width=200, height=80)
        hr_value_frame.pack(pady=20)
        hr_value_frame.pack_propagate(False)  # Prevent frame from resizing
        
        self.hr_value = tk.Label(hr_value_frame, text="--", font=("Helvetica", 48),
                                bg='#7C6992', fg='white', width=4, anchor='center')
        self.hr_value.pack(expand=True)
        
        tk.Label(self.hr_frame, text="BPM", font=("Helvetica", 12),
                bg='#7C6992', fg='white').pack()

        # Breathing Rate Display
        self.br_frame = tk.Frame(self.container, bg='#7C6992', relief=tk.RAISED, bd=2)
        self.br_frame.pack(side=tk.RIGHT, padx=10, fill=tk.BOTH, expand=True)
        
        # Fixed width for the frames
        self.br_frame.pack_propagate(False)  # Prevent frame from resizing
        self.br_frame.configure(width=300, height=200)  # Set fixed size
        
        tk.Label(self.br_frame, text="Breathing Rate", font=("Helvetica", 16, "bold"),
                bg='#7C6992', fg='white').pack(pady=10)
        
        # Create a fixed-width frame for the value
        br_value_frame = tk.Frame(self.br_frame, bg='#7C6992', width=200, height=80)
        br_value_frame.pack(pady=20)
        br_value_frame.pack_propagate(False)  # Prevent frame from resizing
        
        self.br_value = tk.Label(br_value_frame, text="--", font=("Helvetica", 48),
                                bg='#7C6992', fg='white', width=4, anchor='center')
        self.br_value.pack(expand=True)
        
        tk.Label(self.br_frame, text="BPM", font=("Helvetica", 12),
                bg='#7C6992', fg='white').pack()

        # Add status label with fixed width
        status_frame = tk.Frame(self.container, bg='#4C3575', width=600)
        status_frame.pack(side=tk.BOTTOM, pady=10)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Waiting for data...",
                                   bg='#4C3575', fg='white', width=50)
        self.status_label.pack()

    def update_vitals(self, hr, br):
        """Update the GUI with new vital signs values"""
        # Round the values if they exist
        if hr is not None:
            self.last_hr = round(float(hr))
        if br is not None:
            self.last_br = round(float(br))

        # Display the last known values (or '--' if none available)
        hr_display = f"{self.last_hr:3d}" if self.last_hr is not None else '--'
        br_display = f"{self.last_br:3d}" if self.last_br is not None else '--'

        self.hr_value.config(text=hr_display)
        self.br_value.config(text=br_display)

        # Update status with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        if hr is not None or br is not None:
            self.status_label.config(text=f"Last update: {timestamp}")
        else:
            self.status_label.config(text=f"No new data - Showing last known values ({timestamp})")

    async def start_monitoring(self):
        """Start monitoring vital signs"""
        try:
            print("Setting up board interface ports")
            self.board_interface.setup_ports()
            print("Starting parse_output_2")
            
            def callback(hr, br):
                print(f"Callback received - HR: {hr}, BR: {br}")
                self.after(0, self.update_vitals, hr, br)
            
            await self.board_interface.parse_output_2(callback)
        except Exception as e:
            print(f"Error in monitoring: {e}")
            self.status_label.config(text=f"Error: {str(e)}")

    def run_async_loop(self):
        """Run the asyncio event loop in a separate thread"""
        asyncio.set_event_loop(self.loop)
        try:
            print("Starting async monitoring")
            self.loop.run_until_complete(self.start_monitoring())
        except Exception as e:
            print(f"Error in async loop: {e}")

def main():
    app = VitalsMonitor()
    try:
        app.mainloop()
    except Exception as e:
        print(f"Error in main loop: {e}")

if __name__ == "__main__":
    main()