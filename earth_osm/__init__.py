import logging
import os

logging.basicConfig(level=logging.INFO)  # Basic configuration
logger = logging.getLogger('eo')

# specify version
fp_version = os.path.join(os.path.dirname(__file__), "VERSION")
with open(fp_version) as f:
    __version__ = f.read().strip()