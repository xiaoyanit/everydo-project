from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.component import getUtility

from Products.CMFCore.utils import getToolByName

from interfaces import ISubscriptionManager

from OFS.interfaces import IPropertyManager

SUBSCRIPTION_PROPERTY_ID = 'object_subscribers'

class PropertySubscriptionManager:
    implements(ISubscriptionManager)
    adapts(IPropertyManager)

    def __init__(self, context):
        self.context = context

    def getSubscribedMembers(self):
        """Return a tuple of portal members who are subscribed here.
        """
        return self.context.getProperty(SUBSCRIPTION_PROPERTY_ID, [])

    def getSubscriptionEmailList(self, includeme=False):
        """ get the subscription email list """
        portal_membership = getToolByName(self.context, 'portal_membership')
        auth_member = portal_membership.getAuthenticatedMember()

        maillist = []
        for id in self.getSubscribedMembers():
            # exclude the current user
            if not includeme and id == auth_member.getId():
                continue

            member = portal_membership.getMemberById(id)
            if member:
                email = member.getProperty('email').strip()
                if email: 
                    maillist.append(email)
        return maillist

    def setSubscribedMembers(self, members):
        if self.context.hasProperty(SUBSCRIPTION_PROPERTY_ID):
            self.context._setPropValue(SUBSCRIPTION_PROPERTY_ID,members)
        else:
            self.context._setProperty(SUBSCRIPTION_PROPERTY_ID, members, 'lines')

    def subscribeMember(self, member):
        """Subscribe the member to this list.  Use the currently authenticated user if
        member is None.
        Do not raise an error if the member is already subscribed.
        Do raise an error if the member is 'Anonymous'.
        """
        members = list(self.getSubscribedMembers())
        if member not in members:
            members.append(member)

            if self.context.hasProperty(SUBSCRIPTION_PROPERTY_ID):
                self.context._setPropValue(SUBSCRIPTION_PROPERTY_ID,members)
            else:
                self.context._setProperty(SUBSCRIPTION_PROPERTY_ID, members, 'lines')

    def unsubscribeMember(self, member):
        """Unsubscribe the address from the mailing list.  Do not raise an error
        if the address is not currently subscribed.
        """
        members = list(self.getSubscribedMembers())
        if member in members:
            members.remove(member)
            self.context._setPropValue(SUBSCRIPTION_PROPERTY_ID,members)

    def subscribeAuthenticatedMember(self):
        """Subscribe the currently authenticated member to this list.
        Do not raise an error if the member is already subscribed.
        Do raise an error if the member is 'Anonymous'.
        """
        portal_membership = getToolByName(self.context, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        self.subscribeMember(member.getId())

    def unsubscribeAuthenticatedMember(self):
        """Unsubscribe the currently authenticated member from this list.
        Do not raise an error if the member is not currently subscribed.
        Do raise an error if the member is 'Anonymous'.
        """
        portal_membership = getToolByName(self.context, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        self.unsubscribeMember(member.getId())

    def hasSubscriptionFor(self, address=None, member=None):
        """Boolean for whether the address or member is currently subscribed.
        """
        if member is not None:
            return member in self.getSubscribedMembers()

    def hasSubscriptionForAuthenticatedMember(self):
        portal_membership = getToolByName(self.context, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        return self.hasSubscriptionFor(member = member.getId())

    def sendMail(self, subject='', body='', includeme=False):
        emails = self.getSubscriptionEmailList(includeme)
        if not emails:
            return 

        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        mfrom = '"%s" <%s>' % (portal.email_from_name, portal.email_from_address)

        mh = getToolByName(self.context, 'MailHost')
        mh.secureSend(body, mto=emails, mfrom=mfrom,subject=subject, charset='UTF-8')

