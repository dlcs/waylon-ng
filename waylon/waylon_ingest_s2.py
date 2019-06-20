import importlib
import json
import logging
from collections import OrderedDict

import boto3
import requests
from iris.iris_client import IrisListener, IrisClient

import settings
from waylon import aws_ops, util
from waylon.jwt_client import JWTClient


def main():

    parser_module = importlib.import_module('modules.' + settings.PARSER_PATH)
    parser = parser_module.Parser(space=settings.CURRENT_SPACE)
    s3_client = boto3.client('s3')
    jwt = JWTClient(settings.PRESLEY_BASE + "/iiif/login",
                    settings.PRESLEY_USER, settings.PRESLEY_PASS)
    iris = IrisClient()

    def callback(message):
        process_message(message, parser, s3_client, jwt, iris)

    listener = IrisListener()
    listener.run(callback=callback, message_filter="Imagey_Batch_Completed")


def process_message(message, parser, s3_client, jwt, iris):

    logging.debug("Processing message")

    success = message['resolution'] == 'success'
    if success:

        filename = aws_ops.download_file(s3_client, message['bucket'], message['key'])
        work = parser.parse(message['key'], filename)
        manifest = get_manifest(work)

        update_manifest_ids(manifest, work.id)

        canvas_mapping = generate_canvas_map(manifest)

        manifest['metadata'] = work.work_metadata

        decorate_manifest_toc(work, manifest, canvas_mapping)

        decorate_manifest_image_metadata(work, manifest)

        parser.custom_decoration(work, manifest)

        store_manifest(manifest, message['session'], jwt)

        iris.send_iris_message({
            'session': message['session'],
            'message_type': 'Waylon_S2_Complete',
            'work': work.id,
        })

    logging.debug("Message processed")


def store_manifest(manifest, session, jwt):

    delete = {
            "manifest_id": manifest['@id'],
            "cascade": True
        }
    jwt.post(
        url=settings.PRESLEY_BASE + "iiif/customer/manifest/delete",
        data=json.dumps(delete)
    )

    resp = jwt.post(settings.PRESLEY_BASE + "iiif/customer/manifest/add",
                    data=json.dumps(manifest),
                    params={'session': session},
                    headers={'Content-Type': 'application/json'})
    resp.raise_for_status()


def get_manifest(work):

    manifest_uri = settings.DLCS_PATH + 'iiif-resource/' \
        + str(settings.DLCS_CUSTOMER_ID) + '/waylon/' + work.id + '/0'
    response = requests.get(manifest_uri)

    if not response.status_code == 200:
        raise IOError("Could not get manifest to remove existing images")
    result_string = response.text
    manifest = json.loads(result_string, object_pairs_hook=OrderedDict)
    return manifest


def update_manifest_ids(manifest, work_id):

    manifest['@id'] = settings.MANIFEST_BASE + 'iiif/' + work_id + '.manifest'
    manifest['sequences'][0]['@id'] = settings.MANIFEST_BASE + 'iiif/' + work_id + '/sequences/0'
    canvas_index = 0
    for canvas in manifest['sequences'][0]['canvases']:
        canvas_id = settings.MANIFEST_BASE + 'iiif/' + work_id + '/canvas/' + str(canvas_index)
        canvas['@id'] = canvas_id
        for image in canvas['images']:
            image['on'] = canvas_id
        canvas_index += 1


def decorate_manifest_image_metadata(work, manifest):

    image_metadata = work.image_metadata
    canvases = manifest['sequences'][0]['canvases']

    canvas_label_field = None
    flags = work.flags
    if flags:
        canvas_label_field = flags.get('Canvas_Label_Field')

    for image_index_string in image_metadata:
        image_index = int(image_index_string)
        canvases[image_index]['metadata'] = image_metadata[image_index_string]
        if canvas_label_field is None:
            canvases[image_index]['label'] = str(image_index + 1)
        else:
            page = ""
            for image in image_metadata[image_index_string]:
                label = image.get('label')
                if label is not None and label == canvas_label_field:
                    val = image.get('value')
                    if val is not None:
                        page = val
            canvases[image_index]['label'] = page


def decorate_manifest_toc(work, manifest, canvas_mapping):

    structures = []
    toc = work.toc
    if toc is None:
        return
    rng = 0
    for entry in toc.keys():
        structure = {
            '@type': 'sc:Range',
            '@id': settings.MANIFEST_BASE + 'iiif/' + work.id + '/range/range-' + str(rng),
            'label': entry,
            'canvases': [canvas_mapping[e] for e in toc[entry]]
        }
        rng += 1
        structures.append(structure)

    manifest['structures'] = structures


def generate_canvas_map(manifest):

    canvases = manifest['sequences'][0]['canvases']
    mapping = {i: x['@id'] for (i, x) in enumerate(canvases)}
    return mapping


if __name__ == "__main__":

    util.set_logging()
    main()
