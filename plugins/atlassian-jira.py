"""!jira - !help atlassian-jira
!jira info <issue-id>
!jira comment <issue-id> <comment>
!jira create <project-key> <summary>
!jira close <issue-id> <comment>
!jira projects
"""

import re
from config import config
from jira.client import JIRA


def atlassian_jira(user, action, parameter):

    jira_username = config.get("jira_username")
    jira_password = config.get("jira_password")

    options = {
        'server': 'https://agapigroup.atlassian.net',
    }
    jira = JIRA(options, basic_auth=(jira_username, jira_password))

    if action == 'projects':
        return projects(jira, parameter)
    elif action == 'info':
        return info(jira, parameter)
    elif action == 'comment':
        comment(user, jira, parameter)
    elif action == 'create':
        create(user, jira, parameter)
    elif action == 'close':
        close(user, jira, parameter)


def info(jira, parameter):
    issue = jira.issue(parameter, fields='summary,assignee,status')
    issue_id = parameter
    issue_url = "<" + issue.permalink() + "|" + issue_id + ">"
    summary = issue.fields.summary
    assignee = str(issue.fields.assignee)
    status = str(issue.fields.status)

    if status == "Open":
        color = "#4a6785"
    elif status == "Resolved":
        color = "#14892c"
    elif status == "Closed":
        color = "#14892c"
    elif status == "In Progress":
        color = "#ffd351"

    message = {'fallback': 'jira integration', 'pretext': summary, 'color': color,
                            'fields': [{'title': 'Issue ID', 'value': issue_url, 'short': True},
                                       {'title': 'Assignee', 'value': assignee, 'short': True},
                                       {'title': 'Status', 'value': status, 'short': True}, ]}
    return message


def comment(user, jira, parameter):
    m = re.match(r"(\w+-\d+) (.*)", parameter)
    jira_id = m.group(1)
    jira_comment = m.group(2)
    jira_comment =+ "\n Comment by %s" % user

    jira.add_comment(jira_id, jira_comment)


def create(user, jira, parameter):
    m = re.match(r"(\w+) (.*)", parameter)
    jira_key = m.group(1)
    jira_summary = m.group(2)
    jira_description = "Created by user %s" % user
    issue_dict = {
        'project': {'key': jira_key},
        'summary': jira_summary,
        'description': jira_description,
        'issuetype': {'name': 'Bug'},
        'assignee': {'name': user},
    }
    jira.create_issue(fields=issue_dict)


def close(user, jira, parameter):
    m = re.match(r"(\w+-\d+) ?(.*)", parameter)
    jira_comment = None
    jira_key = m.group(1)
    jira_comment = m.group(2)
    jira_comment += "\n Closed by user %s" % user
    issue = jira.issue(jira_key)

    jira.transition_issue(issue, '5', comment=jira_comment)


def projects(jira, parameter):
    p = jira.projects()

    all_projects = ''
    for project in p:
        all_projects += "%s: %s\n" % (project.key, project.name)

    return all_projects


def on_message(msg, server):
    text = msg.get("text", "")
    user = msg.get("user_name", "")
    parameter = None
    m = re.match(r"!jira (info|comment|create|close|projects) ?(.*)", text)
    if not m:
        return

    action = m.group(1)
    parameter = m.group(2)
    return atlassian_jira(user, action, parameter)


if __name__ == '__main__':
    print "Running from cmd line"
    atlassian_jira('fsalum', 'info', 'INFRA-35')
    #atlassian_jira('fsalum', 'comment', 'INFRA-20 testing comment')
    #atlassian_jira('fsalum', 'create', 'INFRA Create new ticket via Slack')
    #atlassian_jira('fsalum', 'close', 'INFRA-33 test completed')
    #atlassian_jira('fsalum', 'projects', None)
