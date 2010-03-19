import random
from zope import lifecycleevent, event
from zope.interface import implements
from zope.event import notify

from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.interfaces.IRepository import IRepositoryTool
from zope.component.interfaces import ObjectEvent

from Products.Five import BrowserView

from kss.core import kssaction
from kss.core import force_unicode
from plone.app.kss.plonekssview import PloneKSSView
from plone.app.kss.interfaces import IPortalObject

from zopen.plone.writeboard.interfaces import IWriteboardCreatedEvent
from zopen.plone.subscription.interfaces import ISubscriptionManager

from archetypes.kss.fields import FieldsView 
from Products.Archetypes.event import ObjectEditedEvent
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from htmldiff import htmldiff
import re 

from zope.i18nmessageid import MessageFactory
from zope.i18n import translate
_ = MessageFactory('zopen.writeboard')


rx_chinese=re.compile(u"([\u2e80-\uffff])", re.UNICODE)

import logging; info = logging.getLogger("zopen.plone.writeboard").info

class KssView(PloneKSSView):

    writeboards_template = ZopeTwoPageTemplateFile('writeboards_listing.pt')
    writeboard_template = ZopeTwoPageTemplateFile('writeboard_view.pt')
    version_diff_template = ZopeTwoPageTemplateFile('version_diff.pt')

    @kssaction
    def saveNewVersion(self, fieldname, templateId, macro, comment=''):
        #fv = FieldsView(self.context, self.request)
        #rendered = fv.saveField(fieldname, value, templateId, macro)
 
        instance = self.context.aq_inner
        field = instance.getField(fieldname)
        value = self.request.form
        value, kwargs = field.widget.process_form(instance, field, value)
        error = field.validate(value, instance, {})
        if not error and field.writeable(instance):
            setField = field.getMutator(instance)
            setField(value, **kwargs)
            instance.reindexObject() #XXX: Temp workaround, should be gone in AT 1.5 -
            descriptor = lifecycleevent.Attributes(IPortalObject, fieldname)
            event.notify(ObjectEditedEvent(self.context, descriptor))

            rep_tool = getToolByName(instance, 'portal_repository')
            # 需要回避权限问题
            # rep_tool.save(instance)
            rep_tool._recursiveSave(instance, {},
                            rep_tool._prepareSysMetadata(comment),
                            autoapply=rep_tool.autoapply)

            parent_fieldname = "parent-fieldname-%s" % fieldname

            fv = FieldsView(self.context, self.request)
            content = fv.renderViewField(fieldname, templateId, macro)
            content = content.strip()
            ksscore = self.getCommandSet('core')
            ksscore.replaceInnerHTML(ksscore.getHtmlIdSelector(parent_fieldname),
                    content) 
            revisions = self.macroContent('context/writeboard_view/macros/revisions')
            ksscore.replaceHTML(ksscore.getHtmlIdSelector("compare-revisions"), revisions)
            # rendered = fv.saveField(fieldname, value, templateId, macro)

        else:
            if not error:
                # XXX This should not actually happen...
                error = 'Field is not writeable.'
            # Send back the validation error
            self.getCommandSet('atvalidation').issueFieldError(fieldname, error                                                                             )

        #effects = self.getCommandSet('mess')
        #selector = core.getParentNodeSelector('.kssDeletionRegion')
        #effects.effect(selector, 'fade')
        #return self.render()
    
    @kssaction
    def changePrivacy(self, cur_state):
        if cur_state == 'private':
            transition = 'show'
        else:
            transition = 'hide'

        wftool = getToolByName(self.context, 'portal_workflow')
        obj = self.context
        wftool.doActionFor(obj, transition)
        state = wftool.getInfoFor(obj, 'review_state')

        macro = self.writeboards_template.macros['post']
        content = self.header_macros(the_macro=macro, 
                review_state = state,
                obj = obj)
        content = force_unicode(content, 'utf')

        ksscore = self.getCommandSet('core')
        ksscore.replaceHTML(ksscore.getParentNodeSelector(".kssDeletionRegion"),
                content)


    @kssaction
    def displayVersion(self, version_id):
        # info("%r" % version_id)

        # here get the historical content of a version_id
        instance = self.context.aq_inner
        rep_tool = getToolByName(instance, 'portal_repository')
        vdata = rep_tool.retrieve(instance, version_id)
        content = vdata.object.getText()
        content = force_unicode(content, 'utf')

        ksscore = self.getCommandSet('core')
        ksscore.replaceInnerHTML(
                ksscore.getHtmlIdSelector('body-wrapper'), content) 

    @kssaction
    def displayDiff(self):
        diff = self.request.form
        info("%r" % diff)
        context = self.context.aq_inner

        # here calculate the diff data
        # the_macro = self.version_diff_template.macros['main']
        #content = self.header_macros(the_macro=the_macro, **vars(diff))
        #content = force_unicode(content, 'utf')
        
        versions = []
        for key in diff.keys():
            if key.startswith('version_'):
                versions.append(diff[key])

        versions.sort()
        rep_tool = getToolByName(context, 'portal_repository')
        v1_body = rep_tool.retrieve(context, versions[0]).object.getText().decode('utf-8')
        if versions[1] != 'current':
            v2_body = rep_tool.retrieve(context, versions[1]).object.getText().decode('utf-8')
        else:
            v2_body = context.getText().decode('utf-8')

        # 补充空格让只懂英文的htmldiff可以工作
        v1 = rx_chinese.sub(r'\1\0 ', v1_body)
        v2 = rx_chinese.sub(r'\1\0 ', v2_body)
        #print v1
        #print v2
        content = htmldiff(v1, v2).replace('\0 ' ,'')
        #print content
        #content = htmldiff(v1_body, v2_body)
        content = force_unicode(content, 'utf')

        ksscore = self.getCommandSet('core')
        ksscore.replaceInnerHTML(
                ksscore.getHtmlIdSelector('body-wrapper'), content) 

    @kssaction
    def editProperty(self, title, description, private=False):
        context = self.context.aq_inner

        context.setTitle(title)
        context.setDescription(description)

        wftool = getToolByName(context, 'portal_workflow')
        review_state = wftool.getInfoFor(context, 'review_state')

        if(private != False and review_state != 'private'):
            wftool.doActionFor(context, 'hide')
        elif(review_state == 'private' and private == False):
            wftool.doActionFor(context, 'show')
        context.reindexObject()

        ksscore = self.getCommandSet('core')
        content_title = title.decode('utf-8')
        content_description = description.decode('utf-8')

        ksscore.replaceInnerHTML('.SectionHeader h1', content_title)
        ksscore.replaceInnerHTML('p.documentDiscription', content_description)

        self.getCommandSet('plone').issuePortalMessage(
                translate(_(u'modified_success', default="Modified success."), context=self.request),
                translate(_(u'Info', default='Info'), context=self.request))



    @kssaction
    def delete_writeboard_version(self, version_id):
        rep_tool = getToolByName(self.context, 'portal_repository')

        obj = self.context.aq_inner

        version_id = int(version_id)
        old_version = rep_tool.retrieve(obj, version_id)
        rep_tool.purge(obj, version_id)
        ksscore = self.getCommandSet('core')
        selector = ksscore.getSelector('parentnode', 'div.versionkss')
        ksscore.deleteNode(selector)

    def TimeToSave(self, fieldname):

        instance = self.context.aq_inner
        field = instance.getField(fieldname)
        form = self.request.form
        value, kwargs = field.widget.process_form(instance, field, form)
        error = field.validate(value, instance, {})
        if not error and field.writeable(instance):
            setField = field.getMutator(instance)
            setField(value, **kwargs)

            ksscore = self.getCommandSet('core')
            content = translate(_(u'auto_save', default='Auto Save success.'), context=self.request)
            content = force_unicode(content, 'utf')
            ksscore.replaceInnerHTML('.SectionHeader .TimeToView', content)

        return self.render()

class CreateBoard(BrowserView):

    def createWriteboard(self, title, category, description, text_format='', private=False):
        category_folder = getattr(self.context.aq_inner, category)
        id = str(random.randrange(100000, 999999))
        while id in category_folder.objectIds():
            id = str(random.randrange(100000, 999999))

        category_folder.invokeFactory('Document', id)

        doc = getattr(category_folder, id)
        doc.setTitle(title)
        doc.setDescription(description)
        if text_format:
            doc.setContentType(text_format)
        if private:
            wftool = getToolByName(self.context, 'portal_workflow')
            wftool.doActionFor(doc, 'hide')
        doc.unmarkCreationFlag()
        doc.reindexObject()

        notify(WriteboardCreatedEvent(doc))
        sm = ISubscriptionManager(doc)
        sm.subscribeAuthenticatedMember()

        self.request.response.redirect(doc.absolute_url()+'?edit=true')


class WriteboardCreatedEvent(ObjectEvent):
    """ repository path changed event """

    implements(IWriteboardCreatedEvent)

