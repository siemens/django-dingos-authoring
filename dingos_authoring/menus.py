from menu import Menu, MenuItem
from django.core.urlresolvers import reverse

Menu.add_item( "mantis_main",
               MenuItem("Authoring", "",
                        weight = 10,
                        children = (
                            MenuItem("Existing Reports", "%s?&o=-timestamp" % reverse("url.dingos_authoring.index"), ),
                            MenuItem("My Imports", "%s?&o=-timestamp" % reverse("url.dingos_authoring.imports"), ),
                        ),
                        check = lambda request: request.user.is_authenticated()
                    )
)
