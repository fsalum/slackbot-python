"""stackdriver-reader listens to policy alerts sent via SNS notification integration"""

import requests
import json
from config import config


def stackdriver(text):
    incident_id = text.get("incident_id", "")
    resource_id = text.get("resource_id", "")
    resource_name = text.get("resource_name", "")
    state = text.get("state", "")
    started_at = text.get("started_at", "")
    ended_at = text.get("ended_at", "")
    incident_url = "<" + text.get("url", "") + "|" + incident_id + ">"
    summary = text.get("summary", "")

    if state == "open":
        color = "#d00000"
    elif state == "acknowledged":
        color = "0000d0"
    elif state == "closed":
        color = "00d000"

    send_msg(summary, color, incident_url, resource_id, resource_name, state)
    return


def send_msg(summary, color, incident_url, resource_id, resource_name, state):
    webhook_token = config.get("webhook_token")
    domain = config.get("domain")
    stackdriver_username = config.get("stackdriver_username")
    stackdriver_channel = config.get("stackdriver_channel")
    stackdriver_icon = config.get("stackdriver_icon")
    url = "https://" + domain + "/services/hooks/incoming-webhook?token=" + webhook_token

    payload = {'channel': stackdriver_channel, 'username': stackdriver_username, 'icon_url': stackdriver_icon,
               'attachments': [{'fallback': 'stackdriver alerts', 'pretext': summary, "color": color,
                                'fields': [{'title': 'Incident', 'value': incident_url, 'short': True},
                                           {'title': 'State', 'value': state, 'short': True},
                                           {'title': 'Resource ID', 'value': resource_id, 'short': True},
                                           {'title': 'Resource Name', 'value': resource_name, 'short': True}, ]}]}

    r = requests.post(url, data=json.dumps(payload), timeout=5)
    print r.status_code


def on_message(msg, server):
    topic_arn = msg.get("TopicArn", "")

    if topic_arn:
        stackdriver_sns_topic = config.get("stackdriver_sns_topic")
        if stackdriver_sns_topic in topic_arn:
            incident_dict = json.loads(msg.get("Message", ""))
            text = incident_dict.get("incident", "")
        else:
            return
    else:
        return

    if not text:
        return

    return stackdriver(text)
