# Telegag - telegram bot with Reddit channels subscriptions.

## Usage

What it can:
1. Show you posts from the particular channel immediately
2. Create a subscription to the channel manually
3. Create a subscription to the channel using helper 
4. Create a subscription to the channel from the top channels list.

#### To show the menu
```
/start
```

#### To show posts:
```
/show aww 3
```
Will show you 3 posts from the aww Reddit channel

#### To subscribe manually
```
/sub aww 1 3
```
Will subscribe you to the aww Subreddit showing 3 posts every 1 hour

#### To use helper
Just tap the button in the menu and answer some questions

#### To use top channels helper
Just tap the button in the menu and answer some questions


## For developers

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
It will run all tests in the tests directory. To generate an html report (it will be in `./htmlcov/index.html`), run:
```
pytest --cov=app --cov-report html tests/
```
