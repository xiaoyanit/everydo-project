# -*- coding: UTF-8 -*-

import time
import os
from Products.Five import BrowserView
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from kss.core import kssaction
from Products.Archetypes.event import ObjectEditedEvent
from zope import event

from DateTime import DateTime

from zopen.plone.widgets.category.interfaces import ICategoryManager

from zope.i18nmessageid import MessageFactory
from zope.i18n import translate
_ = MessageFactory('zopen.filerepos')

# import logging; info = logging.getLogger('zopen.plone.filerepos').info


class WriteboardsView(BrowserView):

    def canAdd(self):
        context = self.context.aq_inner.aq_parent.files
        # 只有自文件夹可以添加，才显示
        return ICategoryManager(context).getCategories(addable=True)
