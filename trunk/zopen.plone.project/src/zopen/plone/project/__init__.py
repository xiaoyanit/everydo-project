from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore.utils import ContentInit
from config import PROJECTNAME
from permissions import AddProject

def initialize(context):
    ##Import Types here to register them
    import content

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = AddProject,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)


