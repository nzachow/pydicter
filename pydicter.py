from imdbpie import Imdb
import urllib2
import linkGrabber
import guessit
import argparse

parser = argparse.ArgumentParser(description='Scan open directories')
parser.add_argument("-l", help="The url you want to scan")
args = parser.parse_args()

# This is what allow us to search IMDB
imdb = Imdb()
imdb = Imdb(anonymize=True)

# The open movie data base url. I added it as a var instead of hardcoding it so the info displayed to the user can be changed in oneline
omdburl = 'http://www.omdbapi.com/?t='

def is_relevant_file(link):
    """
        Check the extension of the file.
        We do not want to go through all files.
        link is a dict.
        I am sure that there is a better way to do this!
    """
    if link['href'][-4:] == '.mp4':
        return True
    elif link['href'][-4:] == '.mkv':
        return True
    elif link['href'][-4:] == '.avi':
        return True
    else:
        return False



def is_directory(link):
    """
        link is a string.
    """
    if link[-1] == '/':
        return True
    elif args.l[-1] != '/':
        print "Error: Link must end in /"
    else:
        return False


def check_movie_info(guess, imdb_check = True):
    if guess.has_key('title'):
        title = guess['title']
        if title == '':
            return False
    else:
        # Title not found, let's play safe and discard this
        return False
    if imdb_check:
        if guess.has_key('year'):
            year = guess['year']
        else:
            # If we don't have the year we can't check against imdb
            return False
        res = imdb.search_for_title(title.encode("utf-8"))
        for r in res:
            # Sometime imdb returns None as a year :)
            if type(r['year']) != type(None):
                if year == int(r['year']):
                        return True
    else:
        # Without imdb_check we return True if title is not empty
        return True


def check_series_info(guess, imdb_check = True):
    """
        {There is no easy way to check series with IMDB api.  
        The main problem is the lack of a method for searching
        information about a specific episode.} The omdbapi can do this http://omdbapi.com/
        The best I can do now is check for a non-empty response.
    """
    if guess.has_key('series'):
        title = guess['series']
        if title == '':
            return False
    else:
        # Title not found, let's play safe and discard this
        return False
    if imdb_check:
        res = []
        res = imdb.search_for_title(title.encode("utf-8"))
        if len(res) > 0:
            return True
        else:
            return False

def check_media_info(guess, imdb_check = True):
    """
        Receives a Guess - guessit.Guess - object and search in IMDB
        for more information to confirm the guess.
    """
    if guess['type'] == u'movie':
        return check_movie_info(guess, imdb_check)
    elif guess['type'] == u'episode':
        return check_series_info(guess, imdb_check)
    else:
        # GuessIt failed.
        return False


def get_files(url, base_url=''):
    """
        For now this works ONLY with apache directories listing.
    """
    list_files = []
    list_dir = []
    url = base_url+url
    if is_directory(url):
        links = linkGrabber.Links(url)
        # Skip the first 5 links ( Name, Last Modified, Size,
        #                          Description, Parent Directory )
        # This is why the script only works with Apache
        list_links = links.find()[5:]
        for l in list_links:
            if is_relevant_file(l):
                list_files.append(l)
            else:
                list_dir.append(urllib2.unquote(l['href']))
        for n in list_files:
            gg = guessit.guess_file_info(url+urllib2.unquote(n['href']))
            x = check_media_info(gg)
            if x:
                if gg.has_key('title'):
                    # I replaced spaces instead of just url encoding because url.encode(gg['title']) throws 
                    #LookupError: unknown encoding: Jurassic World. I tried encoding it as utf-8 before urlencode
                    # but no dice.
                    print gg['type'] + ": " + gg['title'] +'\nMoive info: ' + omdburl + gg['title'].replace(' ','%20')
                else:
                    if gg.has_key('series'):
                        print gg['type'] + ": " + gg['series']
                print urllib2.quote(url)+(n['href'])
    for d in list_dir:
        get_files(d, url)


if __name__ == '__main__':
    get_files(args.l)
    # get_files("http://www.bdhdmovies.com/data/disk1/")
