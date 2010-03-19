from zope.interface import implements
from zope.component import getUtility

from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

class SiteSettingsView(BrowserView):

    def saveLogo(self, site_logo=''):
        portal = self.context.portal_url.getPortalObject()

        owner_company = portal.companies.owner_company
        if site_logo:
            owner_company.setLogo(site_logo)

        if self.request.form.has_key('logoInWhiteBox'):
            owner_company.setLogoInWhiteBox(True)
        else:
            owner_company.setLogoInWhiteBox(False)
        self.request.response.redirect('prefs_site_settings')

    def changeTitle(self, site_name):
        portal = self.context.portal_url.getPortalObject()
        portal.setTitle(site_name)
        self.request.response.redirect('prefs_site_settings')

    def deleteLogo(self):
        portal = self.context.portal_url.getPortalObject()
        owner_company = portal.companies.owner_company
        owner_company.setLogo("DELETE_IMAGE")
        self.request.response.redirect('prefs_site_settings')

    def selectTheme(self, theme):
        portal = self.context.portal_url.getPortalObject()
        if not portal.hasProperty('theme'):
            portal.manage_addProperty('theme', '1','string')
       
        portal.manage_changeProperties(theme=theme)
        self.request.response.redirect('prefs_site_settings')

     
    def setDefaultLanguage(self, langCode):
        """Sets the default language."""
        portal_properties = getToolByName(self, "portal_properties")
        site_properties = portal_properties.site_properties
        if site_properties.hasProperty('default_language'):
            site_properties._updateProperty('default_language', langCode)

        self.request.response.redirect('prefs_site_settings')
       
