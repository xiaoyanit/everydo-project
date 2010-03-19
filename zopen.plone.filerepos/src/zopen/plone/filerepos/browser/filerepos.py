# -*- coding: UTF-8 -*-

import time
import os
from Products.Five import BrowserView
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from kss.core import kssaction
from Products.Archetypes.event import ObjectEditedEvent
from zope import event


from Products.CMFEditions.interfaces.IRepository import IRepositoryTool
#from Products.CMFPlone.interfaces import IPloneTool
from DateTime import DateTime

from zopen.plone.filerepos.config import typesToShow
from zopen.plone.widgets.category.interfaces import ICategoryManager
from zopen.plone.filerepos.interfaces import IFileManager
from zopen.plone.subscription.interfaces import ISubscriptionManager
from Products.CMFCore.utils import _checkPermission


from zope.i18nmessageid import MessageFactory
from zope.i18n import translate
_ = MessageFactory('zopen.filerepos')

# import logging; info = logging.getLogger('zopen.plone.filerepos').info

def sendNotification(self, msg):
        sm = ISubscriptionManager(msg)

        portal_url = getToolByName(msg, 'portal_url')
        portal = portal_url.getPortalObject()
        subject = '[%s] %s' % (portal.Title(), msg.Title())

        mtool = getToolByName(msg, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        fullname = member.getProperty('fullname')
        email = member.getProperty('email')

        body= translate(_(u'mail_body',
                         default='A file submitted. DO NOT REPLY TO THIS EMAIL.\n\nSubmitted by ${user_name} <${user_email}>: \n\nFile: ${filename}\nDownload: ${file_url}\n\n${description}',    
                         mapping={u'file_url':msg.absolute_url() + '/@@file_view',
                                u'user_name':fullname or member.getId(),
                                u'user_email':email,
                                u'filename':msg.Title(),
                                u'description':msg.Description()}
                         ),context=self.request)
        sm.sendMail(subject=subject, body=body, includeme = True)

def getArchiveTime(versiondata):
    """
    从VersionData对象中得到在ZODB中的存档时间
    时间格式为2007-11-14-14-25-34
    """
    
    timedate = versiondata.sys_metadata["timestamp"]
    archiveTime = time.strftime("%Y-%m-%d-%H-%M-%S",time.localtime(timedate))
    return archiveTime


def isNullFileField(self, formFileField):
    if not formFileField:
        plone_utils = getToolByName(self.context, 'plone_utils')
        msg = translate(_(u'va_need_file', default="You must choose a file."), context=self.request)
        plone_utils.addPortalMessage(msg, 'error')
        return True
    else:
        return False


class FileReposView(BrowserView):

    def canAdd(self):
        context = self.context.aq_inner
        # 只有自文件夹可以添加，才显示
        return ICategoryManager(context).getCategories(addable=True)

    def getTimelinedResults(self, category=None, group_by='modified'):
        
        path = '/'.join(self.context.getPhysicalPath())
        if category:
            path += '/' + category

        portal_catalog = getToolByName(self.context, 'portal_catalog')
        brains = portal_catalog.searchResults({
                    'path'       : path,
                    'portal_type': typesToShow,
                },
                sort_order = 'reverse',
                sort_on    = group_by,
                )

        return brains

        # to caculate a dict keyworded by date
        dates_result = {}
        for b in brains:
            # XXX
            # 在manage_cutObjects和manage_pasteObjects过程中
            # 出现旧的brain对象仍在，但旧的brain对象调用getObject会报告异常

            try:
                obj = b.getObject()
            except AttributeError:
                continue

            modified = b.modified
            day = DateTime(
                    modified.year(),
                    modified.month(),
                    modified.day())
            if not dates_result.has_key(day):
                dates_result[day] = []

            data = {}
            data['getId'] = b.getId
            data['getIcon'] = b.getIcon
            data['Description'] = b.Description
            data['modified'] = b.modified
            data['getObjSize'] = b.getObjSize

            data['is_private'] = b.review_state == 'private'
            data['getPath'] = b.getPath()

            # 获取作者信息
            mtool = getToolByName(self.context, 'portal_membership')
            author = mtool.getMemberInfo(b.Creator)
            data['author'] = author and author['fullname'] or b.Creator

            data['obj'] = obj
            data['pretty_title_or_id'] = obj.pretty_title_or_id()
            cat = obj.aq_parent
            data['category'] = {
                'getId'              : cat.getId(),
                'pretty_title_or_id' : cat.pretty_title_or_id(),
            }
            dates_result[day].append(data)

        # info("%r" % dates_result)
        return dates_result

    def categoryTitle(self):
        category = self.request.get('category', '')
        return category and ICategoryManager(self.context).getCategoryTitle(category)

    def getReviewContents(self, category='None'):
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        path = '/'.join(self.context.getPhysicalPath())
        if category:
            path += '/' + category
        review_list = portal_catalog.searchResults(
                                     path = path,
                                     portal_type = ['File', 'Image'],
                                     review_state = ['pending', 'privatepending'],
                                     sort_on = 'modified',
                                     sort_order = 'reverse',
                                     )
        results = []
        for result in review_list:
            o = result.getObject()
            if o and _checkPermission('Review portal content', o):
                results.append(result)

        return results
                
            
class FileReposOperView(BrowserView):

    def filerepos_add(self):
        files = self.request.form['file']
        
        file_manager = getUtility(IFileManager, 'file_manager')

        wtool = getToolByName(self.context, 'portal_workflow')
        #计数器
        count = 0
        for item in files:
            file_from_request = item.file
            if not file_from_request:
                continue
            else:
                count += 1
        

            # TODO:
            # automatically judge the type of the file,
            # to File, Image, or others.
            category = getattr(self.context, item.category)

            portal_membership = getToolByName(self.context, 'portal_membership')
            member = portal_membership.getAuthenticatedMember()
            fileObj = file_manager.addFile(category, file_from_request)


            if item.has_key("description"):
                fileObj.setDescription(item["description"])

            if item.get("mark_private", 0):
                wtool.doActionFor(fileObj, 'hide')
                if item.get("submit", 0):
                    wtool.doActionFor(fileObj, 'privatesubmit')
            elif item.get("submit", 0):
                wtool.doActionFor(fileObj, 'submit')

            # use the adapter to configure the subscribers
            if self.request.form.has_key('persons'):
                adapted = ISubscriptionManager(fileObj)
                adapted.setSubscribedMembers(self.request.form['persons'])
                adapted.subscribeAuthenticatedMember()
                sendNotification(self, fileObj)

            fileObj.reindexObject()

        if count == 0:
            #当用户没有选择一个文件做为上传对象时，给予警告
            isNullFileField(self, '')
            return self.request.response.redirect(self.context.absolute_url())

        plone_utils = getToolByName(self.context, 'plone_utils')
        msg = translate(_(u'you added ${count} files success.', default="You added ${count} files success.", mapping={u'count' : len(files)}), context=self.request)
        plone_utils.addPortalMessage(msg, 'info')


        # back to the folder
        self.request.response.redirect(self.context.absolute_url())


    def save_as_new_version(self, fileViewUrl=None):
        
        """更新文件版本"""
        form = self.request.form
        file_from_request = form['file']
        fileObj = self.context.aq_inner
        category = fileObj.aq_parent
        filerepos = category.aq_parent
        if isNullFileField(self, file_from_request):
            return self.request.response.redirect(filerepos.absolute_url())

        if category.getId() != form['category']:
            cat_m = ICategoryManager(filerepos)
            fileObj = cat_m.setContentCategory(fileObj, form['category'])
            
        rep_tool = getToolByName(self.context, 'portal_repository')
        comment = ''
        byte_size = fileObj.get_size()
        currentContributor = fileObj.Contributors() and \
                fileObj.Contributors()[0] or fileObj.Creator()
        rep_tool.save(fileObj, comment, { \
                "byte_size": byte_size, "title": fileObj.Title(),\
                "principal": currentContributor})
        history = rep_tool.getHistory(fileObj)
        portal_membership = getToolByName(self.context, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()

        zpath = '/'.join(fileObj.getPhysicalPath())
        ext = zpath.split(".")[-1]
        archiveName = getArchiveTime(history[0]) + "." + ext
        tramline_archive_params = '|'.join((zpath, member.getId(),archiveName, comment))
        self.request.response.setHeader("tramline_archive", tramline_archive_params)

    
        if file_from_request:
            if hasattr(fileObj, 'setFile'):
                fileObj.setFile(file_from_request)
            else:
                fileObj.setImage(file_from_request)
                
        if form.has_key("description"):
            fileObj.setDescription(form["description"])

        # to get review_state and check and set
        #wtool = getToolByName(self.context, 'portal_workflow')
        #review_state = wtool.getInfoFor(fileObj, 'review_state', '')
        #if review_state == 'private':
        #    if not form.has_key("mark_private") or form["mark_private"] != 'on':
        #        wtool.doActionFor(fileObj, 'show')
        #else:
        #    if form.has_key("mark_private") and form["mark_private"]:
        #        wtool.doActionFor(fileObj, 'hide')

        # use the adapter to configure the subscribers
        if form.has_key('persons'):
            adapted = ISubscriptionManager(fileObj)
            adapted.setSubscribedMembers(form['persons'])
            adapted.subscribeAuthenticatedMember()
            sendNotification(self, fileObj)

        fileObj.reindexObject()

        plone_utils = getToolByName(self.context, 'plone_utils')
        msg = translate(_(u'save as new version success.', default="Save as new version  success."), context=self.request)
        plone_utils.addPortalMessage(msg, 'info')
        if fileViewUrl:
            self.request.response.redirect(fileObj.absolute_url() + '/@@' + \
                                            fileViewUrl)
        else:
            self.request.response.redirect(filerepos.absolute_url())

    def view_version(self, version_id):
        
        rep_tool = getToolByName(self.context, 'portal_repository')
        obj = self.context.aq_inner
        version_id = int(version_id)
        zpath = '/'.join(obj.getPhysicalPath())
        ext = zpath.split(".")[-1]
        old_version = rep_tool.retrieve(obj, version_id)
        archiveName = getArchiveTime(old_version) + "." + ext
        self.request.form['archive_name'] = archiveName
        old_version_file = old_version.object
        return old_version_file.download(self.request, self.request.response)


    def edit_file(self, fileViewUrl=None):
        form = self.request.form
        fileObj = self.context.aq_inner
        # info("%r" % form)

        category = fileObj.aq_parent
        filerepos = category.aq_parent
        file_from_request = form['file']

        # 移动位置
        if category.getId() != form['category']:
            cat_m = ICategoryManager(filerepos)
            fileObj = cat_m.setContentCategory(fileObj, form['category'])

        portal_membership = getToolByName(self.context, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()

        if file_from_request:
            if hasattr(fileObj, 'setFile'):
                fileObj.setFile(file_from_request)
            else:
                fileObj.setImage(file_from_request)
                
        if form.has_key("description"):
            fileObj.setDescription(form["description"])

        # to get review_state and check and set
        #wtool = getToolByName(self.context, 'portal_workflow')
        #review_state = wtool.getInfoFor(fileObj, 'review_state', '')
        #if review_state == 'private':
        #    if not form.has_key("mark_private") or form["mark_private"] != 'on':
        #        wtool.doActionFor(fileObj, 'show')
        #else:
        #    if form.has_key("mark_private") and form["mark_private"]:
        #        wtool.doActionFor(fileObj, 'hide')

        # use the adapter to configure the subscribers
        if form.has_key('persons'):
            adapted = ISubscriptionManager(fileObj)
            adapted.setSubscribedMembers(form['persons'])
            adapted.subscribeAuthenticatedMember()
            sendNotification(self, fileObj)

        fileObj.reindexObject()

        plone_utils = getToolByName(self.context, 'plone_utils')
        msg = translate(_(u'modified success.', default="Modified success."), context=self.request)
        plone_utils.addPortalMessage(msg, 'info')
        if fileViewUrl:
            self.request.response.redirect(fileObj.absolute_url() + '/@@' + \
                                            fileViewUrl)
        else:
            self.request.response.redirect(filerepos.absolute_url())


from plone.app.kss.plonekssview import PloneKSSView
from kss.core import force_unicode
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

class FileReposOperKssView(PloneKSSView):

    edit_file = ZopeTwoPageTemplateFile("edit_file.pt")
    save_new_version_pt = ZopeTwoPageTemplateFile("save_new_version.pt")
    filerepos_listing = ZopeTwoPageTemplateFile("filerepos_listing.pt")


    #@kssaction
    #def validate_file(self, files):
    #    if files == '' or len(files) < 1:
    #        error_date = translate(_(u'va_need_file', default='You must choose \
    #                a file to upload at least!'), context=self.request)
#
#        if error_date:
#            error_date = error_date.decode('utf-8', 'replace')
#            core.replaceInnerHTML(core.getSelector('parentnode', '.trackitem|.errmsgDate'), error_date)
#            core.addClass(core.getSelector('parentnodecss', '.trackitem|.errmsgDate'), 'error')


    @kssaction
    def delete_version(self, version_id):
        rep_tool = getToolByName(self.context, 'portal_repository')

        obj = self.context.aq_inner

        version_id = int(version_id)
        old_version = rep_tool.retrieve(obj, version_id)
        rep_tool.purge(obj, version_id)

        # 更新索引，以便计算配额限制
        obj.indexObject()

        zpath = '/'.join(obj.getPhysicalPath())
        ext = zpath.split(".")[-1]
        archiveName = getArchiveTime(old_version) + "." + ext
        tramline_remove_archive = '|'.join((zpath, archiveName)) 
        self.request.response.setHeader("tramline_remove_archive",tramline_remove_archive)
        ksscore = self.getCommandSet('core')
        selector = ksscore.getSelector('parentnode', 'h3')
        ksscore.deleteNode(selector)

    @kssaction
    def editFile(self, fileViewUrl=None):
        fileObj = self.context.aq_inner
        wrapperid = "shw-%s" % fileObj.UID()
        category_id = fileObj.aq_parent.getId()

        wtool = getToolByName(self.context, 'portal_workflow')
        review_state = wtool.getInfoFor(fileObj, 'review_state', '')

        the_macro = self.edit_file.macros['uploadfile']
        content = self.header_macros(the_macro=the_macro,
                private=review_state == 'private',
                category=category_id,
                fileViewUrl=fileViewUrl
                )

        content = force_unicode(content, 'utf-8')

        ksscore = self.getCommandSet('core')
        selector = ksscore.getSelector('parentnode', 'div.kssDeletionRegion')

        wrapper="""<div class="showhidewrapper" id="%s" />""" % wrapperid
        ksscore.insertHTMLBefore(selector, wrapper)
        ksscore.replaceInnerHTML('#' + wrapperid, content)
        ksscore.toggleClass(selector, classname="hideme")

    @kssaction
    def save_new_version(self, fileViewUrl=None):
        fileObj = self.context.aq_inner
        wrapperid = "shw-%s" % fileObj.UID()
        category_id = fileObj.aq_parent.getId()

        wtool = getToolByName(self.context, 'portal_workflow')
        review_state = wtool.getInfoFor(fileObj, 'review_state', '')

        the_macro = self.save_new_version_pt.macros['save_new_version']
        content = self.header_macros(the_macro=the_macro,
                private=review_state == 'private',
                category=category_id,
                fileViewUrl=fileViewUrl
                )

        content = force_unicode(content, 'utf-8')

        ksscore = self.getCommandSet('core')
        selector = ksscore.getSelector('parentnode', 'div.kssDeletionRegion')

        wrapper="""<div class="showhidewrapper" id="%s" />""" % wrapperid
        ksscore.insertHTMLBefore(selector, wrapper)
        ksscore.replaceInnerHTML('#' + wrapperid, content)
        ksscore.toggleClass(selector, classname="hideme")

    @kssaction
    def selectCategory(self):
        fileObj = self.context.aq_inner
        ## 文件是否正在编辑，被锁定
        if fileObj.getPortalTypeName() == 'Document':
           lockable = getattr(fileObj.aq_explicit, 'wl_isLocked', None) is not None
           locked = lockable and fileObj.wl_isLocked()
           if locked:
               warning = translate(_(u'warning_locked', default="This document was locked, you cann't move it."), context=self.request)
               warning = warning.decode('utf-8', 'replace')
               self.getCommandSet('plone').issuePortalMessage(warning,translate(_(u'warning'), context=self.request))
               
               ksscore = self.getCommandSet('core')
               selector = ksscore.getSelector('css', '.EVselCat')
               ksscore.toggleClass(selector, classname="hideme")
               return self.render()

        category_id = fileObj.aq_parent.getId()

        the_macro = self.edit_file.macros['edit_category']
        content = self.header_macros(the_macro=the_macro, category=category_id)

        content = force_unicode(content, 'utf-8')

        ksscore = self.getCommandSet('core')
        selector = ksscore.getSelector('samenode','')

        ksscore.insertHTMLBefore(selector, content)
        selectarea = ksscore.getSelector('css', '.categorySelect')
        ksscore.focus(selectarea)

    @kssaction
    def changeCategory(self, value):
        fileObj = self.context.aq_inner
        category = fileObj.aq_parent
        filerepos = category.aq_parent
        if category.getId() != value:
            cat_m = ICategoryManager(filerepos)
            fileObj = cat_m.setContentCategory(fileObj, value)
             
            the_macro = self.filerepos_listing.macros['fileitem']
            wtool = getToolByName(self.context, 'portal_workflow')
            review_state = wtool.getInfoFor(fileObj, 'review_state', '')
            content = self.header_macros(the_macro=the_macro, 
                    obj = fileObj,
                    review_state = review_state,
                    canEdit = 1)
            content = force_unicode(content, 'utf')

            ksscore = self.getCommandSet('core')
            file_id = '#file_%s' % fileObj.UID()
            ksscore.replaceHTML(file_id, content)

class ReviewLists(BrowserView):
    def _reviewResults(self, path):
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        review_list = portal_catalog.searchResults(
                                     path = path,
                                     portal_type = ['File', 'Image'],
                                     review_state = ['pending', 'privatepending'],
                                     sort_on = 'modified',
                                     sort_order = 'reverse',
                                     )
        results = []
        for result in review_list:
            o = result.getObject()
            if o and _checkPermission('Review portal content', o):
                results.append(result)

        return results


    def getReviewList(self, category='None'):
        """get project review lists"""
        path = '/'.join(self.context.getPhysicalPath())

        if category:
            path += '/' + category

        return self._reviewResults(path)

    def getReviewLists(self):
        """get site review lists"""
        portal_catalog = getToolByName(self.context, 'portal_catalog')
                
        active_projects = portal_catalog(portal_type='Project', review_state='active')
        paths = [p.getPath() for p in active_projects]
        
        l_result = []
        for p in active_projects:
            path = p.getPath()
            project = p.getObject()
            review_list = self._reviewResults(path)
            if review_list:
                s = (project, len(review_list))
                l_result.append(s)

        return l_result


class FileViewBase:

    def getActions(self, isShowOrHide=False):
        """
        如果SHState=None，得到对象当前工作流状态下所有的transition的字典的列表
        如果SHState=True，只得到一个关于当前对象有关保密的transition的字典
        """
        waction = getToolByName(self.context, 'portal_workflow')
        action_list = waction.listActions(object=self.context.aq_inner)
        if isShowOrHide:
            for a in action_list:
                if a['id'].find('show') != -1 or \
                                 a['id'].find('hide') != -1:
                    return a
        else:
            return [a for a in action_list if a['name'].find('Pending') == -1 \
                                and a['id'].find('show') == -1 and \
                                a['id'].find('hide') == -1 and \
                                a['id'].find('protect') == -1]
    

class FileView(BrowserView, FileViewBase):
    pass

    

class FileKssView(PloneKSSView, FileViewBase):
    file_view_pt = ZopeTwoPageTemplateFile("file_view.pt")

    @kssaction
    def changeFileState(self, transition):
        wtool = getToolByName(self.context, 'portal_workflow')
        fileObj = self.context.aq_inner
        wtool.doActionFor(fileObj, transition)
        ksscore = self.getCommandSet('core')

        change_sh_state_macro = self.file_view_pt.macros['change_sh_state']
        review_state = wtool.getInfoFor(fileObj, 'review_state', '')
        content = self.header_macros(the_macro=change_sh_state_macro,
                                     shaction=self.getActions(True),
                                     review_state=review_state)
        content = force_unicode(content, 'utf-8')
        ksscore.replaceHTML(ksscore.getSelector('css', '.change_sh_state'), content)
        
        change_other_state_macro = self.file_view_pt.macros['change_other_state']
        review_state = wtool.getInfoFor(fileObj, 'review_state', '')
        content = self.header_macros(the_macro=change_other_state_macro,
                                     otherActions=self.getActions(),
                                     review_state=review_state)
        content = force_unicode(content, 'utf-8')
        ksscore.replaceHTML(ksscore.getSelector('css', '.change_other_state'), content)
        
        file_operate_macro = self.file_view_pt.macros['file_operate']
        content = self.header_macros(the_macro=file_operate_macro,
                                     obj=fileObj)
        content = force_unicode(content, 'utf-8')
        ksscore.replaceHTML(ksscore.getSelector('css', '.file_operate'), content)

        upload_version_macro = self.file_view_pt.macros['history_version']
        content = self.header_macros(the_macro=upload_version_macro,
                                     obj=fileObj)
        content = force_unicode(content, 'utf-8')
        ksscore.replaceHTML(ksscore.getSelector('css', '.history_version'), content)
