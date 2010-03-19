# -*- encoding: UTF-8 -*-

from zope.interface import implements
from zope.component import adapts

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.atapi import *

from Products.borg import permissions
from Products.borg.content import Employee

from zopen.plone.org.config import PROJECTNAME
from zopen.plone.org.interfaces import IPersonContent

from zope.i18nmessageid import MessageFactory
from zope.i18n import translate
_ = MessageFactory('zopen.org')

PersonSchema = Employee.schema + Schema((

    StringField('id',
        languageIndependent=True,
        required=True,
        # write_permission=permissions.ManageUsers,
        #widget=StringWidget(
        widget=ComputedWidget(
            i18n_domain='zopen.org',
            label=u'Login Username',
            label_msgid=u'label_user_name',
            description=u"Login website, useing for login. Once creation, cannot be amended.",
            description_msgid=u'description_user_name',
        ),
    ),
               
    StringField('password',
        languageIndependent=True,
        required=False,
        mode='w',
        write_permission=permissions.SetPassword,
        widget=PasswordWidget(
            i18n_domain='zopen.org',
            label=u'Password',
            label_msgid=u'label_user_password',
            macro='org_password',
            description=u"Setting your password. If you don't want to change, keep the blank.",
            description_msgid=u'description_user_password',
        ),
    ),
     
    StringField('confirmPassword',
        languageIndependent=True,
        required=False,
        mode='w',
        write_permission=permissions.SetPassword,
        widget=PasswordWidget(
            i18n_domain='zopen.org',
            label=u'Confirm password',
            label_msgid=u'label_user_confirm_password',
            description=u"Please input your password again. If you don't want to change, keep the blank.",
            description_msgid=u'description_user_confirm_password',
        ),
    ),         

    StringField('email',
        validators=('isEmail'),
        required=True,
        searchable=True,
        user_property=True,
        widget=StringWidget(
            i18n_domain='zopen.org',
            label=u"Email",
            label_msgid=u'label_user_email',
            description=u"Please input your email.",
            description_msgid=u'description_user_email',
        ),
    ),

    StringField('phone',
        required=False,
        searchable=True,
        user_property=True,
        widget=StringWidget(
            i18n_domain='zopen.org',
            label=u"Telephone Number",
            label_msgid=u'label_user_telephone',
            description=u"Please input your telephone number.",
            description_msgid=u'description_user_telephone',
        ),
    ),

    StringField('title',
        accessor='Title',
        required=True,
        user_property='fullname',
        widget=StringWidget(
            i18n_domain='zopen.org',
            label=u"Fullname",
            label_msgid=u'label_user_fullname',
            description=u"Please input your fullname.",
            description_msgid=u'description_user_fullname',
        ),

    ),

    StringField('position',
        required=False,
        user_property=False,
        widget=StringWidget(
            i18n_domain='zopen.org',
            label=u"Duty",
            label_msgid=u'label_user_duty',
            description=u"Please input your duty.",
            description_msgid=u'description_user_duty',
        ),

    ),

    StringField('mobilePhone',
        required=False,
        searchable=True,
        user_property=True,
        widget=StringWidget(
            i18n_domain='zopen.org',
            label=u"Mobile",
            label_msgid=u'label_user_mobile',
            description=u"Please input your mobile.",
            description_msgid=u'description_user_mobile',
        ),
    ),

    StringField('office',
        required=False,
        searchable=True,
        user_property=True,
        widget=StringWidget(
            i18n_domain='zopen.org',
            label=u"Office Number",
            label_msgid=u'label_user_office',
            description=u"Please input your office number.",
            description_msgid=u'description_user_office',
        ),
    ),

    StringField('fax',
        required=False,
        searchable=True,
        user_property=True,
        widget=StringWidget(
            i18n_domain='zopen.org',
            label=u"Fax Number",
            label_msgid=u'label_user_fax',
            description=u"Please input your fax number.",
            description_msgid=u'description_user_fax',
        ),
    ),

    StringField('location',
        searchable=True,
        user_property=True,
        widget=StringWidget(
            i18n_domain='zopen.org',
            label=u"Location",
            label_msgid=u'label_user_location',
            description=u"Please input the city or the province where you located in",
            description_msgid=u'description_user_location',
        ),
    ),

    ImageField('photo',
        original_size=(48,48),
        widget=ImageWidget(
            i18n_domain='zopen.org',
            label=u"Portrait",
            label_msgid=u'label_user_portrait',
            description=u"upload your portrait.",
            description_msgid=u'description_user_portrait',
        ),
    ),


    ))

PersonSchema['roles_'].mode = ''

ACCOUNT_INFO_EMAIL = """%(companyname)s已经为您创建了一个帐号。您的帐号信息是:

 用户名: %(username)s
 密码: %(password)s

可访问下面的地址登录:
%(portal_url)s

登录后，请到站点右上方 “我的资料” 处，及时修改自己的密码。
"""

class Person(Employee):
    """Extend the schema of an employee to include additional fields.
    """

    schema = PersonSchema
    implements(IPersonContent)

    def sendAccountInfoEmail(self, password):
        mh = self.MailHost
        portal = self.portal_url.getPortalObject()
        portal_url = self.portal_url()
        companyname = portal.companies.owner_company.Title()
        username = self.getId()

       # body = ACCOUNT_INFO_EMAIL % {'portal_url':portal_url, 
       #                              'companyname':companyname,
       #                              'username':username,
       #                              'password':password}
        body = translate(_(u'mail_body',
                          default='${companyname} create a account for you.  your account information is:\n Username: ${username}\n Password: ${password}\n\nPlease visit the following address and Login:\n${portal_url}\n\nThen visit the site top right corner "My Info", amend your password in time.',
                          mapping={u'portal_url':portal_url,
                                   u'companyname':companyname,
                                   u'username':username,
                                   u'password':password}),
                          context=self.REQUEST)

        mfrom = '"%s" <%s>' % (portal.email_from_name, portal.email_from_address)
      #  subject = '[%s] 您的帐号已经创建' % portal.Title()
        subject = translate(_(u'mail_subject',
                             default='[${project_title}] Your account has been created.',
                             mapping={u'project_title':portal.Title()}),
                             context=self.REQUEST)

        emails = self.getEmail()

        mh = getToolByName(self, 'MailHost')
        if emails.strip():
            mh.secureSend(body, mto=emails, mfrom=mfrom,subject=subject, charset='UTF-8')

registerType(Person, PROJECTNAME)

