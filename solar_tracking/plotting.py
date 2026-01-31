import matplotlib.pyplot as plt
import numpy as np
import astropy.units as u
from matplotlib.backends.backend_pdf import PdfPages
from solar_tracking.fitting import fit_func

def plot_results(lat_all, omega_all, popt, filename="Plots_fits.pdf"):
    """
    Erstellt Diagramme zur Sonnenrotation und speichert sie als PDF.

    Args:
        lat_all (array): Breitengrade der Sonnenflecken
        omega_all (array): Rotationsgeschwindigkeiten
        popt (array): Fit-Parameter
        filename (str): Name der PDF-Datei
    """
    
    lat_all = np.array(np.abs(lat_all))
    omega_all = np.array(omega_all)
    lat1 = np.arange(np.min(lat_all), np.max(lat_all), 1)

    with PdfPages(filename) as pdf:
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_ylabel('Period [sidereal days]', fontsize=20)
        ax.set_xlabel('Latitude [deg]', fontsize=20)
        ax.set_title('Differential Rotation of Sunspots', fontsize=25)
        ax.grid(True, ls='--', linewidth=0.8)

        ax.plot(np.abs(lat_all), 360 / omega_all, "x", markersize=8, markeredgewidth=2, color='black')
        ax.plot(lat1, 360 / fit_func(lat1, *popt), color="green")

        ax.annotate(r"$\Omega(B) = %.3f + %.3f \cdot \sin^2(B)$"
                    % (popt[0], popt[1]), xy=(16, 26.5),
                    xytext=(0.04, 4/5), textcoords='axes fraction',
                    bbox=dict(facecolor='grey', alpha=0.5, edgecolor='None', pad=10.0),
                    fontsize=15, arrowprops=dict(facecolor='green', shrink=0.02, width=0.25, headwidth=5, headlength=7))

        pdf.savefig(fig)
        plt.show()
