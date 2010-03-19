# encoding: utf-8
from zope.interface import implements
from zope.component import getUtility

from Acquisition import aq_inner, aq_parent
from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import getToolByName

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.Archetypes.atapi import *
from zope.i18nmessageid import MessageFactory

from Products.Archetypes.utils import DisplayList

from Products.borg import permissions

from zopen.plone.project.interfaces import IProjectContent
from zopen.plone.project.config import PROJECTNAME
from zopen.plone.project import permissions

_ = MessageFactory('zopen.project')

ProjectSchema = BaseSchema + Schema((

        TextField(
            'description',
            default='',
            searchable=1,
            accessor="Description",
            default_content_type = 'text/html',
            default_output_type = 'text/html',
            allowable_content_types = ('text/html',),
            widget=TextAreaWidget(
                label=_(u'label_description', default=u'Description'),
                description=_(u'help_description',
                              default=u'A short summary of the content.'),
                ),
        ),

    ReferenceField('company',
        relationship='participatesInProject',
        allowed_types=('OrganizationUnit',),
        required=1,
        languageIndependent=True,
        widget=ReferenceWidget(
            label=u'Main company or client',
            label_msgid="label_related_company",
            format="radio",
            description=u"Select a company or client related to this project.",
            description_msgid="help_related_company",
            i18n_domain="zopen.project"
            ),
        ),

    StringField('projectState',
        mutator="setNewProjectState",
        widget=SelectionWidget(
            label="Change project state",
            description="Select a new state for the project",
            format="radio",
            label_msgid='label_projectState',
            description_msgid='help_projectState',
            i18n_domain='zopen.project',
        ),
        vocabulary=DisplayList((
                ('active', _(u'label_active_state', default=u'Active — Fully functional project.')),
                # ('onhold', _(u'label_onhold_state', default=u"On hold — Fully functional project, but milestones, messages, comments, and to-do items don't show up on the Dashboard.")),
                ('archived', _(u'label_archived_state', default=u"Archived — This project is frozen: it can be viewed but not edited.  Archived projects don't count against your active project total.")),
            )),
        default='',
        enforceVocabulary=False,
        accessor="getProjectState",
        write_permission=permissions.ManageProject
    ),

    ))


#ProjectSchema['description'].schemata = 'default'

class Project(BrowserDefaultMixin, BaseFolder):
    """A project.

    Persons can be made members or managers of projects by reference.
    """
    
    security = ClassSecurityInfo()
    implements(IProjectContent)
    
    # Note: ExtensibleSchemaSupport means this may get expanded.
    schema = ProjectSchema
    _at_rename_after_creation = True

    def getProject(self):
        return self

    security.declareProtected(permissions.ManageProject, 'setNewProjectState')
    def setNewProjectState(self, new_state):
        """
        Set a new review state for the project , by executing
        the given transition.
        """
        state_map = {'active':'activate', 
                      'onhold':'hold',
                      'archived':'archive',}

        wftool = getToolByName(self, 'portal_workflow')
        old_state = wftool.getInfoFor(self, 'review_state')

        if new_state not in state_map or new_state == old_state:
            return

        transition = state_map[new_state]
        wftool.doActionFor(self, transition)

    def getProjectState(self):
        wftool = getToolByName(self, 'portal_workflow')
        return wftool.getInfoFor(self, 'review_state')
 
registerType(Project, PROJECTNAME)
