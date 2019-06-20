import logging
import json
from urllib.parse import quote_plus
import boto3
from iris.iris_client import IrisListener, IrisClient
from waylon import util, aws_ops
import settings


def main():

    s3_client = boto3.client('s3')
    iris = IrisClient()

    def callback(message):
        process_message(message, s3_client, iris)

    listener = IrisListener()
    listener.run(callback=callback, message_filter="Waylon_S1_Complete")


def process_message(message, s3_client, iris):

    logging.debug("Processing message")
    try:

        session = message['session']
        batch_id = message['batch']
        work_id = message['work']
        bucket = message['bucket']
        key = message['key']

        payload = {
            'session': session,
            'work': work_id,
            'bucket': bucket,
            'key': key
        }

        aws_ops.add_key(s3_client, settings.PENDING_BATCHES_BUCKET,
                        quote_plus(batch_id), json.dumps(payload))
        logging.info(f"Added key to pending batches bucket for batch {batch_id}")
        iris.send_iris_message({
            'message_type': 'Pending_Batch_Tracked',
            'session': session,
            'work': work_id,
            'batch': batch_id
        })

    except Exception:
        logging.exception("Error processing message")

    logging.debug("Message processed")


if __name__ == "__main__":

    util.set_logging()
    main()
