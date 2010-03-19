from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from archetypes.kss.fields import FieldsView

FieldsView.edit_field_wrapper = ZopeTwoPageTemplateFile('edit_field_wrapper.pt')

from Products.kupu.plone.plonelibrarytool import PloneKupuLibraryTool
from Products.kupu.plone import helpers

helpers.FILTERDICT['bg-undo'] = True
helpers.FILTERDICT['undo-button'] = True
helpers.FILTERDICT['redo-button'] = True
helpers.FILTERDICT['anchors-button'] = False
helpers.FILTERDICT['linklibdrawer-button'] = False

def filterToolbar(self, context, field=None):
    return helpers.FILTERDICT

PloneKupuLibraryTool.filterToolbar = filterToolbar
from Products.CMFCore.Expression import Expression

_default_libraries = (
    dict(id="files",
         title=Expression("string:项目文件"),
         uri=Expression("string:${folder_url}/.."),
         src=Expression("string:${folder_url}/../kupucollection.xml"),
         icon=Expression("string:${folder/getIcon}") ),
    dict(id="current",
         title=Expression("string:当前位置"),
         uri=Expression("string:${folder_url}"),
         src=Expression("string:${folder_url}/kupucollection.xml"),
         icon=Expression("string:${folder/getIcon}")),
    dict(id="myitems",
         title=Expression("string:我最近提交的"),
         uri=Expression("string:${portal_url}/kupumyitems.xml"),
         src=Expression("string:${portal_url}/kupumyitems.xml"),
         icon=Expression("string:${portal_url}/kupuimages/kupusearch_icon.gif")),
    dict(id="recentitems",
         title=Expression("string:全部最近提交的"),
         uri=Expression("string:${portal_url}/kupurecentitems.xml"),
         src=Expression("string:${portal_url}/kupurecentitems.xml"),
         icon=Expression("string:${portal_url}/kupuimages/kupusearch_icon.gif"))
    )

def getLibraries(self, context):
        """See ILibraryManager"""
        expr_context = self._getExpressionContext(context)
        libraries = []
        for library in _default_libraries:
            lib = {}
            for key in library.keys():
                if isinstance(library[key], str):
                    lib[key] = library[key]
                else:
                    # Automatic migration from old version.
                    if key=='id':
                        lib[key] = library[key] = library[key].text
                    else:
                        lib[key] = library[key](expr_context)
            libraries.append(lib)
        return tuple(libraries)

PloneKupuLibraryTool.getLibraries = getLibraries
