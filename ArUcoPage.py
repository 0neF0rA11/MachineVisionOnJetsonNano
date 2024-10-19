import cv2
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image


class ArUcoPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.cap = None
        self.video_paused = False
        self.update_flag = False
        self.controller = controller
        self.image_shape = [int(1200 * self.controller.scale_factor),
                            int(840 * self.controller.scale_factor)]
        self.create_widgets()

    def create_widgets(self):
        paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        camera_frame = tk.Frame(paned_window)
        paned_window.add(camera_frame, weight=7)

        settings_frame = ttk.Frame(paned_window)
        paned_window.add(settings_frame, weight=2)

        label_settings = ttk.Label(settings_frame, text="Настройки", background="#001f4b", foreground='white',
                                   font=("Arial", int(30 * self.controller.scale_factor)))
        label_settings.pack(pady=10)

        stop_icon = ImageTk.PhotoImage(
            Image.open("images_data/stop_icon.png").resize((int(50 * self.controller.scale_factor),
                                                            int(50 * self.controller.scale_factor))))
        pause_icon = ImageTk.PhotoImage(
            Image.open("images_data/pause_icon.png").resize((int(50 * self.controller.scale_factor),
                                                             int(50 * self.controller.scale_factor))))

        button_frame = tk.Frame(settings_frame, bg='#001f4b')
        button_frame.pack(pady=10)

        self.pause_button = tk.Button(button_frame, image=pause_icon, command=self.pause_action,
                                      borderwidth=0)
        self.pause_button.image = pause_icon
        self.pause_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(button_frame, image=stop_icon,
                                     command=lambda: self.controller.show_frame("HomePage"),
                                     borderwidth=0)
        self.stop_button.image = stop_icon
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.cam_label = tk.Label(camera_frame, bg='#001f4b')
        self.cam_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.cam_label = ttk.Label(camera_frame)
        self.cam_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def pause_action(self):
        if self.video_paused:
            self.video_paused = False
        else:
            self.video_paused = True

    def update_stream(self):
        if not self.video_paused:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, self.image_shape)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
                aruco_params = cv2.aruco.DetectorParameters()
                corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=aruco_params)
                if len(corners) > 0:
                    frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)

                self.cam_label.imgtk = imgtk
                self.cam_label.config(image=imgtk)

        if self.update_flag:
            self.cam_label.after(10, self.update_stream)
