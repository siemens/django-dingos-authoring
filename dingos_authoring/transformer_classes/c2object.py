from .__object_base__ import *


class transformer_class(transformer_object):
    def process(self, properties):
        import socket
        
        return_objects = []

        for ln in properties['data'].splitlines(False):
            ln = ln.strip()
            is_ip = False
            try:
                socket.inet_aton(ln)
                is_ip=True
            except:
                pass
        
            if is_ip:
                ao = address_object.Address()
                ao.address_value = ln
                ao.is_destination = True
                return_objects.append(ao)
            else:
                do = dns_record_object.DNSRecord()
                do.domain_name = ln
                return_objects.append(do)

        return return_objects
        
