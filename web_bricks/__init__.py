from .resolver_interface import ResolverInputSet
from .component import WebBrick
from .resolve_result import ResolveResult
from .resolver import web_resolver
from .utils import checkable, many
from .web_bricks_config import WebBricksConfig

__all__ = (
    'WebBrick', 'WebBricksConfig', 'web_resolver', 'ResolveResult', 'many', 'checkable'
)
__version__ = "0.0.3"
