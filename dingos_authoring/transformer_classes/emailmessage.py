from .__object_base__ import *


class transformer_class(transformer_object):
    def process(self, properties):
        cybox_email = email_message_object.EmailMessage()
        if properties['raw_body']:
            cybox_email.raw_body = String(properties['raw_body'])
        if properties['raw_header']:
            cybox_email.raw_header = String(properties['raw_header'])
        cybox_email.header = self.__create_cybox_email_header_part(properties)
        if len(properties['links'])>0:
            url_list, domain_list = self.__create_cybox_email_links(properties['links'])
            if url_list:
                email_links = email_message_object.Links()
                for url in url_list:
                    links.append(email_message_object.LinkReference(url.parent.id_))
                if links:
                    cybox_email.links = links
        return cybox_email

    def __create_cybox_domain_object(self, domain, ip=None):
        new_domain_obj = {'URI': None, 'Whois': None, 'DNSQueryV4': None, 'DNSResultV4': None, 'ipv4': None, 'DNSQueryV6': None, 'DNSResultV6': None, 'ipv6': None}
        domain_name_obj = self.__create_domain_name_object(domain)
        if ip:
            new_domain_obj['ipv4'] = ip
        new_domain_obj['URI'] = domain_name_obj
        return new_domain_obj

    def __reorder_domain_objects(self, domain_obj_map):
        ordered_objs = [domain_obj_map['URI']]
        if domain_obj_map['Whois']:
            ordered_objs.append(domain_obj_map['Whois'])
        if domain_obj_map['DNSQueryV4']:
            ordered_objs.append(domain_obj_map['DNSQueryV4'])
        if domain_obj_map['DNSResultV4']:
            ordered_objs.append(domain_obj_map['DNSResultV4'])
        if domain_obj_map['ipv4']:
            ordered_objs.append(domain_obj_map['ipv4'])
        if domain_obj_map['DNSQueryV6']:
            ordered_objs.append(domain_obj_map['DNSQueryV6'])
        if domain_obj_map['DNSResultV6']:
            ordered_objs.append(domain_obj_map['DNSResultV6'])
        if domain_obj_map['ipv6']:
            ordered_objs.append(domain_obj_map['ipv6'])
        return ordered_objs

    def __create_cybox_email_links(self, links):
        unique_urls = set()
        unique_domains = set()
        for link in links:
            unique_urls.add(link)
            domain = whois.extract_domain(link)
            unique_domains.add(domain)
        domain_map = {}
        domain_list = []
        url_list = []
        for domain in unique_domains:
            domain_obj = self.__create_cybox_domain_object(domain)
            domain_list.extend(self.__reorder_domain_objects(domain_obj))
            domain_map[domain] = domain_obj['URI']
        for url in unique_urls:
            url_obj = self.__create_cybox_url_object(url)
            if not url_obj:
                continue
            domain_obj = domain_map[whois.extract_domain(url)]
            if domain_obj:
                domain_obj.add_related(url_obj, 'Extracted_From', inline=False)
                domain_obj.add_related(url_obj, 'FQDN_Of', inline=False)
                url_obj.add_related(domain_obj, 'Contains', inline=False)
            url_list.append(url_obj)
        return url_list, domain_list

    def __create_cybox_email_header_part(self, properties):
        cybox_email_header = email_message_object.EmailHeader()
        """ recipients """
        recipient_list = email_message_object.EmailRecipients()
        recipient_list.append(address_object.EmailAddress(properties['to']))
        cybox_email_header.to = recipient_list
        """ sender """
        cybox_email_header.from_ = address_object.EmailAddress(properties['from_'])
        """ subject """
        cybox_email_header.subject = String(properties['subject'])
        """ in reply to list """
        cybox_email_header.in_reply_to = String(properties['in_reply_to'])
        """ received date """
        cybox_email_header.date = DateTime(properties['received_date'])
        return cybox_email_header


        
