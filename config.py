import os

config = {
    'TELEGRAM_TOKEN': None,
    'MYSQL_HOST': '192.168.99.100',
    'MYSQL_DATABASE': 'roulette',
    'MYSQL_USER': 'root',
    'MYSQL_ROOT_PASSWORD': 'password',
    'MYSQL_CONNECTION_POOL_SIZE': 8
}

# Update config with environment variables
for k, v in config.items():
    config[k] = os.getenv(k, v)
