import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import time
import cv2
import numpy as np
import threading
from PIL import Image, ImageFilter, ImageEnhance, ImageTk
import subprocess
import tempfile
import shutil

import os

# Добавь это в начало скрипта, перед созданием ASCIIViewer
ffmpeg_path = r"C:\Projects\24_september\FFMPEG\ffmpeg-8.0-full_build\bin"
os.environ['PATH'] = ffmpeg_path + os.pathsep + os.environ['PATH']

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
        self.video_writer = None
        self.output_video_path = None
        self.is_processing_video = False
        self.progress_window = None
        self.current_video_path = None  # Путь к текущему видео

        # Бинды клавиш
        self.root.bind('<Escape>', lambda e: self.stop_video() or self.root.quit())
        self.root.bind('<c>', lambda e: self.change_color())
        self.root.bind('<o>', lambda e: self.open_file())
        self.root.bind('<space>', lambda e: self.toggle_video_playback())
        self.root.bind('<q>', lambda e: self.stop_video())
        # Бинды для сохранения
        self.root.bind('<s>', lambda e: self.save_video())
        self.root.bind('<a>', lambda e: self.save_audio())  # НОВЫЙ БИНД: Сохранение аудио

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
        ║    S - сохранить видео как MP4                              ║
        ║    A - сохранить аудио из видео                             ║
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
                self.current_video_path = media_path  # Сохраняем путь к видео
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
            self.current_video_path = video_path  # Сохраняем путь к видео

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
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None

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

    def save_video(self):
        """Сохранить обработанное видео как MP4"""
        if not self.video_capture or not self.video_capture.isOpened():
            messagebox.showwarning("Предупреждение", "Сначала откройте видео файл")
            return

        # Спросить куда сохранить
        output_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 Video", "*.mp4"), ("Все файлы", "*.*")]
        )

        if not output_path:
            return

        try:
            # Создать окно прогресса
            self.create_progress_window()

            # Запустить обработку в отдельном потоке
            processing_thread = threading.Thread(
                target=self.process_video_for_saving,
                args=(output_path,),
                daemon=True
            )
            processing_thread.start()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении видео:\n{str(e)}")

    # НОВЫЙ МЕТОД: Сохранение аудио из видео
    def save_audio(self):
        """Извлечь и сохранить аудио из исходного видео"""
        if not self.current_video_path or not os.path.exists(self.current_video_path):
            messagebox.showwarning("Предупреждение", "Сначала откройте видео файл")
            return

        # Спросить куда сохранить аудио
        output_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[
                ("MP3 Audio", "*.mp3"),
                ("WAV Audio", "*.wav"),
                ("Все файлы", "*.*")
            ]
        )

        if not output_path:
            return

        try:
            # Создать окно прогресса
            self.create_progress_window("Извлечение аудио...")

            # Запустить извлечение аудио в отдельном потоке
            audio_thread = threading.Thread(
                target=self.extract_audio,
                args=(self.current_video_path, output_path),
                daemon=True
            )
            audio_thread.start()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении аудио:\n{str(e)}")

    # НОВЫЙ МЕТОД: Извлечение аудио с помощью ffmpeg
    def extract_audio(self, input_path, output_path):
        """Извлечь аудио из видео файла"""
        try:
            # Проверяем доступность ffmpeg
            if not self.check_ffmpeg_available():
                self.root.after(0, lambda: messagebox.showerror(
                    "Ошибка",
                    "FFmpeg не найден. Установите FFmpeg и добавьте его в PATH:\n"
                    "Windows: https://ffmpeg.org/download.html\n"
                    "Linux: sudo apt install ffmpeg\n"
                    "Mac: brew install ffmpeg"
                ))
                self.root.after(0, self.close_progress_window)
                return

            # Определяем формат выходного файла по расширению
            ext = os.path.splitext(output_path)[1].lower()
            if ext == '.wav':
                codec = 'pcm_s16le'
            else:
                codec = 'libmp3lame'  # По умолчанию MP3

            # Команда для извлечения аудио
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-vn',              # Без видео
                '-acodec', codec,
                '-y',               # Перезаписать существующий файл
                output_path
            ]

            # Запускаем процесс
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # Мониторим прогресс
            duration = self.get_video_duration(input_path)
            for line in process.stderr:
                if 'time=' in line:
                    time_str = line.split('time=')[1].split(' ')[0]
                    current_time = self.time_to_seconds(time_str)
                    if duration > 0:
                        progress = (current_time / duration) * 100
                        self.root.after(0, self.update_progress, progress)

            process.wait()

            if process.returncode == 0:
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успех",
                    f"Аудио сохранено как:\n{output_path}\n\n"
                    f"Формат: {ext.upper()[1:]}\n"
                    f"Исходное видео: {os.path.basename(input_path)}"
                ))
            else:
                error = process.stderr.read()
                raise Exception(f"Ошибка FFmpeg: {error}")

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Ошибка",
                f"Ошибка при извлечении аудио:\n{str(e)}"
            ))
        finally:
            self.root.after(0, self.close_progress_window)

    # НОВЫЙ МЕТОД: Проверка доступности ffmpeg
    def check_ffmpeg_available(self):
        """Проверить, доступен ли ffmpeg"""
        try:
            subprocess.run(['ffmpeg', '-version'],
                         capture_output=True,
                         check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    # НОВЫЙ МЕТОД: Получение длительности видео
    def get_video_duration(self, video_path):
        """Получить длительность видео в секундах"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return float(result.stdout.strip())
        except:
            return 0

    # НОВЫЙ МЕТОД: Конвертация времени в секунды
    def time_to_seconds(self, time_str):
        """Конвертировать время формата HH:MM:SS.mmm в секунды"""
        try:
            h, m, s = time_str.split(':')
            return int(h) * 3600 + int(m) * 60 + float(s)
        except:
            return 0

    def create_progress_window(self, title="Обработка видео..."):
        """Создать окно с прогресс баром"""
        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title(title)
        self.progress_window.geometry("300x100")
        self.progress_window.resizable(False, False)

        tk.Label(self.progress_window, text=title).pack(pady=10)

        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            self.progress_window,
            variable=self.progress_var,
            maximum=100
        )
        progress_bar.pack(pady=10, padx=20, fill=tk.X)

        self.progress_label = tk.Label(self.progress_window, text="0%")
        self.progress_label.pack()

    def update_progress(self, percentage):
        """Обновить прогресс бар"""
        if self.progress_window:
            self.progress_var.set(percentage)
            self.progress_label.config(text=f"{percentage:.1f}%")
            self.progress_window.update()

    def close_progress_window(self):
        """Закрыть окно прогресса"""
        if self.progress_window:
            self.progress_window.destroy()
            self.progress_window = None

    def process_video_for_saving(self, output_path):
        """Обработать видео и сохранить как MP4"""
        try:
            self.is_processing_video = True
            self.is_playing_video = False

            # Получить параметры исходного видео
            fps = self.video_capture.get(cv2.CAP_PROP_FPS)
            total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

            # Перемотать в начало
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

            # Получить размер ASCII кадра для создания видео
            ret, test_frame = self.video_capture.read()
            if not ret:
                raise Exception("Не удалось прочитать тестовый кадр")

            ascii_test = self.convert_frame_to_ascii(test_frame)
            lines = ascii_test.split('\n')
            frame_height = len(lines)
            frame_width = len(lines[0]) if lines else 80

            # Создать видео writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                output_path,
                fourcc,
                fps,
                (frame_width * 6, frame_height * 12)  # Умножаем на размер символа
            )

            # Перемотать обратно в начало
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

            # Обработать все кадры
            for frame_num in range(total_frames):
                if not self.is_processing_video:
                    break

                ret, frame = self.video_capture.read()
                if not ret:
                    break

                # Конвертировать в ASCII
                ascii_frame = self.convert_frame_to_ascii(frame)

                # Создать изображение из ASCII текста
                ascii_image = self.ascii_to_image(ascii_frame)

                # Записать кадр в видео
                self.video_writer.write(ascii_image)

                # Обновить прогресс
                progress = (frame_num + 1) / total_frames * 100
                self.root.after(0, self.update_progress, progress)

            # Завершить запись
            self.video_writer.release()
            self.video_writer = None

            self.root.after(0, lambda: messagebox.showinfo("Успех", f"Видео сохранено как:\n{output_path}"))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка обработки видео:\n{str(e)}"))
        finally:
            self.is_processing_video = False
            self.root.after(0, self.close_progress_window)
            # Вернуться к началу видео
            if self.video_capture:
                self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def ascii_to_image(self, ascii_text):
        """Конвертировать ASCII текст в изображение OpenCV"""
        lines = ascii_text.split('\n')
        if not lines:
            return np.zeros((100, 100, 3), dtype=np.uint8)

        # Создать белое изображение
        height = len(lines) * 12
        width = len(lines[0]) * 6
        image = np.ones((height, width, 3), dtype=np.uint8) * 255

        # Нарисовать текст
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.2
        color = (0, 0, 0)  # Черный текст
        thickness = 1

        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char != ' ':
                    position = (x * 6, (y + 1) * 12)
                    cv2.putText(image, char, position, font, font_scale, color, thickness, cv2.LINE_AA)

        return image

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

    # Проверка ffmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg доступен для извлечения аудио")
        else:
            print("⚠️  FFmpeg не найден - извлечение аудио не будет работать")
    except FileNotFoundError:
        print("⚠️  FFmpeg не установлен - извлечение аудио не будет работать")

    return True


if __name__ == "__main__":
    print("🚀 Запуск ASCII Viewer...")

    if check_dependencies():
        print("✅ Основные зависимости доступны!")
        viewer = ASCIIViewer('VID_20240804_140007.mp4')
        viewer.run()
    else:
        print("❌ Не все зависимости установлены")
        input("Нажмите Enter для выхода...")