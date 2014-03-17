#!/usr/bin/python2.7

import sys
import json
import importlib
import whois
import datetime
import pytz

from cybox.common import Hash, String, Time, ToolInformation, ToolInformationList, ObjectProperties, DateTime, StructuredText
from cybox.objects.file_object import File
from cybox.objects.address_object import Address, EmailAddress
from cybox.objects.dns_record_object import DNSRecord
from cybox.objects.email_message_object import EmailMessage, EmailHeader, EmailRecipients, LinkReference, Links
from cybox.objects.uri_object import URI
from cybox.core import Observable, Observables
import cybox.utils

from stix.indicator import Indicator
from stix.core import STIXPackage, STIXHeader
from stix.common import InformationSource, Confidence
from stix.common.handling import Handling
#from stix.bindings.data_marking import MarkingSpecificationType, MarkingStructureType, MarkingType
from stix.extensions.marking.tlp import TLPMarkingStructure
from stix.data_marking import Marking, MarkingSpecification
from stix.bindings.extensions.marking.tlp import TLPMarkingStructureType
import stix.utils

class stixTransformer:
    def __init__(self, jsn):
        NS = cybox.utils.Namespace("cert.siemens.com", "siemens_cert")
        cybox.utils.set_id_namespace(NS)
        stix.utils.set_id_namespace({"cert.siemens.com": "siemens_cert"})
        self.jsn = jsn

    def __create_cybox_file_object(self, properties):
        cybox_file = File()
        cybox_file.file_name = String(properties['file_name'])
        if str(properties['file_name']).count('.')>0:
            file_extension = properties['file_name'].rsplit('.')[-1]
        else:
            file_extension = "None"
        cybox_file.file_extension = String(file_extension)
        if properties['file_size'] != '':
            cybox_file.size_in_bytes = int(properties['file_size'])
        if properties['md5'] != '':
            cybox_file.add_hash(Hash(properties['md5'], type_="MD5", exact=True))
        if properties['sha1'] != '':
            cybox_file.add_hash(Hash(properties['sha1'], type_="SHA1", exact=True))
        if properties['sha256'] != '':
            cybox_file.add_hash(Hash(properties['sha256'], type_="SHA256", exact=True))
        return cybox_file

    def __create_cybox_address_object(self, properties):
        cybox_address = Address()
        cybox_address.address_value = String(properties['ip_addr'])
        cybox_address.category = properties['category']
        cybox_address.condition = properties['condition']
        return cybox_address

    def __create_cybox_dns_record_object(self, properties):
        cybox_dns_record = DNSRecord()
        cybox_dns_record.description = StructuredText(properties['description'])
        cybox_dns_record.domain_name = self.__create_domain_name_object(properties['domain_name'])
        cybox_dns_record.ip_address = Address(properties['ip_address'])
        return cybox_dns_record

    def __create_domain_name_object(self, domain_name):
        if not domain_name:
            return None
        return URI(domain_name)

    def __create_cybox_url_object(self, url):
        if not url:
            return None
        return URI(url)

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
        cybox_email_header = EmailHeader()
        """ recipients """
        recipient_list = EmailRecipients()
        recipient_list.append(EmailAddress(properties['to']))
        cybox_email_header.to = recipient_list
        """ sender """
        cybox_email_header.from_ = EmailAddress(properties['from_'])
        """ subject """
        cybox_email_header.subject = String(properties['subject'])
        """ in reply to list """
        cybox_email_header.in_reply_to = String(properties['in_reply_to'])
        """ received date """
        cybox_email_header.date = DateTime(properties['received_date'])
        return cybox_email_header

    def __create_cybox_email_message_object(self, properties):
        cybox_email = EmailMessage()
        if properties['raw_body']:
            cybox_email.raw_body = String(properties['raw_body'])
        if properties['raw_header']:
            cybox_email.raw_header = String(properties['raw_header'])
        cybox_email.header = self.__create_cybox_email_header_part(properties)
        if len(properties['links'])>0:
            url_list, domain_list = self.__create_cybox_email_links(properties['links'])
            if url_list:
                email_links = Links()
                for url in url_list:
                    links.append(LinkReference(url.parent.id_))
                if links:
                    cybox_email.links = links
        return cybox_email

    def iterate_observables(self, observables):
        cybox_observable_dict = {}
        """ create observables """
        for obs in observables:
            object_type = obs['observable_properties']['object_type']
            if object_type == 'File':
                cybox_obs = self.__create_cybox_file_object(obs['observable_properties'])
            elif object_type == 'Address':
                cybox_obs = self.__create_cybox_address_object(obs['observable_properties'])
            elif object_type == 'DNSRecord':
                cybox_obs = self.__create_cybox_dns_record_object(obs['observable_properties'])
            elif object_type == 'EmailMessage':
                cybox_obs = self.__create_cybox_email_message_object(obs['observable_properties'])
            else:
                print "Unkown Type: %s" % (object_type)
                continue
            cybox_observable_dict[obs['observable_id']] = cybox_obs
        """ create relations """
        for obs in observables:
            try:
                current_object = cybox_observable_dict[obs['observable_id']]
            except KeyError:
                continue
            relations = obs['related_observables']
            for rel in relations:
                try:
                    related_object = cybox_observable_dict[rel]
                    current_object.add_related(related_object, relations[rel], inline=False)
                except KeyError:
                    continue
            cybox_observable_dict[obs['observable_id']] = current_object
        cybox_observables = []
        for obs_id in cybox_observable_dict:
            cybox_observables.append(Observable(cybox_observable_dict[obs_id], obs_id))
        return cybox_observables

    def __create_stix_indicator(self, indicator):
        stix_indicator = Indicator(indicator['indicator_id'])
        stix_indicator.title = String(indicator['indicator_title'])
        stix_indicator.description = String(indicator['indicator_description'])
        stix_indicator.confidence = Confidence(indicator['indicator_confidence'])
        stix_indicator.indicator_types = String(indicator['indicator_type'])
        return stix_indicator, indicator['related_observables']

    def iterate_indicators(self, indicators, observable_list):
        stix_indicators = []
        to_remove = []
        for indicator in indicators:
            stix_indicator, related_observables = self.__create_stix_indicator(indicator)
            for observable in observable_list:
                if observable.id_ in related_observables:
                    stix_indicator.add_observable(observable)
                    to_remove.append(observable)
            stix_indicators.append(stix_indicator)
        """ remove all observables that are assigned to an indicator """
        for observable in to_remove:
            observable_list.remove(observable)
        return stix_indicators, observable_list

    def __create_stix_package(self, stix_props, indicators, observables):
        stix_id_generator = stix.utils.IDGenerator(namespace={"cert.siemens.com": "siemens_cert"})
        stix_id = stix_id_generator.create_id()
        #spec = MarkingSpecificationType(idref=stix_id)
        spec = MarkingSpecification()
        spec.idref = stix_id
        #spec.set_Controlled_Structure("//node()")
        spec.controlled_structure = "//node()"
        #tlpmark = TLPMarkingStructureType()
        #tlpmark.set_color(stix_props['stix_header_tlp'])
        tlpmark = TLPMarkingStructure()
        tlpmark.color = stix_props['stix_header_tlp']
        #spec.set_Marking_Structure([tlpmark])
        spec.marking_structure = [tlpmark]
        stix_package = STIXPackage(indicators=indicators, observables=observables, id_=stix_id)
        stix_header = STIXHeader()
        stix_header.title = stix_props['stix_header_title']
        stix_header.description = stix_props['stix_header_description']
        stix_header.handling = Marking([spec])
        stix_information_source = InformationSource()
        stix_information_source.time = Time(produced_time=datetime.datetime.now(pytz.timezone('Europe/Berlin')).isoformat())
        stix_information_source.tools = ToolInformationList([ToolInformation(tool_name="GUI", tool_vendor="Siemens CERT")])
        stix_header.information_source = stix_information_source
        stix_package.stix_header = stix_header
        #print stix_package.to_xml(ns_dict={'http://data-marking.mitre.org/Marking-1': 'stixMarking'})
        #print stix_package.to_dict()

    def run(self):
        observable_list = self.iterate_observables(self.jsn['observables'])
        indicator_list, observable_list = self.iterate_indicators(self.jsn['indicators'], observable_list)
        self.__create_stix_package(self.jsn['stix_header'], indicator_list, Observables(observable_list))

if __name__ == '__main__':
    fn = sys.argv[1]
    fp = open(fn)
    jsn = json.load(fp)
    fp.close()

    t = stixTransformer(jsn)
    t.run()
