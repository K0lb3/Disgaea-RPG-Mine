from .api import base_api, asset_api

import os
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
RES = os.path.join(ROOT, "res")