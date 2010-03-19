from zope.interface import Interface

class IExistsId(Interface):

    def exitsId(id):
        """ check if the id exists """
