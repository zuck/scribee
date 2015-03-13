#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This file is part of the Scribee project.
"""

__author__ = 'Emanuele Bertoldi <emanuele.bertoldi@gmail.com>'
__copyright__ = 'Copyright (c) 2011 Emanuele Bertoldi'
__version__ = '0.0.1'

import sys
import os
import fileinput

import settings

class Scribox(object):
    def __init__(self):
        self._inspectors = getattr(settings, "INSPECTORS", {})
        self._output_dir = getattr(settings, "OUTPUT_DIR", 'output')
        self._verbose = getattr(settings, "VERBOSE", False)
        self._cache_sources = []
        
    def generate(self, sources=[], renderers=getattr(settings, "RENDERERS", {})):
        from entity import Entity, DocBlock

        # Clear buffers.
        Entity.entities = []
        DocBlock.blocks = []
        self._cache_sources = []

        # Start a new generation.
        print 'SCRIBOX ----- ver %s' % __version__
        print '======================='
        print 'Searching for entities...'
        for source in sources:
            self.parse_file(source)
            sys.stdout.flush()
        print 'Found a total of %d entity/ies.' % len(Entity.entities)
        for format, renderer in renderers.items():
            print 'Generating contents in "%s" format...' % format,
            renderer.render(Entity.entities, self._output_dir)
            print "Done."
        print 'Generated %d format/s.' % len(renderers)
            
    def parse_file(self, filename=''):
        filename = filename.replace('\\', '/').replace('//', '/')

        if filename not in self._cache_sources:
            self._cache_sources.append(filename)
        
            # File not found.
            if not os.path.exists(filename):
                return
                
            # File.
            elif os.path.isfile(filename):
                root, ext = os.path.splitext(filename)
                
                # Inspector not found for this extension.
                if not self._inspectors.has_key(ext):
                    if self._verbose:
                        print "Skipped %s." % filename
                    return
                    
                inspector = self._inspectors[ext]
                f = fileinput.input(filename)
                print "Inspecting %s..." % filename,
                sys.stdout.flush()
                new_entities_count = inspector.parse(f)
                print "Found %d entity/ies." % new_entities_count
                    
            # Directory.
            elif os.path.isdir(filename):
                os.path.walk(filename, self.parse_dir, [])
            
    def parse_dir(self, arg, dirname, fnames):
        for filename in fnames:
            pathname = '/'.join([dirname, filename])
            self.parse_file(pathname)

if __name__ == "__main__":
    s = Scribox()
    s.generate(sys.argv[1:])

