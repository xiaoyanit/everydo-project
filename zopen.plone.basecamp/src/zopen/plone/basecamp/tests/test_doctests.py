# -*- coding: UTF-8 -*-

import unittest
from zope.testing.doctest import ELLIPSIS

from Testing.ZopeTestCase import installProduct
from Products.PloneTestCase.ptc import setupPloneSite

# don't need to install products in lib/python
installProduct('CMFPlacefulWorkflow')
installProduct('membrane')
installProduct('borg')
installProduct('PloneChat')
installProduct('SimpleAttachment')
installProduct('Ploneboard')

setupPloneSite(with_default_memberarea=0,
        extension_profiles=('zopen.plone.basecamp:default',))

from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Testing.ZopeTestCase import ZopeDocFileSuite, FunctionalDocFileSuite

class TestCase(FunctionalTestCase):
    """Passubscribers test case."""

    def _setup(self):
        super(TestCase, self)._setup()

    def _setupHomeFolder(self):
        """ 我们的网站没有home folder，重载这个函数，以便让测试能够跑下去 """
        pass

def test_suite():
    suites = [
        FunctionalDocFileSuite(
            filename,
            package='zopen.plone.basecamp',
            optionflags=ELLIPSIS,
            test_class=TestCase)

        for filename in ['README.txt']
        ]

    return unittest.TestSuite(suites)
