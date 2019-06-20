import logging
import os
import sys
from iris.iris_client import IrisClient
from waylon import aws_ops, util
import settings


def main():

    input_queue = aws_ops.get_input_queue()
    if input_queue is None:
        logging.error("Could not obtain input queue")

    messages_per_fetch = settings.MESSAGES_PER_FETCH
    iris = IrisClient()

    while True:
        if os.path.exists('/tmp/s3-notification-stop.txt'):
            sys.exit()
        messages = input_queue.receive_messages(
            MaxNumberOfMessages=messages_per_fetch,
            VisibilityTimeout=120,
            WaitTimeSeconds=20
        )

        if messages:
            for message in messages:
                try:
                    process_message(iris, message)
                except Exception:
                    logging.exception("Error processing message")
                message.delete()


def process_message(iris, message):

    bucket, key = aws_ops.get_file_details_from_message(message)
    session = iris.get_new_session_id()
    logging.debug(f">>>Session {session} created for {key}")
    iris.send_iris_message({
        'message_type': 'S3_Key_Added',
        'session': session,
        'bucket': bucket,
        'key': key
    })


if __name__ == "__main__":

    util.set_logging()
    main()
