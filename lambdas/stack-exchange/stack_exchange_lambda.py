"""
Search StackOverflow
"""

from __future__ import print_function
import stackexchange
from slackclient import SlackClient
from stackexchange import Site, StackOverflow
import boto3
import os

QUEUE_NAME = "lambda-stack-overflow"
SQS = boto3.client("sqs")

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def send_to_sqs(url):
    q = SQS.get_queue_url(QueueName=QUEUE_NAME).get('QueueUrl')
    resp = SQS.send_message(QueueUrl=q, MessageBody=url)
    return

def send_to_slack(url):
    slack_token = os.environ["SLACK_API_TOKEN"]
    sc = SlackClient(slack_token)
    sc.api_call(
      "chat.postMessage",
      channel="#alexa",
      text="open " + url
    )

def get_reputation(intent, session, user_id):
    so = Site(StackOverflow)
    user = so.user(user_id)
    session_attributes = {}
    reprompt_text = None
    should_end_session = True
    speech_output = "You have %d reputation" % (user.reputation)

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))    



def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to StackOverflow. You can ask to search StackOverflow."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Try asking a question to StackOverflow."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Happy coding. Goodbye."
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_search_results_attributes(results):
    res0 = results[0]
    return {"title": res0.title, "id": res0.id, "url": res0.link}

def show_results_in_browser(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "title" in session.get('attributes', {}):
        title = session['attributes']['title']
        url = session['attributes']['url']
        speech_output = "Ok. Coming right up."

        send_to_sqs(url)
        send_to_slack(url)

        # TODO: display the query in the browser
        should_end_session = True
    else:
        speech_output = "I don't know what you want me to display. Try searching for something first."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


def search_so(intent, session):
    session_attributes = {}
    reprompt_text = None
    should_end_session = False
    if 'Query' in intent['slots']:
        query = intent['slots']['Query']['value']
        so = stackexchange.Site(stackexchange.StackOverflow)
        qs = so.search(intitle=query)

        print('I found %d results' % (len(qs)))

        if len(qs) > 0:
            speech_output = "I found something. " + qs[0].title + ".  Would you like me to display it for you?"
            session_attributes = create_search_results_attributes(qs)
        else:
            speech_output = "Sorry. I couldn't find anything matching your query."

        # session_attributes = create_favorite_color_attributes(favorite_color)
    else:
        speech_output = "I'm not sure what your query is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your query is. " \
                        "You can tell me your query by saying, " \
                        "Alexa, ask stack overflow to search java to string."

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))
    
# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "Search":
        return search_so(intent, session)
    if intent_name == "Display":
        return show_results_in_browser(intent, session)
    if intent_name == "Cancel":
        return handle_session_end_request()
    if intent_name == "Reputation":
        return get_reputation(intent, session, 8217);
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] != "amzn1.ask.skill.dc723a59-5691-4ff4-8b2f-9895852a537c"):
    #      raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
