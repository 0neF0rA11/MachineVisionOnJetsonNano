import cv2
import tkinter as tk
from tkinter import ttk

import pandas as pd
import torch
from PIL import ImageTk, Image
from ultralytics import YOLO


class NeuralNetPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.cap = None
        self.video_paused = False
        self.update_flag = False
        self.controller = controller
        self.image_shape = [int(1200 * self.controller.scale_factor),
                            int(840 * self.controller.scale_factor)]
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.model = YOLO('yolov8s.pt').to(device)
        self.classes = self.model.names
        self.selected_class = None
        self.class_labels = {1: 'person', 2: 'bicycle', 3: 'car', 4: 'motorcycle', 5: 'airplane', 6: 'bs', 7: 'train',
                             8: 'trck', 9: 'boat', 10: 'traffic light', 11: 'fire hydrant', 12: 'stop sign',
                             13: 'parking meter', 14: 'bench', 15: 'bird', 16: 'cat', 17: 'dog', 18: 'horse',
                             19: 'sheep', 20: 'cow', 21: 'elephant', 22: 'bear', 23: 'zebra', 24: 'giraffe',
                             25: 'backpack', 26: 'mbrella', 27: 'handbag', 28: 'tie', 29: 'sitcase', 30: 'frisbee',
                             31: 'skis', 32: 'snowboard', 33: 'sports ball', 34: 'kite', 35: 'baseball bat',
                             36: 'baseball glove', 37: 'skateboard', 38: 'srfboard', 39: 'tennis racket', 40: 'bottle',
                             41: 'wine glass', 42: 'cp', 43: 'fork', 44: 'knife', 45: 'spoon', 46: 'bowl', 47: 'banana',
                             48: 'apple', 49: 'sandwich', 50: 'orange', 51: 'broccoli', 52: 'carrot', 53: 'hot dog',
                             54: 'pizza', 55: 'dont', 56: 'cake', 57: 'chair', 58: 'coch', 59: 'potted plant',
                             60: 'bed', 61: 'dining table', 62: 'toilet', 63: 'tv', 64: 'laptop', 65: 'mose',
                             66: 'remote', 67: 'keyboard', 68: 'cell phone', 69: 'microwave', 70: 'oven', 71: 'toaster',
                             72: 'sink', 73: 'refrigerator', 74: 'book', 75: 'clock', 76: 'vase', 77: 'scissors',
                             78: 'teddy bear', 79: 'hair drier', 80: 'toothbrsh'
                             }

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

        self.create_neuro_widgets(settings_frame)

    def create_neuro_widgets(self, frame):
        list_frame = tk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Создаем Listbox
        self.class_listbox = tk.Listbox(
            list_frame,
            selectmode=tk.SINGLE,
            height=10,
            bg='#001f4b',  # Синий фон
            fg='white',  # Белый текст
            width=10
        )
        self.class_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Заполняем Listbox названиями классов
        for key, label in self.class_labels.items():
            self.class_listbox.insert(tk.END, label)

        # Добавляем Scrollbar
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Привязываем Scrollbar к Listbox
        self.class_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.class_listbox.yview)

        # Устанавливаем масштабируемый шрифт
        self.class_listbox.config(font=("TkDefaultFont", int(25 * self.controller.scale_factor)))

        # Обработчик выбора элемента
        self.class_listbox.bind('<<ListboxSelect>>', self.on_class_select)

    def on_class_select(self, event):
        selected_index = self.class_listbox.curselection()
        if selected_index:
            class_name = self.class_listbox.get(selected_index)
            if self.selected_class == class_name:
                self.class_listbox.selection_clear(0, tk.END)
                self.selected_class = None
            else:
                self.selected_class = class_name

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

                results = self.model.predict(frame, stream_buffer=True, verbose=False)

                a = results[0].boxes.data
                px = pd.DataFrame(a).astype("float")

                for index, row in px.iterrows():
                    confidence = row[4]
                    x1 = int(row[0])
                    y1 = int(row[1])
                    x2 = int(row[2])
                    y2 = int(row[3])
                    d = int(row[5])
                    c = self.classes[d]
                    if self.selected_class is None or c == self.selected_class:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
                        cv2.putText(frame, f'{c} {confidence:.2f}', (x1, y1 - 25), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.5, (255, 255, 255), 2)

                im = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=im)

                self.cam_label.imgtk = imgtk
                self.cam_label.config(image=imgtk)

        if self.update_flag:
            self.cam_label.after(10, self.update_stream)