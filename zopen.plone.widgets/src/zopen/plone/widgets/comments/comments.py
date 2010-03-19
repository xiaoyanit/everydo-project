from zope.interface import Interface
from zope.interface import implements

from zope.component import getUtility
from zope.component import adapts

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zopen.plone.subscription.interfaces import ISubscriptionManager
from zope.publisher.interfaces.browser import IBrowserView

from zope.contentprovider.interfaces import IContentProvider

from Acquisition import Explicit

from plone.app.kss.plonekssview import PloneKSSView
from kss.core import force_unicode

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from interfaces import ICommentsManager

from zope.i18nmessageid import MessageFactory
from zope.i18n import translate
_ = MessageFactory('zopen.widgets')

comments_template = ViewPageTemplateFile('comments.pt')

class CommentsListProvider(Explicit):
    implements(IContentProvider)
    adapts(Interface, IDefaultBrowserLayer, IBrowserView)

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.view = view
        self.context = context
        self.request = request

    # From IContentProvider
    def update(self):
        cm = ICommentsManager(self.context)
        self.comments = cm.getComments()
        self.attachable = cm.attachable()
        self.count = len(self.comments)

        mtool = getToolByName(self.context, 'portal_membership')
        username = mtool.getAuthenticatedMember().getUserName()
        mi = mtool.getMemberInfo(username)
        self.myname = mi and mi['fullname'] or username

        self.canPost = mtool.checkPermission('Reply to item', self.context)

    render = comments_template


class AddCommentView(PloneKSSView):

    def attachable(self):
        cm = ICommentsManager(self.context)
        return cm.attachable()

    def _addComment(self, text, attaches=[]):
        cm = ICommentsManager(self.context)
        comment = cm.addComment(text, attaches)

        # send notifications
        msg = self.context.aq_inner
        type_name = msg.portal_type
        sm = ISubscriptionManager(msg)

        portal_url = getToolByName(msg, 'portal_url')

        project = msg.getProject()
        company = project.getCompany()

        # attachments in msg
        attachments_msg = ''
        attachments = self.attachable() and comment.getCommentAttaches() or [(), ()]
        image_urls = [img.absolute_url() for img in attachments[0]]
        file_urls = [file.absolute_url() for file in attachments[1]]
        len_attachments = len(image_urls + file_urls)

        if image_urls or file_urls:
            attachments_msg = translate(_(u'attachments_msg',
                                        default='This comment contains ${len_attachments} attachment(s): \n ',
                                        mapping={u'len_attachments':len_attachments}),
                                        context=self.request) 
            for url in (image_urls + file_urls):
                url = url + '/@@file_view' + '\n'
                attachments_msg+=url

        subject = '[%s] %s' % (project.Title(), comment.Title())

        mtool = getToolByName(msg, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        fullname = member.getProperty('fullname')
        email = member.getProperty('email')

        if type_name in ['Image', 'File']:
            bc_url = '%s/@@file_view' % msg.absolute_url()
        else:
            bc_url = msg.absolute_url()


        body = translate(_(u'mail_body',
                        default='${project_name} of the ${company_name} have a new comment posted. DO NOT REPLY TO THIS EMAIL. To comment on this message, visit:\n${msg_url}\n\n${user_name} <${user_email}> said:\n--------------------------------------------------------------------------\n${msg_body}\n\n${attachments}\n\n--\nDO NOT REPLY TO THIS EMAIL.\nTo comment on this message, visit:\n${msg_url}', 
                        mapping={u'company_name':company.Title(),
                               u'project_name':project.Title(),
                               u'msg_url':bc_url,
                               u'user_name':fullname or member.getId(),
                               u'user_email':email,
                               u'msg_body':text,
                               u'attachments':attachments_msg}),
                        context=self.request)
        sm.sendMail(subject=subject, body=body)
        sm.subscribeAuthenticatedMember()
        return comment


    def addComment(self, text):
        core = self.getCommandSet('core')
        core.toggleClass('.waitIndicator', 'hideme')
        if not text.strip():
            return self.render()

        comment = self._addComment(text)
        the_macro = comments_template.macros['post']
        content = self.header_macros(the_macro=the_macro, comment=comment)
        # Always encoded as utf-8
        content = force_unicode(content, 'utf')

        core.insertHTMLBefore("#your_comment", content)
        ksszopen=self.getCommandSet('zopen')
        ksszopen.clear('#commentBody')

        cm = ICommentsManager(self.context)
        count = str(len(cm.getComments()))
        core.replaceInnerHTML('#comments_count span', count)

        return self.render()

    def submitComment(self):
        text = self.request.get('text', '')
        attaches = self.request.get('upload', [])
        
        self._addComment(text, attaches)
        return self.request.response.redirect(self.context.absolute_url())


