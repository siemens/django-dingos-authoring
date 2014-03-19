from .__object_base__ import *


class transformer_class(transformer_object):
    def process(self, properties):
        cybox_dns_record = dns_record_object.DNSRecord()
        cybox_dns_record.description = StructuredText(properties['description'])
        cybox_dns_record.domain_name = self.create_cybox_uri_object(properties['domain_name'])
        cybox_dns_record.ip_address = address_object.Address(properties['ip_address'])
        return cybox_dns_record
        
