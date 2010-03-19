#-*- coding:utf-8 -*-
from zope.interface import Interface

class IFileManager(Interface):
    """ """

    def validateAddAttachment(file_upload):
        """ """

    def addAttachment(context, file_upload):
        """ """
