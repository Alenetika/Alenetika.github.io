"""
ASCII Viewer - работает без установки дополнительных пакетов!
Поддерживает изображения и видео (если OpenCV установлен)
Использует Tkinter, PIL и опционально OpenCV
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import os
import time
import threading




try:


    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL не установлен, используем упрощенный режим")

try:


    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("NumPy не установлен, используем упрощенный режим")

try:
    import cv2

    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("OpenCV не установлен. Видео не будет работать.")
print("✅ Все пакеты успешно установлены!")
print(f"PIL version: {PIL.__version__}")
print(f"NumPy version: {numpy.__version__}")
print(f"OpenCV version: {cv2.__version__}")
#
#