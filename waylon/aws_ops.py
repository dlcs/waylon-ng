import json
import uuid
import boto3
import settings


def download_file(s3_client, bucket, key):

    tmp_path = settings.TMP_PATH
    if not tmp_path.endswith('/'):
        tmp_path += '/'
    filename = tmp_path + 'waylon_' + str(uuid.uuid4())
    s3_client.download_file(bucket, key, filename)
    return filename


def add_key(s3_client, bucket, key, data):

    s3_client.put_object(Bucket=bucket, Key=key, Body=data)


def get_key(s3_client, bucket, key):

    response = s3_client.get_object(Bucket=bucket, Key=key)
    return response.get("Body").read().decode()


def delete_key(s3_client, bucket, key):

    s3_client.delete_object(Bucket=bucket, Key=key)


def get_bucket_keys(s3_client, bucket):

    response = s3_client.list_objects(Bucket=bucket)
    if 'Contents' in response:
        return [(key['Key'], key['LastModified']) for key in response['Contents']]
    return None


def get_file_details_from_message(message_body):

    bucket_name, key = None, None
    message = json.loads(message_body.body)
    records = message.get('Records')
    if records:
        s3_records = records[0].get('s3')
        if s3_records is not None:
            bucket = s3_records.get('bucket')
            if bucket is not None:
                bucket_name = bucket.get('name')
            s3_object = s3_records.get('object')
            if s3_object is not None:
                key = s3_object.get('key')
    return bucket_name, key


def get_input_queue():

    sqs_client = boto3.resource('sqs', settings.SQS_REGION)
    queue = sqs_client.get_queue_by_name(QueueName=settings.INPUT_QUEUE)
    return queue
