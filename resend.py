from telegram.ext import Filters


def send_text(bot, message, user_id, formatter, **kwargs):
    text = formatter(message.text)
    bot.sendMessage(user_id, text=text, **kwargs)


def send_audio(bot, message, user_id, **kwargs):
    audio = message.audio
    bot.sendAudio(user_id, audio=audio.file_id, **{**audio.__dict__, **kwargs})


def send_document(bot, message, user_id, **kwargs):
    document = message.document
    bot.sendDocument(user_id, document=document.file_id, **{**document.__dict__, **kwargs})


def send_photo(bot, message, user_id, **kwargs):
    photo = message.photo[0]
    bot.sendPhoto(user_id, photo=photo.file_id, **{**photo.__dict__, **kwargs})


def send_sticker(bot, message, user_id, **kwargs):
    sticker = message.sticker
    bot.sendSticker(user_id, sticker=sticker.file_id, **{**sticker.__dict__, **kwargs})


def send_video(bot, message, user_id, **kwargs):
    video = message.video
    bot.sendVideo(user_id, video=video.file_id, **{**video.__dict__, **kwargs})


def send_voice(bot, message, user_id, **kwargs):
    voice = message.voice
    bot.sendVoice(user_id, voice=voice.file_id, **{**voice.__dict__, **kwargs})


def send_contact(bot, message, user_id, **kwargs):
    contact = message.contact
    bot.sendContact(user_id, **{**contact.__dict__, **kwargs})


def send_location(bot, message, user_id, **kwargs):
    location = message.location
    bot.sendLocation(user_id, **{**location.__dict__, **kwargs})


def send_venue(bot, message, user_id, **kwargs):
    venue = message.venue
    bot.sendVenue(user_id, **{**venue.__dict__, **kwargs})


USER_MESSAGE_FILTERS = [
    (Filters.text, send_text),
    (Filters.audio, send_audio),
    (Filters.document, send_document),
    (Filters.photo, send_photo),
    (Filters.sticker, send_sticker),
    (Filters.video, send_video),
    (Filters.voice, send_voice),
    (Filters.contact, send_contact),
    (Filters.location, send_location),
    (Filters.venue, send_venue)
]


def resend_message(bot, original_message, user_id, formatter=lambda m: m, **kwargs):
    """
    Forward original message to user_id
    :param bot: python-telegram-bot Bot class
    :param original_message: python-telegram-bot Message class
    :param user_id: receiver
    :param formatter: text message formatter
    """
    for message_filter, sender in USER_MESSAGE_FILTERS:
        if message_filter(original_message):
            sender(bot, original_message, user_id, formatter=formatter, **kwargs)
            break
