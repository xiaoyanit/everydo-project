from zopen.plone.org.interfaces import IOrganizedEmployess
from Products.CMFCore.utils import getToolByName

from AccessControl import SecurityManagement
from zope.i18nmessageid import MessageFactory
from zope.i18n import translate
_ = MessageFactory('zopen.filerepos')

def sendNotification(ob, members, operation):
    """ 发送审核通知邮件

    ob: 审核的文档
    members: 要通知的人
    operation: submit/publish/reject
    """
    portal = getToolByName(ob, 'portal_url').getPortalObject()
    mailhost = getToolByName(portal, 'MailHost')
    mtool = getToolByName(ob, 'portal_membership')
    project = ob.getProject()
    ob_url = ob.absolute_url() + '/file_view'

    if operation == 'submit':

        subject = translate(_(u'subject_submit', default='[${project}] have file submitted', mapping={u'project':project.Title()}), context=ob.REQUEST)
        creator = ob.Creator()
        creator_fullname = mtool.getMemberById(creator).getProperty('fullname')
        creator_email = mtool.getMemberById(creator).getProperty('email')

        body = translate(_(u'mail_submit_review', default='A file submitted and needed you to review. DO NOT REPLY TO THIS EMAIL.\n\nSubmitted by ${user_name} <${user_email}>: \n\nFile: ${filename}\nVisit: ${file_url}\n\n${description}\n\n--\nDO NOT REPLY TO THIS EMAIL.',                      
                   mapping={u'file_url':ob_url, 
                            u'user_name':creator_fullname or creator,
                            u'user_email':creator_email,
                            u'filename':ob.Title(),
                            u'description':ob.Description()}
                     ),context=ob.REQUEST)

    elif operation == 'publish':
        subject = translate(_(u'subject_publish', default='[${project}] have file published', mapping={u'project':project.Title()}), context=ob.REQUEST)
        body = translate(_(u'mail_publish_review', default='A file published by review. DO NOT REPLY TO THIS EMAIL\n\nYou submitted file ${filename} that has published, please visit: ${file_url}\n\n--\nDO NOT REPLY TO THIS EMAIL.',
                      mapping={u'filename':ob.Title(),
                              u'file_url':ob_url}),
                              context=ob.REQUEST) 

    elif operation == 'reject':
        subject = translate(_(u'subject_reject', default='[${project}] have file rejected', mapping={u'project':project.Title()}), context=ob.REQUEST)
        body = translate(_(u'mail_reject_review', default='A file reject by review. DO NOT REPLY TO THIS EMAIL\n\nYou submitted file ${filename} that has rejected, please visit: ${file_url}\n\n--\nDO NOT REPLY TO THIS EMAIL.',
                      mapping={u'filename':ob.Title(),
                              u'file_url':ob_url}),
                              context=ob.REQUEST) 

    for m in members:
        memberId = m.getId()
        member = mtool.getMemberById(memberId)
        
        fullname = member.getProperty('fullname')
        email = member.getProperty('email')
        mfrom = '"%s" <%s>' % (portal.email_from_name, portal.email_from_address)
        mto = '"%s"<%s>' %  (fullname or memberId, email)

        mailhost.secureSend(body, mto, mfrom,subject,charset='utf-8')


def notifyAboutReview(ob, event):
    # 仅当文件或者图片(File/Image)的时候，才发送
    if ob.getPortalTypeName() not in ['File', 'Image']:
        return

    # 仅当处于提交、审核通过、拒绝的时候才通知
    mtool = getToolByName(ob, 'portal_membership')
    userid = mtool.getAuthenticatedMember().getId()

    operation = ''
    if event.action.endswith('submit'):
        operation = 'submit'
    elif event.action.endswith('publish'):
        operation = 'publish'
    elif event.action.endswith('reject'):
        operation = 'reject'
    # 工作流就是这样定义的, 下面逻辑没错!
    elif event.action.endswith('retract') and ob.Creator() != userid:
        operation = 'reject'
    else:
        return

    #  必须在项目中
    if hasattr(ob, 'getProject'):
        project = ob.getProject().aq_inner 

        acl_users = getToolByName(project, 'acl_users')

        oe = IOrganizedEmployess(project.teams)
        all_members = oe.get_all_people() 

        members = []
        if operation == 'submit':
            # 只有Administrator或者Reviewer才能收到邮件
            # userids = ob.users_with_local_role('Administrator') + ob.users_with_local_role('Reviewer')
            originalSecurityManager = SecurityManagement.getSecurityManager()
            for member in all_members:
                user = acl_users.getUserById(member.getId())
                if user is not None: 
                    # 模拟那个用户来登录
                    SecurityManagement.newSecurityManager(None, user)
                if mtool.checkPermission('Review portal content', ob):
                    members.append(member)
            SecurityManagement.setSecurityManager(originalSecurityManager)
        else:
           member = mtool.getMemberById(ob.Creator())
           if member:
               members.append(member)

        sendNotification(ob, members, operation)
