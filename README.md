# roulette-bot
Chat with random user in telegram. Live demo: [@roulettegram_bot](https://telegram.me/roulettegram_bot).

## Run
### Create enviroments.private file
This file contains user specific enviroment variables. Fill it like this:
```
MYSQL_ROOT_PASSWORD=password
TELEGRAM_TOKEN=252651561:AAH5vQSl09NDgh1CeUshff-u62WLSlMVhp0
```
### Deploy bot
Run all services:
```docker-compose up -d```

That's it!

### Warning
Use [webhook](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks) update method for real deployment.
