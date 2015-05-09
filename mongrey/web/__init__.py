try:
    __import__('pkg_resources').declare_namespace(__name__)
except:
    pass

from .wsgi import create_app
from .manager import main