import numpy as np
from scipy.optimize import curve_fit

def fit_func(B_0, a, b):
    """Fit-Funktion für die differentielle Rotation."""
    return a + b * np.sin(np.deg2rad(B_0))**2

def perform_fitting(lat_all, omega_all):
    """
    Führt das Curve Fitting für die differentielle Rotation durch.

    Args:
        lat_all (array): Breitengrade der Sonnenflecken
        omega_all (array): Rotationsgeschwindigkeiten

    Returns:
        tuple: (Fit-Parameter, R-Quadrat-Wert)
    """
    popt, pcov = curve_fit(fit_func, lat_all, omega_all)
    residuals = omega_all - fit_func(lat_all, *popt)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((omega_all - np.mean(omega_all))**2)
    r_squared = 1 - (ss_res / ss_tot)

    return popt, r_squared
