import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import json

import pytest

from tools import extractJSON


message_list = [os.listdir(os.path.join(os.path.dirname(__file__), 'messages'))]



