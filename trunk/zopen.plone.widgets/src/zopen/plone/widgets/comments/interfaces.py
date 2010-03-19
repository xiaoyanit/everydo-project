from zope.interface import Interface

class ICommentsManager(Interface):

    def getComments():
        """ """

    def addComment(text, attachements):
        """ """

    def attachable():
        """ """

    def getReplay(id):
        """ """
