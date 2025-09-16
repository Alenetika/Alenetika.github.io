import tkinter as tk
from tkinter import filedialog, messagebox
import os
import time
import cv2
import numpy as np
import threading
from PIL import Image, ImageFilter, ImageEnhance, ImageTk

class ASCIIViewer:
    def __init__(self, media_path=None):
        self.root = tk.Tk()
        self.root.title("ASCII Art Viewer")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')

        # Основной текстовый виджет
        self.text_widget = tk.Text(
            self.root,
            font=('Courier New', 6),
            bg='black',
            fg='green',
            wrap=tk.NONE,
            insertbackground='green',
            borderwidth=0,
            highlightthickness=0
        )

        # Прокрутка
        scroll_y = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.text_widget.yview)
        scroll_x = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.text_widget.xview)

        self.text_widget.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        # Размещение
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Палитра символов
        self.ascii_chars = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]
        self.colors = ['green', 'white', '#FFBF00', 'cyan', 'magenta']
        self.current_color = 0

        # Переменные для видео
        self.video_capture = None
        self.is_playing_video = False
        self.video_thread = None
        self.current_frame = None

        # Бинды клавиш
        self.root.bind('<Escape>', lambda e: self.stop_video() or self.root.quit())
        self.root.bind('<c>', lambda e: self.change_color())
        self.root.bind('<o>', lambda e: self.open_file())
        self.root.bind('<space>', lambda e: self.toggle_video_playback())
        self.root.bind('<q>', lambda e: self.stop_video())

        # Загрузка медиа
        if media_path and os.path.exists(media_path):
            self.load_media(media_path)
        else:
            self.show_test_image()

    def show_test_image(self):
        """Показать тестовое изображение"""
        test_ascii = """
        ╔══════════════════════════════════════════════════════════════╗
        ║                     ASCII ART VIEWER                        ║
        ║                                                              ║
        ║    Нажмите O для открытия файла                             ║
        ║    C - смена цвета, ESC - выход                             ║
        ║                                                              ║
        ║    Поддерживаемые форматы:                                  ║
        ║    • Изображения: JPG, PNG, BMP, GIF                        ║
        """


        test_ascii += """║    • Видео: MP4, AVI, MOV, MKV (пробел - пауза)      ║"""


        test_ascii += """
        ║                                                              ║
        ╚══════════════════════════════════════════════════════════════╝
        """
        self.text_widget.insert(1.0, test_ascii)

    def change_color(self, event=None):
        """Смена цвета текста"""
        self.current_color = (self.current_color + 1) % len(self.colors)
        color = self.colors[self.current_color]
        self.text_widget.config(fg=color, insertbackground=color)

    def load_media(self, media_path):
        """Загрузка медиа"""
        try:
            ext = os.path.splitext(media_path)[1].lower()

            if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']:
                self.load_image(media_path)
            elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv']:
                self.load_video(media_path)
            else:
                messagebox.showerror("Ошибка", f"Неподдерживаемый формат: {ext}")
                self.show_test_image()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки:\n{str(e)}")
            self.show_test_image()

    def load_image(self, image_path):
        """Загрузка изображения"""
        try:
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(1.0, "Загрузка изображения...")
            self.root.update()

            ascii_art = self.convert_to_ascii(image_path)
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(1.0, ascii_art)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки изображения:\n{str(e)}")
            self.show_test_image()

    def load_video(self, video_path):
        """Загрузка видео"""
        try:
            self.stop_video()
            self.video_capture = cv2.VideoCapture(video_path)

            if not self.video_capture.isOpened():
                raise Exception("Не удалось открыть видео файл")

            self.is_playing_video = True
            self.start_video_playback()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки видео:\n{str(e)}")
            self.show_test_image()

    def start_video_playback(self):
        """Запуск воспроизведения видео"""
        if self.video_thread and self.video_thread.is_alive():
            return

        self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
        self.video_thread.start()

    def video_loop(self):
        """Цикл воспроизведения видео"""
        fps = self.video_capture.get(cv2.CAP_PROP_FPS)
        frame_delay = 1.0 / fps if fps > 0 else 1.0 / 30.0

        while self.is_playing_video and self.video_capture.isOpened():
            start_time = time.time()

            ret, frame = self.video_capture.read()
            if not ret:
                self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            ascii_frame = self.convert_frame_to_ascii(frame)
            self.root.after(0, self.update_ascii_display, ascii_frame)

            processing_time = time.time() - start_time
            sleep_time = max(0, frame_delay - processing_time)
            time.sleep(sleep_time)

    def convert_frame_to_ascii(self, frame):
        """Конвертация кадра видео в ASCII"""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb).convert('L')

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        width, height = img.size
        aspect_ratio = height / width

        max_chars_x = min(200, screen_width // 6)
        max_chars_y = min(100, screen_height // 12)

        new_width = min(max_chars_x, width)
        new_height = int(new_width * aspect_ratio * 0.55)

        if new_height > max_chars_y:
            new_height = max_chars_y
            new_width = int(new_height / (aspect_ratio * 0.55))

        img = img.resize((new_width, new_height), Image.LANCZOS)
        img = img.filter(ImageFilter.SHARPEN)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.3)


        pixels = np.array(img)
        ascii_str = ""
        for y in range(pixels.shape[0]):
            for x in range(pixels.shape[1]):
                brightness = pixels[y, x]
                index = int(brightness / 255 * (len(self.ascii_chars) - 1))
                ascii_str += self.ascii_chars[index]
            ascii_str += "\n"


        return ascii_str

    def update_ascii_display(self, ascii_text):
        """Обновление отображения"""
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, ascii_text)

    def convert_to_ascii(self, image_path):
        """Конвертация изображения в ASCII"""
        img = Image.open(image_path).convert('L')

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        width, height = img.size
        aspect_ratio = height / width

        max_chars_x = min(200, screen_width // 6)
        max_chars_y = min(100, screen_height // 12)

        new_width = min(max_chars_x, width)
        new_height = int(new_width * aspect_ratio * 0.55)

        if new_height > max_chars_y:
            new_height = max_chars_y
            new_width = int(new_height / (aspect_ratio * 0.55))

        img = img.resize((new_width, new_height), Image.LANCZOS)
        img = img.filter(ImageFilter.SHARPEN)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.3)


        pixels = np.array(img)
        ascii_str = ""
        for y in range(pixels.shape[0]):
            for x in range(pixels.shape[1]):
                brightness = pixels[y, x]
                index = int(brightness / 255 * (len(self.ascii_chars) - 1))
                ascii_str += self.ascii_chars[index]
            ascii_str += "\n"


        return ascii_str

    def toggle_video_playback(self):
        """Пауза/воспроизведение видео"""
        if self.video_capture and self.video_capture.isOpened():
            self.is_playing_video = not self.is_playing_video
            if self.is_playing_video:
                self.start_video_playback()

    def stop_video(self):
        """Остановка видео"""
        self.is_playing_video = False
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None

    def open_file(self):
        """Открытие файла"""
        filetypes = [
            ("Все поддерживаемые форматы", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.mp4 *.avi *.mov *.mkv *.wmv"),
            ("Изображения", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
            ("Видео", "*.mp4 *.avi *.mov *.mkv *.wmv"),
            ("Все файлы", "*.*")
        ]

        file_path = filedialog.askopenfilename(filetypes=filetypes)
        if file_path:
            self.stop_video()
            self.load_media(file_path)

    def run(self):
        """Запуск приложения"""
        self.root.mainloop()
        self.stop_video()


def check_dependencies():
    """Проверка зависимостей"""
    missing = []

    try:
        import PIL
    except ImportError:
        missing.append("pillow")

    if missing:
        print("⚠️  Отсутствуют пакеты:", ", ".join(missing))
        print("📦 Установите: pip install pillow")
        return False

    try:
        import cv2
        print("✅ OpenCV доступен для видео")
    except ImportError:
        print("⚠️  OpenCV не установлен - видео не будет работать")

    return True


if __name__ == "__main__":
    print("🚀 Запуск ASCII Viewer...")

    if check_dependencies():
        print("✅ Основные зависимости доступны!")
        viewer = ASCIIViewer('VID_20240818_112526.mp4')
        viewer.run()
    else:
        print("❌ Не все зависимости установлены")
        input("Нажмите Enter для выхода...")