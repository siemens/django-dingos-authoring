from .__object_base__ import *


class transformer_class(transformer_object):
    def process(self, properties):
        return self.create_cybox_uri_object(properties['value'], properties['type_'])
