#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This file is part of the Scribee project.
"""

__author__ = 'Emanuele Bertoldi <emanuele.bertoldi@gmail.com>'
__copyright__ = 'Copyright (c) 2011 Emanuele Bertoldi'
__version__ = '0.0.1'

from entity import Entity, DocBlock
import settings

DOXYGEN_TOKEN_CHAR = getattr(settings, "DOXYGEN_TOKEN_CHAR", "@")
DOXYGEN_ENTITY_DIRECTIVE = DOXYGEN_TOKEN_CHAR + getattr(settings, "DOXYGEN_ENTITY_DIRECTIVE", "entity") + " "

def filter(block):
    lines = block.filtered.splitlines()

    for index, line in enumerate(lines):

        if line.startswith(DOXYGEN_ENTITY_DIRECTIVE):

            # Remove next lines from the original block.
            if index > 0:
                block.filtered = "\n".join(lines[:index-1])
            else:
                block.filtered = ""
            
            # Split in a new block.
            tokens = line.split()
            if len(tokens) > 1:
                name = tokens[1]
                entity = Entity.nearest(name)
                if entity:
                    entity_doc = DocBlock.get_or_create('\n'.join(lines[index+1:]), source=block.source, parent=entity)

        else:
            pass
