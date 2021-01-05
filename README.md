### Installation

1. Set up the config file with `telegram` and `reddit` credentials. Create file named `config.yml` with the following parameters (telegram credentials faq: https://core.telegram.org/bots#creating-a-new-bot, reddit: https://www.reddit.com/prefs/apps/):
```
TELEGRAM_TOKEN: "dummy"
REDDIT_CLIENT_ID: "dummy"
REDDIT_USERNAME: "dummy-dummy"
REDDIT_PASSWORD: "dummy"

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