from base import LoaderRegistry
from ipko import IPKOLoader

registry = LoaderRegistry()
registry.register( 'ipk', IPKOLoader )
