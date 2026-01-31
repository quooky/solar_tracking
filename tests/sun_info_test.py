import pytest
from solar_tracking.sunspot_detection import sun_infos

def test_sun_infos():
    """Testet, ob die Normalisierung einer FITS-Datei korrekt funktioniert."""
    
    # Testdatei
    test_file = "test.fits"
    sun_r, sun_center, resolution = sun_infos(test_file)
    
    assert sun_center == (50,50) 
    assert resolution == 100 