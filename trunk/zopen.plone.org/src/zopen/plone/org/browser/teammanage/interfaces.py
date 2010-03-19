from zope.interface import Interface

class ITeamManager(Interface):

    def getContentUrl():
        """ """

    def getTeams():
        """ """

    def getTeamTitle(id):
        """ """

    def addTeam(id, title):
        """ """

    def delTeam(id):
        """ """

    def renameTeam(id, new_title):
        """ """

    def teamDeletable(id):
        """ """

    def getContentCatetory(obj):
        """ """

    def setContentCategory(obj, new_cat_id):
        """ """

