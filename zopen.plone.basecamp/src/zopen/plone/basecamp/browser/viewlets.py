# -*- encoding: utf-8 -*-

from zope.viewlet.viewlet import CSSViewlet, JavaScriptViewlet, ViewletBase

SkinCSSViewlet = CSSViewlet('zopen.css')
SkinJSViewlet = JavaScriptViewlet('zopen.js')
KSSJSViewlet = JavaScriptViewlet('kss.js')
SkinKSSViewlet = CSSViewlet('zopen.kss', rel='kinetic-stylesheet')
HideLeftCSSViewlet = CSSViewlet('hideleft.css')
HideRightCSSViewlet = CSSViewlet('hideright.css')

