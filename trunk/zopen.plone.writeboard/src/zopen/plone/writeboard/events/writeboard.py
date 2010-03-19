from Products.CMFCore.utils import getToolByName
from zope import component
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from kss.core.interfaces import IKSSView
from zopen.plone.writeboard.interfaces import IWriteboardContent

def notifySetContributors(ob, ev):

    portal_membership = getToolByName(ob, 'portal_membership')
    member = portal_membership.getAuthenticatedMember()
    ob.setContributors((member.getId(),))
    ob.reindexObject()

@component.adapter(IWriteboardContent, IKSSView, IObjectModifiedEvent)
def notifyRegionReload(ob, view, ev):
    ksscore = view.getCommandSet('core')
    revisions = view.macroContent('context/writeboard_view/macros/revisions')
    ksscore.replaceHTML(ksscore.getHtmlIdSelector("compare-revisions"), revisions)
