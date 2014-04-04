__version__ = '0.0.1'

from mantis_stix_importer.importer import STIX_Import
from mantis_openioc_importer.importer import OpenIOC_Import
import re

DINGOS_AUTHORING_IMPORTER_REGISTRY = ((re.compile("http://stix.mitre.org.*"), STIX_Import),
                                      (re.compile("http://cybox.mitre.org.*"), STIX_Import),
                                      (re.compile("http://schemas.mandiant.com/2010/ioc"), OpenIOC_Import),

)
