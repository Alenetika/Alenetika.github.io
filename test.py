from PIL import Image
import numpy as np


def image_to_ascii_high_res(image_path, output_width=150, chars_per_pixel=2):
    """
    Преобразует изображение в ASCII-арт с высоким разрешением

    Args:
        image_path: путь к изображению
        output_width: ширина выходного ASCII-арта (в символах)
        chars_per_pixel: количество символов на пиксель (для большей детализации)
    """

    # Открываем и конвертируем в grayscale
    img = Image.open(image_path).convert('L')

    # Увеличиваем разрешение для большей детализации
    width, height = img.size
    aspect_ratio = height / width

    # Увеличиваем размер изображения перед обработкой
    scale_factor = chars_per_pixel
    new_width = output_width * scale_factor
    new_height = int(new_width * aspect_ratio * 0.55)  # Коррекция пропорций символов

    img = img.resize((new_width, new_height), Image.LANCZOS)  # Высококачественное масштабирование

    # Получаем пиксели как numpy массив для быстрой обработки
    pixels = np.array(img)

    # Расширенная палитра символов для большей детализации
    ascii_chars = [
        "@", "#", "W", "B", "8", "&", "M", "*", "o", "a", "h", "k",
        "b", "d", "p", "q", "w", "m", "Z", "O", "0", "Q", "L", "C",
        "J", "U", "Y", "X", "z", "c", "v", "u", "n", "x", "r", "j",
        "f", "t", "/", "\\", "|", "(", ")", "1", "{", "}", "[", "]",
        "?", "-", "_", "+", "~", "<", ">", "i", "!", "l", "I", ";",
        ":", ",", "\"", "^", "`", "'", ".", " "
    ]

    # Преобразуем пиксели в ASCII символы
    ascii_str = ""

    for y in range(pixels.shape[0]):
        for x in range(0, pixels.shape[1], scale_factor):
            # Берем среднее значение группы пикселей для сглаживания
            if x + scale_factor <= pixels.shape[1]:
                pixel_group = pixels[y, x:x + scale_factor]
                avg_brightness = np.mean(pixel_group)
            else:
                avg_brightness = pixels[y, x]

            # Нормализуем значение пикселя к индексу символа
            index = int(avg_brightness / 255 * (len(ascii_chars) - 1))
            ascii_str += ascii_chars[index]

        ascii_str += "\n"

    return ascii_str


def image_to_ascii_enhanced(image_path, output_width=120, method='standard'):
    """
    Улучшенная версия с разными методами обработки

    Args:
        image_path: путь к изображению
        output_width: ширина выходного ASCII-арта
        method: 'standard', 'detailed', 'artistic'
    """

    img = Image.open(image_path).convert('L')
    width, height = img.size
    aspect_ratio = height / width

    # Разные настройки для разных методов
    if method == 'detailed':
        new_height = int(output_width * aspect_ratio * 0.6)
        img = img.resize((output_width * 2, new_height * 2), Image.LANCZOS)
        chars = list("@%#*+=-:. ")  # Простая палитра для детализации
    elif method == 'artistic':
        new_height = int(output_width * aspect_ratio * 0.5)
        img = img.resize((output_width, new_height), Image.BICUBIC)
        chars = list("▓▒░ ")  # Блок-символы для художественного эффекта
    else:  # standard
        new_height = int(output_width * aspect_ratio * 0.55)
        img = img.resize((output_width, new_height), Image.LANCZOS)
        chars = list("@#S%?*+;:,. ")  # Стандартная палитра

    pixels = np.array(img)
    ascii_str = ""

    for y in range(pixels.shape[0]):
        for x in range(pixels.shape[1]):
            index = int(pixels[y, x] / 255 * (len(chars) - 1))
            ascii_str += chars[index]
        ascii_str += "\n"

    return ascii_str


# Функция для сохранения в файл
def save_ascii_to_file(ascii_str, filename="ascii_art.txt"):
    """Сохраняет ASCII-арт в текстовый файл"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(ascii_str)
    print(f"ASCII-арт сохранен в файл: {filename}")


# Пример использования
if __name__ == "__main__":
    # Высокое разрешение
    ascii_art_high_res = image_to_ascii_high_res('проба.jpg', output_width=120, chars_per_pixel=2)
    print("Высокодетализированный ASCII-арт:")
    print(ascii_art_high_res)

    # Сохранение в файл
    save_ascii_to_file(ascii_art_high_res, "high_res_ascii.txt")

    # Разные методы
    print("\nДетализированная версия:")
    ascii_detailed = image_to_ascii_enhanced('проба.jpg', output_width=100, method='detailed')
    print(ascii_detailed)

    print("\nХудожественная версия:")
    ascii_artistic = image_to_ascii_enhanced('проба.jpg', output_width=80, method='artistic')
    print(ascii_artistic)