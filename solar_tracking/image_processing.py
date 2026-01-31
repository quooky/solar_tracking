import cv2
import numpy as np
from astropy.io import fits
import os

def image_processing_fits(fits_path:str, data_layer: int = 1):
    """
    Opens the fits image and noramalize it that it can be used in the 
    function to find the boxes around the spots(features)

    Args:
        fits_path (str): path to the fits file that should be used in the func
        data_layer int): the index of the data layer in the fits file
    Returns:
        normalized_image (np.ndarry): normalized image between 0 and 255
    """

    if not os.path.exists(fits_path):
        raise FileNotFoundError(f"Die Datei {fits_path} wurde nicht gefunden!")

    
    # Open the FITS file and read the data
    with fits.open(fits_path) as hdul:
        data = hdul[data_layer].data  # The 1 because in this fits files is the data safed
                                        # in the second position 
    
    #Converte the image in to a ndarray    
    image_data = np.array(data, dtype=np.float32)
    image_data = np.nan_to_num(data, nan=0.0)  # Alle NaN-Werte werden durch 0 ersetzt
   
    #Normalizing the image
    normalized_image = cv2.normalize(image_data, None, alpha=0, beta=255,\
                                     norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    return normalized_image

