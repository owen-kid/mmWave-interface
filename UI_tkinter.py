import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from board_interface import *
import asyncio
import threading

def run_asyncio_coroutine(coroutine):
    """Run an asyncio coroutine in a separate thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coroutine)
    loop.close()

async def send_config_async():
    await asyncio.to_thread(board_interface.send_config, board_interface.config, board_interface.config_file)

async def read_vitals_async():
    await asyncio.to_thread(board_interface.parse_output)

def on_send_config():
    threading.Thread(target=run_asyncio_coroutine, args=(send_config_async(),)).start()

def on_read_vitals():
    threading.Thread(target=run_asyncio_coroutine, args=(read_vitals_async(),)).start()

def on_update_vitals():
    threading.Thread(target=run_asyncio_coroutine, args=(update_vitals_async(),)).start()

async def update_vitals_async():
    await asyncio.to_thread(board_interface.parse_output)

def create_rounded_button(parent, text, command):
    # Create a canvas to hold the button
    canvas = tk.Canvas(parent, width=200, height=50, bg='#4C3575', highlightthickness=0)
    canvas.pack(pady=10)

    # Center the canvas by setting a fixed width and using anchor='center'
    canvas.update()  

    # Draw a rounded rectangle (simulated using an oval inside a rectangle)
    radius = 20  # Corner radius
    button_color = '#6C5B7B'
    text_color = 'white'

    # Rounded rectangle (4 arcs and 1 rectangle)
    create_rounded_rectangle(canvas, 5, 5, 200 - 5, 45, fill=button_color, outline='', radius=radius)

    # Button text
    canvas.create_text(200 // 2, 25, text=text, fill=text_color, font=("Helvetica", 12, "bold"))

    # Bind click event to canvas
    canvas.tag_bind('all', '<Button-1>', lambda event: command())

    return canvas

# Custom rounded rectangle function for the canvas
def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=10, **kwargs):
    points = [
        (x1 + radius, y1), (x2 - radius, y1),
        (x2, y1), (x2, y1 + radius),
        (x2, y2 - radius), (x2, y2),
        (x2 - radius, y2), (x1 + radius, y2),
        (x1, y2), (x1, y2 - radius),
        (x1, y1 + radius), (x1, y1)
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)



board_interface = BoardInterface()

class DashboardPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='#4C3575')
        common_width = 25
        common_height = 5

        patient_info = tk.Label(self, text="Patient Information\n24 | Guelph ON\nHalf Cuban\nSingle", 
                                bg='#7C6992', fg='white', font=("Helvetica", 10, "bold"), 
                                width=common_width, height=common_height, relief=tk.GROOVE)
        patient_info.place(x=200, y=40)

        risk_factor = tk.Label(self, text="Risk Factor\n69", 
                            bg='#7C6992', fg='white', font=("Helvetica", 10, "bold"), 
                            width=common_width, height=common_height, relief=tk.GROOVE)
        risk_factor.place(x=400, y=40)

        self.br_label = tk.Label(self, text="br\n69", 
                                bg='#7C6992', fg='white', font=("Helvetica", 10, "bold"), 
                                width=common_width, height=common_height, relief=tk.GROOVE)
        self.br_label.place(x=200, y=200)

        self.hr_label = tk.Label(self, text="hr\n9", 
                            bg='#7C6992', fg='white', font=("Helvetica", 10, "bold"), 
                            width=common_width, height=common_height, relief=tk.GROOVE)
        self.hr_label.place(x=400, y=200)


        figure2 = Figure(figsize=(4,3), dpi=100)
        ax2 = figure2.add_subplot(111)
        ax2.plot([6, 7, 8, 9, 10], [5, 15, 35, 30, 32], color='red', linewidth=3, marker='o', label='Heart Rate')
        ax2.plot([6, 7, 8, 9, 10], [10, 5, 20, 25, 45], color='deepskyblue', linewidth=3, marker='s', label='Breathing Rate')
        ax2.set_title("Heart & Breathing Rate", fontsize=14, fontweight='bold')
        ax2.legend()

        canvas2 = FigureCanvasTkAgg(figure2, self)
        canvas2.get_tk_widget().place(x=200, y=300)
        board_interface.setup_ports()
        asyncio.create_task(board_interface.parse_output_2(self.update_labels))


    def update_labels(self, hr, br):
        self.hr_label.config(text=f"hr\n{hr}")
        self.br_label.config(text=f"br\n{br}")

class ReportsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='#4C3575')
        label = tk.Label(self, text="Reports Page", fg='white', bg='#4C3575', font=("Helvetica", 24))
        label.pack(pady=50)

class SchedulePage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='#4C3575')
        label = tk.Label(self, text="Schedule Page", fg='white', bg='#4C3575', font=("Helvetica", 24))
        label.pack(pady=50)

class SettingsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='#4C3575')
        label = tk.Label(self, text="Settings Page", fg='white', bg='#4C3575', font=("Helvetica", 24))
        label.pack(pady=50)

        # connect
        # send config
        #try:
        board_interface.setup_ports()
        # except Exception as e:
        #     print("Error loading ports:", e)

        create_rounded_button(self, "Send Config", lambda: on_send_config())
        create_rounded_button(self, "Read Vitals", lambda: on_read_vitals())

class FluidAIDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fluid AI Dashboard")
        self.geometry("1200x700")
        self.configure(bg='#4C3575')

        self.sidebar = tk.Frame(self, bg='#2D1E56', width=100, height=700)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        try:
            logo_image = Image.open("fluidai-web.png").resize((150, 50))
            self.logo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(self.sidebar, image=self.logo, bg='#2D1E56')
            logo_label.pack(pady=20)
        except Exception as e:
            print("Error loading image:", e)

        self.pages = {}
        container = tk.Frame(self, bg='#4C3575')
        container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        for Page in (DashboardPage, ReportsPage, SchedulePage, SettingsPage):
            page = Page(container)
            self.pages[Page.__name__] = page
            page.place(x=0, y=0, relwidth=1, relheight=1)

        self.show_page("DashboardPage")

        create_rounded_button(self.sidebar, "Dashboard", lambda: self.show_page("DashboardPage"))
        create_rounded_button(self.sidebar, "Reports", lambda: self.show_page("ReportsPage"))
        create_rounded_button(self.sidebar, "Schedule", lambda: self.show_page("SchedulePage"))
        create_rounded_button(self.sidebar, "Settings", lambda: self.show_page("SettingsPage"))

    def show_page(self, page_name):
        page = self.pages[page_name]
        page.tkraise()

if __name__ == "__main__":
    app = FluidAIDashboard()
    app.mainloop()
