#!/usr/bin/env python

import os
import sys
from mapnik import render, render_to_file, save_map, Image

try:
    import cairo
    HAS_CAIRO = True
    cairo_mapping = {'svg':cairo.SVGSurface,
                'pdf':cairo.PDFSurface,
                'ps':cairo.PSSurface,
                'ARGB32':cairo.FORMAT_ARGB32,
                'RGB24':cairo.FORMAT_RGB24}

except ImportError:
    HAS_CAIRO = False


# Win32 workaround graciously provided by crschmidt
# from http://svn.tilecache.org/trunk/tilecache/TileCache/Service.py
def binaryPrint(binary_data):
    """This function is designed to work around the fact that Python
       in Windows does not handle binary output correctly. This function
       will set the output to binary, and then write to stdout directly
       rather than using print."""
    try:
        import msvcrt
        msvcrt.setmode(sys.__stdout__.fileno(), os.O_BINARY)
    except:
        pass
    sys.stdout.write(binary_data)


class Render(object):
    def __init__(self,m,image,format):
        
        self.m = m
        self.image = image
        self.format = format #kwargs.get('format','png')
        self.re_render_times = 0 #kwargs.get('re_render_times',0)
        self.world_file = None
        self.save_map = None
        
        self.ALL_FORMATS = {}
        self.AGG_FORMATS = {'png':'png','png256':'png','jpeg':'jpg'}
        self.ALL_FORMATS.update(self.AGG_FORMATS)
        self.CAIRO_FILE_FORMATS = {'svg':'svg','pdf':'pdf','ps':'ps'}
        self.ALL_FORMATS.update(self.CAIRO_FILE_FORMATS)
        self.CAIRO_IMAGE_FORMATS = {'ARGB32':'png','RGB24':'png'}
        self.ALL_FORMATS.update(self.CAIRO_IMAGE_FORMATS)

    def stream(self): 
        """
        Routine to render the an image to a string
        """
        im = Image(self.m.width,self.m.height)
        render(self.m,im)
        return im.tostring(self.format)

    def print_stream(self):
        if sys.platform == 'win32':
            binaryPrint(self.stream())
        else:
            print self.stream() 

    def local_render_wrapper(self,*args):
        """
        Abstraction wrapper for calling for map images rendered with either AGG or Cairo.
        """        
        if args[2] in self.CAIRO_FILE_FORMATS:
            self.render_cairo(*args)
        # todo: support rendering to image formats with cairo
        #elif args[2] in self.CAIRO_IMAGE_FORMATS:
            #self.render_cairo(*args)
        elif args[2] in self.AGG_FORMATS:
            self.render_agg(*args)

    def render_cairo(self,*args):
        """
        Routine to render the requested Cairo format.
        """
        if not HAS_CAIRO:
            sys.exit('PyCairo is not installed or available, therefore you cannot write to svg, pdf, ps, or cairo-rendered png')
        else:
            context = [args[1], self.m.width, self.m.height]
            if args[2] in self.CAIRO_FILE_FORMATS:
                surface = cairo_mapping[args[2]](*context)
            elif args[2] in self.CAIRO_IMAGE_FORMATS:
                surface = cairo.ImageSurface(cairo_mapping[args[2]], *context[1:])
            if self.re_render_times:
                for n in range(1, int(self.re_render_times)):
                    render(args[0],surface)
                    if args[2] in self.CAIRO_IMAGE_FORMATS:
                        surface.write_to_png(args[1])
                surface.finish()
            else:
                render(args[0],surface)
                if args[2] in self.CAIRO_IMAGE_FORMATS:
                    surface.write_to_png(args[1])
                surface.finish()
            if self.world_file:
                basename = args[1].split('.')[0]
                f_ptr = '%s.%s' % (basename, self.world_file)
                f = open(f_ptr, 'w')
                f.write(self.m.to_wld())
                f.close()
            if self.save_map:
                save_map(self.m,self.save_map)

    def call_CAIRO_FORMATS(self, basename):
        """
        Abstraction wrapper to allow for the same call
        to any image and file formats requested from Cairo.
        """
        if not HAS_CAIRO:
            sys.exit('PyCairo is not installed or available, therefore you cannot write to svg, pdf, ps, or cairo-rendered png')
        else:
            for k, v in self.CAIRO_FILE_FORMATS.iteritems():
                path = '%s_%s.%s' % (basename,k,v)
                self.render_cairo(self.m,path,k)
            for k, v in self.CAIRO_IMAGE_FORMATS.iteritems():
                path = '%s_%s.%s' % (basename,k,v)
                self.render_cairo(self.m,path,k)

    def render_agg(self,*args):
        """
        Routine to render the requested AGG format.
        """
        if self.re_render_times:
            for n in range(1, int(self.re_render_times)):
                render_to_file(*args)
        else:
            render_to_file(*args)
        if self.world_file:
            basename = args[1].split('.')[0]
            f_ptr = '%s.%s' % (basename, self.world_file)
            f = open(f_ptr, 'w')
            f.write(self.m.to_wld())
            f.close()
        if self.save_map:
            save_map(self.m,self.save_map)

    def call_AGG_FORMATS(self, basename):
        """
        Abstraction wrapper to allow for calling 
        any requested AGG Formats.
        """
        for k, v in self.AGG_FORMATS.iteritems():
            path = '%s_%s.%s' % (basename,k,v)
            self.render_agg(self.m,path,k)
           
    def render_file(self): 
        """
        Routine to render the output image(s) for all requested formats and resolutions.
        """
        dirname, basename = os.path.dirname(self.image),os.path.basename(self.image)
        if basename:
            if not True in [self.image.split('.')[-1].lower() == ext for ext in self.ALL_FORMATS]:
                sys.exit("Unrecognized format (needs .ext) or directory (needs trailing /).")
        else:
            basename_from_dir = dirname.split('/')[-1]
            if not basename_from_dir: 
                basename_from_dir = 'nik2img_output'
            if dirname == '':
                sys.exit("Must write to either file or directory")
        if not os.path.exists(dirname) and dirname != '':
            try:
                os.mkdir(dirname)
            except OSError:
                os.makedirs(dirname)
        if not dirname.endswith('/'):
            dirname = dirname + '/'
        if self.format == 'all':
            if basename:
                sys.exit("Must write to a directory/ to produce all formats")
            else:                    
                self.call_AGG_FORMATS(dirname + basename_from_dir)
                if HAS_CAIRO:
                    self.call_CAIRO_FORMATS(dirname + basename_from_dir)
        else:
            if not basename:
                self.local_render_wrapper(self.m, dirname + basename_from_dir + '.' + self.format.rstrip('256'), self.format)
            else:
                self.local_render_wrapper(self.m, self.image, self.format)