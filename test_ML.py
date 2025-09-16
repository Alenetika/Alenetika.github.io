from PIL import Image
import numpy as np


class ImageToASCII:
    def __init__(self, width=100, charset="@%#*+=-:. "):
        self.width = width
        self.charset = charset  # Градации яркости от темного к светлому

    def image_to_ascii(self, image_path):
        """Преобразование изображения в ASCII арт"""
        try:
            # Загружаем и конвертируем в grayscale
            img = Image.open(image_path).convert('L')

            # Масштабируем сохраняя пропорции
            orig_width, orig_height = img.size
            aspect_ratio = orig_height / orig_width
            height = int(self.width * aspect_ratio * 0.55)  # 0.55 для коррекции пропорций символов

            # Изменяем размер
            img = img.resize((self.width, height))

            # Конвертируем в numpy array
            pixels = np.array(img)

            # Нормализуем пиксели к диапазону [0, len(charset)-1]
            pixels_normalized = (pixels / 255 * (len(self.charset) - 1)).astype(int)

            # Создаем ASCII арт
            ascii_art = []
            for row in pixels_normalized:
                ascii_row = ''.join(self.charset[pixel] for pixel in row)
                ascii_art.append(ascii_row)

            return '\n'.join(ascii_art)

        except Exception as e:
            return f"Ошибка: {e}"


# === ПРИМЕР ИСПОЛЬЗОВАНИЯ ===
if __name__ == "__main__":
    # Создаем конвертер
    converter = ImageToASCII(width=80)  # Ширина в символах

    # Преобразуем изображение в ASCII
    ascii_result = converter.image_to_ascii("проба.jpg")  # Укажите путь к вашему изображению

    # Выводим результат
    print(ascii_result)

    # Сохраняем в файл
    with open("ascii_art.txt", "w", encoding="utf-8") as f:
        f.write(ascii_result)
    print("\nРезультат сохранен в ascii_art.txt")