
import hashlib
from django.utils import timezone


from dingos.importer import DingoImportCommand

from dingos.models import InfoObject
from .models import AuthoredData

from dingos_authoring.models import FILE_SYSTEM



class DingosAuthoringImportCommand(DingoImportCommand):
    """
    This class serves as basis for import commands that are specified
    in the management/commands directory of a Django app using DINGO
    for imports.

    It basically adds the following command line arguments and associated
    processing to the Dingo.BaseCommand class:

    - `--marking_json` is used to specify a json file that contains
      data for an information object with which all information objects
      generated by the XML import are to be marked. Here is an example
      the contents of such a json file::

           {"Mechanism" : {"Category":"Commandline Import",
                           "User": "DINGO[_username]",
                           "Commandline": {"Command":"DINGO[_command]",
				           "KeywordArguments":"DINGO[_kargs]",
				           "Arguments":"DINGO[_args]"}
	                      },
          "Source" : "DINGO[source]"}

      As becomes apparent above, the JSON may contain placeholders.
      of form 'DINGO[<placeholder_name>]'. Placeholders with names
      that start with a '_' are filled in automatically -- the definition
      for user-defined placeholders is provided with the
      command-line argument --marking-pfill.

    - `--marking-pfill` takes a list of arguments that are processed pairwise:
      the first component of each pair is interpreted as placeholder name,
      the second as value to fill in for that placeholder.

      To fill in the 'source' placeholder in the above example, you
      might call the command line with::

                  --marking-pfill  source "Regular import from Malware Sandbox"

      Be sure to encompass placeholder values in quotation marks
      (If you are using PyCharm as IDE: note that PyCharm messes up quoted
      commandline arguments in its run configuration -- you have to test
      that stuff from a true commandline).
    - `--id-namespace-uri` stores URI for namespace to be used for qualifying
         the identifiers of the information objects.
    """


    custom_options = {'track_created_objects':True}

    def import_postprocessor_handle(self,import_result):

        created_objects_info = import_result.get('created_object_info',None)

        xml = import_result.get('file_content',None)

        if xml and created_objects_info:
            identifier = hashlib.sha256(xml).hexdigest()
            xml_import_obj = AuthoredData.object_create(identifier = identifier,
                                                        name = "Import of XML via commandline",
                                                        status = AuthoredData.IMPORTED,
                                                        kind = AuthoredData.XML,
                                                        data = xml,
                                                        user = None,
                                                        group = None,
                                                        timestamp = timezone.now(),
                                                        storage_location=FILE_SYSTEM)


            # Now call set_name on each object once more;
            # this is required, because object names may depend on
            # names of referenced objects, and they do not always
            # get created in the proper order.

            created_object_ids = [x['pk'] for x in created_objects_info if x['existed'] != 'existed']

            created_objects = list(InfoObject.objects.filter(pk__in=created_object_ids))

            for object in created_objects:
                name = object.set_name()

            xml_import_obj.yielded_iobjects.add(*created_objects)

            try:
                top_level_iobject = InfoObject.objects.get(pk=created_object_ids[-1])
            except:
                top_level_iobject = None

            if top_level_iobject:
                # We need to retrieve the object once more, because
                # if we save now, we are going to overwrite the object
                # that has been written directly after the scheduled
                # import was called.
                # The 'add' call above, on the other hand, was ok,
                # because that does not change the object -- it creates
                # objects in an internal through-model

                xml_import_obj_reloaded = AuthoredData.objects.get(pk=xml_import_obj.pk)

                xml_import_obj_reloaded.top_level_iobject = top_level_iobject

                xml_import_obj_reloaded.save()
