我们先导入订阅管理接口:

    >>> from zopen.plone.subscription.interfaces import ISubscriptionManager

我们任何一个支持属性操作的对象，都可以订阅:

    >>> sm = ISubscriptionManager(self.portal)
    >>> sm.getSubscribedMembers()
    []

我们先以管理员身份创建几个系统用户:

    >>> self.setRoles(('Manager',))
    >>> from zope.component import getUtility
    >>> from Products.CMFCore.interfaces import IRegistrationTool, IMembershipTool
    >>> portal_registration = getUtility(IRegistrationTool)
    >>> portal_membership = getUtility(IMembershipTool)
    >>> member = portal_membership.getAuthenticatedMember()
    >>> md = portal_registration.addMember('aa', 'aa')
    >>> md = portal_registration.addMember('bb','bb')

开始订阅:

   >>> sm.setSubscribedMembers(('aa', 'bb'))
   >>> sm.getSubscribedMembers()
   ('aa', 'bb')

自行订阅:

   >>> sm.hasSubscriptionForAuthenticatedMember()
   False
   >>> sm.subscribeAuthenticatedMember()
   >>> members = sm.getSubscribedMembers()
   >>> len(members)
   3
   >>> sm.hasSubscriptionFor(member=member.getId())
   True
   >>> sm.hasSubscriptionForAuthenticatedMember()
   True
   >>> sm.unsubscribeAuthenticatedMember()
   >>> sm.getSubscribedMembers()
   ('aa', 'bb')
   >>> sm.hasSubscriptionFor(member=member.getId())
   False

调整订阅:

   >>> sm.setSubscribedMembers(('aa', ))
   >>> sm.getSubscribedMembers()
   ('aa',)
