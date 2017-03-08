import boto3
import time
import shlex, subprocess

QUEUE_NAME = "lambda-stack-overflow"
SQS = boto3.resource("sqs")

def main():
    # q = SQS.get_queue_url(QueueName=QUEUE_NAME).get('QueueUrl')
    queue = SQS.get_queue_by_name(QueueName=QUEUE_NAME)


    while(True):
        # Process messages by printing out body and optional author name
        for message in queue.receive_messages():
            # Get the custom author message attribute if it was set
            print(message.body)
            cmd = "open " + message.body
            subprocess.call(cmd, shell=True)
            # author_text = ''
            # if message.message_attributes is not None:
            #     author_name = message.message_attributes.get('Author').get('StringValue')
            #     if author_name:
            #         author_text = ' ({0})'.format(author_name)

            # # Print out the body and author (if set)
            # print('Hello, {0}!{1}'.format(message.body, author_text))

            # Let the queue know that the message is processed
            message.delete()

        time.sleep(1)



if __name__ == '__main__':
    main()