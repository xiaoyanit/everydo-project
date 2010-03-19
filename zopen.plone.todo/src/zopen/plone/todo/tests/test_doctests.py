import os, sys

import unittest
from zope.testing.doctest import ELLIPSIS

from Testing.ZopeTestCase import installProduct
from Products.PloneTestCase.ptc import setupPloneSite

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
                ['zopen.plone.todo'], stoponerror=True)

def test_suite():
    suites = [
        FunctionalDocFileSuite(
            filename,
            package='zopen.plone.todo',
            optionflags=ELLIPSIS,
            test_class=TestCase)

        for filename in ['README.txt']
        ]

    return unittest.TestSuite(suites)
