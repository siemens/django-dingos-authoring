from .__object_base__ import *


class transformer_class(transformer_object):
    def process(self, properties):
        cybox_dns_record = dns_record_object.DNSRecord()
        cybox_dns_record.description = StructuredText(properties['description'])
        cybox_dns_record.domain_name = self.__create_domain_name_object(properties['domain_name'])
        cybox_dns_record.ip_address = address_object.Address(properties['ip_address'])
        return cybox_dns_record
        

    def __create_domain_name_object(self, domain_name):
        if not domain_name:
            return None
        return uri_object.URI(domain_name)
