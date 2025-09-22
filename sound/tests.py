from gtts import gTTS
import os

tts = gTTS(
    text="Салам алейкум, друзья! Как ваше настроение?",
    lang="ru",
    tld="kz"  # Казахстанский Google
)
tts.save("russian_kazakh.mp3")