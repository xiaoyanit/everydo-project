# -*- encoding: UTF-8 -*-

from plone.app.kss.plonekssview import PloneKSSView
from kss.core import force_unicode
from datetime import datetime
from interfaces import ICategoryManager
from copy import copy

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from category import CategorySelectionProvider

from zope.i18nmessageid import MessageFactory
from zope.i18n import translate
_ = MessageFactory('zopen.widgets')

list_template = ZopeTwoPageTemplateFile('list.pt')

class SelectionView(PloneKSSView):

    def _createCategory(self, title):
        # build HTML
        title = title.strip()

        # force_unicode 是从 kss.core 导入
        title = force_unicode(title, 'utf')
        id = self.context.plone_utils.normalizeString(title)
        if id in self.context.objectIds():
            return None

        cm = ICategoryManager(self.context)
        cm.addCategory(id, title)
        return id, title

    def selectionCreateCategory(self, title):
        if title=='': 
            self.getCommandSet('plone').issuePortalMessage(
                    translate(_(u'please enter category title.'), default="Please enter category title.", context=self.request),
                    translate(_(u'Error'), default="Error", context=self.request))
            return self.render()
        id,title = self._createCategory(title)
        # content = u'<option value="%s" selected="selected">%s</option>' % (id, title)

        content = u'<option value="%s" selected="selected">%s</option>' % (id, title)
        content = content.replace('<', '&lt;').replace('>', '&gt;')
        # KSS specific calls
        core = self.getCommandSet('core')
        zopen = self.getCommandSet('zopen')
        zopen.addSelectOption(core.getSelector('samenode', ''), id, title.decode('utf-8'))
        #core.replaceHTML(core.getSelector('samenode', ''), content)
        return self.render()

    def listCreateCategory(self, title, is_template_setting=False):
        cm = ICategoryManager(self.context)
        content_url = cm.getContentInfo()[1]
        content_id = cm.getContentInfo()[0]
        if title=='': 
            self.getCommandSet('plone').issuePortalMessage(
                    translate(_(u'please enter category title.'),
                                default="Please enter category title.", context=self.request),
                    translate(_(u'Error'), default="Error", context=self.request))
            return self.render()
        result = self._createCategory(title)
        if result == None:
            msg = _(u'category ${title} was existed.', 
                      default='Category ${title} was existed.', mapping={u'title' : title})
            self.getCommandSet('plone').issuePortalMessage(
                    translate(msg, context=self.request),
                    translate(_(u'Error'), default="Error", context=self.request))
            return self.render()
        else:
            id,title = result 
        the_macro = list_template.macros['categoryitem']
        content = self.header_macros(the_macro=the_macro,
                        here_url = content_url,
                        cat_del = 1,
                        cat_cur = 0,
                        cat_title = title,
                        cat_id   = id,
                        is_template_setting = is_template_setting=='True')
        # Always encoded as utf-8
        content = force_unicode(content, 'utf')

        core = self.getCommandSet('core')
        core.insertHTMLBefore('#add_new_category_'+content_id, content)

        msg = _(u'category ${title} was added.', default="Category ${title} was added.", mapping={u'title' : title})
        self.getCommandSet('plone').issuePortalMessage(
                translate(msg, context=self.request),
                translate(_(u'Info'), default="Info", context=self.request))
        
        ksszopen=self.getCommandSet('zopen')
        ksszopen.clear(core.getSelector('css', '#new_category_input_'+content_id))

        return self.render()

    def renameCategory(self, id, new_title, is_template_setting=False):
        context = self.context.aq_inner
        new_title = new_title.strip()
        cm = ICategoryManager(self.context)
        cm.renameCategory(id, new_title)
        content_url = cm.getContentInfo()[1]

        core = self.getCommandSet('core')
        selector = core.getParentNodeSelector('.kssDeletionRegion')

        the_macro = list_template.macros['categoryitem']
        content = self.header_macros(the_macro=the_macro,
                here_url = content_url,
                cat_del = cm.categoryDeletable(id),
                cat_cur = 0,
                cat_title = new_title,
                cat_id   = id,
                is_template_setting=is_template_setting=='True')
        content = force_unicode(content, 'utf')
        core.replaceInnerHTML(selector, content)

        # XXX refresh category selection
        #cp = CategorySelectionProvider(context.aq_parent, self.request, None)
        #cp.update()
        #content = cp.render()
        #content = force_unicode(content, 'utf')
        #core.replaceHTML('.categorySelect', content)
        self.getCommandSet('plone').issuePortalMessage(
                translate(_(u'modified success.'), default="Modified success", context=self.request),
                translate(_(u'Info'), default='Info', context=self.request))

        return self.render()
