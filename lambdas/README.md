# AWS Lambdas implementing Alexa skills

In order to turn a lambda into an Alexa skill, you need an intent schema, custom slot definitions (if any), and sample utterances.
These are entered into a form when setting up the skill on the developer site (developer.amazon.com). You can find these for
each skill inside intent_schema.json, custom_slots.txt and sample_utterances.txt, respectively.

## guess-fingers

Performs a "magic trick" by guessing how many fingers you are holding up. This lambda (fingers_lambda.py) has no external dependencies, 
so the code can be copy/pasted into the AWS Lambda form.

## stack-exchange

Searches stack exchange for questions with titles matching your query. For any results found, it can optionally post the top hit
to both SQS and a slack channel named #alexa within WTF. (The latter requires a slack API token to be set in the environment
variable `SLACK_API_TOKEN`). Also tells you reputation points (hard-coded to a specific
user for now). This lambda has dependencies, so you need to install them and then create a zip to upload in order to create
your lambda:

```
cd stack-exchange/
pip install -r requirements.txt -t .
zip -r ../stack-exchange.zip .
```

When you create the lambda, your handler should be called `stack_exchange_lambda.lambda_handler`

## wikipedia

Finds pages in Wikipedia. For any results found, it can optionally post the top hit
to both SQS and a slack channel named #alexa within WTF. (The latter requires a slack API token to be set in the environment
variable `SLACK_API_TOKEN`).

To create your lambda zip file for upload, do the following:

```
cd wikipedia/
pip install -r requirements.txt -t .
zip -r ../wikipedia.zip .
```

# Helper scripts

In order for alexa to pull up web pages for you when using the `stack-exchange` or `wikipedia` skills, you need to have an 
agent running locally. WARNING: is very insecure. The agent will pull specific messages from slack and run them as shell
commands. The agent runs only on Mac. 

Before you can run the slack agent, you need to use a slack API token and set the environment variable `SLACK_API_TOKEN`.
To run it:

```
cd terminal/
pip install -r requirements.txt -t .
python poll_slack.py
```

You can also try running `poll_sqs.py` instead, but it is much slower. It also requires that you set up AWS credentials
under `~/.aws/credentials`.



