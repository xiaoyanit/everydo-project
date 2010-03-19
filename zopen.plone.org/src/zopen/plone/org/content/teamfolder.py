# -*- encoding: UTF-8 -*-
from zope.interface import implements

from Products.Archetypes.atapi import *
from Products.borg.content import Department
from zopen.plone.org.config import PROJECTNAME
from zopen.plone.org.interfaces import ITeamFolderContent

from team import TeamSchema
from Products.membrane.interfaces import IPropertiesProvider

class TeamFolder(BaseFolder):
    """
    """

    implements(ITeamFolderContent, IPropertiesProvider)

    schema = TeamSchema

    exclude_from_nav = True

    def recaculateMembers(self):
        """ called by all the contained team;
        
        membrane need references"""
        members = []
        for team in self.contentValues():
            for member in team.getMembers():
                if member not in members:
                    members.append(member)

        self.setMembers(members)

registerType(TeamFolder, PROJECTNAME)
