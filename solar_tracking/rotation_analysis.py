import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord

def cal_lon_and_lat(x_pix, y_pix, hmi_map):
    """
    Konvertiert Pixelkoordinaten in heliographische Koordinaten.

    Args:
        x_pix (float): X-Pixelposition
        y_pix (float): Y-Pixelposition
        hmi_map (sunpy.map.Map): FITS-Kartenobjekt

    Returns:
        heliographic_coords (SkyCoord): Heliographische Koordinaten
    """
    helioprojective_coords = hmi_map.pixel_to_world(x_pix * u.pix, y_pix * u.pix)
    return helioprojective_coords.transform_to(
        SkyCoord(0*u.deg, 0*u.deg, 0*u.m, obstime=hmi_map.date, 
                 observer=hmi_map.observer_coordinate, frame='heliographic_carrington')
    )

def cal_omega_p(lon1, lon2, delta_t):
    """
    Berechnet die Rotationsgeschwindigkeit und Periode basierend auf zwei Längengradmessungen.

    Args:
        lon1 (SkyCoord): Anfangskoordinate
        lon2 (SkyCoord): Endkoordinate
        delta_t (float): Zeitdifferenz in Stunden

    Returns:
        tuple: (Omega in °/Tag, Rotationsperiode in Tagen)
    """
    lon_sep = lon1.separation(lon2)
    delta_t_days = (delta_t / 24.0) * u.day
    omega = (lon_sep.deg / delta_t_days) * u.deg
    period = (360 * u.deg) / omega

    return omega, period
