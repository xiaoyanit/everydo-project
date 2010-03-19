from Products.Five.browser.resource import FileResource

class NewFileResource(object, FileResource): pass

# monkey patch
from z3c.resourcecollector.browser import CollectorResource
CollectorResource.__bases__ = (NewFileResource, )
CollectorResource.GET.im_func.__doc__ = 'damn zope2 need this'

from z3c.zrtresource.zrtresource import ZRTFileResource
ZRTFileResource.__bases__ = (NewFileResource, )
ZRTFileResource.GET.im_func.__doc__ = 'damn zope2 need this'
