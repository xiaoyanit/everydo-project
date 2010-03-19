from kss.core import force_unicode
from plone.app.kss.plonekssview import PloneKSSView

# patch to support more zope 3 stuff
import five

def macroContent(self, macropath, **kw):
        "Renders a macro and returns its text"

        path = macropath.split('/')
        if len(path) < 2 or path[-2] != 'macros':
            raise RuntimeError, 'Path must end with macros/name_of_macro (%s)' % (repr(macropath), )
        # needs string, do not tolerate unicode (causes but at traverse)
        try:
            the_macro = self.context.unrestrictedTraverse(macropath)
        except AttributeError, IndexError:
            raise RuntimeError, 'Macro not found'
        #
        # put parameters on the request, by saving the original context
        self.request.form, orig_form = kw, self.request.form
        content = self.header_macros(the_macro=the_macro, **kw)
        self.request.form = orig_form
        # Always encoded as utf-8
        content = force_unicode(content, 'utf')
        return content

PloneKSSView.macroContent = macroContent

#########################################
# 不去检查是否和上级文件夹对象重名
# 因为上级的site会成千上万，这样去检查，基本是死路一条了
# 
# XXX
# 不知道其他地方还是否有类似的问题，最佳的方法是，对BetreeFolder做一个处理，禁止获取
#########################################

from Products.CMFCore.PortalFolder import PortalFolderBase
from Products.CMFCore.exceptions import BadRequest

def _checkId(self, id, allow_dup=0):
        PortalFolderBase.inheritedAttribute('_checkId')(self, id, allow_dup)

        if allow_dup:
            return

        # FIXME: needed to allow index_html for join code
        if id == 'index_html':
            return

        # Another exception: Must allow "syndication_information" to enable
        # Syndication...
        if id == 'syndication_information':
            return

        # IDs starting with '@@' are reserved for views.
        if id[:2] == '@@':
            raise BadRequest('The id "%s" is invalid because it begins with '
                             '"@@".' % id)

PortalFolderBase._checkId = _checkId

#
# 支持相对路径的catalog

from Products.Archetypes.CatalogMultiplex import CatalogMultiplex

def unindexObject(self):
    """ patched by zopen.plone.basecamp """
    catalogs = self.getCatalogs()
    url0 = '/'.join( self.getPhysicalPath() )
    for c in catalogs:
        # 支持
        url = url0[c._getPortalPathLen():]
        if c._catalog.uids.get(url, None) is not None:
            c.uncatalog_object(url)

# hack only when in zopen's internal CMFPlone version
from Products.CMFPlone.CatalogTool import CatalogTool
if hasattr(CatalogTool, '_getPortalPathLen'):
    CatalogMultiplex.unindexObject = unindexObject

from Products.CMFDefault import utils
import re
utils._DOMAIN_RE = re.compile(r'[^@]{1,64}@[A-Za-z0-9-]*'
                                r'(\.[A-Za-z0-9-][A-Za-z0-9-]*)+$')

# 讨论项采用intelligent text
from Products.CMFDefault.DiscussionItem import DiscussionItem
from plone.intelligenttext.transforms import convertWebIntelligentPlainTextToHtml

def CookedBody(self, stx_level=None, setlevel=0):
    return convertWebIntelligentPlainTextToHtml(self.text)

DiscussionItem.CookedBody = CookedBody

# 改为GBK方式发送邮件
from Products.SecureMailHost.SecureMailHost import SecureMailHost
from types import StringType

SecureMailHost.orig_secureSend = SecureMailHost.secureSend

def secureSend(self, message, mto, mfrom, subject='[No Subject]',
            mcc=None, mbcc=None, subtype='plain',
            charset='us-ascii', debug=False, **kwargs):

    mfrom = '易度EveryDo.com <no-reply@everydo.com>'
    if charset.lower() in ('utf8', 'utf-8'):
        message = message.decode('utf8').encode('gb18030', 'replace')

        if type(mto) == StringType:
            mto = (mto,)
        mto = [to.decode('utf8').encode('gb18030', 'replace') for to in mto]
        mfrom = mfrom.decode('utf8').encode('gb18030', 'replace')
        subject = subject.decode('utf8').encode('gb18030', 'replace')
        charset = 'gbk'

    return self.orig_secureSend(message, mto, mfrom,subject, mcc, mbcc, subtype, charset, debug, **kwargs)

SecureMailHost.secureSend = secureSend
