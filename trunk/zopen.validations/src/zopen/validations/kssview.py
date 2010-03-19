# -*- encoding: UTF-8 -*-

#from plone.app.kss.plonekssview import PloneKSSView
from kss.core import KSSView
from kss.core import force_unicode
from utils import errorFirmName, errorURL, errorFullName, errorPhone, errorEmail, errorUserName, errorPassword, errorConfirmPassword, errorLocation

class KSSView(KSSView):

    def validateFirmName(self, firmname):
        """ validate firmname"""
        error = errorFirmName(firmname)
        core = self.getCommandSet('core')
        core.replaceInnerHTML(core.getSelector('parentnodecss', '.field|.errmsg'), error)
        if not error:
           core.removeClass(core.getSelector('parentnodecss', '.field|.errmsg'), 'error')
           core.removeClass(core.getSelector('parentnodecss', '.field|.formHelp'), 'hidden')
        else:
           core.addClass(core.getSelector('parentnodecss', '.field|.errmsg'), 'error')
           core.addClass(core.getSelector('parentnodecss', '.field|.formHelp'), 'hidden')
        return self.render()

    def validateLocation(self, location):
        """ validate firmname"""
        error = errorLocation(location)
        core = self.getCommandSet('core')
        core.replaceInnerHTML(core.getSelector('parentnodecss', '.field|.errmsg'), error)
        if not error:
           core.removeClass(core.getSelector('parentnodecss', '.field|.errmsg'), 'error')
           core.removeClass(core.getSelector('parentnodecss', '.field|.formHelp'), 'hidden')
        else:
           core.addClass(core.getSelector('parentnodecss', '.field|.errmsg'), 'error')
           core.addClass(core.getSelector('parentnodecss', '.field|.formHelp'), 'hidden')
        return self.render()


    def validateURL(self, urlname):
        """ validate url"""
        error = errorURL(urlname.lower(),self.context)
        core = self.getCommandSet('core')
        core.replaceInnerHTML(core.getSelector('parentnodecss', '.field|.errmsg'), error)
        if not error:
           core.removeClass(core.getSelector('parentnodecss', '.field|.errmsg'), 'error')
           core.removeClass(core.getSelector('parentnodecss', '.field|.formHelp'), 'hidden')
        else:
           core.addClass(core.getSelector('parentnodecss', '.field|.errmsg'), 'error')
           core.addClass(core.getSelector('parentnodecss', '.field|.formHelp'), 'hidden')
        return self.render()

    def validateFullName(self, fullname):
        """ validate fullname"""
        error = errorFullName(fullname)
        core = self.getCommandSet('core')
        core.replaceInnerHTML(core.getSelector('parentnodecss', '.field|.errmsg'), error)
        if not error:
           core.removeClass(core.getSelector('parentnodecss', '.field|.errmsg'), 'error')
           core.removeClass(core.getSelector('parentnodecss', '.field|.formHelp'), 'hidden')
        else:
           core.addClass(core.getSelector('parentnodecss', '.field|.errmsg'), 'error')
           core.addClass(core.getSelector('parentnodecss', '.field|.formHelp'), 'hidden')
        return self.render()

    def validatePhone(self, userphone):
        """ validate phone"""
        error = errorPhone(userphone)
        core = self.getCommandSet('core')
        core.replaceInnerHTML(core.getSelector('parentnodecss', '.field|.errmsg'), error)
        if not error:
           core.removeClass(core.getSelector('parentnodecss', '.field|.errmsg'), 'error')
           core.removeClass(core.getSelector('parentnodecss', '.field|.formHelp'), 'hidden')
        else:
           core.addClass(core.getSelector('parentnodecss', '.field|.errmsg'), 'error')
           core.addClass(core.getSelector('parentnodecss', '.field|.formHelp'), 'hidden')
        return self.render()

    def validateEmail(self, useremail):
        """ validate email"""
        error = errorEmail(useremail)
        core = self.getCommandSet('core')
        core.replaceInnerHTML(core.getSelector('parentnodecss', '.field|.errmsg'), error)
        if not error:
           core.removeClass(core.getSelector('parentnodecss', '.field|.errmsg'), 'error')
           core.removeClass(core.getSelector('parentnodecss', '.field|.formHelp'), 'hidden')
        else:
           core.addClass(core.getSelector('parentnodecss', '.field|.errmsg'), 'error')
           core.addClass(core.getSelector('parentnodecss', '.field|.formHelp'), 'hidden')
        return self.render()


    def validateUserName(self, username):
        """ validate user name"""
        error = errorUserName(username)
        core = self.getCommandSet('core')
        core.replaceInnerHTML(core.getSelector('parentnodecss', '.field|.errmsg'), error)
        if not error:
           core.removeClass(core.getSelector('parentnodecss', '.field|.errmsg'), 'error')
           core.removeClass(core.getSelector('parentnodecss', '.field|.formHelp'), 'hidden')
        else:
           core.addClass(core.getSelector('parentnodecss', '.field|.errmsg'), 'error')
           core.addClass(core.getSelector('parentnodecss', '.field|.formHelp'), 'hidden')
        return self.render()

    def validatePassword(self, userpassword):
        """validate password"""
        error = errorPassword(userpassword)
        core = self.getCommandSet('core')
        core.replaceInnerHTML(core.getSelector('parentnodecss', '.field|.errmsg'), error)
        if not error:
           core.removeClass(core.getSelector('parentnodecss', '.field|.errmsg'), 'error')
           core.removeClass(core.getSelector('parentnodecss', '.field|.formHelp'), 'hidden')
        else:
           core.addClass(core.getSelector('parentnodecss', '.field|.errmsg'), 'error')
           core.addClass(core.getSelector('parentnodecss', '.field|.formHelp'), 'hidden')
        return self.render()

    def validateConfirmPassword(self, userpassword, confirmpassword):
        """ validate Confirm password"""
        error = errorConfirmPassword(userpassword, confirmpassword)
        core = self.getCommandSet('core')
        core.replaceInnerHTML(core.getSelector('parentnodecss', '.field|.errmsg'), error)
        if not error:
           core.removeClass(core.getSelector('parentnodecss', '.field|.errmsg'), 'error')
           core.removeClass(core.getSelector('parentnodecss', '.field|.formHelp'), 'hidden')
        else:
           core.addClass(core.getSelector('parentnodecss', '.field|.errmsg'), 'error')
           core.addClass(core.getSelector('parentnodecss', '.field|.formHelp'), 'hidden')
        return self.render()

        
