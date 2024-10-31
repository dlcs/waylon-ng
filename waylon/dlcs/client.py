from dlcs.queue_response import Batch
from requests import post, auth
import settings

JSON_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

def register_collection(image_collection):

    authorisation = auth.HTTPBasicAuth(settings.DLCS_API_KEY, settings.DLCS_API_SECRET)
    url = settings.DLCS_ENTRY + 'customers/' + str(settings.DLCS_CUSTOMER_ID) + '/queue'
    json = image_collection.to_json_dict()
    response = post(url, json=json, auth=authorisation, headers=JSON_HEADERS)
    batch = Batch(response.json())

    return batch
