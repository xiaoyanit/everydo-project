from wicked.interfaces import IScope, IAmWickedField, IAmWicked
from zope.component import adapter
from zope.component import provideAdapter
from zope.interface import implementer
from zope.interface import alsoProvides, noLongerProvides

from Products.ATContentTypes.atct import ATDocument

class IScopedField(IAmWickedField):
    """ scope marker """

@implementer(IScope)
@adapter(IScopedField, IAmWicked)
def wicked_scope(field, context):
    scope_obj = context.aq_inner.aq_parent
    path = '/'.join(scope_obj.getPhysicalPath())
    return path

alsoProvides(ATDocument.schema['text'], IScopedField)
provideAdapter(wicked_scope)
