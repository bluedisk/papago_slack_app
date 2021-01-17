# papago_slack_app
Papago as a Slack App

# install (rough)
```bash
$ pip install poetry
$ poetry install
```

download language detection `lid.176.bin` model for `fasttest` from [here](https://fasttext.cc/docs/en/language-identification.html)

# run 
something like
```bash
ENV=production poetry run ./manage.py runserver
```