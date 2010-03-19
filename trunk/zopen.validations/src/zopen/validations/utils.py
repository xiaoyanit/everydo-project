# -*- encoding: UTF-8 -*-

import re
import compiler

_DOMAIN_RE = re.compile(r'[^@]{1,64}@[A-Za-z0-9][A-Za-z0-9-]*'
                                r'(\.[A-Za-z0-9][A-Za-z0-9-]*)+$')

from interfaces import IExistsId

def errorFirmName(firmname):
    error = ''
    if firmname == '':
        error = '必须填写公司或团队名称；'

    error = error.decode('utf', 'replace')
    return error

def errorLocation(firmname):
    error = ''
    if firmname == '':
        error = '必须填写公司所在城市；'

    error = error.decode('utf', 'replace')
    return error

def errorURL(urlname,vendor):
    error = ''
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{1,14}$'
    if urlname == '':
        error = '必须填写网站地址；'

    # acsii字母
    elif re.search(pattern,urlname) == None:
        error = 'ULR必须是字母数字和短横线，2－15字符；'

    elif urlname in ['zeo', 'zope1', 'zope2', 'zope3','zope4','zope5', 'zope6', 'zope7',  'www', 'ftp', 'download', 'export', 'cache', 'proxy', 'mail', 'signup', 'paycenter', 'docs', 'blog', 'ldap']:
        error = '此URL被保留，请尝试其它的URL；'

    elif IExistsId(vendor).existsId(urlname):
        error = '这个网站名字已经被注册，请另选一个；'

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

def errorMobilePhone(mobile_phone):
    error = ''
    pattern = r'^(13[0-9]|15[^4]|18[6|8|9])\d{8}$'
    if mobile_phone == '':
        error = '请填写移动电话，以方便我们的服务支持;'
    elif re.search(pattern,mobile_phone) == None:
        error = '移动电话号码格式应该为13787654321;'

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
    pattern = re.compile(r'[^@]{1,64}@[A-Za-z0-9][A-Za-z0-9-]*'
                                r'(\.[A-Za-z0-9][A-Za-z0-9-]*)+$')
    if useremail == '':
        error = '必须填写邮件地址；'

    elif re.search(pattern,useremail) == None:
        error = '请正确填写邮件地址；'

    error = error.decode('utf', 'replace')
    return error

def errorUserName(username):
    error = ''
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9_-]{1,14}$'
    if username == '':
        error = '必须填写用户名；'
    elif re.search(pattern,username) == None:
        error = '用户名必须是字母数字下划线，2－15字符；'
    
    error = error.decode('utf', 'replace')
    return error

def errorPassword(userpassword):
    error = ''
    pattern = r'^[a-zA-Z0-9_]{5,}$'
    if userpassword == '':
        error = '必须填写密码；'
    elif re.search(pattern,userpassword) == None:
        error = '密码必须是由字母、数字和下划线组成，并且5个字符以上；'

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

def errorPythonSource(source):
    """ 检查python代码的合理性 """
    try:
        source = source.replace('\r', '')
        compiler.parse(source)
    except:
        return "语法错误"
    return ''

