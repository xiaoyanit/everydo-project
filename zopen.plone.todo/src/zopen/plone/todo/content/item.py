from DateTime import DateTime
from zope.interface import implements
from Products.Archetypes.atapi import *
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

from Products.ATContentTypes.content.schemata import relatedItemsField

from zopen.plone.todo.config import PROJECTNAME
from zopen.plone.todo.interfaces import ITodoItemContent, IStandaloneTodo
from zopen.plone.todo.utils import transformToRichTitle

from Products.ATContentTypes import ATCTMessageFactory as _


TodoItemSchema = BaseSchema + Schema((

    StringField('responsibleParty',
        index="FieldIndex:schema",
        widget=SelectionWidget(),
    ),

    DateTimeField('endDate',
                  required=True,
                  searchable=False,
                  accessor='end',
                  #default_method=DateTime,
                  widget = CalendarWidget(
                        description = '',
                        label = _(u'label_event_end', default=u'Event Ends')
                        )),
    relatedItemsField,
    # BooleanField('notify'),

    ))

class TodoItem(BaseContent):
    """ todo  item """
    implements(ITodoItemContent)

    schema = TodoItemSchema

    def Description(self):
        return self.aq_inner.aq_parent.Title()

    def setResponsibleParty(self, value):
        self.getField('responsibleParty').set(self, value)

        if IStandaloneTodo.providedBy(self):
            return

        userids = self.users_with_local_role('Responsor')
        owners = self.users_with_local_role('Owner')
        if userids:
            self.manage_delLocalRoles(userids)
        if value:
            if value in owners:
                self.manage_setLocalRoles(value, ['Responsor', 'Owner'])
            else:
                self.manage_setLocalRoles(value, ['Responsor'])
        else:
            # XXX some hack for project teamfolder
            if hasattr(self, 'getProject'):
                project = self.getProject()
                self.manage_setLocalRoles('teams-' + project.getId(), ['Responsor'])
        self.reindexObjectSecurity()

    def getResponsiblePartyTitle(self):
        responsor = self.getResponsibleParty()

        bv = getMultiAdapter( (self, self.REQUEST), name=u'basecamp_view')
        if bv:
            name = bv.getMemberName(responsor)
            if name: 
                return name
            else:
                name = bv.getGroupName(responsor)
                if name:
                    return name
                else:
                    return responsor

        mtool = getToolByName(self, 'portal_membership')
        responsor = self.getResponsibleParty()
        mi = mtool.getMemberInfo(responsor)
        if mi:
            return mi['fullname'] or responsor

        # a group?
        else:
            gtool = getToolByName(self, 'portal_groups')
            group = gtool.getGroupInfo(responsor)
            if group:
                return group['title'] or responsor
            else:
                return responsor

    def richTitle(self):
        return transformToRichTitle(self.Title())

registerType(TodoItem, PROJECTNAME)
