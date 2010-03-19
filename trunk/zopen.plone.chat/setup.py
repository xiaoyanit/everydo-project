################################
import os
import xml.sax.saxutils
from setuptools import setup, find_packages

def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    return xml.sax.saxutils.escape(text)

setup (
    name='zopen.plone.chat',
    version='0.1.1dev',
    author = "Benky",
    author_email = "benky52@gmail.com",
    description = "Everydo chat management",
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
    url = 'http://pypi.zopen.cn/zopen.wgsiapp',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages= ['zopen', 'zopen.plone'],
    extras_require = dict(
        
	    test = ['z3c.coverage',
                'z3c.testing',
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
        ],
    zip_safe = False,
)
