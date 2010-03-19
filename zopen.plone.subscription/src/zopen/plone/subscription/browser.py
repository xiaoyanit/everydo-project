import random
from DateTime import DateTime
from zope import lifecycleevent, event
from zope.component import getUtility

from interfaces import ISubscriptionManager
from Products.CMFCore.utils import getToolByName

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from utils import parseTicket, generateTicket

bodys = """您好，有人以您的邮件地址在易度网站(http://everydo.com)上申请订阅了易度公告。

点击下面的链接确认：

%s

注：易度公告仅提供易度的最新特性和新闻，不会频繁发送，请放心订阅。
"""

bodyu = """您好，有人以您的邮件地址在易度网站(http://everydo.com)上申请退订易度公告。

点击下面的链接确认：

%s

注：易度公告仅提供易度的最新特性和新闻，不会频繁发送，请放心订阅。
"""

class SubManager(BrowserView):

    sub_template = ZopeTwoPageTemplateFile('subscription.pt')

    def subconfirm(self, id):
        context = self.context.aq_inner
        email, operation = parseTicket(id)

        subm = ISubscriptionManager(context)
        # subscribe
        if operation == 's':
            subm.subscribeMember(email)
            return self.sub_template(email=email, status='s_ok')
        else:
            subm.unsubscribeMember(email)
            return self.sub_template( email=email, status='u_ok')

    def subrequest(self, email, oper='s'):
        email = email.lower().strip()
        context = self.context.aq_inner
        subm = ISubscriptionManager(context)
        hassub = subm.hasSubscriptionFor(member = email)

        if oper == 's':
            if hassub:
                return self.sub_template( email=email, status='s_fail')

            message = '订阅确认邮件已经发送到 %s, 请收到后点击确认链接即可。' % email
            subject = '易度公告邮件订阅确认'
            body = bodys
        else:
            if not hassub:
                return self.sub_template( email=email, status='u_fail')

            message = '退定确认邮件已经发送到 %s，请收到后点击其中的确认链接即可。' % email
            subject = '易度公告邮件退定确认'
            body = bodyu

        ticketurl = self._getTicketULR(email, oper)
        body = body % ticketurl

        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        mfrom = '"%s" <%s>' % (portal.email_from_name, portal.email_from_address)

        #mh = getToolByName(self.context, 'MailHost')
        mh = self.context.MailHost
        mh.secureSend(body, mto=email, mfrom=mfrom,subject=subject, charset='UTF-8')

        return self.sub_template( email=email, status=oper)

    def _getTicketULR(self, email, oper):
        email = email.lower().strip()
        ticket = generateTicket(email, oper)
        context = self.context.aq_inner
        ticketurl = '%s/@@subconfirm?id=%s' % (context.absolute_url(), ticket)
        return ticketurl

    def sendNewsletter(self):
        subject = '[易度公告]' + self.context.Title()
        body = self.context.getRawText()

        subm = ISubscriptionManager(self.context.newsletter)

        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        mfrom = '"%s" <%s>' % (portal.email_from_name, portal.email_from_address)

        #mh = getToolByName(self.context, 'MailHost')
        mh = self.context.MailHost

        for email in subm.getSubscribedMembers():
            url = self._getTicketULR(email, 'u')

            new_body = '%s\n\n --\n易度团队 (http://everydo.com)\n\n如不想再收到易度公告，请访问: \n\n%s' % (body, url)

            mh.secureSend(new_body, mto=email, mfrom=mfrom,subject=subject, charset='UTF-8')

        return 'all sent!'

