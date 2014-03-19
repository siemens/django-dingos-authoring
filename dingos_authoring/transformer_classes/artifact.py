from .__object_base__ import *


class transformer_class(transformer_object):
    def process(self, properties):
        return artifact_object.Artifact(properties['data'], properties['artifact_type'])
        
