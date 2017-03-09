from slackclient import SlackClient
import os
import time

slack_token = os.environ["SLACK_API_TOKEN"]
sc = SlackClient(slack_token)

if sc.rtm_connect():
    while True:
        print sc.rtm_read()
        time.sleep(1)
else:
    print "Connection Failed, invalid token?"