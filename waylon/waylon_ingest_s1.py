import logging
import os
import json
import importlib
from collections import OrderedDict
import boto3
from requests import post, get, auth
import dlcs
import dlcs.image_collection
from iris.iris_client import IrisClient, IrisListener
import settings
from waylon import aws_ops, util


def main():

    parser_module = importlib.import_module('modules.' + settings.PARSER_PATH)
    parser = parser_module.Parser(space=settings.CURRENT_SPACE)
    s3_client = boto3.client('s3')
    iris = IrisClient()

    def callback(message):
        process_message(message, parser, s3_client, iris)

    listener = IrisListener()
    listener.run(callback=callback, message_filter="S3_Key_Added")


def process_message(message, parser, s3_client, iris):

    logging.debug("Processing message")
    filename = None
    try:

        session = message['session']

        # download the new file to a temporary location
        filename = aws_ops.download_file(s3_client, message['bucket'], message['key'])

        # use the configured parser to extract metadata and ImageCollections for DLCS registration
        work = parser.parse(message['key'], filename)

        # process parse results
        process_work(work, message['bucket'], message['key'], session, iris)

    finally:

        # delete temporary file
        if filename:
            os.remove(filename)

    logging.debug("Message processed")


def process_work(work, bucket, key, session, iris):

    remove_existing_images(work)
    batch = register_work_imagecollection(work)
    iris.send_iris_message({
        'session': session,
        'message_type': 'Waylon_S1_Complete',
        'batch': batch.id,
        'work': work.id,
        'bucket': bucket,
        'key': key
    })


def remove_existing_images(work):

    manifest_url = settings.DLCS_PATH + 'raw-resource/' \
        + str(settings.DLCS_CUSTOMER_ID) + '/waylon/' + work.id + '/0'
    response = get(manifest_url)

    if not response.status_code == 200:
        raise RuntimeError(f"Could not get manifest to remove existing images, "
                           f"status code: {response.status_code}")

    result_string = response.text
    result = json.loads(result_string, object_pairs_hook=OrderedDict)
    images = []
    for image_id in result:
        images.append(dlcs.image_collection.Image(id=str(image_id)))
    image_collection = dlcs.image_collection.ImageCollection(images)
    collection_json = json.dumps(image_collection.to_json_dict())
    authorisation = auth.HTTPBasicAuth(settings.DLCS_API_KEY, settings.DLCS_API_SECRET)
    delete_response = post(
        settings.DLCS_ENTRY + 'customers/' + str(settings.DLCS_CUSTOMER_ID) +
        '/deleteImages', data=collection_json, auth=authorisation
    )
    if not delete_response.status_code == 200:
        raise RuntimeError(f"Could not remove existing images, status code: {response.status_code}")


def register_work_imagecollection(work):

    return dlcs.client.register_collection(work.image_collection)


def batch_completed(batch_id):

    batch = dlcs.Batch(batch_id=batch_id)
    return batch.is_completed()


if __name__ == "__main__":

    util.set_logging()
    main()
