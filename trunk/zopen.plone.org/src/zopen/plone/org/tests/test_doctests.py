import os, sys

import unittest
from zope.testing.doctest import ELLIPSIS

from Testing.ZopeTestCase import installProduct
from Products.PloneTestCase.ptc import setupPloneSite

installProduct('CMFPlacefulWorkflow')
installProduct('membrane')
installProduct('borg')
# don't need to install products in lib/python
setupPloneSite()

from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.setup import _createObjectByType
from Testing.ZopeTestCase import ZopeDocFileSuite, FunctionalDocFileSuite

class TestCase(FunctionalTestCase):
    """Passubscribers test case."""

    def _setup(self):
        super(TestCase, self)._setup()
        self.portal.portal_quickinstaller.installProducts(
                ['CMFPlacefulWorkflow', 'membrane', 'zopen.plone.org',], stoponerror=True)

def test_suite():
    suites = [
        FunctionalDocFileSuite(
            filename,
            package='zopen.plone.org',
            optionflags=ELLIPSIS,
            test_class=TestCase)

        for filename in ['team.txt', 'borgext.txt']
        ]

    return unittest.TestSuite(suites)
