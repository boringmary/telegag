#### Telegram bot which allows you to subscribe to channels you like and get daily updates (actually whatever time range you want)

!Attentions: Currently still in development.

### Installation

1. Set up the config file with `telegram`, `aws` and `reddit` credentials. Create files with the following parameters (telegram credentials faq: https://core.telegram.org/bots#creating-a-new-bot, reddit: https://www.reddit.com/prefs/apps/):

app/config.yaml
```
LOG_LEVEL: DEBUG
TELEGRAM_TOKEN: "dummy"
REDDIT_CLIENT_ID: "dummy"
REDDIT_USERNAME: "dummy-dummy"
REDDIT_PASSWORD: "dummy"

```

app/credentials
```
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region=us-east-1
```

2. Create virtualenv
```
python3 -m venv env
```

3. Activate virtualenv
```
. env/bin/activate
```

4. Install dependencies
```
pip3 install -r requirements.txt
```

5. Run
```
python3 bot.py
```

### Testing
To run unit tests just execute:
```
pytest --cov=app tests/
```
It will run all tests in tests directory. To generate a html report (it will be in `./htmlcov/index.html`), run:
```
pytest --cov=app --cov-report html tests/
```
