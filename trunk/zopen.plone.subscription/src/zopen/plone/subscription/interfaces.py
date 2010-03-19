from zope.interface import Interface


class ISubscriptionManager(Interface):
    """
    """

    def getSubscribedAddresses():
        """Return a tuple of all the subscriber addresses.
        """

    def getSubscribedMembers():
        """Return a tuple of portal members who are subscribed here.
        """

    def acceptsSubscriptionChanges():
        """Boolean for whether calls to [un]subscribeAddress should be made.
        Allows for lists with addresses that are populated from a database, for example.
        """

    def subscribeAddress(address):
        """Subscribe the address to the mailing list.  Do not raise an error
        if the address is already subscribed.
        """

    def unsubscribeAddress(address):
        """Unsubscribe the address from the mailing list.  Do not raise an error
        if the address is not currently subscribed.
        """

    def subscribeMember(member):
        """Subscribe the member to this list.  Use the currently authenticated user if
        member is None.
        Do not raise an error if the member is already subscribed.
        Do raise an error if the member is 'Anonymous'.
        """

    def unsubscribeMember(member):
        """Unsubscribe the address from the mailing list.  Do not raise an error
        if the address is not currently subscribed.
        """

    def subscribeAuthenticatedMember():
        """Subscribe the currently authenticated member to this list.
        Do not raise an error if the member is already subscribed.
        Do raise an error if the member is 'Anonymous'.
        """

    def unsubscribeAuthenticatedMember():
        """Unsubscribe the currently authenticated member from this list.
        Do not raise an error if the member is not currently subscribed.
        Do raise an error if the member is 'Anonymous'.
        """

    def hasSubscriptionFor(address=None, member=None):
        """Boolean for whether the address or member is currently subscribed.
        """

    def sendMail(subject, body):
        """ send mail """




