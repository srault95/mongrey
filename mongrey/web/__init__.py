__import__('pkg_resources').declare_namespace(__name__)

from .wsgi import create_app
from .manager import main