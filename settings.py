import os

DLCS_PATH = os.environ.get('DLCS_PATH')
DLCS_ENTRY = os.environ.get('DLCS_ENTRY')
DLCS_CUSTOMER_ID = int(os.environ.get('DLCS_CUSTOMER_ID'))
DLCS_API_KEY = os.environ.get('DLCS_API_KEY')
DLCS_API_SECRET = os.environ.get('DLCS_API_SECRET')
CURRENT_SPACE = int(os.environ.get('CURRENT_SPACE'))
MESSAGES_PER_FETCH = int(os.environ.get('MESSAGES_PER_FETCH'))
PENDING_BATCHES_BUCKET = os.environ.get('PENDING_BATCHES_BUCKET')
PENDING_BATCH_TIMEOUT = int(os.environ.get('PENDING_BATCH_TIMEOUT'))
SQS_REGION = os.environ.get('SQS_REGION')
INPUT_QUEUE = os.environ.get('INPUT_QUEUE')
TMP_PATH = os.environ.get('TMP_PATH')
PARSER_PATH = os.environ.get('PARSER_PATH')
MANIFEST_BASE = os.environ.get('MANIFEST_BASE')
PRESLEY_BASE = os.environ.get('PRESLEY_BASE')
PRESLEY_USER = os.environ.get('PRESLEY_USER')
PRESLEY_PASS = os.environ.get('PRESLEY_PASS')
PROXY_CACHE_BUCKET = os.environ.get('PROXY_CACHE_BUCKET')

# module specific
RCVS_RELATIVE = os.environ.get('RCVS_RELATIVE')