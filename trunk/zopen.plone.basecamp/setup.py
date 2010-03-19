################################
import os
import xml.sax.saxutils
from setuptools import setup, find_packages

def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    return xml.sax.saxutils.escape(text)

setup (
    name='zopen.plone.basecamp',
    version='0.1.1dev',
    author = "Benky",
    author_email = "benky52@gmail.com",
    description = "everydo site manage",
    long_description=(
        read('readme.txt')
        + '\n\n' +
        read ('changes.txt')
        ),
    license = "Private",
    keywords = "zope3 z3c rpc server client operation",
    classifiers = [
        'Development Status :: 4 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Natural Language :: Chinese',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://epk.zopen.cn/pypi/zopen.edo.basecamp',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages= ['zopen','zopen.plone'],
    extras_require = dict(
        
	    test = ['z3c.coverage',
                'z3c.testing',
                'docutils',
                'zope.app.appsetup',
                'zope.app.authentication',
                'zope.app.component',
                'zope.app.keyreference',
                'zope.app.publication',
                'zope.app.schema',
                'zope.app.testing',
                'zope.i18n',
                'zope.publisher',
                'zope.schema',
                'zope.security',
                'zope.securitypolicy',
                'zope.session',
                'zope.testing',
                'zope.testbrowser',
                ]
        ),
    install_requires = [
    "zopen.kssaddons",
    "zopen.plone.subscription",
    "zopen.plone.project",
    "zopen.plone.org",
    "zopen.plone.widgets",
    "zopen.plone.messageboard",
    "zopen.plone.milestone",
    "zopen.plone.todo",
    "zopen.plone.writeboard",
    "zopen.plone.timetracker",
    "zopen.plone.chat",
    "zopen.plone.filerepos",
    "zopen.validations",
    "z3ext.cssregistry"
        ],
    zip_safe = False,
)
