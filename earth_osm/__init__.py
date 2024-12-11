import logging

logging.basicConfig(level=logging.INFO)  # Basic configuration
logger = logging.getLogger('eo')

# specify version 
with open("VERSION") as f:
    __version__ = f.read().strip()