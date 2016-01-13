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
import sys
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

    def __init__(self, path, from_file=False):
        """Given path to image (local file or URL), initialize glitchable object"""
        self.path = path
        self.from_file = from_file

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


    def write_to_file( self, outdir, pop_open=True ):
        """Write glitch art to file"""
        outfile = utils.outfile_path(outdir, self.glitchname)

        with open(outfile, "w") as file_out:
            file_out.write(self.data)
            self.change_log.append('>>>>>>>>>>>>> {}'.format(file_out.name))
        print self

        # After printing to file, remove this line from changelog to reset for future files
        self.change_log = self.change_log[:-1]

        if pop_open:
            webbrowser.get("open -a /Applications/Google\ Chrome.app %s")\
                .open('file://localhost{}'.format(outfile), new=2) # open in new tab, if possible


    def reload(self):
        """Restarts glitch object from scratch (original source image and empty changelog)"""
        self.__init__(path = self.path, from_file = self.from_file)
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
            globj.write_to_file(outdir=PATH_OUT)
        globj.reload()
    # also implement pixel sort
    globj.pixel_sort()
    globj.write_to_file(outdir=PATH_OUT)



def doWork_flickr(key, n):
    hits = utils.flickr_browse(text = key)
    # n random images from flickr search as seeds
    for i in xrange(n):
        rando = hits.random( write = True )
        glitch_routine( glitch(rando) )



def doWork_file(img_in):
    glitch_routine( glitch(img_in, from_file = True) )



def parse_args():
    _USAGE = 'USAGE: python glitch_random.py [file, flickr] [ <path/to/file> OR <flickr keyword/s> ] [ <path/to/outdir> ]'
    global PATH_OUT

    #for i, thing in enumerate(sys.argv):
        #print '{}) {}'.format(i, thing)
#
    #return

    if len(sys.argv) == 1 or ( len(sys.argv) == 2 and sys.argv[1] in ('-h', '--help') ):
        print _USAGE
        return
    if len(sys.argv) < 4:
        raise Exception( '\n\n'.join(('Missing command-line arguments!', _USAGE)) )
    input_arg = sys.argv[1].lower()
    if input_arg not in ('file', 'flickr'):
        raise Exception( '\n\n'.join(('Specify from "file" or "flickr" keyword!', _USAGE)) )

    # specify last argument as outdir, since flickr keyword search might be >1 wd
    PATH_OUT = sys.argv[-1]

    if input_arg == 'file':
        IMG_IN = sys.argv[2]
        doWork_file(IMG_IN)

    # otherwise, input must be keyword search of Flickr
    else:
        # convert multi-wd keyword search to single key string
        KEY = ' '.join(sys.argv[2:-1])
        doWork_flickr(KEY, 2)



###############################################################################
###############################################################################
###############################################################################
###############################################################################

PATH_OUT = '.'

#KEY = 'new york city'
#IMG_IN = '/Users/miriamshiffman/Downloads/screen-shot-2015-10-08-at-105557-am.png'
#PATH_OUT = '/Users/miriamshiffman/Downloads/glitched'
#TODO: args to parse:
# -f / --file_in OR -k / --flickr_key
# -o / --outdir
# glitch_random.py <file / flickr> <path/to/file OR flickr keyword> <outdir>

if __name__ == '__main__':
    parse_args()
