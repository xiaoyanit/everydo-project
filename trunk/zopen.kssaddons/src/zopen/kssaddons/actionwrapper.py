# -*- encoding:utf-8 -*-
from kss.core import kssaction

class kssaction(kssaction):

    def apply(self, obj, *arg, **kw):
        kss_files = obj.request.get('files', None)
        if kss_files: 
            ksszopen = obj.getCommandSet('zopen')
            ksszopen.loadKss(kss_files)
        return super(kssaction, self).apply(obj, *arg, **kw)
