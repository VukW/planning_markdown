PORT = 8000

OBJECT_TYPES = [{'name': 'my_point',
                 'color': '#00FF00',
                 'basic_type': 'POINT'},
                {'name': 'my_segment',
                 'color': '#FF0000',
                 'basic_type': 'SEGMENT'},
                {'name': 'my_region1',
                 'color': '#0000FF',
                 'basic_type': 'REGION'},
                {'name': 'my_region2',
                 'color': '#00CCCC',
                 'basic_type': 'REGION'}]

# loading local config (if exists)
try:
    from local_config import *
except ImportError:
    pass
