from .__object_base__ import *


class transformer_class(transformer_object):
    def process(self, properties):
        cybox_port = port_object.Port()
        cybox_port.port_value = PositiveInteger(properties['port_value'])
        cybox_port.layer4_protocol = String(properties['layer4_protocol'])
        return cybox_port
        
