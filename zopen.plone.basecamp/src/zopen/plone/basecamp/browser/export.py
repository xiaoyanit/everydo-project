# -*- coding: UTF-8 -*-

import os
from zope.i18nmessageid import MessageFactory

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

try:
    from zopen.plone.frs.frsexport import frsExportTree
except ImportError: 
    pass

from fcrypt import crypt

_ = MessageFactory('zopen.project')

# import logging; info = logging.getLogger('zopen.plone.org').info

class Export2FRS(BrowserView):

    def __call__(self, projectid):
        context = self.context.aq_inner
        project = getattr(context.projects, projectid)
        frsExportTree(project)
        portal_url = getToolByName(context, 'portal_url')
        portal = portal_url.getPortalObject()

        frsExportTree(portal.teams)
        frsExportTree(portal.companies)

        #msg = _(u'Project data exported successfully.')
        plone_utils = getToolByName(self.context, 'plone_utils')
        #plone_utils.addPortalMessage(msg, 'info')
        plone_utils.addPortalMessage('项目数据已经成功导出，请进行第二步。', 'info')
        return self.request.response.redirect(portal.absolute_url()+'/@@@@prefs_export_data')

    def setExportPWD(self, password):
        context = self.context.aq_inner
        enc_pwd = crypt(password, 'ad')

        root_path = '/var/everydo-frs%s' % '/'.join(context.getPhysicalPath())
        if not os.path.exists(root_path):
            os.makedirs(root_path, 0777)
        path = root_path + '/.htaccess'

        htaccess = """<IfDefine neverdefine>
export:%s
</IfDefine>
AuthUserFile %s"""
        htaccess = htaccess % (enc_pwd, path)
        f = open(path, 'w')
        f.write(htaccess)
        plone_utils = getToolByName(context, 'plone_utils')
        plone_utils.addPortalMessage('导出数据访问密码已经成功设置，请进行第三步。', 'info')
        return self.request.response.redirect(self.context.absolute_url()+'/@@@@prefs_export_data')
