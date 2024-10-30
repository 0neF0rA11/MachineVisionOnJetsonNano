import math

import cv2
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from PIL import ImageTk, Image


def is_convertible_to_int(element):
    try:
        int(element)
        return True
    except (ValueError, TypeError):
        return False


class CalibrationPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.cap = None
        self.video_paused = False
        self.update_flag = False
        self.rotate_flag = True
        self.controller = controller
        self.font = cv2.FONT_HERSHEY_SIMPLEX

        self.image_shape = [int(1200 * self.controller.scale_factor),
                            int(840 * self.controller.scale_factor)]
        self.center_x = self.image_shape[0] // 2
        self.center_y = self.image_shape[1] // 2

        self.min_area = 250
        self.objects_coord = []
        self.kernelOpen = np.ones((5, 5))
        self.kernelClose = np.ones((20, 20))
        self.lowerBound = None
        self.upperBound = None

        self.color_dict = {
            'blue': (105, 219, 129),
            'orange': (11, 252, 176),
            'yellow': (19, 255, 169),
            'green': (77, 225, 77)
        }

        self.exposure = 0
        self.white_balance = 0

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
        rotate_icon = ImageTk.PhotoImage(
            Image.open("images_data/rotate_icon.png").resize((int(50 * self.controller.scale_factor),
                                                              int(50 * self.controller.scale_factor))))
        save_icon = ImageTk.PhotoImage(
            Image.open("images_data/save_icon.png").resize((int(50 * self.controller.scale_factor),
                                                            int(50 * self.controller.scale_factor))))

        button_frame = tk.Frame(settings_frame, bg='#001f4b')
        button_frame.pack(pady=10)

        self.rotate_button = tk.Button(button_frame, image=rotate_icon, command=self.rotate_action,
                                       borderwidth=0)
        self.rotate_button.image = rotate_icon
        self.rotate_button.pack(side=tk.LEFT, padx=5)

        self.pause_button = tk.Button(button_frame, image=pause_icon, command=self.pause_action,
                                      borderwidth=0)
        self.pause_button.image = pause_icon
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(button_frame, image=save_icon, command=self.save_config,
                                     borderwidth=0)
        self.save_button.image = save_icon
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(button_frame, image=stop_icon,
                                     command=lambda: self.controller.show_frame("HomePage"),
                                     borderwidth=0)
        self.stop_button.image = stop_icon
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.cam_label = tk.Label(camera_frame, bg='#001f4b')
        self.cam_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.cam_label.bind("<Button-1>", self.pick_color)

        self.create_management_widgets(settings_frame)

    def create_management_widgets(self, frame):
        config_frame = ttk.Frame(frame, width=int(450 * self.controller.scale_factor),
                                 height=int(600 * self.controller.scale_factor))
        config_frame.place(x=50, y=150)
        self.fields = {"w": self.create_field(config_frame, "Длина объекта, мм:", 40, row=4),
                       "l": self.create_field(config_frame, "Ширина объекта, мм", 40, row=5),
                       "h": self.create_field(config_frame, "Высота объекта, мм:", 40, row=6),
                       "field_x_size": self.create_field(config_frame, "Длина поля по оси X, мм:", 620, row=7),
                       "field_y_size": self.create_field(config_frame, "Длина поля по оси Y, мм:", 620, row=8)}

    def create_field(self, frame, text, default, row):
        label = ttk.Label(frame, text=f"{text}",
                          font=("Arial", int(20 * self.controller.scale_factor)),
                          background="#001f4b",
                          foreground="white")
        label.place(x=10, y=15 * self.controller.scale_factor + row * 50, anchor='w')

        frame.update_idletasks()
        frame_width = frame.winfo_width()

        entry = ttk.Entry(frame, width=15,)
        entry.configure(font=("Arial", int(20 * self.controller.scale_factor)))
        entry.insert(0, f'{default}')

        entry_width = int(100 * self.controller.scale_factor)
        entry_x = frame_width - entry_width - 10
        entry.place(x=entry_x, y=row * 50, width=entry_width)

        return entry

    def save_config(self):
        if len(self.objects_coord) == 0:
            messagebox.showerror("Ошибка", "Нет выделенных объектов, нельзя записать настройки")
            return

        closest_object = None
        min_distance = float('inf')
        for obj in self.objects_coord:
            (x, y), h, w = obj
            distance = math.sqrt((x - self.image_shape[0] // 2) ** 2 + (y - self.image_shape[1] // 2) ** 2)
            if distance < min_distance:
                min_distance = distance
                closest_object = obj

        coord, h, w = closest_object
        config_dict = {
            'scale_x': w / int(self.fields['l'].get()),
            'scale_y': h / int(self.fields['w'].get()),
            'h': self.fields['h'].get(),
            'field_x_size': self.fields['field_x_size'].get(),
            'field_y_size': self.fields['field_y_size'].get(),
        }

        with open("config.txt", "w") as file:
            for key, value in config_dict.items():
                file.write(f"{key} {value}\n")

        self.controller.frames["ManipulatorPage"].set_camera_config()

    def pick_color(self, event, color=None):
        if self.controller.current_frame == self and self.cap is not None and not self.video_paused:
            x, y = 0, 0
            if event is not None:
                x, y = event.x, event.y
            image_width, image_height = self.image_shape

            if 0 <= x < image_width and 0 <= y < image_height:
                frame_x = int((x / image_width) * self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                frame_y = int((y / image_height) * self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                _, frame = self.cap.read()
                if frame is not None:

                    if self.rotate_flag:
                        frame = cv2.rotate(frame, cv2.ROTATE_180)

                    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                    if event is not None:
                        hsv_value = hsv_frame[frame_y, frame_x]
                    else:
                        hsv_value = self.color_dict[color]

                    h_val = int(hsv_value[0])
                    s_val = int(hsv_value[1])
                    v_val = int(hsv_value[2])

                    tol_h = 2
                    tol_s = 50
                    tol_v = 50

                    self.lowerBound = np.array([
                        max(h_val - tol_h, 0),
                        max(s_val - tol_s, 0),
                        max(v_val - tol_v, 0)
                    ], dtype=np.uint8)
                    self.upperBound = np.array([
                        min(h_val + tol_h, 179),
                        min(s_val + tol_s, 255),
                        min(v_val + tol_v, 255)
                    ], dtype=np.uint8)

    def pause_action(self):
        self.video_paused = not self.video_paused

    def rotate_action(self):
        self.rotate_flag = not self.rotate_flag

    def update_stream(self):
        if not self.video_paused:
            ret, frame = self.cap.read()
            if ret:
                conts = []
                frame = cv2.resize(frame, self.image_shape)
                if self.lowerBound is not None and self.upperBound is not None:
                    imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    mask = cv2.inRange(imgHSV, self.lowerBound, self.upperBound)
                    maskOpen = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernelOpen)
                    maskClose = cv2.morphologyEx(maskOpen, cv2.MORPH_CLOSE, self.kernelClose)
                    maskFinal = maskClose
                    conts, _ = cv2.findContours(maskFinal.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.objects_coord = []
                for i, contour in enumerate(conts):
                    x, y, w, h = cv2.boundingRect(contour)
                    if w * h > self.min_area:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        self.objects_coord.append([(x + w // 2, y + h // 2), w, h])

                if self.rotate_flag:
                    frame = cv2.rotate(frame, cv2.ROTATE_180)
                line_length = int(40 * self.controller.scale_factor)
                cv2.line(frame,
                         (self.center_x - line_length // 2, self.center_y),
                         (self.center_x + line_length // 2, self.center_y),
                         (255, 0, 0), 1)
                cv2.line(frame, (self.center_x, self.center_y - line_length // 2),
                         (self.center_x, self.center_y + line_length // 2),
                         (255, 0, 0), 1)

                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.cam_label.imgtk = imgtk
                self.cam_label.config(image=imgtk)

        if self.update_flag:
            self.cam_label.after(10, self.update_stream)
