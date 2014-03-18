#!/usr/bin/python2.7

import sys, datetime 
import json, whois, pytz
import importlib

from cybox.core import Observable, Observables
from cybox.common import Hash, String, Time, ToolInformation, ToolInformationList, ObjectProperties, DateTime, StructuredText
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


    def iterate_observables(self, observables):
        cybox_observable_dict = {}
        """ create observables """
        for obs in observables:
            object_type = obs['observable_properties']['object_type']

            try:
                im = importlib.import_module('dingos_authoring.transformer_classes.' + object_type.lower())
                cls = im.transformer_class()
                cybox_obs = cls.process(obs['observable_properties'])
            except Exception as e:
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
        return stix_package.to_xml(ns_dict={'http://data-marking.mitre.org/Marking-1': 'stixMarking'})
        #print stix_package.to_dict()

    def run(self):
        observable_list = self.iterate_observables(self.jsn['observables'])
        indicator_list, observable_list = self.iterate_indicators(self.jsn['indicators'], observable_list)
        return self.__create_stix_package(self.jsn['stix_header'], indicator_list, Observables(observable_list))



if __name__ == '__main__':
    fn = sys.argv[1]
    fp = open(fn)
    jsn = json.load(fp)
    fp.close()

    t = stixTransformer(jsn)
    print t.run()
