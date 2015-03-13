#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This file is part of the Scribee project.
"""

__author__ = 'Emanuele Bertoldi <emanuele.bertoldi@gmail.com>'
__copyright__ = 'Copyright (c) 2011 Emanuele Bertoldi'
__version__ = '0.0.1'

import os, shutil
from StringIO import StringIO

from mako.lookup import TemplateLookup
from mako.template import Template
from mako.runtime import Context

from entity import Entity
import settings

def render(entities, output_dir):
    basepath = os.path.join(output_dir, "html")
    if os.path.exists(basepath):
        shutil.rmtree(basepath)

    HTML_ENTITIES_TEMPLATE = getattr(settings, "HTML_ENTITIES_TEMPLATE", "templates/entities.html")
    HTML_ENTITY_TEMPLATE = getattr(settings, "HTML_ENTITY_TEMPLATE", "templates/entity.html")
    HTML_INDEX_TEMPLATE = getattr(settings, "HTML_INDEX_TEMPLATE", "templates/index.html")
    HTML_STATIC_ROOT = getattr(settings, "HTML_STATIC_ROOT", "templates/static")

    # 1) Copies static files (it also creates <basepath>).
    shutil.copytree(HTML_STATIC_ROOT, basepath)
        
    # 2) Renders entity list page.
    render_template({'entities': entities}, os.path.join(basepath, 'entities' + ".html"), HTML_ENTITIES_TEMPLATE)
    
    # 3) Renders single entity page.
    for entity in entities:
        if not entity.parent or entity.type == Entity.Types.Class or entity.parent.type not in (Entity.Types.Class, Entity.Types.Function):
            render_template({'entity': entity}, os.path.join(basepath, entity.uid() + ".html"), HTML_ENTITY_TEMPLATE)
            
    # 4) Renders the index page.
    render_template({'entities': entities}, os.path.join(basepath, 'index' + ".html"), HTML_INDEX_TEMPLATE)
        
def render_template(context, filename, template):
    fd = open(filename, "w")
    output = render_to_string(context, template)
    fd.write(output)
    fd.close()
    
def render_to_string(context, template):
    fd = open(template, "r")
    source = fd.read()
    fd.close()
    output = StringIO()
    lookup = TemplateLookup(directories=[template.rpartition("/")[0]]) 
    ctx = Context(output, **context)
    Template(source, lookup=lookup).render_context(ctx)
    return output.getvalue()
