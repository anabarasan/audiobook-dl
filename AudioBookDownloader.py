# podiobooks.py
from argparse import ArgumentParser
from HTMLParser import HTMLParser
from urllib2 import urlopen
import os

class PodioBooks(HTMLParser):
    def __init__(self):
        self.result = []
        self.__process__ = False
        self.__link__ = ""
        HTMLParser.__init__(self)
        
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = "";
            self.__process__ = False
            for attr in attrs:
                if attr[0] == 'href':
                    href = attr[1]
                if attr[0] == 'class' and attr[1] == 'episode-audio-link':
                    self.__process__ = True
            if self.__process__:
                self.__link__ = href;

    def handle_data(self, data):
        if self.__process__:
            self.__process__ = False
            self.result.append({'name':data, 'link':self.__link__})
            
class AudioBookDownloader(object):
    def __init__(self, **kwargs):
        self.book = kwargs.get('book', None)
        self.book_title = '-'.join(self.book.lower().split(' '))
        
        start = kwargs.get('start', None)
        if start:
            self.start = start -1
            
        self.end = kwargs.get('end', None)
        
        destination = kwargs.get('destination', None)
        if destination:
            self.destination = destination.replace('\\', '/')
        else:
            self.destination = destination = "."
        self.rename = kwargs.get('rename', False)
        
    def __get_page__(self, book_url):
        return PodioBooks().feed(urlopen(book_url))
        
    def __get_episode_links__(self, page, start, end):
        return page.result[start:end]

    def __download__(self, destination, episode):
        dir_name = episode_link.split('/')[-2]
        episode_link = episode.link
        
        if self.rename:
            file_name = episode.name
        else:
            file_name = episode_link.split('/')[-1]
        
        if not os.path.exists(destination + '/' + dir_name):
            os.makedirs(destination + '/' + dir_name)
            
        target = destination + '/' + dir_name + '/' + file_name
        
        if not os.path.isfile(target):
            with open(target, 'wb') as file:
                episode_file = urlopen(episode_link)
                episode_file_info = episode_file.info()
                file_size = int(episode_file_info.getheaders("Content-Length")[0])
                print "Downloading: %s Bytes: %s" % (file_name, file_size)
            
                file_size_downloaded = 0
                block_size = 8192
                
                while True:
                    buffer = episode_file.read(block_size)
                    if not buffer:
                        break
                    file_size_downloaded += len(buffer)
                    file.write(buffer)
                    status = r"%10d  [%3.2f%%]" % (file_size_downloaded, file_size_downloaded * 100. / file_size)
                    status = status + chr(8)*(len(status)+1)
                    print status,
                print ""
            
    def download(self):
        book_url  = self.host + self.book_title + '/'
        page = self.__get_page__(book_url)
        episode_list = self.__get_episode_links__(page, self.start, self.end)
        for episode in episode_list:
            self.__download__(self.destination, episode)

parser = ArgumentParser()
parser.add_argument("--book", help="Book Name, use \"\" if name has spaces", required=True)
parser.add_argument("--start", help="from which file to download", type=int)
parser.add_argument("--end", help="up to which file to download", type=int)
parser.add_argument("--rename", help="save file with name as chapter name", action="store_true")
parser.add_argument("--output", help="Where the downloaded episode needs to be stored.")
args = parser.parse_args()

AudioBookDownloader.host = 'http://podiobooks.com/title/'
abd = AudioBookDownloader(book=args.book, start=args.start, end=args.end, destination=args.output, rename=args.rename)
abd.download()