import cv2
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import ImageTk, Image
from server import Server
from ArUcoPage import ArUcoPage
from NeuralNetPage import NeuralNetPage
from ManipulatorPage import ManipulatorPage
from CalibrationPage import CalibrationPage


def get_available_cameras():
    available_cameras = []
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append(f"Камера {i+1}")
            cap.release()
        else:
            break
    return available_cameras if available_cameras else ["Нет доступной камеры"]


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.current_frame = None
        self.cap = None

        self.title("Vision")
        self.attributes('-fullscreen', True)
        self.geometry("1920x1080")
        self.minsize(800, 600)
        self.ser = Server()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        self.scale_factor = min(screen_width, screen_height) / 1080

        self.create_top_bar()
        style = ttk.Style()
        style.configure("TFrame", background="#001f4b")

        container = ttk.Frame(self, style="TFrame", relief="flat", borderwidth=0)
        container.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}

        for F in (HomePage, ManipulatorPage, CalibrationPage, NeuralNetPage, ArUcoPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("HomePage")

    def create_top_bar(self):
        top_bar = tk.Frame(self, bg='#00326e')
        top_bar.grid(row=0, column=0, sticky="ew")

        top_bar.grid_propagate(False)
        top_bar.config(height=int(80 * self.scale_factor))

        close_icon = Image.open("images_data/close_icon.png")
        close_icon_resized = ImageTk.PhotoImage(close_icon.resize((int(50 * self.scale_factor),
                                                                   int(50 * self.scale_factor))))

        home_icon = Image.open("images_data/home_icon.png")
        home_icon_resized = ImageTk.PhotoImage(home_icon.resize((int(50 * self.scale_factor),
                                                                 int(50 * self.scale_factor))))

        settings_icon = Image.open("images_data/settings_icon.png")
        settings_icon_resized = ImageTk.PhotoImage(settings_icon.resize((int(50 * self.scale_factor),
                                                                         int(50 * self.scale_factor))))

        disconnect_icon = Image.open("images_data/disconnect_icon.png")
        self.disconnect_icon_resized = ImageTk.PhotoImage(disconnect_icon.resize((int(50 * self.scale_factor),
                                                                                  int(50 * self.scale_factor))))

        connect_icon = Image.open("images_data/connect_icon.png")
        self.connect_icon_resized = ImageTk.PhotoImage(connect_icon.resize((int(50 * self.scale_factor),
                                                                            int(50 * self.scale_factor))))

        self.connection_button = tk.Button(top_bar, image=self.disconnect_icon_resized, bg='#00326e', relief="flat",
                                           command=self.toggle_connection, activebackground='#00326e',
                                           highlightthickness=0)
        self.connection_button.image = self.disconnect_icon_resized
        self.connection_button.pack(side="left", padx=int(30 * self.scale_factor), pady=int(10 * self.scale_factor))

        camera_list = get_available_cameras()
        self.camera_combobox = ttk.Combobox(top_bar, values=camera_list, state="readonly",
                                            width=19)
        self.camera_combobox.set(camera_list[0] if camera_list else "Нет доступной камеры")
        self.camera_combobox.configure(font=("Arial", int(20 * self.scale_factor)))
        self.camera_combobox.pack(side="left", padx=int(30 * self.scale_factor), pady=int(10 * self.scale_factor))

        close_button = tk.Button(top_bar, image=close_icon_resized, bg='#00326e', relief="flat", command=self.quit,
                                 activebackground='#001f4b', highlightthickness=0)
        close_button.image = close_icon_resized
        close_button.pack(side="right", padx=int(10 * self.scale_factor), pady=int(10 * self.scale_factor))

        home_button = tk.Button(top_bar, image=home_icon_resized, bg='#00326e', relief="flat",
                                command=lambda: self.show_frame("HomePage"),
                                activebackground='#001f4b', highlightthickness=0)
        home_button.image = home_icon_resized
        home_button.pack(side="right", padx=int(10 * self.scale_factor), pady=int(10 * self.scale_factor))

        settings_button = tk.Button(top_bar, image=settings_icon_resized, bg='#00326e', relief="flat",
                                    command=lambda: self.show_frame("CalibrationPage"),
                                    activebackground='#001f4b', highlightthickness=0)
        settings_button.image = settings_icon_resized
        settings_button.pack(side="right", padx=int(10 * self.scale_factor), pady=int(10 * self.scale_factor))

    def show_frame(self, page_name):
        if self.frames[page_name] == self.current_frame:
            return
        if self.cap is not None:
            self.cap.release()
            self.cap = None

        if page_name == "HomePage":
            if self.current_frame is not None:
                self.current_frame.update_flag = False
            self.current_frame = self.frames[page_name]
            self.current_frame.tkraise()

        if page_name != "HomePage":
            if self.camera_combobox.get() == "Нет доступной камеры":
                messagebox.showerror("Ошибка", "Нет доступной камеры. Запуск невозможен!")
            else:
                self.cap = cv2.VideoCapture(int(self.camera_combobox.get().split()[1]) - 1)
                self.current_frame = self.frames[page_name]
                self.current_frame.cap = self.cap
                self.current_frame.update_flag = True
                self.current_frame.video_paused = False
                self.current_frame.update_stream()
                self.current_frame.tkraise()

    def toggle_connection(self):
        if self.connection_button.image == self.disconnect_icon_resized:
            self.ser.connect_port(self.frames['ManipulatorPage'])
            if self.ser.ser and self.ser.ser.is_open:
                self.connection_button.config(image=self.connect_icon_resized)
                self.connection_button.image = self.connect_icon_resized
        else:
            if self.ser.ser and self.ser.ser.is_open:
                self.ser.close_port()
                self.connection_button.config(image=self.disconnect_icon_resized)
                self.connection_button.image = self.disconnect_icon_resized


class HomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style()
        style.configure("WhiteText.TLabel", foreground="white", background="#001f4b", font=("Arial", 18))

        label = ttk.Label(self, text="Приложения", style="WhiteText.TLabel")
        label.pack(pady=int(30 * self.controller.scale_factor))

        button_frame = tk.Frame(self, bg="#001f4b")
        button_frame.pack(expand=True)

        manipulator_image = Image.open("images_data/manipulator_icon.png")
        manipulator_icon = ImageTk.PhotoImage(manipulator_image.resize((int(400 * self.controller.scale_factor), int(500 * self.controller.scale_factor))))

        neural_net_image = Image.open("images_data/neural_net_icon.png")
        neural_net_icon = ImageTk.PhotoImage(neural_net_image.resize((int(400 * self.controller.scale_factor), int(500 * self.controller.scale_factor))))

        aruco_image = Image.open("images_data/aruco_icon.png")
        aruco_icon = ImageTk.PhotoImage(aruco_image.resize((int(400 * self.controller.scale_factor), int(500 * self.controller.scale_factor))))

        btn_manipulator = tk.Button(button_frame, text="Манипулятор\n", image=manipulator_icon, compound="top",
                                    command=lambda: self.controller.show_frame("ManipulatorPage"),
                                    bg="#00326e", fg="white", relief="raised",
                                    font=("Arial", int(30 * self.controller.scale_factor)))
        btn_manipulator.image = manipulator_icon
        btn_manipulator.grid(row=0, column=0, padx=int(50 * self.controller.scale_factor), pady=int(20 * self.controller.scale_factor))

        btn_neural_net = tk.Button(button_frame, text="Нейронная\nсеть", image=neural_net_icon, compound="top",
                                   command=lambda: self.controller.show_frame("NeuralNetPage"),
                                   bg="#00326e", fg="white", relief="raised",
                                   font=("Arial", int(30 * self.controller.scale_factor)))
        btn_neural_net.image = neural_net_icon
        btn_neural_net.grid(row=0, column=1, padx=int(50 * self.controller.scale_factor), pady=int(20 * self.controller.scale_factor))

        btn_aruco = tk.Button(button_frame, text="Распознание\nArUco", image=aruco_icon, compound="top",
                              command=lambda: self.controller.show_frame("ArUcoPage"),
                              bg="#00326e", fg="white", relief="raised",
                              font=("Arial", int(30 * self.controller.scale_factor)))
        btn_aruco.image = aruco_icon
        btn_aruco.grid(row=0, column=2, padx=int(50 * self.controller.scale_factor), pady=int(20 * self.controller.scale_factor))

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
