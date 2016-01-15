import os, subprocess, glob
import re
import webbrowser, requests
import random


class flickr_browse():
    """Access images using Flickr API"""
    _API_KEY='6fb8c9ee707ff3eb8c610d4bfba9ddaf'
    BASE_URL='https://api.flickr.com/services/rest/?method=flickr.photos.search'

    def __init__(self, text='', outdir='.'):
        self.outdir = outdir
        if text:
            # get random images matching given keyword using Flickr's API
            # construct dictionary of arguments and use to construct URL to curl
            d_args = { 'api_key': self._API_KEY, \
                       'format': 'json', \
                       'nojsoncallback': '1', \
                       # safe search off
                       'safe_search': '3', \
                       # sort by mysterious flickr algorithm for 'interestingness'
                       'sort': 'interestingness-desc', \
                       # maximum number of search results
                       'per_page': '500', \
                       # text to search (all fields)
                       'text': text.replace(' ','+') }
            args = ''.join( '&{}={}'.format(k,v) for k,v in d_args.items() )
            curled = subprocess.check_output("curl \
            '{}{}'".format( self.BASE_URL, args ), shell = True)

        # TODO: other ways to search flickr? (by geotag, etc)
        else:
            pass

        # create hit list from returned json, ignoring header text
        self.l_hits = [ img.split(",") for img in curled.split('{') ][3:]


    def random(self, pop_open=True, write=False):
        """Returns random hit from among list of hits"""
        random_hit = random.choice(self.l_hits)
        # parse hit for relevant data and use to contruct image URL
        d_hit = dict( t for t in ( tuple( txt.strip('"') for txt in elem.split(':') ) \
                                  for elem in random_hit ) if len(t) == 2 )
        # image sizes, in increasing order from small square (75x75)
            # through large (1024 longest side)
        sizes = ['s','t','m','z','b']
        d_hit['size'] = sizes[-1]
        hit_url = 'https://farm{}.staticflickr.com/{}/{}_{}_{}.jpg'\
              .format( *( d_hit[key] for key in ['farm','server','id','secret','size'] ) )

        if pop_open:
            # open in new Chrome tab
            #webbrowser.get("open -a /Applications/Google\ Chrome.app %s").open(hit_url, new=2)

            # open in default browser (new tab if possible)
            webbrowser.open(hit_url, new=2)

        if write:
            # write image data to file in directory specified by global PATH_OUT
            outfile = outfile_path( self.outdir, '{}.jpg'.format(d_hit['id']) )
            with open(outfile, "w") as file_out:
                file_out.write( requests.get(hit_url).content )

        return hit_url



def outfile_path(path_to_dir, filename):
    """Given directory and desired filename, returns path to outfile that will not overwrite existing file/s by appending '_<i>' to filename"""
    # only alter filename if necessary to avoid clobbering preexisting file
    if glob.glob( os.path.join(path_to_dir, filename) ):
        i = 1
        # add '_<i>' before file suffix
        filename = re.sub('(\.[^\.]*)$', r'_{}\1'.format(i), filename)
        # continually check for pre-existing file
        while glob.glob( os.path.join(path_to_dir, filename) ):
            # update i in filename
            filename = re.sub('_[0-9]*(\.[^\.]*)$', r'_{}\1'.format(i), filename)
            # ^^ 'r' for raw string to enable back-referencing
            i += 1

    return os.path.join(path_to_dir, filename)
