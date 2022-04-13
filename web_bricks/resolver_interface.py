from collections import namedtuple

ResolverInputSet = namedtuple('ResolverInputSet',
                              ['parent', 'driver', 'locator', 'full_locator', 'strategy', 'logger'])
