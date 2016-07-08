# TODO: extract to files, add multi-language support, use built-in i18n module\

DEFAULT_LOCALE = {
    'HELP': "Use /roulette command to connect with random user,/n /disconnect to stop chatting",
    'START': "Hi! I can connect you with random stranger.\nLet's start! Use /roulette command.",
    'DISCONNECTED_SEARCH_NEW': "Disconnected. Searching new user...",
    'DISCONNECTED': "Disconnected. Use /roulette to connect to new user.",
    'SEARCHING': "Waiting for an available stranger...",
    'ESTABLISHED': "Connection established. Say hi :)",
    'ERROR_SEARCHING': "Please, wait. User not found yet...",
    'ERROR_IDLE': "You are not connected. Use /roulette command to connect with random user.",
    'MESSAGE_BODY': "Anonymous:\n%s",
}


def _(key):
    """
    Return localized string by key
    :param key: Localization string key
    :return: Localized string
    """
    return DEFAULT_LOCALE[key]
