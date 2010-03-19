from zope.interface import Interface

class ICategoryManager(Interface):

    def getContentUrl():
        """ """

    def getCategories():
        """ """

    def getCategoryTitle(id):
        """ """

    def addCategory(id, title):
        """ """

    def delCategory(id):
        """ """

    def renameCategory(id, new_title):
        """ """

    def categoryDeletable(id):
        """ """

    def getContentCatetory(obj):
        """ """

    def setContentCategory(obj, new_cat_id):
        """ """

