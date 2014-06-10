"""!echo [<message>] echo a test message"""

import re

def echo(message):
    return message


def on_message(msg, server):
    text = msg.get("text", "")
    match = re.findall(r"!echo( .*)?", text)
    if not match: return

    message = match[0]
    return echo(message)
