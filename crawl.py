#!/usr/bin/env python
# -*- coding: utf-8 -*-
""""Saves a list of Rosetta FITS files that are publicly available from the
ESA image archive.
"""
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
from astropy.utils.console import ProgressBar
from astropy import log


class LinkNotFoundError(Exception):
    pass


def get_fits_url(imageid):
    """Searches a single url for links to FITS files."""
    url = 'http://imagearchives.esac.esa.int/picture.php?/{0}'.format(imageid)
    html = urlopen(url)
    soup = BeautifulSoup(html)
    links = [link.get('href') for link in soup.find_all('a', href=True)]
    for lnk in links:
        if lnk.endswith('.FIT'):
            return lnk
    raise LinkNotFoundError()


def save_list(output_fn, id_begin, id_end):
    output = open(output_fn, 'w')
    log.info('Writing {0}'.format(output_fn))
    for imageid in ProgressBar(range(id_begin, id_end)):
        time.sleep(1.)  # Be nice to ESA's servers
        try:
            output.write('{0},{1}\n'.format(imageid, get_fits_url(imageid)))
        except LinkNotFoundError:
            pass
    output.close()


if __name__ == '__main__':
    save_list('data/rosetta-fits-files.csv', 2130, 2427)
