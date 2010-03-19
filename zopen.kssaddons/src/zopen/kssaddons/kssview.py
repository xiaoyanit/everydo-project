# -*- encoding:utf-8 -*-

from kss.core.kssview import KSSView as BaseKSSView
from zope.security.proxy import removeSecurityProxy

class KSSView(BaseKSSView):

    def __init__(self, context, request):
        super(KSSView, self).__init__(context, request)
        self.context = removeSecurityProxy( context )
    
    @property
    def ksszopen(self):
        return self.getCommandSet('zopen')

    @property
    def ksscore(self):
        return self.getCommandSet('core')
