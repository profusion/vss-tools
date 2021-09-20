import os
import re
import pkg_resources

NON_ALPHANUMERIC_WORD = re.compile('[^A-Za-z0-9]+')
CONFIG_PATH = pkg_resources.resource_filename('vspec', 'config.yaml')

