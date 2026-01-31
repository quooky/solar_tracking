import pytest
import numpy as np
from solar_tracking.image_processing import image_processing_fits  # Direkter Import

def test_process_fit():
    """Testet, ob die Normalisierung einer FITS-Datei korrekt funktioniert."""
    
    # Testdatei
    test_file = "test.fits"
    
    # Funktion ausführen
    normalized_image = image_processing_fits(test_file)
    
    # Überprüfen, ob das Ergebnis eine NumPy-Array ist
    assert isinstance(normalized_image, np.ndarray), "Ergebnis sollte ein NumPy-Array sein"
    
    # Überprüfen, ob die Werte zwischen 0 und 255 liegen
    assert normalized_image.min() == 0, "Minimum sollte 0 sein"
    assert normalized_image.max() == 255, "Maximum sollte 255 sein"

    # Zusätzliche Ausgabe
    print("Test erfolgreich!")