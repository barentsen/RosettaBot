"""Smart cropping of an image by maximizing information entropy."""
import numpy as np


def image_entropy(img, img_min, img_max):
    """Calculate the entropy of an image.

    Parameters
    ----------
    img : numpy array
        The image data.

    img_min, img_max : float, float
        Minimum and maximum to consider when computing the entropy.

    Returns
    -------
    entropy : float
    """
    histo, bins = np.histogram(img, bins=255, range=(img_min, img_max))
    probabilities = histo / np.sum(histo)
    entropy = -sum([p * np.log2(p) for p in probabilities if p != 0])
    return entropy


def entropy_crop(img, width, height, max_steps=10):
    """Crops an image such that information entropy is maximized.

    This function is originally adapted from the FreeBSD-licensed `cropy`
    package, see credits here: https://pypi.python.org/pypi/cropy/0.1

    Parameters
    ----------
    img : numpy array
        The image data.

    width, height : int, int
        Desired dimensions of the cropped image.

    max_steps : int
        Maximum number of iterations (default: 10).

    Returns
    -------
    cropped_img : numpy array
        The cropped image data.
    """
    img_min, img_max = np.min(img), np.max(img)
    original_height, original_width = img.shape
    right_x, bottom_y = original_width, original_height
    left_x, top_y = 0, 0

    # calculate slice size based on max steps
    slice_size = int(round((original_width - width) / max_steps))
    if slice_size == 0:
        slice_size = 1

    left_slice = None
    right_slice = None

    # cut left or right slice of image based on min entropy value until targetwidth is reached
    # while there still are uninvestigated slices of the image (left and right)
    while ((right_x - left_x - slice_size) > width):
        if (left_slice is None):
            left_slice = img[0: original_height + 1, left_x: left_x + slice_size + 1]

        if (right_slice is None):
            right_slice = img[0: original_height + 1, right_x - slice_size: right_x + 1]

        if (image_entropy(left_slice, img_min, img_max) < image_entropy(right_slice, img_min, img_max)):
            left_x = left_x + slice_size
            left_slice = None
        else:
            right_x = right_x - slice_size
            right_slice = None

    top_slice = None
    bottom_slice = None

    # calculate slice size based on max steps
    slice_size = int(round((original_height - height) / max_steps))
    if slice_size == 0:
        slice_size = 1

    # cut upper or bottom slice of image based on min entropy value until
    # target height is reached
    # while there still are uninvestigated slices of the image (top and bottom)
    while ((bottom_y - top_y - slice_size) > height):
        if (top_slice is None):
            top_slice = img[top_y: top_y + slice_size + 1, 0: original_width + 1]

        if (bottom_slice is None):
            bottom_slice = img[bottom_y - slice_size:bottom_y + 1, 0: original_width + 1]

        if (image_entropy(top_slice, img_min, img_max) < image_entropy(bottom_slice, img_min, img_max)):
            top_y = top_y + slice_size
            top_slice = None
        else:
            bottom_y = bottom_y - slice_size
            bottom_slice = None

    return img[top_y : top_y + height,
               left_x + width : left_x : -1]


if __name__ == '__main__':
    """Example use"""
    from matplotlib.image import imsave
    from matplotlib import cm
    from astropy.io import fits
    from astropy import log
    from astropy.visualization import scale_image

    fts = fits.open('http://imagearchives.esac.esa.int/data_raw/ROSETTA/NAVCAM/RO-C-NAVCAM-2-PRL-MTP007-V1.0/DATA/CAM1/ROS_CAM1_20140922T060854F.FIT')
    img = fts[0].data
    width, height = 512, 256
    image_cropped = entropy_crop(img, width, height)
    image_scaled = scale_image(image_cropped, scale='linear',
                               min_percent=0.05, max_percent=99.95)
    jpg_fn = 'test.jpg'
    log.info('Writing {0}'.format(jpg_fn))
    imsave(jpg_fn, image_scaled, cmap=cm.gray)
