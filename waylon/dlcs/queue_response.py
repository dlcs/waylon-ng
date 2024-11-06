from requests import get, auth
import settings

mapping = {
    '@context': 'context',
    '@id': 'id',
    '@type': 'type',
    'errorImages': 'error_images',
    'completedImages': 'completed_images',
}


class Batch:

    @staticmethod
    def get_attribute_name(json_name):
        if json_name in mapping:
            return mapping.get(json_name)
        return json_name

    def __init__(self, batch_data=None, batch_id=None):

        self.count = 0
        self.completed = 0
        self.id = batch_id
        if batch_data is not None:
            self.update_data(batch_data)
        else:
            self.update()

    def update(self):
        url = self.id
        a = auth.HTTPBasicAuth(settings.DLCS_API_KEY, settings.DLCS_API_SECRET)
        response = get(url, auth=a)
        self.update_data(response.json())

    def update_data(self, batch_data):

        for element in batch_data:
            value = batch_data.get(element)
            setattr(self, self.get_attribute_name(element), value)

    def is_completed(self):
        # TODO check for errors count. e.g. errors + completed == count and return number of errors
        return self.count > 0 and self.count == int(self.completed)
