#xoxp-16403402883-16413588660-151092478496-d2dd69f400440627e951af32a33fd05f
import os
from slackclient import SlackClient

def send_to_slack(url):
    slack_token = os.environ["SLACK_API_TOKEN"]
    sc = SlackClient(slack_token)
    sc.api_call(
      "chat.postMessage",
      channel="#alexa",
      text="open " + url
    )

if __name__ == '__main__':
	send_to_slack("hello world")