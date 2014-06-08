#!/usr/bin/env python
#
# Python example to send SQS messages
#

import sys
import os
import re
import time
import json
import logging
import requests
import importlib
import traceback
import boto.sqs
from boto.sqs.message import RawMessage
from glob import glob
from daemon import runner

curdir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curdir)

from config import config

queue_name = config.get("queue")
aws_access_key = config.get("aws_access_key")
aws_secret_key = config.get("aws_secret_key")
region = 'us-east-1'
hooks = {}

conn = boto.sqs.connect_to_region(region,aws_access_key_id=aws_access_key,aws_secret_access_key=aws_secret_key)

q = conn.get_queue(queue_name)
q.set_message_class(RawMessage)

DEPLOY_DAEMON_PID = "/tmp/slackbot.pid"
DEPLOY_DAEMON_ERROR = "/tmp/slackbot.log"


class StartBot():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = DEPLOY_DAEMON_ERROR
        self.pidfile_path = DEPLOY_DAEMON_PID
        self.pidfile_timeout = 5

    def run(self):
        while True:
            get_msg()
            time.sleep(1)


def init_plugins():
    for plugin in glob('plugins/[!_]*.py'):
        print "plugin: %s" % plugin
        try:
            mod = importlib.import_module(plugin.replace("/", ".")[:-3])
            modname = mod.__name__.split('.')[1]

            for hook in re.findall("on_(\w+)", " ".join(dir(mod))):
                hookfun = getattr(mod, "on_" + hook)
                print "attaching %s.%s to %s" % (modname, hookfun, hook)
                hooks.setdefault(hook, []).append(hookfun)

            if mod.__doc__:
                firstline = mod.__doc__.split('\n')[0]
                hooks.setdefault('help', {})[modname] = firstline
                hooks.setdefault('extendedhelp', {})[modname] = mod.__doc__

        # bare except, because the modules could raise any number of errors
        # on import, and we want them not to kill our server
        except:
            print "import failed on module %s, module not loaded" % plugin
            print "%s" % sys.exc_info()[0]
            print "%s" % traceback.format_exc()


def run_hook(hook, data, server):
    responses = []
    for hook in hooks.get(hook, []):
        h = hook(data, server)
        if h:
            responses.append(h)

    return responses


def get_msg():
    results = q.get_messages(num_messages=1, wait_time_seconds=1, visibility_timeout=30)

    if not len(results) == 0:
        for result in results:
            body = json.loads(result.get_body())
            user = str(body['user_name'])
            channel = "#" + str(body['channel_name'])
            text = (body['text']).encode('utf-8')

            # ignore/delete message we sent
            if user == "slackbot":
                q.delete_message(result)
                return ""

            response = run_hook("message", text, {"config": config, "hooks": hooks})
            q.delete_message(result)
            if not response:
                return ""

            send_msg(channel, response)
            # Uncomment to debug on console
            # print response


def send_msg(channel, response):
    username = config.get("username")
    icon_url = config.get("icon_url")
    token = config.get("token")
    domain = config.get("domain")
    url = "https://" + domain + "/services/hooks/incoming-webhook?token=" + token
    payload = {'channel': channel, 'username': username, 'text': response, 'icon_url': icon_url}
    r = requests.post(url, data=json.dumps(payload), timeout=5)
    print r.status_code


def initialize_logging(logfile):
    """ Log information based upon users options"""

    logger = logging.getLogger(logfile)
    formatter = logging.Formatter('%(asctime)s\t%(message)s')
    level = logging.DEBUG
    logger.setLevel(level)

    # Output logging information to screen
    #if 'now' in ACTION:
    #    hdlr = logging.StreamHandler(sys.stderr)
    #    hdlr.setFormatter(formatter)
    #    logger.addHandler(hdlr)

    # Output logging information to file
    hdlr2 = logging.FileHandler(logfile)
    hdlr2.setFormatter(formatter)
    logger.addHandler(hdlr2)

    return logger


if __name__ == '__main__':
    init_plugins()
    app = StartBot()
    daemon_runner = runner.DaemonRunner(app)
    daemon_runner.do_action()
