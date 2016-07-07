# TODO: extract to files, use built-in i18n module
DEFAULT_LOCALE = {
    'HELP': "Use /roulette command to connect with random user",
    'START': "Hi! I can connect you with random stranger.\nLet's start! Use /roulette command.",
    'DISCONNECTED_SEARCH_NEW': "Disconnected. Searching new user...",
    'DISCONNECTED': "Disconnected. Use /roulette to connect to new user.",
    'SEARCHING': "Looking for a couple...",
    'ESTABLISHED': "Connection established. Say hello :)",
    'ERROR_SEARCHING': "Please, wait. User not found yet...",
    'ERROR_IDLE': "You are not connected. Use /roulette command to connect with random user.",
}


def _(key):
    return DEFAULT_LOCALE[key]
