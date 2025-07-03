import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from typing import Optional


class IMGEditor:
    """Главный класс приложения для обработки изображений"""
    def __init__(self, master):
        """Инициализация приложения
        Args: master (tk.Tk): Главное окно Tkinter"""
        self.master = master
        self.master.title("IMGEditor")
        self.master.geometry("1280x720")

        # Инициализация всех атрибутов
        self.image: Optional[np.ndarray] = None
        self.display_image: Optional[np.ndarray] = None
        self.camera: Optional[cv2.VideoCapture] = None
        self.tk_image: Optional[ImageTk.PhotoImage] = None

        # Виджеты
        self.load_frame: Optional[tk.Frame] = None
        self.image_label: Optional[tk.Label] = None
        self.load_frame: Optional[tk.Frame] = None
        self.channel_var: Optional[tk.StringVar] = None

        # Интерфейс (создание)
        self.create_widgets()

    def create_widgets(self):
        """Функция, которая создает графический интерфейс приложения"""
        # Кнопки загрузки изображения
        self.load_frame = tk.Frame(self.master)
        self.load_frame.pack(pady=10)

        tk.Button(self.load_frame, text="Загрузить изображение",
                  command=self.load_image).pack(side=tk.LEFT, padx=5)
        tk.Button(self.load_frame, text="Сделать снимок",
                  command=self.capture_image).pack(side=tk.LEFT, padx=5)

        # Операции с изображением
        tk.Button(self.load_frame, text="Показать изображение",
                  command=self.show_image).pack(side=tk.LEFT, padx=5)

        tk.Button(self.load_frame, text="Показать канал",
                  command=self.show_channel).pack(side=tk.LEFT, padx=5)
        self.channel_var = tk.StringVar(value="red")
        tk.Label(self.load_frame, text="Канал:").pack(side=tk.LEFT, padx=5)
        ttk.Combobox(self.load_frame, textvariable=self.channel_var,
                     values=["red", "green", "blue"],
                     width=7).pack(side=tk.LEFT, padx=5)

        tk.Button(self.load_frame, text="Оттенки серого",
                  command=self.get_grey).pack(side=tk.LEFT, padx=5)
        tk.Button(self.load_frame, text="Вращение",
                  command=self.rotate_image).pack(side=tk.LEFT, padx=5)
        tk.Button(self.load_frame, text="Нарисовать прямоугольник",
                  command=self.draw_rectangle).pack(side=tk.LEFT, padx=5)

        # Поле для отображения изображения
        self.image_label = tk.Label(self.master)
        self.image_label.pack(pady=10, fill=tk.BOTH, expand=True)

    def load_image(self):
        """Функция, которая загружает изображение через диалоговое окно"""
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if path:
            try:
                self.image = cv2.imread(path)
                if self.image is None:
                    raise ValueError("Ошибка загрузки изображения")
                self.show_image()
            except Exception as e:
                messagebox.showerror("Ошибка",
                                     f"Не удалось загрузить изображение: {str(e)}")

    def capture_image(self):
        """Функция, которая захватывает изображение с камеры"""
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                messagebox.showerror("Ошибка",
                                     "Не удалось подключить камеру")
                self.camera = None
                return

        ret, frame = self.camera.read()
        if ret:
            self.image = frame
            self.show_image()
        else:
            messagebox.showerror("Ошибка",
                                 "Не удалось сделать снимок")

    def show_image(self):
        """Функция, которая отображает исходное изображение"""
        if self.image is None:
            messagebox.showwarning("Предупреждение",
                                   "Сначала загрузите изображение")
            return
        self.display_image = self.image.copy()
        self.update_display()

    def show_channel(self):
        """Функция, которая отображает выбранный цветовой канал"""
        if self.image is None:
            messagebox.showwarning("Предупреждение",
                                   "Сначала загрузите изображение")
            return

        channel = self.channel_var.get()
        idx = {"red": 2, "green": 1, "blue": 0}.get(channel, 2)

        # Создаем пустую матрицу и заполняем выбранный канал
        zeros = np.zeros_like(self.image[:, :, 0])
        channels = [zeros, zeros, zeros]
        channels[idx] = self.image[:, :, idx]

        self.display_image = cv2.merge(channels)
        self.update_display()

    def get_grey(self):
        """Преобразует текущее изображение в оттенки серого и отображает его"""
        if self.image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return
        grey = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        # Для отображения в Tkinter нужно вернуть 3 канала
        self.display_image = cv2.cvtColor(grey, cv2.COLOR_GRAY2BGR)
        self.update_display()

    def rotate_image(self):
        """Вращает изображение на угол, введённый пользователем"""
        if self.image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return

        dialog = tk.Toplevel(self.master)
        dialog.title("Вращение изображения")
        dialog.geometry("200x100")

        tk.Label(dialog, text="Угол (градусы):").pack(pady=5)
        angle_entry = tk.Entry(dialog)
        angle_entry.pack(pady=5)

        def apply_rotation():
            try:
                angle = -float(angle_entry.get())
                (h, w) = self.image.shape[:2]
                center = (w // 2, h // 2)
                m = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(self.image, m, (w, h))
                self.display_image = rotated
                self.update_display()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Некорректные данные: {str(e)}")

        tk.Button(dialog, text="Применить", command=apply_rotation).pack(pady=5)

    def draw_rectangle(self):
        """Рисует синий залитый прямоугольник по координатам, введённым пользователем"""
        if self.image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return

        dialog = tk.Toplevel(self.master)
        dialog.title("Рисование прямоугольника")
        dialog.geometry("200x150")

        tk.Label(dialog, text="X1:").grid(row=0, column=0, padx=5, pady=3)
        x1_entry = tk.Entry(dialog)
        x1_entry.grid(row=0, column=1, padx=5, pady=3)

        tk.Label(dialog, text="Y1:").grid(row=1, column=0, padx=5, pady=3)
        y1_entry = tk.Entry(dialog)
        y1_entry.grid(row=1, column=1, padx=5, pady=3)

        tk.Label(dialog, text="X2:").grid(row=2, column=0, padx=5, pady=3)
        x2_entry = tk.Entry(dialog)
        x2_entry.grid(row=2, column=1, padx=5, pady=3)

        tk.Label(dialog, text="Y2:").grid(row=3, column=0, padx=5, pady=3)
        y2_entry = tk.Entry(dialog)
        y2_entry.grid(row=3, column=1, padx=5, pady=3)

        def apply_rectangle():
            try:
                x1 = int(x1_entry.get())
                y1 = int(y1_entry.get())
                x2 = int(x2_entry.get())
                y2 = int(y2_entry.get())

                height, width = self.image.shape[:2]

                # Проверяем положительность и границы
                if not (0 <= x1 < width and 0 <= x2 < width):
                    raise ValueError(f"Координаты X должны быть в диапазоне [0, {width - 1}]")
                if not (0 <= y1 < height and 0 <= y2 < height):
                    raise ValueError(f"Координаты Y должны быть в диапазоне [0, {height - 1}]")

                # При необходимости можно поправить порядок координат
                pt1 = (min(x1, x2), min(y1, y2))
                pt2 = (max(x1, x2), max(y1, y2))

                img_copy = self.image.copy()
                color = (255, 0, 0)  # синий в BGR
                thickness = -1  # заливка
                cv2.rectangle(img_copy, pt1, pt2, color, thickness)
                self.display_image = img_copy
                self.update_display()
                dialog.destroy()
            except ValueError as ve:
                messagebox.showerror("Ошибка ввода", str(ve))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Некорректные данные: {str(e)}")

        tk.Button(dialog, text="Применить", command=apply_rectangle).grid(row=4, columnspan=2, pady=10)

    def update_display(self):
        """Функция, которая обновляет отображаемое изображение в интерфейсе"""
        if self.display_image is None:
            return

        # Конвертация для Tkinter
        img_rgb = cv2.cvtColor(self.display_image, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)

        # Явное создание объекта PhotoImage
        self.tk_image = ImageTk.PhotoImage(image=img_pil)

        self.image_label.configure(image=self.tk_image)  # type: ignore
        self.image_label.image = self.tk_image

    def __del__(self):
        """Функция, которая освобождает ресурсы при
        завершении работы приложения"""
        if self.camera is not None:
            self.camera.release()


if __name__ == "__main__":
    root = tk.Tk()
    app = IMGEditor(root)
    root.mainloop()
