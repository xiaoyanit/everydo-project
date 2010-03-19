# -*- encoding: utf-8 -*-

import httplib, urllib

base_url = "http://svn.plone.org/svn/plone/CMFPlone/branches/3.1/skins/plone_styles/"

#base_url = '../skins/basecamp_site/'
base_url = 'resources/kupu/'
base_property = base_url + "base_properties.props"

def getFile(file_url):
    if file_url.startswith('http'):
        http, host, path = httplib.urlsplit(file_url)[:3]

        if http == 'https':
            conn = httplib.HTTPSConnection(host)
        else:
            conn = httplib.HTTPConnection(host)

        conn.request("GET", path)
        response = conn.getresponse()
        return response.read().strip() 
    else:
        return open(file_url).read().strip()

def parseProperty(source):
    lines = source.split('\n')
    ppts = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        k, v = line.split('=', 1)
        k = k.split(':', 1)[0]
        ppts[k] =v.replace('"', '&quot;')
    return ppts

def buildCSSReg(ppts):
    cssregs = []
    for k,v in ppts.items():
        cssregs.append('<property name="%s" value="%s" />' % (k, v))

    return """<configure
    xmlns:zope="http://namespaces.zope.org/zope"
    xmlns="http://namespaces.zope.org/browser"
    xmlns:z3c="http://namespaces.zope.org/z3c"
    i18n_domain="zopen.edo.oc.portal">

<cssregistry name="base_properties"
               layer=".layer.IZopenCSSLayer">
            %s
            </cssregistry>
</configure>""" % ('\n'.join(cssregs))

def convertDTML(source):
    lines = source.split('\n')
    nlines = []
    for line in lines:
        #if line[:2] in ['/*', '**', '*/']:
        #    continue
        line = line.strip()
        line = line.replace('<dtml-var ', '')
        line = line.replace('>', '')
        line = line.replace(';;', ';')
        line = line.replace('; ', ' ')
        line = line.replace('&dtml-', '')
        line = line.replace('portal_url;/', '')
        line = line.replace(' missing="16em"', '')
        nlines.append(line)

    return """
    /* zrt-cssregistry: base_properties */
    %s
    """ % ('\n'.join(nlines))

#print 'base_property ...'
#open('baseproperty.zcml','w').write( buildCSSReg( parseProperty(getFile(base_property)) ))

for filename in ['kupuplone.css','kupucontentstyles.css', 'kupudrawerstyles.css']:
#for filename in ['public.css','base.css', 'forms.css']:
    print filename, ' ...'
    open('css/' + filename, 'w').write( convertDTML(getFile(base_url + filename + '.dtml')) )

