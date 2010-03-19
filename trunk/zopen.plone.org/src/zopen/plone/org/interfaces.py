# -*- encoding: UTF-8 -*-

from zope.interface import Interface
from zope import schema

class ITeamContent(Interface):
    """Marker interface for team content objects"""

class ITeam(Interface):
    """A team, which may contain employees. 
    
    team can also act as groups.
    """
    
    id = schema.TextLine(title=u'Identifier',
                         description=u'An identifier for the team',
                         required=True,
                         readonly=True)

    def getMembers():
        """Get a list of IEmployee's in this team.
        """

class ITeamFolderContent(Interface):
    pass

class IOrganizationUnitContent(Interface):
    """ """

class IPersonContent(Interface):
    """ """

class IOrganizedEmployess(Interface):
    """
        this interface adapts to teams' folder,
            (such as IProject'teams, and portal's teams)
        and provides functionality
    """

    def get_teams():
        """ return all the teams in this project """

    def get_companies_and_people(team):
        """ get all ou and people in a secific team """

    def get_people(team):
        """ get all people in a secific team """

    def get_all_companies_and_people():
        """
            get all people in a this project
            the returning data structure is:

            {   'owner_company':
                    [<OrganizationUnit at ...>, <Person at ...>, <Person at ...>],
                'ibc':
                    [<OrganizationUnit at ...>, <Person at ...>],
                'zopen':
                    [<OrganizationUnit at ...>, <Person at ...>, ...]
            }

            namely: ths first is an OU, any later are Persons.
        """

    def get_available_companies(team):
        """ get a list of company names unused in this project """

    def get_available_companies_and_people(team):
        """ this is used for edit teams in a project """

    def caculateCompanyPeople(subscribers):
        """
            # input:
            #   subscribers: [id1, id2, id3, ...]
            # 
            # output:
            #   { 'zopen': [company, person1, person2, ...],
            #     'ibc': [company, person1, person2, ...]
            #   }
        """

class IOrgInstance(Interface):
    """ """

    def createCompany(name):
        """ """

    def getAvailableCompanies():
        """ """

    def getAvailableTeams():
        """ """

    def randomId():
        """ """

    def getCompany(id):
        """ """

    def getOwnerCompany():
        """ """

    def get_team_of_person(person):
        """
            # 找到person所在的系统teams
            # 找不到则返回None
        """

class IPersonTeamChangedEvent(Interface):
    """ """

