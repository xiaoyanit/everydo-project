# -*- encoding: utf-8 -*-
import zope.interface
from zope.interface import implements, Interface
from zope.component import getGlobalSiteManager
from zope.component.interfaces import IResource

from plone.memoize import instance
from kss.core import force_unicode
from kss.core.kssview import CommandSet
from kss.core.plugins.core.interfaces import IKSSCoreCommands

class IZopenAddonCommands(Interface):

    def sortTodoItems(ids):
        pass

    def clear():
        pass

class KSSResourceRegistry(object):

    @instance.memoize
    def getKSS(self, filename, request):
        gsm = getGlobalSiteManager()
        for name,factory in gsm.adapters.lookupAll(map(zope.interface.providedBy,(request,)),zope.interface.Interface):
            try:
                adapter = factory(request)
            except TypeError:
                continue
            if IResource.providedBy(adapter) and name==filename:
                source = adapter.GET()
                lines = []
                for line in source.splitlines():
                    line = line.strip()
                    if not line: continue
                    if line.startswith('/*') and line.endswith('*/'): continue
                    lines.append(line)
                return '\n'.join(lines)
        return ''

kss_reg = KSSResourceRegistry()

class ZopenAddonCommands(CommandSet):
    implements(IZopenAddonCommands)

    def sortTodoItems(self):
        command = self.commands.addCommand('sortTodoItems')

    def clear(self, selector):
        """ see interfaces.py """
        command = self.commands.addCommand('clear', selector)

    def setupKss(self, selector):
        """ see interfaces.py """
        command = self.commands.addCommand('setupKss', selector)

    def redirect(self, url, target=''):
        """ see interfaces.py """
        command = self.commands.addCommand('redirect', url=url, target=target)

    def addSelectOption(self, selector, value, title):
        """ see interfaces.py """
        command = self.commands.addCommand('addSelectOption', selector, value=value, title=title)

    def issuePortalMessage(self, message, msgtype='info', position='portal'):
        """ position: portal, contentbar """
        if not message:
            return

        ksscore = self.getCommandSet('core')

        selector = ksscore.getHtmlIdSelector('%s-message' % position)
        msgtype_str = {'info':'信息', 'error':'错误', 'warning':'注意'}.get(msgtype, msgtype)
        html = '<dl class="portalMessage %s"><dt>%s</dt><dd>%s</dd></dl>' % (msgtype, msgtype_str, message)
        html = force_unicode(html, 'utf')
        ksscore.replaceInnerHTML(selector, html)

        ksscore.addClass(ksscore.getSelector('htmlid','kss-spinner'), 'hidden')


    def actionShowHide(self):
        """ ShowHide模式，触发一个action"""
        ksscore = self.getCommandSet('core')
        ksscore.toggleClass(ksscore.getSelector('parentnodecss','.KSSShowHideArea|.KSSShowHideTarget'), 'hidden')
