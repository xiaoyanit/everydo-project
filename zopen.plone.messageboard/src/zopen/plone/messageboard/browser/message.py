# -*- coding: UTF-8 -*-

import random
import os.path
from zope import event
from Products.Archetypes.event import ObjectEditedEvent

from zope.lifecycleevent import ObjectModifiedEvent

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName

from zopen.plone.subscription.interfaces import ISubscriptionManager
from zopen.plone.filerepos.interfaces import IFileManager
from zopen.plone.widgets.category.interfaces import ICategoryManager

from zope.i18nmessageid import MessageFactory
from zope.i18n import translate
_ = MessageFactory('zopen.messages')

# import logging; info = logging.getLogger('zopen.plone.messageboard').info

def sendNotification(self, msg):
        sm = ISubscriptionManager(msg)

        portal_url = getToolByName(msg, 'portal_url')
        project = msg.getProject()
        company =project.getCompany()

        # attachments in msg
        attachments_msg = ''
        attachments = msg.getAttachedImagesAndFiles()
        image_urls = [img.absolute_url() for img in attachments[0]]
        file_urls = [file.absolute_url() for file in attachments[1]]
        len_attachments = len(image_urls + file_urls)

        if image_urls or file_urls:
            attachments_msg = translate(_(u'attachment_msg_msg', default='This message contains ${len_attachments} attachment(s)：\n ', mapping={u'len_attachments':len_attachments}), context=self.request)
            for url in (image_urls + file_urls):
                url = url + '\n'
                attachments_msg+=url

        subject = '[%s] %s' % (project.Title(), msg.Title())

        mtool = getToolByName(msg, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        fullname = member.getProperty('fullname')
        email = member.getProperty('email')
        body = translate(_(u'body_email',
                           default='A new message has been posted. DO NOT REPLY TO THIS EMAIL. To comment on this message, visit: \n ${msg_url} \n \n${user_name} <${user_email}> said：\n--------------------------------------------------------------- \n${msg_body} \n${attachments} \n \n--\nDO NOT REPLY TO THIS EMAIL.\nTo comment on this message, visit: \n${msg_url}',
            mapping={u'msg_url':msg.absolute_url(),
                     u'user_name':fullname or member.getId(),
                     u'user_email':email,
                     u'msg_body':msg.getRawText(),
                     u'attachments':attachments_msg}),context=self.request)

        sm.sendMail(subject=subject, body=body, includeme=True)


class AddMessageView(BrowserView):
    """ the add form """

    template = ViewPageTemplateFile('add_message.pt')

    def __call__(self):
        """ submit or show the form """

        form = self.request.form
        # info("%r", form)

        if not form.get('form.submitted',''):
            return self.template()

        title = form.get('title', '')
        text = form.get('text', '')
        private = form.get('private', '')
        category_id = form.get('category', '')
        category = getattr(self.context, category_id)

        subscribers = form.get('persons', [])
        milestone = form.get('milestone', '')
        complete = milestone and form.get('completes_milestone', False)

        ctool = getToolByName(self.context, 'portal_catalog')
        messages = ctool( path='/'.join(self.context.getPhysicalPath()), 
                   portal_type='Message')
        ids = [m.getId for m in messages]

        random_id = str(random.randrange(100000, 999999))
        while random_id in ids:
            random_id = str(random.randrange(100000, 999999))

        category.invokeFactory('Message', random_id)
        msg = getattr(category, random_id)
        msg.setTitle(title)
        msg.setText(text, mimetype=form.get('mimetype', 'text/x-web-intelligent'))

        if private:
            wftool = getToolByName(self.context, 'portal_workflow')
            wftool.doActionFor(msg, 'hide')

        if form.has_key("upload"):
            file_manager = getUtility(IFileManager, 'file_manager')
            filerepos = file_manager.getFilerepos(msg)
            files = []
            for request_file in form["upload"]:
                if not hasattr(request_file, 'file'):
                    continue
                file_cat = getattr(filerepos, request_file.category)
                the_file = file_manager.addFile(file_cat, request_file.file)

                if the_file is not None:
                    files.append(the_file)
                    if private:
                        wftool.doActionFor(the_file, 'hide')
            if files:
                msg.setRelatedItems(files)

        # 订阅
        sm = ISubscriptionManager(msg)
        sm.setSubscribedMembers(subscribers)
        msg.reindexObject()

        event.notify(ObjectModifiedEvent(msg))
    
        sendNotification(self, msg)
        sm.subscribeAuthenticatedMember()

        # 和milestone关联
        if milestone:
            brains = ctool(UID = milestone)
            if brains:
                obj = brains[0].getObject()
                obj.addRelatedItem( msg.UID() )
                obj.indexObject()

                if complete:
                    wftool = getToolByName(self.context, 'portal_workflow')
                    state = wftool.getInfoFor(obj, 'review_state')
                    if state != 'completed':
                        wftool.doActionFor(obj, 'complete')

        return self.request.response.redirect(self.context.absolute_url())

class MessageView(BrowserView):
    """ view the whole conversation """

    def creatorName(self):
        mtool = getToolByName(self.context, 'portal_membership')
        creator = self.context.Creator()
        mi = mtool.getMemberInfo(creator)
        return mi and mi['fullname'] or creator

    def categoryInfo(self):
        category = self.context.aq_inner.aq_parent
        board = category.aq_parent
        return {'url':board.absolute_url() + '?category=' +category.getId(),
                'title':category.Title() or category.getId(),
                'id': category.getId(),
                }

    def review_state(self):
        wftool = getToolByName(self.context, 'portal_workflow')
        state = wftool.getInfoFor(self.context, 'review_state')
        return state

    def messages_url(self):
        return self.context.aq_inner.aq_parent.aq_parent.absolute_url()

    def save_message(self):
        form = self.request.form
        # info("%r" % form)

        msg = self.context.aq_inner

        if form.has_key("title"):
            msg.setTitle(form["title"])
        if form.has_key("body"):
            msg.setText(form["body"], mimetype=form.get('mimetype', 'text/x-web-intelligent' ))
        if form.has_key("category"):
            # context is the message, parent is the category
            if self.context.aq_inner.aq_parent.getId() != form["category"]:
                cat_m = ICategoryManager(msg.aq_parent.aq_parent)
                # info("%r" % self.context)
                # info("%r" % self.context.aq_parent)
                # info("%r" % self.context.aq_inner.aq_parent)
                msg = cat_m.setContentCategory(msg, form["category"])

        if form.has_key("persons"):
            sm = ISubscriptionManager(msg)
            sm.setSubscribedMembers(form["persons"])
            sendNotification(self, msg)
            sm.subscribeAuthenticatedMember()

        wftool = getToolByName(msg, 'portal_workflow')
        review_state = self.review_state()
        private = form.has_key('private')
        if(private and review_state != 'private'): 
            wftool.doActionFor(msg, 'hide')
        elif(review_state == 'private' and not private):
            wftool.doActionFor(msg, 'show')

        comments = msg.contentValues()
        for msg_cmt in [msg] + comments:
            attachments = msg_cmt.getRelatedItems()
            for obj in attachments:
                obj_state = wftool.getInfoFor(obj, 'review_state') 
                if private and obj_state != 'private':
                    wftool.doActionFor(obj, 'hide')
                elif obj_state == 'private' and not private:
                    wftool.doActionFor(obj, 'show')

        if form.has_key("upload"):
            file_manager = getUtility(IFileManager, 'file_manager')
            filerepos = file_manager.getFilerepos(msg)
            files = msg.getRawRelatedItems()
            for request_file in form["upload"]:
                if not hasattr(request_file, 'file'):
                    continue
                file_cat = getattr(filerepos, request_file.category)
                the_file = file_manager.addFile(file_cat, request_file.file)

                if the_file is not None:
                    if private:
                        wftool.doActionFor(the_file, 'hide')
                    files.append(the_file.UID())
            msg.setRelatedItems(files)

        # 和milestone关联
        milestone = form.get('milestone', '')
        milestone_old = msg.getRelatedMilestones()
        milestone_obj = None
        milestone_changed = milestone != (milestone_old and milestone_old[0].UID or '')
        if milestone_changed:
            for brain in milestone_old:
                m = brain.getObject()
                m.removeRelatedItem(msg.UID())
                m.indexObject()

        if milestone:
            ctool = getToolByName(msg, 'portal_catalog')
            brains = ctool(UID = milestone)
            if brains:
                milestone_obj = brains[0].getObject()

            if milestone_changed:
                milestone_obj.addRelatedItem(msg.UID())
                milestone_obj.indexObject()

        if form.get('completes_milestone', '') and (milestone_obj is not None):
            wftool = getToolByName(msg, 'portal_workflow')
            state = wftool.getInfoFor(milestone_obj, 'review_state')
            if state != 'completed':
                wftool.doActionFor(milestone_obj, 'complete')

        msg.reindexObject()

        event.notify(ObjectEditedEvent(msg))
        event.notify(ObjectModifiedEvent(msg))
        self.request.response.redirect(msg.aq_parent.aq_parent.absolute_url())

