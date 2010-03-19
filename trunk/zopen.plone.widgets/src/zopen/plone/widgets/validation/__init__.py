# -*- encoding: UTF-8 -*-

from Products.CMFDefault.utils import checkEmailAddress
from Products.CMFDefault.exceptions import EmailAddressInvalid
import re
from Products.CMFCore.utils import getToolByName

def errorFirmName(firmname):
    error = ''
    if firmname == '':
        error = '必须填写公司或团队名称；'

    error = error.decode('utf', 'replace')
    return error

def errorPhone(userphone):
    error = ''
    pattern = r'^[0-9][0-9-]'
    if userphone == '':
        error = '必须填写联系电话，以方便我们的服务支持;'
    elif re.search(pattern,userphone) == None:
        error = '电话号码格式为020-87654321或02087654321;'

    error = error.decode('utf', 'replace')
    return error

def errorFullName(fullname):
    error = ''
    if fullname == '':
        error = '必须填写管理用户姓名；'
        
    error = error.decode('utf', 'replace')
    return error

def errorEmail(useremail):
    error = ''
    if useremail == '':
        error = '必须填写邮件地址；'

    else:
        try:
            checkEmailAddress(useremail)
        except EmailAddressInvalid:
            error = '请正确填写邮件地址；'

    error = error.decode('utf', 'replace')
    return error

def errorUserName(username, context=None):
    error = ''
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9_-]{1,14}$'
    if context:
        membership = getToolByName(context, 'portal_membership')
    if username == '':
        error = '必须填写用户名；'
    elif re.search(pattern,username) == None:
        error = '用户名必须是字母数字下划线，2－15字符；'
    elif context and membership.getMemberById(username) is not None:
        error = username + '这个ID已经存在！'

    error = error.decode('utf', 'replace')
    return error

def errorPassword(userpassword):
    error = ''
    pattern = r'^[a-zA-Z0-9_]{5,}$'
    if userpassword == '':
        error = '必须填写密码；'
    elif re.search(pattern,userpassword) == None:
        error = '密码必须是母数字下划线，5个字符以上；'

    error = error.decode('utf', 'replace')
    return error

def errorConfirmPassword(userpassword, confirmpassword):
    error = ''
    if confirmpassword == '':
        error = '必须填写确认密码；'
    elif confirmpassword != userpassword:
        error = '注意，密码与确认密码不一致；'

    error = error.decode('utf', 'replace')
    return error

