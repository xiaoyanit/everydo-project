from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore.utils import ContentInit
from config import PROJECTNAME
from permissions import DEFAULT_ADD_CONTENT_PERMISSION, ADD_CONTENT_PERMISSIONS

def initialize(context):
    ##Import Types here to register them
    import content

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)


    ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

    for i in range(0, len(content_types)):
        klassname = content_types[i].__name__
        if not klassname in ADD_CONTENT_PERMISSIONS:
            continue
        context.registerClass(meta_type    = ftis[i]['meta_type'],
                constructors = (constructors[i],),
                permission   = ADD_CONTENT_PERMISSIONS[klassname])

