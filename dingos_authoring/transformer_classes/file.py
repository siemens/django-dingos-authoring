from .__object_base__ import *


class transformer_class(transformer_object):
    def process(self, properties):
        cybox_file = file_object.File()
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
        
