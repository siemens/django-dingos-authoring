import cybox.objects, importlib, os
from cybox.common import Hash, String, Time, ToolInformation, ToolInformationList, ObjectProperties, DateTime, StructuredText
import cybox.utils

# Some ugly hack to import all cybox object classes since 'from cybox.objects import *' did not work properly
cybox_objects = [fname[:-3] for fname in os.listdir(cybox.objects.__path__[0]) if fname.endswith(".py") and not fname.startswith("_")]
for co in cybox_objects:
    globals()[co] = importlib.import_module('.'+co, 'cybox.objects')



class transformer_object:
    def __init__(self):
        pass

    def __create_cybox_url_object(self, url):
        if not url:
            return None
        return uri_object.URI(url)

