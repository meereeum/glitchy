#!/usr/bin/env python

###############################################################################
#
# __glitch_random__.py - Given image as input, glitch at random by selecting
# a random chunk of the file and inserting in a random number of times in
# another place!
#
###############################################################################
# #
# This program is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or #
# (at your option) any later version. #
# #
# This program is distributed in the hope that it will be useful, #
# but WITHOUT ANY WARRANTY; without even the implied warranty of #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the #
# GNU General Public License for more details. #
# #
# You should have received a copy of the GNU General Public License #
# along with this program. If not, see <http://www.gnu.org/licenses/>. #
# #
###############################################################################

__author__ = "Miriam Shiffman"
__copyright__ = "Copyright 2015"
__credits__ = ["Miriam Shiffman"]
__license__ = "GPL3"
__version__ = "0.0.1"
__maintainer__ = "Miriam Shiffman"
__email__ = "meereeum@gmail.com"
__status__ = "Development"

###############################################################################

import utils
import random
import re
import os, sys, getopt
import webbrowser, requests
from PIL import Image
from collections import Counter, defaultdict
from StringIO import StringIO

###############################################################################
###############################################################################
###############################################################################
###############################################################################

class glitch():
    """Glitchable object class"""

    MAX_CHUNK = 300

    def __init__(self, path, from_file=False, outdir='.'):
        """Given path to image (local file or URL), initialize glitchable object"""
        self.path = path
        self.from_file = from_file
        self.outdir = outdir

        if self.from_file:
            self.data = self.read_from_file(path)
            self.name = os.path.basename(self.path)

        # if not from_file, path is a URL to image online
        else:
            self.data = requests.get(path).content
            # use regex to extract name (id) for image from end of URL
            # after final backslash (greedy match) but before '_'
            self.name = '{}.jpg'.format( re.sub(r'^.*/([^\_]*).*$', r'\1', path) )

        self.change_log = []
        # add '.glitched' before file suffix
        self.glitchname = re.sub('(\.[^\.]*)$', r'.glitched\1', self.name)


    def __repr__(self):
        """Print image name and description of changes (glitches, any output to file)"""
        return '\n*~~~~~*~********~*********~***********~~~~~******\n' + \
            'Hey {}... get glitchy with it'.format(self.name) + \
            '\n*~~~~~*~********~*********~***********~~~~~******\n' + \
            '\n'.join(self.change_log) + '\n'


    def read_from_file(self, path_to_file):
        """Read in image data from local file"""
        with open(path_to_file, "r") as file_in:
            return file_in.read()


    def write_to_file( self, pop_open=True ):
        """Write glitch art to file"""
        outfile = utils.outfile_path(self.outdir, self.glitchname)

        with open(outfile, "w") as file_out:
            file_out.write(self.data)
            self.change_log.append('>>>>>>>>>>>>> {}'.format(file_out.name))
        print self

        # After printing to file, remove this line from changelog to reset for future files
        self.change_log = self.change_log[:-1]

        if pop_open:
            # TODO: ranked webbrowser opener ?
            # open in new Chrome tab
            #webbrowser.get("open -a /Applications/Google\ Chrome.app %s").open(outfile, new=2)
            webbrowser.get("open -a /Applications/Firefox.app %s").open(outfile, new=2)

            # open in default browser (new tab if possible)
            #webbrowser.open(outfile, new=2)


    def reset(self):
        """Restarts glitch object from scratch (original source image and empty changelog)"""
        self.__init__(path=self.path, from_file=self.from_file, outdir=self.outdir)
        print '\n{}, looking fresh\n'.format(self.name)
        #print self.change_log


    def is_broken(self):
        # TODO: use PIL to check for broken images and stop glitching if already broken
        # i.e. try/except with Image.open(<path>).verify()
        # only perhaps find way to test image data itself without writing to file?
        pass


    def _random_chunk(self, max_chunk = MAX_CHUNK):
        """Return random chunk of image data and tuple of start/endpoints,
        with optional parameter for max size - output: [ str, (int, int) ]"""
        splice_origin = random.randint(0, len(self.data))
        splice_end = random.randint(splice_origin, splice_origin + max_chunk)
        return [self.data[splice_origin : splice_end], (splice_origin, splice_end)]


    def genome_rearrange(self, max_n=5, max_chunk = MAX_CHUNK):
        """Glitch according to rules of basic genome rearrangement:
        splice chunk, n times, into another location"""
        n = random.randint(1, max_n)
        site = random.randint(0, len(self.data))
        [chunk, (a, b)] = self._random_chunk(max_chunk)

        self.data = self.data[:site] + chunk*n + self.data[site:]

        # update change log
        self.change_log.append('Chunk of {} char ({} to {}) moved to {}, x{}'\
                            .format(b - a, a, b, site, n))


    def digit_increment(self, max_chunk = MAX_CHUNK, max_n=1):
        """Glitch by incrementing all digits in random data chunk by n (mod 10)"""
        n = random.randint(1, max_n)
        [chunk, (a, b)] = self._random_chunk(max_chunk)

        self.data = self.data[:a] + \
                    ''.join( str( (int(x)+n) % 10 ) if x.isdigit() else x for x in chunk ) + \
                    self.data[b:]

        self.change_log.append('Digits in chunk of {} char ({} to {}) incremented by {}'\
                            .format(b - a, a, b, n))


    #def pil_import(self):
        #"""Read globj data into object that can be manipulated using Python Image Library and set relevant attributes"""
        #self.img = Image.open(StringIO(self.data))
        #self.size = self.img.size


    def pixel_sort(self, by_dist=False):
        """Sort pixels by frequency and, optionally, by Euclidean distance (within a given frequency)"""
        # Read globj data into PIL Image object
        self.img = Image.open(StringIO(self.data))
        # overrwrite glitchname to add '.pixelsorted' before file suffix
        self.glitchname = re.sub('(\.[^\.]*)$', r'.pixelsorted\1', self.name)

        # Generate list of tuples representing pixel (R,G,B)s
        pixels = [t for t in self.img.getdata()]
        pixels_sorted = []
        # Count pixel frequency, sorted from most to least common
        #TODO: also sort by Euclidean distance (within each freq)
        if not by_dist:
            for pixel, n in Counter(pixels).most_common():
                # Add each pixel to list of sorted pixels according to its frequency
                pixels_sorted.extend([pixel]*n)
        if by_dist:
            def eucl_dist(p1, p2):
                return sum( abs(x1-x2) for x1,x2 in zip(p1,p2) )
            d = Counter(pixels)
            #TODO: ordered defaultdict to sequentially add pixels to dictionary according to distance from random starting seed within each freq category?
        self.new_img = Image.new(self.img.mode, self.img.size)
        self.new_img.putdata(pixels_sorted)
        #self.new_img.show()

        # create StringIO object to store output of converting Image object back to JPEG
        output = StringIO()
        self.new_img.save(output, format='JPEG')
        self.data = output.getvalue()
        self.change_log.append('Pixels sorted by frequency')



###############################################################################
###############################################################################
###############################################################################
###############################################################################

def glitch_routine(globj):
    """Given glitchable object (globject), applies several rounds of glitching and prints changes as files (and opens in tabs)"""
    # five rounds of attempts to create glitch art per image (from scratch)
    for i in xrange(5):
        # three rounds of incremental glitching per glitched image
        for j in xrange(3):
            globj.digit_increment(max_chunk = 1000, max_n = 4)
            globj.genome_rearrange()
            globj.write_to_file()
        globj.reset()
    # also implement pixel sort
    globj.pixel_sort()
    globj.write_to_file()


def doWork_flickr(key, outdir, n=5):
    hits = utils.flickr_browse(text=key, outdir=outdir)
    # n random images from flickr search as seeds
    for i in xrange(n):
        rando = hits.random( write = True )
        glitch_routine( glitch(rando, from_file=False, outdir=outdir) )


def doWork_file(filename, outdir):
    glitch_routine( glitch(filename, from_file=True, outdir=outdir) )


def usage():
    txt = """
    ./glitch_random.py --mode=(flickr|file) --input=(keyword|filename)
                        [--output=output_directory]

    --input is keyword if in flickr mode OR path/to/file if in file mode
    --output defaults to "."
    """
    print(txt)
    return


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hm:i:o:", ["help",
                                                         "mode=",
                                                         "input=",
                                                         "output="])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit()

    modes = ("flickr", "file")

    # defaults
    mode = None
    input_arg = None
    output_dir = "."

    # switch on our options
    for o, initial_a in opts:
        a = re.sub('^=','',initial_a)
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-m", "--mode"):
            if a in modes:
                mode = a
            else:
                usage()
                sys.exit()
        elif o in ("-i", "--input"):
            # TODO: multiple keywds ??
            input_arg = a
        elif o in ("-o", "--output"):
            output_dir = a

    # if no mode is specified
    if not mode or not input_arg:
        usage()
        sys.exit()

    # change the behavior based on the mode
    if mode == "flickr":
        doWork_flickr(input_arg, output_dir)
    elif mode == "file":
        doWork_file(input_arg, output_dir)

###############################################################################
###############################################################################
###############################################################################
###############################################################################

if __name__ == '__main__':
    main()
