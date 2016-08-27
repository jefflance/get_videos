#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# Imports
import urllib2
import subprocess
import re
import logging
import argparse
import os
from bs4 import BeautifulSoup
from datetime import datetime
from urlparse import urlparse


# Parsing arguments
parser = argparse.ArgumentParser()
parser.add_argument('--log', help='set log level')
args = parser.parse_args()


# Logging configuration
loglevel = 'INFO'
if args.log:
    loglevel = args.log

numeric_level = getattr(logging, loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % loglevel)

logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
            filename='get_manimo.log',
            level=numeric_level
)

logger = logging.getLogger('get_manimo.py')


# Environment variables
source_url = 'http://pluzz.francetv.fr/videos/manimo.html'
# source_url = 'http://pluzz.francetv.fr/videos/manimo_saison1_,133868923.html'
save_path = '/Volumes/DATA/films/Manimo/'


# Parse url to initialize the string passed to youtube-dl
download_url = "%s://%s" % (urlparse(source_url).scheme,
                            urlparse(source_url).netloc)


# Request Peppa Pig page on FranceTV Pluzz, store content and parse it
req = urllib2.Request(source_url)
rep = urllib2.urlopen(req)
page = rep.read()
soup = BeautifulSoup(page, "lxml")
logger.info('Parse page')


# Generate list of url and name files to download
rname = re.compile(r'http://.+/manimo_saison(?P<saison>\d+)'
                   '_,(?P<sitecode>\d+).html')
logger.debug('RegExp compile: %s', rname)

try:
    urls = [download_url + link.get('href') for link in
            soup.find(id='player-memeProgramme').find_all('a')]
except AttributeError as detail:
    print 'No videos on Pluzz'
    logger.error('Impossible to get data from Pluzz: %s' % detail)
else:
    logger.debug('Generate URLs list: %s', urls)

    today = datetime.now().strftime('%d%m%yT%H%M%S')
    dldir = save_path + today

    if not os.path.isfile(dldir) and not os.path.isdir(dldir):
        os.mkdir(dldir)

    names = [dldir + '/' + 'Manimo - S%02d_%d.mp4' %
             tuple(map(int, sname)) for sname in
             [rname.match(name).group('saison', 'sitecode')
                 if rname.match(name) is not None else ('0', '0')
                 for name in urls]]

    logger.debug('Generate filenames list: %s', names)

    # Set args to pass to youtube-dl
    args = [('{1} -o \'{0}\'').format(n, u) for n, u in zip(names, urls)]

    logger.debug('Generate args list: %s', args)

    # Start download with youtube-dl
    print 'Downloading: %s files' % (len(urls))

    logger.info('Start downloading')

    [subprocess.call('youtube-dl -f best ' + arg, shell=True) for arg in args]

    logger.info('End downloading')
