from .__object_base__ import *


class transformer_class(transformer_object):
    def process(self, properties):
        cybox_address = address_object.Address()
        cybox_address.address_value = String(properties['ip_addr'])
        cybox_address.category = properties['category']
        cybox_address.condition = properties['condition']
        return cybox_address
        
