# -*- encoding: UTF-8 -*-
from zope.interface import implements

from Products.Archetypes.atapi import *
from Products.borg.content import Department
from zopen.plone.org.config import PROJECTNAME
from zopen.plone.org.interfaces import IOrganizationUnitContent

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('zopen.org')

OrganizationUnitSchema = Department.schema + Schema((
    
    StringField('title',
        searchable=True,
        user_property=True,
        widget=StringWidget(
            i18n_domain='zopen.org',
            label=u"Company Name",
            label_msgid=u'label_company_name',
            description=u"Your company name.",
            description_msgid=u'description_company_name',
        ),
    ),

    StringField('address_1',
        searchable=True,
        user_property=True,
        widget=StringWidget(
            i18n_domain='zopen.org',
            label=u"Company Address",
            label_msgid=u'label_company_address',
            description=u"Your company address.",
            description_msgid=u'description_company_address',
        ),
    ),

    StringField('address_2',
        searchable=True,
        user_property=True,
        widget=StringWidget(
            i18n_domain='zopen.org',
            label=u"Optional address",
            label_msgid=u'label_company_optional_address',
            description=u"Your company another address(if any).",
            description_msgid=u'description_company_optional_address',
        ),
    ),

    StringField('city',
        searchable=True,
        user_property=True,
        widget=StringWidget(
            i18n_domain='zopen.org',
            label=u"City",
            label_msgid=u'label_company_city',
            description=u"The city in which your company.",
            description_msgid=u'description_company_address',
        ),
    ),

    StringField('state',
        searchable=True,
        user_property=True,
        widget=StringWidget(
            i18n_domain='zopen.org',
            label=u"Province",
            label_msgid=u'label_company_province',
            description=u"The province in which your company.",
            description_msgid=u'description_company_province',
        ),
    ),

    StringField('zipPostalCode',
        searchable=True,
        user_property=True,
        widget=StringWidget(
            label=u"ZipPostalCode",
            i18n_domain='zopen.org',
            label_msgid=u'label_company_zip',
            description=u"The Zip what your company located in.",
            description_msgid=u'description_company_zip',
        ),
    ),

    StringField('webAddress',
        searchable=True,
        user_property=True,
        widget=StringWidget(
            i18n_domain='zopen.org',
            label=u"Website address",
            label_msgid=u'label_company_website',
            description=u"The website of your company.",
            description_msgid=u'description_company_website',
        ),
    ),

    StringField('office',
        searchable=True,
        user_property=True,
        widget=StringWidget(
            i18n_domain='zopen.org',
            label=u"Office Number.",
            label_msgid=u'label_company_office',
            description=u"The Office Number of your company.",
            description_msgid=u'description_company_website',
        ),
    ),

    StringField('fax',
        searchable=True,
        user_property=True,
        widget=StringWidget(
            i18n_domain='zopen.org',
            label=u"Fax Number.",
            label_msgid=u'label_company_fax',
            description=u"The fax number of your company.",
            description_msgid=u'description_company_fax',
        ),
    ),

    ImageField('logo',
        original_size=(200,200),
        widget=ImageWidget(
            i18n_domain='zopen.org',
            label=u"Logo",
            description=u"Your company Logo.",
            description_msgid=u'description_company_logo',
        ),
    ),

    BooleanField('logoInWhiteBox',
        default=True,
        widget=BooleanWidget(
            i18n_domain='zopen.org',
            label=u"Put the logo in a white box",
            label_msgid=u'label_company_logo_in',
        ),
    ),

        TextField(
            'description',
            default='',
            searchable=1,
            accessor="Description",
            default_content_type = 'text/plain',
            default_output_type = 'text/html',
            allowable_content_types = ('text/plain'),
            widget=TextAreaWidget(
            i18n_domain='zopen.org',
                label=_(u'label_description', default=u'Description'),
                description=_(u'help_description',
                              default=u'A short summary of the content.'),
                ),
        ),

    ))

OrganizationUnitSchema['managers'].mode = ''
OrganizationUnitSchema['roles_'].mode = ''

class OrganizationUnit(Department):
    """
    """

    schema = OrganizationUnitSchema

    implements(IOrganizationUnitContent)

registerType(OrganizationUnit, PROJECTNAME)
