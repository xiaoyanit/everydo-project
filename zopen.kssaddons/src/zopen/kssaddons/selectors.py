# -*- encoding: utf-8 -*-

from kss.base.selectors import Selector

class parentnodecss(Selector):
    type = 'parentnodecss'

    def __init__(self, value):
        self.value = value

