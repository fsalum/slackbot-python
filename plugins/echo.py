"""!echo [<message>] echo a test message"""

import re

def echo(message):
    return message


def on_message(msg, server):
    match = re.findall(r"!echo( .*)?", msg)
    if not match: return

    message = match[0]
    return echo(message)
