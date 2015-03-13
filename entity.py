#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This file is part of the Scribee project.
"""

__author__ = 'Emanuele Bertoldi <emanuele.bertoldi@gmail.com>'
__copyright__ = 'Copyright (c) 2011 Emanuele Bertoldi'
__version__ = '0.0.1'

import os

import settings

class Entity(object):
    """An Entity is a generic language-agnostic object.
    """
    class Types:
        Generic     = ""
        Namespace   = "namespace"
        Constant    = "const"
        Variable    = "var"
        Function    = "func"
        Class       = "class"

    class DuplicateEntityException(Exception):
        pass

    entities = []

    def __init__(self, name="", type="", brief="", details="", sources=[], parent=None, **kwargs):
        self.name = name
        self.type = type
        self.brief = brief
        self.details = details
        self.sources = sources
        self.parent = parent
        self.__dict__.update(kwargs)

        uid = self.uid()

        for e in Entity.entities:
            if e.uid() == uid:
                raise DuplicateEntityException
        
        Entity.entities.append(self)

    def __repr__(self):
        string = "Entity: <%s>" % self.uid()
        if self.brief != "":
            string += "\n-- brief: %s" % self.brief
        if self.details != "":
            string += "\n-- details: %s" % self.details
        return string
        
    def __str__(self):
        return self.__repr__()

    def uid(self):
        """Returns the entity's UID.
        """
        return Entity.get_uid(self.name, self.type, self.parent)
    
    def is_valid(self):
        return self.type.lower() != ""

    def ancestors(self):
        if isinstance(self.parent, Entity):
            return self.parent.ancestors() + [self.parent]
        return []

    def children(self, types=None):
        if not isinstance(types, (list, tuple)):
            types = (types)

        return [e for e in Entity.entities if e.parent == self and (not types or e.type in types)]

    @classmethod
    def get_uid(cls, name, type, parent):
        uid = "%s" % name
        if type:
            uid = "%s_%s" % (type, name)
            if parent:
                uid = "%s__%s" % (parent.uid(), uid)
        return uid

    @classmethod
    def nearest(cls, name, type=None, parent=None):
        # TODO: allow to search only with name and parent (without type).
        ref_uid = cls.get_uid(name, type, parent)
        ref_length = len(ref_uid)
        remaining_chars = -1
        nearest_entity = None

        for entity in Entity.entities:
            uid = entity.uid()
            if uid.endswith(ref_uid):
                rc = len(uid) - ref_length
                if remaining_chars < 0 or rc < remaining_chars:
                    remaining_chars = rc
                    nearest_entity = entity
                if rc == 0:
                    break

        return nearest_entity

    @classmethod
    def get_or_create(cls, name, type, sources=[], parent=None):
        if not name and not type:
            return None

        nearest = cls.nearest(name, type, parent)

        if not nearest:
            nearest = Entity(name, type, sources=sources, parent=parent)

        else:   
            for s in sources:
                if s not in nearest.sources:
                    nearest.sources.append(s)

        return nearest

class DocBlock(object):
    """A DocBlock is a generic piece of documentation for one or more entities.
    """
    blocks = []

    def __init__(self, content="", source="", parent=None):
        all_filters = getattr(settings, "FILTERS", {})
        root, ext = os.path.splitext(source)

        self.source = source
        self.parent = parent
        self._original = content
        self.filtered = content.strip()

        if all_filters.has_key(ext):
            for filter_list in all_filters[ext]:
                if isinstance(filter_list, dict):
                    filter_list = filters_list.values()
                elif not isinstance(filter_list, (list, tuple)):
                    filter_list = (filter_list,)
                for f in filter_list:
                    f.filter(self)

        if isinstance(parent, Entity):
            self.parent.details = self.filtered
            try:
                self.parent.brief = [l for l in self.filtered.splitlines() if l][0]
            except IndexError:
                pass

        # FIXME: does it work?
        if self not in self.__class__.blocks:
            self.__class__.blocks.append(self)

    def __repr__(self):
        string = "DocBlock:"
        string += "\n-- content: %s" % self.filtered
        if self.parent:
            string += "\n-- parent: %s" % self.parent.uid()
        return string
        
    def __str__(self):
        return self.__repr__()
    
    def is_valid(self):
        return (self._original or self.filtered)

    @classmethod
    def get_or_create(cls, content, source=None, parent=None):
        for block in cls.blocks:
            if block._original == content:
                if source and block.source != source:
                    continue
                if parent and block.parent != parent:
                    continue
                return block

        return DocBlock(content, source=source, parent=parent)
