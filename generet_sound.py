from gtts import gTTS
import os

# Текст для озвучки
text = "Уважаемая Анна Вадимовна! Сегодня я поздравляю Вас с самым главным событием сентября, которое по своей легендарности затмевает даже коллаб Шуфутинского и третье сентября. Вы — самая лучшая женщина на свете... Вы объединяете вокруг себя большое весёлое комьюнити, потому что все мы стремимся к прекрасному. Поздравляю Вас, любовь моя, с днём рождения! Желаю, чтобы новый год Вашей жизни начался легендарно, ярко и максимально продуктивно."


def save_google_tts(text, filename='поздравление_анне.mp3', lang='ru'):
    """
    Сохраняет текст в MP3 используя Google Text-to-Speech
    """
    try:
        print("🎙️  Синтез речи через Google TTS...")

        # Создаем объект gTTS
        tts = gTTS(text=text, lang=lang, slow=False)

        # Сохраняем в MP3
        tts.save(filename)

        if os.path.exists(filename):
            file_size = os.path.getsize(filename) / 1024
            print(f"✅ MP3 файл успешно сохранен!")
            print(f"📊 Размер файла: {file_size:.1f} KB")
            print(f"📍 Полный путь: {os.path.abspath(filename)}")
            return True
        else:
            print("❌ Файл не был создан")
            return False

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("⚠️  Проверьте подключение к интернету (gTTS требует интернет)")
        return False


# Используем Google TTS для настоящего MP3
save_google_tts(text, 'поздравление_анне_google.mp3')