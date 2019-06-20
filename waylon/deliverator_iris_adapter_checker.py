import logging
import json
import datetime
from urllib.parse import unquote_plus
import dlcs
import boto3
from dateutil.tz import tzutc
from iris.iris_client import IrisClient
from waylon import util, aws_ops
import settings


def main():

    s3_client = boto3.client('s3')
    iris = IrisClient()

    for batch_info in get_batches_info(s3_client):
        check_batch(s3_client, iris, batch_info)

    logging.debug("All batches checked")


def check_batch(s3_client, iris, batch_info):

    logging.info(f"Checking batch {batch_info['batch']}")
    batch = dlcs.Batch(batch_id=batch_info['batch'])

    if batch.completed + batch.errors == batch.count:

        iris.send_iris_message({
            'message_type': 'Imagey_Batch_Completed',
            'resolution': 'success' if batch.errors == 0 else 'failure',
            'batch': batch_info['batch'],
            'session': batch_info['session'],
            'work': batch_info['work'],
            'succeeded': batch.completed,
            'failed': batch.errors,
            'bucket': batch_info['original_bucket'],
            'key': batch_info['original_key']
        })

        aws_ops.delete_key(s3_client, settings.PENDING_BATCHES_BUCKET,
                           batch_info['batch_key'])
        logging.debug(f"Batch complete for {batch_info['batch']}")

    elif batch_info['timestamp'] + datetime.timedelta(0,
                                                      settings.PENDING_BATCH_TIMEOUT * 60) \
            < datetime.datetime.utcnow().replace(tzinfo=tzutc()):

        iris.send_iris_message({
            'message_type': 'Imagey_Batch_Timeout',
            'batch': batch_info['batch'],
            'session': batch_info['session'],
            'work': batch_info['work'],
            'bucket': batch_info['original_bucket'],
            'key': batch_info['original_key']
        })

        aws_ops.delete_key(s3_client, settings.PENDING_BATCHES_BUCKET,
                           batch_info['batch_key'])
        logging.debug(f"Batch timed out for {batch_info['batch']}")

    else:
        logging.debug(f"Batch still in progress for {batch_info['batch']}")


def get_batches_info(s3_client):

    infos = []
    keys = aws_ops.get_bucket_keys(s3_client, settings.PENDING_BATCHES_BUCKET)
    if keys:
        for (key, timestamp) in keys:
            key_contents = aws_ops.get_key(s3_client,
                                           settings.PENDING_BATCHES_BUCKET, key)
            key_data = json.loads(key_contents)
            info = {
                'batch': unquote_plus(key),
                'batch_key': key,
                'session': key_data['session'],
                'work': key_data['work'],
                'timestamp': timestamp,
                'original_bucket': key_data['bucket'],
                'original_key': key_data['key']
            }
            infos.append(info)
    return infos


if __name__ == "__main__":

    util.set_logging()
    main()
