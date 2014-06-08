# Slask
A [Slack](https://slack.com/) bot running in *daemon mode* with *Amazon SQS* integration.

Original version using *Flask* and *Outgoing WebHooks* integration by [llimllib/slask](https://github.com/llimllib/slask).

## Installation

1. Clone the repo
2. `pip install -r requirements.txt`
3. Update config.py with your custom information
3. `python bot.py start`
4. Add the Amazon SQS integration on [Slack](https://slack.com)
5. That's it! Try typing `!echo Hello World` into any chat room

You can also host your Bot for free on [Heroku](http://heroku.com). It is ready to deploy.
```bash
heroku create
git push heroku master
heroku ps:scale worker=1
heroku ps
heroku logs
```

## Commands

Right now, `!help`, `!echo`, `!gif`, `!image`, `!youtube` and `!wiki` are the only available commands.

It's super easy to add your own commands! Just create a python file in the plugins directory with an `on_message` function that returns a string.
