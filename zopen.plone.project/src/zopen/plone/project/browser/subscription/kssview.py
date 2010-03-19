# -*- encoding: UTF-8 -*-

import zope.component
from plone.app.kss.plonekssview import PloneKSSView
from kss.core import force_unicode
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

# import logging; info = logging.getLogger('zopen.plone.org').info

from zopen.plone.subscription.interfaces import ISubscriptionManager
from zopen.plone.org.interfaces import IOrganizedEmployess
from Products.CMFCore.utils import getToolByName

from zope.i18nmessageid import MessageFactory
from zope.i18n import translate
_ = MessageFactory('zopen.project')

def sendNotification(self, obj):
        sm = ISubscriptionManager(obj)

        portal_url = getToolByName(obj, 'portal_url')
        project = obj.getProject()
        company =project.getCompany()

        subject = '[%s] %s' % (project.Title(), obj.Title())

        mtool = getToolByName(obj, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        fullname = member.getProperty('fullname')
        email = member.getProperty('email')
        body = translate(_(u'body_email', default='${user_name} <${user_email}> invitation you view ${obj_title}. \n\nVisit URL:  ${obj_url} \n \n--\nDO NOT REPLY TO THIS EMAIL.\nTo comment on this content, visit: \n${obj_url}',
            mapping={u'obj_url':obj.absolute_url(),
                     u'user_name':fullname or member.getId(),
                     u'user_email':email,
                     u'obj_title':obj.Title()}),context=self.request)

        sm.sendMail(subject=subject, body=body, includeme=True)

class SubKssView(PloneKSSView):

    column_two = ZopeTwoPageTemplateFile('sub-in.pt')
    edit_sub_page = ZopeTwoPageTemplateFile('edit_sub.pt')

    def subscribeAuthenticatedMember(self):
        sm = ISubscriptionManager(self.context)
        sm.subscribeAuthenticatedMember()

        core = self.getCommandSet("core")
        core.replaceInnerHTML("#subscription", self.column_two())

        return self.render()

    def unsubscribeAuthenticatedMember(self):
        sm = ISubscriptionManager(self.context)
        sm.unsubscribeAuthenticatedMember()

        core = self.getCommandSet("core")
        core.replaceInnerHTML("#subscription", self.column_two())

        return self.render()

    def subscribeNotified(self):
        # use the adapter to configure the subscribers
        obj = self.context.aq_inner
        adapted = ISubscriptionManager(obj)
        form = self.request.form
        if form.has_key('persons'):
            adapted.setSubscribedMembers(form['persons'])

            if form.has_key('notified'):
                sendNotification(self, obj)
        else:
            persons = self.context.getProperty('object_subscribers')
            for person in persons:
                adapted.unsubscribeMember(person)


        ksscore = self.getCommandSet('core')

        #cp_view = zope.component.getMultiAdapter((obj, self.request, self), name='zopen.subscription') 
        #content_html = cp_view.render()
        #print content_html
        
        #ksscore.replaceInnerHTML('dl.GeditNotified', content_html)

        ksscore.replaceHTML("#subscription", self.column_two())
        self.getCommandSet('plone').issuePortalMessage(
                translate(_(u'modified_success', default="Modified success."), context=self.request),
                translate(_(u'Info', default='Info'), context=self.request))
        

        return self.render()


    def editSub(self):

        core = self.getCommandSet("core")
        core.replaceInnerHTML("#sub_m", self.edit_sub_page())

        return self.render()


