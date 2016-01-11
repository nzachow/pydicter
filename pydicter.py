from imdbpie import Imdb
from BeautifulSoup import BeautifulSoup
import urllib2
import guessit
import argparse


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
        There is no easy way to check series with IMDB api.
        The main problem is the lack of a method for searching
        information about a specific episode.
        The best I can do now is check for a non-empty response. 

        ^You can search for specific episodes with omdbapi
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



def print_guess_info(guess, key, msg):
    """
        Using msg.format() you can easily display nice messages.
        https://docs.python.org/2/library/string.html#formatstrings
    """
    if guess.has_key(key):
        print msg.format(guess[key])


def print_info(guess, link):
    """
        Just pass a Guess object and the link to this function.
        link is a string.
    """
    if guess['type'] == u'movie':
        print_guess_info(guess, 'title', 'Movie name:  {}')
        print 'Movie info:  ' + omdblink + guess['title'] + '&plot=full&v=1' #This gives the full plot and makes sure we use version 1 of the api
        # there are 2 spaces after the : so it lines up with the other info printed
    elif guess['type'] == u'episode':
        print_guess_info(guess, 'series', 'Series name: {}')
         
        
        # there are 2 spaces after the : so it lines up with the other info printed
        try:
            title = guess['title']
            print 'Series info:  ' + omdblink + title.replace(' ','%20') + '&plot=full&v=1' #This gives the full plot and makes sure we use version 1 of the api
        except KeyError:
            print "There was an error"
    print_guess_info(guess, 'videoCodec', 'VCodec:      {}')
    print_guess_info(guess, 'audioCodec', 'ACodec:      {}')
    print_guess_info(guess, 'container', 'Container:   {}')
    print_guess_info(guess, 'format', 'Format:      {}')
    print_guess_info(guess, 'screenSize', 'Screen size: {}')
    print_guess_info(guess, 'year', 'Year:        {}')
    link = link.replace('http%3A','http:')
    print 'Link:        {}.'.format(link)
    print '#'*20


def get_links(html_str):
    '''
        This function receives a string with the html of a page and returns
        all the links.
        This is a good idea because it make easier to create tests.
    '''
    # Skip the first 5 links ( Name, Last Modified, Size,
    #                          Description, Parent Directory )
    # This is why the script only works with Apache
    unwanted_links = ['name', 'last modified', 'size', 'description', 'parent directory']
    result = []
    soup = BeautifulSoup(html_str)
    for link in soup('a'):
        if link.contents[0].lower() not in unwanted_links:
            result.append(link)
    return result


def get_files(url, base_url=''):
    """
        For now this works ONLY with apache directories listing.
    """
    list_files = []
    list_dir = []
    url = base_url+url
    if is_directory(url):
        page = urllib2.urlopen(url)
        page_html = page.read()
        list_links = get_links(page_html)
        for l in list_links:
            if is_relevant_file(l):
                list_files.append(l)
            else:
                list_dir.append(urllib2.unquote(l['href']))
        for n in list_files:
            gg = guessit.guess_file_info(url+urllib2.unquote(n['href']))
            x = check_media_info(gg)
            if x:
                print_info(gg, urllib2.quote(url)+(n['href']))
    for d in list_dir:
        # urllib2.quote() is the best way to handle url's
        get_files(urllib2.quote(d), url)


if __name__ == '__main__':
    # Option parser
    description_str = "Script to scan an open directorie and based on \
                       filenames print possibles movies/series."
    parser = argparse.ArgumentParser(description=description_str)
    parser.add_argument("location", help="Link to the open directory you want to scan", \
                        type=str)
    args = parser.parse_args()

    # This prints an error if the link doesn't end in /
    if args.location[-1] != '/':
        print "Error: Directories must end in /"

    # OMDB api link
    omdblink = 'http://www.omdbapi.com/?t='

    # This is what allow us to search IMDB
    imdb = Imdb()
    imdb = Imdb(anonymize=True)

    get_files(args.location)
