#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tweets a random Rosetta image as @RosettaBot."""
import random
from twython import Twython
from matplotlib.image import imsave
from matplotlib import cm

from astropy import log
from astropy.io import fits
from astropy.time import Time
from astropy.visualization import scale_image

from secrets import *


def get_random_fits_url(db_fn='data/rosetta-fits-files.txt'):
    db = open(db_fn, 'r').readlines()
    idx = random.randint(0, len(db))
    return db[idx]


def generate_tweet(fits_fn=None):
    """Generate a tweet and jpg.

    Parameters
    ----------
    fits_fn : str (optional)
        Path or url to FITS file. If `None`, a random file will be downloaded.

    Returns
    -------
    (status, jpg) : (str, str)
    """
    # Open the FITS file
    if fits_fn is None:  # Get a random url
        fits_fn = get_random_fits_url()
    log.info('Opening {0}'.format(fits_fn))
    fts = fits.open(fits_fn)
    # Create the status message
    imgtime = fts[0].header['IMG-TIME']
    instrument = fts[0].header['INSTRUME']
    exptime = fts[0].header['EXPTIME']
    timestr = Time(imgtime).datetime.strftime('%d %b %Y at %H:%M').lstrip("0")
    status = ('{0} image taken on {1}. '
              'Exposure time: {2:.0f}s.'.format(instrument, timestr, exptime))
    # Create the scaled jpg
    jpg_fn = '/tmp/rosettabot.jpg'
    image_scaled = scale_image(fts[0].data, scale='linear', percent=95)
    log.info('Writing {0}'.format(jpg_fn))
    imsave(jpg_fn, image_scaled, cmap=cm.gray)
    return (status, jpg_fn)


def post_tweet(status, media_fn):
    """Post media and an associated status message to Twitter."""
    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    upload_response = twitter.upload_media(media=open(media_fn, 'rb'))
    response = twitter.update_status(status=status,
                                     media_ids=upload_response['media_id'])
    log.info(response)
    return twitter, response


if __name__ == '__main__':
    # Failsafe: attempt multiple files until successful
    attempt_no = 0
    while attempt_no < 10:
        attempt_no += 1
        try:
            status, jpg = generate_tweet()
            twitter, response = post_tweet(status, jpg)
            break
        except Exception as e:
            log.warning(e)
