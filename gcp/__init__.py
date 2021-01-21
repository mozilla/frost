import warnings

# Filters out the warning about using end user credentials.
warnings.filterwarnings(
    "ignore", "Your application has authenticated using end user credentials"
)

import logging

# Filters out a warning around a feature we don't use - https://github.com/googleapis/google-api-python-client/issues/299
logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)

# Filters out a warning about not have a default GCP Project ID. Not required for Frost, no need to display.
logging.getLogger("google.auth._default").setLevel(logging.ERROR)
