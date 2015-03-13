#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This file is part of the Scribee project.
"""

__author__ = 'Emanuele Bertoldi <emanuele.bertoldi@gmail.com>'
__copyright__ = 'Copyright (c) 2011 Emanuele Bertoldi'
__version__ = '0.0.1'

import os
import itertools

from pygments.token import Token
from pygments.lexers import get_lexer_by_name

from entity import Entity, DocBlock

lexer = get_lexer_by_name('python')

def get_module(filename):
    if not filename or not os.path.exists(filename):
        return None

    root, ext = os.path.splitext(filename)

    parent_filename, sep, module_name = root.replace('\\', '/').rpartition('/')

    if module_name == "__init__":
        parent_filename, sep, module_name = parent_filename.rpartition('/')

    if not ext:
        filename = "/".join((filename, "__init__.py"))
        if not os.path.exists(filename):
            return None

    parent = get_module(parent_filename)

    return Entity.get_or_create(module_name, Entity.Types.Namespace, sources=[filename], parent=parent)

def parse(file):
    content = "\n".join(file)
    tokens = lexer.get_tokens(content)
    return parseTokens(tokens, file.filename())
    
def parseTokens(tokens, filename):
    start = len(Entity.entities)

    module = get_module(filename)        

    token_rows = splitTokenRows(tokens)

    findMembers(token_rows, filename, module)

    return len(Entity.entities) - start
        
def splitTokenRows(tokens):
    token_rows = []
    token_row = []

    for token in tokens:
        type = token[0]
        content = token[1]

        if type == Token.Text and content == "\n":
            if len(token_row) > 0:
                token_rows.append(token_row)
                token_row = []

        else:
            token_row.append(token)

    return token_rows

def findMembers(token_rows, filename, parent, row_cursor = 0, block_space = 0):    
    out = False
    current_row = row_cursor

    # Analyze tokens, row by row.
    while (current_row < len(token_rows)):
        token_row = token_rows[current_row]

        def token_streamer():
            for t in token_row:
                yield t

        tokens = token_streamer()

        spacing = True
        space = 0

        for token in tokens:
            type = token[0]
            content = token[1]

            if type == Token.Text and spacing:
                space += len(content)

            else:
                spacing = False

                if block_space == space:

                    if type == Token.Keyword.Namespace:
                        # Skip the current row.
                        break

                    if type == Token.Name.Function:
                        entity = Entity.get_or_create(content, Entity.Types.Function, sources=[filename], parent=parent)
                        findArguments(tokens, filename, entity)
                        findDoc(token_rows[current_row + 1], filename, entity)
                        appendFunction(entity, parent)
                        
                    elif type == Token.Name.Class:
                        entity = Entity.get_or_create(content, Entity.Types.Class, sources=[filename], parent=parent)
                        findDoc(token_rows[current_row + 1], filename, entity)
                        findMembers(token_rows, filename, entity, current_row + 1, space + 4)
                        appendClass(entity, parent)
                        
                    elif type == Token.Name:
                        entity = Entity.get_or_create(content, Entity.Types.Variable, sources=[filename], parent=parent)
                        entity.value = None
                        findAssignment(tokens, filename, entity)
                        appendVariable(entity, parent)

                    elif type == Token.Literal.String.Doc:
                        doc = DocBlock.get_or_create(content, source=filename, parent=parent)

                elif space < block_space:
                    out = True
                    break

        if out:
            break

        current_row += 1

def findAssignment(tokens, filename, parent):
    assignment = False

    for token in tokens:
        type = token[0]
        content = token[1]
        
        if type == Token.Punctuation and content == ',':
            break

        elif type == Token.Operator and content == '=':
            assignment = True

        elif assignment and type in [Token.Literal.Number.Integer, Token.Name.Builtin.Pseudo]: 
            parent.value = content

def findArguments(tokens, filename, parent):
    # Find open bracket.
    for token in tokens:
        type = token[0]
        content = token[1]
        
        if type == Token.Punctuation and content == '(':
            break

    # Find all arguments before the first close bracket.
    for token in tokens:
        type = token[0]
        content = token[1]

        if type == Token.Punctuation and content == ')':
            break
        
        elif type == Token.Name:
            argument = Entity.get_or_create(content, Entity.Types.Variable, sources=[filename], parent=parent)
            argument.value = None
            findAssignment(tokens, filename, argument)
            appendArgument(argument, parent)

def findDoc(tokens, filename, parent):
    doc = None

    for token in tokens:
        type = token[0]
        content = token[1]

        if type == Token.Literal.String.Doc:
            doc = DocBlock.get_or_create(content, source=filename, parent=parent)

    return doc

def appendClass(entity, parent):
    if parent:
        if not hasattr(parent, "classes"):
            parent.classes = []
        parent.classes.append(entity)

def appendFunction(entity, parent):
    if parent:
        if not hasattr(parent, "functions"):
            parent.functions = []
        parent.functions.append(entity)

def appendVariable(entity, parent):
    if parent:
        if not hasattr(parent, "variables"):
            parent.variables = []
        parent.variables.append(entity)

def appendArgument(entity, parent):
    if parent:
        if not hasattr(parent, "arguments"):
            parent.arguments = []
        parent.arguments.append(entity)
