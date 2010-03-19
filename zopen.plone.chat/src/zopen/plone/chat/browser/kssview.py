import random
from zope import lifecycleevent, event
from zope.component import getUtility

from Products.CMFCore.utils import getToolByName

from Products.Five import BrowserView

from kss.core import force_unicode
from plone.app.kss.plonekssview import PloneKSSView

from archetypes.kss.fields import FieldsView 
from Products.Archetypes.event import ObjectEditedEvent
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

class KssView(PloneKSSView):

    def saveChatSetting(self, description, private=False):
        context = self.context.aq_inner

        context.setDescription(description)
        wftool = getToolByName(context, 'portal_workflow')

        for obj in [context] + context.getRelatedItems():
            review_state = wftool.getInfoFor(obj, 'review_state')

            if(private != False and review_state != 'private'):
                wftool.doActionFor(obj, 'hide')
                review_state= wftool.getInfoFor(obj, 'review_state')
            elif(review_state == 'private' and private == False):
                wftool.doActionFor(obj, 'show')
                review_state= wftool.getInfoFor(obj, 'review_state')
            obj.reindexObject()

        ksscore = self.getCommandSet('core')
        content = description
        content = content.decode('utf-8')

        ksscore.toggleClass(ksscore.getSelector('parentnodecss','#chat-topic|.submit'), 'hideme' )
        ksscore.toggleClass('.TGedit', 'hideme')

        ksscore.replaceInnerHTML('#chat-topic-content', content)

        if private:
            private_note = '<span class="private_bug">保密</span>'
        else:
            private_note = '<span></span>'
        private_note = private_note.decode('utf-8')

        ksscore.replaceHTML('#chat-topic h1 span', private_note)
        return self.render()

