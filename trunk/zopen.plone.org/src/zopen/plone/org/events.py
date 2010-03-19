from zope.interface import implements
from zope.component.interfaces import ObjectEvent

from interfaces import IPersonTeamChangedEvent

class PersonTeamChangedEvent(ObjectEvent):
    """ repository path changed event """

    implements(IPersonTeamChangedEvent)

    def __init__(self, object, team_id, old_team_id):
        ObjectEvent.__init__(self, object)
        self.team_id = team_id
        self.old_team_id = old_team_id

