#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This file is part of the Scribee project.
"""

__author__ = 'Emanuele Bertoldi <emanuele.bertoldi@gmail.com>'
__copyright__ = 'Copyright (c) 2011 Emanuele Bertoldi'
__version__ = '0.0.1'

from pygments.token import Token
from pygments.lexers import get_lexer_by_name

from entity import Entity, DocBlock

lexer = get_lexer_by_name('cpp')

def parse(file):
    content = "\n".join(file)
    tokens = lexer.get_tokens(content)
    return parseTokens(tokens, file.filename())
    
def parseTokens(tokens, filename):
    start = len(Entity.entities)

    token_rows = splitTokenRows(tokens)

    findMembers(token_rows, filename, None)

    return len(Entity.entities) - start
        
def splitTokenRows(tokens):
    token_rows = []
    token_row = []

    for token in tokens:
        type = token[0]
        content = token[1]

        if type in (Token.Text, Token.Comment.Preproc) and content == "\n":
            if len(token_row) > 0:
                token_rows.append(token_row)
                token_row = []

        elif type == Token.Punctuation and content in ('{', '}'):
            if len(token_row) > 0:
                token_rows.append(token_row)
                token_row = []
            token_rows.append([token])

        else:
            token_row.append(token)

    return token_rows

def findMembers(token_rows, filename, parent, row_cursor = 0, wait_block = False):
    current_row = row_cursor

    inner_block = -1
    if not wait_block:
        inner_block = 0

    entity_cpp_type = None
    access_rights = "public"

    # Analyze tokens, row by row.
    while (current_row < len(token_rows)):
        token_row = token_rows[current_row]

        def token_streamer():
            for t in token_row:
                yield t

        tokens = token_streamer()

        for token in tokens:
            type = token[0]
            content = token[1]

            if type == Token.Punctuation and content == "{":
                access_rights = "protected"
                inner_block += 1

            elif type == Token.Punctuation and content == "}":
                inner_block -= 1

            elif inner_block == 0:

                if type == Token.Keyword and content in ("protected", "public", "private"):
                    access_rights = content

                elif type == Token.Keyword and content == "namespace":
                    tokens.next()               # Skips space.
                    content = tokens.next()[1]  # Captures namespace name.
                    entity = Entity.get_or_create(content, Entity.Types.Namespace, sources=[filename], parent=parent)
                    findMembers(token_rows, filename, entity, current_row + 1, True)
    
                elif type == Token.Keyword.Type:
                    entity_cpp_type = content
                    
                elif type == Token.Name.Class:
                    entity = Entity.get_or_create(content, Entity.Types.Class, sources=[filename], parent=parent)
                    entity.access_rights = access_rights
                    findDoc(token_rows[current_row - 1], filename, entity)
                    findMembers(token_rows, filename, entity, current_row + 1, True)
                    appendClass(entity, parent)
                    access_rights = "public"
                    
                elif type == Token.Name:
                    entity_type = Entity.Types.Variable
                    try:
                        next = tokens.next()
                        if next[0] == Token.Punctuation and next[1] == "(":
                            entity_type = Entity.Types.Function
                    except:
                        pass

                    entity = Entity.get_or_create(content, entity_type, sources=[filename], parent=parent)
                    entity.access_rights = access_rights
                    findDoc(token_rows[current_row - 1], filename, entity)

                    if entity_type == Entity.Types.Variable:
                        entity.var_type = entity_cpp_type
                        entity.value = None
                        appendVariable(entity, parent)

                    elif entity_type == Entity.Types.Function:
                        entity.return_type = entity_cpp_type
                        findArguments(tokens, filename, entity)
                        findDoc(token_rows[current_row - 1], filename, entity)
                        appendFunction(entity, parent)

                elif type == Token.Comment.Multiline:
                    doc = DocBlock.get_or_create(content, source=filename, parent=None)

        current_row += 1

def findArguments(tokens, filename, parent):
    argument = None
    argument_type = None
    assignment = False

    # Find all arguments before the first close bracket.
    for token in tokens:
        type = token[0]
        content = token[1]

        if type == Token.Punctuation and content == ')':
            break
        
        elif type == Token.Keyword.Type:
            argument_type = content
        
        elif type == Token.Name:
            argument = Entity.get_or_create(content, Entity.Types.Variable, sources=[filename], parent=parent)
            argument.var_type = argument_type
            argument.value = None
            appendArgument(argument, parent)
            assignment = False

        elif type == Token.Operator and content == '=':
            assignment = True

        elif type in [Token.Literal.Number.Integer, Token.Keyword.Constant] and assignment and argument:
            argument.value = content

def findDoc(tokens, filename, parent):
    doc = None

    for token in tokens:
        type = token[0]
        content = token[1]

        if type == Token.Comment.Multiline:
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
