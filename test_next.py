#!/usr/bin/env python3
"""
ASCII Viewer - работает без установки дополнительных пакетов!
Использует только Tkinter и PIL (который обычно уже установлен)
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import os

try:
    from PIL import Image, ImageFilter, ImageEnhance

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL не установлен, используем упрощенный режим")

try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("NumPy не установлен, используем упрощенный режим")


class ASCIIViewer:
    def __init__(self, image_path=None):
        self.root = tk.Tk()
        self.root.title("ASCII Art Viewer - Полный экран")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')

        # Основной текстовый виджет
        self.text_widget = tk.Text(
            self.root,
            font=('Courier New', self.font_size),
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

        # Бинды клавиш
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.root.bind('<c>', lambda e: self.change_color())

        # Загрузка изображения
        if image_path and os.path.exists(image_path):
            self.load_image(image_path)
        else:
            # Если изображение не указано или не найдено, показываем тестовое изображение
            self.show_test_image()

    def show_test_image(self):
        """Показать тестовое изображение (геометрические фигуры)"""
        test_ascii = """
        ╔══════════════════════════════════════════════════════════════╗
        ║                     ASCII ART VIEWER                        ║
        ║                                                              ║
        ║    ██████████████████████████████████████████████████████    ║
        ║    █                                                █    ║
        ║    █          ТЕСТОВОЕ ИЗОБРАЖЕНИЕ                 █    ║
        ║    █                                                █    ║
        ║    █    ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄    █    ║
        ║    █    █                                    █    █    ║
        ║    █    █           ПРЯМОУГОЛЬНИК            █    █    ║
        ║    █    █                                    █    █    ║
        ║    █    ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀    █    ║
        ║    █                                                █    ║
        ║    █          ○○○○○○○○○○○○○○○○○○○○○○○○             █    ║
        ║    █        ○○                    ○○             █    ║
        ║    █        ○○        КРУГ        ○○             █    ║
        ║    █        ○○                    ○○             █    ║
        ║    █          ○○○○○○○○○○○○○○○○○○○○○○○○             █    ║
        ║    █                                                █    ║
        ║    █    ╱▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔╲    █    ║
        ║    █    ╲    ТРЕУГОЛЬНИК              ╱    █    ║
        ║    █        ╲                    ╱        █    ║
        ║    █            ╲            ╱            █    ║
        ║    █                ╲    ╱                █    ║
        ║    █                    ▼                    █    ║
        ║    █                                                █    ║
        ║    ██████████████████████████████████████████████████████    ║
        ║                                                              ║
        ║        Нажмите ESC для выхода, C для смены цвета             ║
        ╚══════════════════════════════════════════════════════════════╝
        """
        self.text_widget.insert(1.0, test_ascii)

    def change_color(self, event=None):
        """Смена цвета текста"""
        self.current_color = (self.current_color + 1) % len(self.colors)
        color = self.colors[self.current_color]
        self.text_widget.config(fg=color, insertbackground=color)

    def load_image(self, image_path):
        """Загрузка и конвертация изображения"""
        try:
            if not PIL_AVAILABLE:
                messagebox.showerror("Ошибка", "PIL не установлен. Установите: pip install pillow")
                return

            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(1.0, "🔄 Загружаем и конвертируем изображение...")
            self.root.update()

            ascii_art = self.convert_to_ascii(image_path)

            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(1.0, ascii_art)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{str(e)}")
            self.show_test_image()

    def convert_to_ascii(self, image_path):
        """Конвертация изображения в ASCII"""
        img = Image.open(image_path).convert('L')

        # Определяем размеры экрана
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Автоматическое масштабирование
        width, height = img.size
        aspect_ratio = height / width

        # Максимальное количество символов
        max_chars_x = min(200, screen_width // 6)  # 6px на символ
        max_chars_y = min(100, screen_height // 12)  # 12px на символ

        new_width = min(max_chars_x, width)
        new_height = int(new_width * aspect_ratio * 0.55)

        if new_height > max_chars_y:
            new_height = max_chars_y
            new_width = int(new_height / (aspect_ratio * 0.55))

        img = img.resize((new_width, new_height), Image.LANCZOS)

        # Улучшаем изображение
        img = img.filter(ImageFilter.SHARPEN)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.3)

        # Конвертируем в ASCII
        if NUMPY_AVAILABLE:
            pixels = np.array(img)
            ascii_str = ""
            for y in range(pixels.shape[0]):
                for x in range(pixels.shape[1]):
                    brightness = pixels[y, x]
                    index = int(brightness / 255 * (len(self.ascii_chars) - 1))
                    ascii_str += self.ascii_chars[index]
                ascii_str += "\n"
        else:
            # Упрощенная версия без numpy
            pixels = list(img.getdata())
            ascii_str = ""
            for i in range(new_height):
                for j in range(new_width):
                    brightness = pixels[i * new_width + j]
                    index = int(brightness / 255 * (len(self.ascii_chars) - 1))
                    ascii_str += self.ascii_chars[index]
                ascii_str += "\n"

        return ascii_str

    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


def check_dependencies():
    """Проверка зависимостей"""
    missing = []

    try:
        import PIL
    except ImportError:
        missing.append("pillow (PIL)")

    if missing:
        print("⚠️  Отсутствуют пакеты:", ", ".join(missing))
        print("📦 Установите: pip install pillow")
        return False
    return True


if __name__ == "__main__":
    print("🚀 Запуск ASCII Viewer...")
    print("📋 Проверка зависимостей...")

    # УКАЖИТЕ ПУТЬ К ВАШЕМУ ИЗОБРАЖЕНИЮ ЗДЕСЬ
    IMAGE_PATH = "проба.jpg"  # ← ИЗМЕНИТЕ ЭТУ СТРОКУ

    if check_dependencies():
        print("✅ Все зависимости доступны!")
        viewer = ASCIIViewer(IMAGE_PATH)
        viewer.run()
    else:
        print("❌ Не все зависимости установлены")
        input("Нажмите Enter для выхода...")