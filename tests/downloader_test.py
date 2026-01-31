import os
import pytest
from sunpy.net import Fido, attrs as a
from astropy import units as u

# Importiere hier deine Funktion. Passe den Modulpfad an:
from solar_tracking.downloader import download_fits


# --- Fake-Funktionen für Fido.search und Fido.fetch ---

def fake_search(*args, **kwargs):
    """
    Gibt ein Dummy-Ergebnis zurück, das von Fido.fetch verwendet wird.
    """
    # Wir geben hier einfach einen Dummy-String zurück.
    return "dummy_results"

def fake_fetch(results, path, **kwargs):
    """
    Simuliert den Download, indem eine Dummy-Datei erstellt wird.
    Die Funktion ersetzt Fido.fetch.
    """
    # Ersetze den Platzhalter {file} im Pfad durch einen Dummy-Dateinamen.
    dummy_filename = "dummy_file.fits"
    dummy_path = path.format(file=dummy_filename)
    
    # Erstelle den übergeordneten Ordner, falls nicht vorhanden.
    os.makedirs(os.path.dirname(dummy_path), exist_ok=True)
    
    # Schreibe Dummy-Inhalt in die Datei.
    with open(dummy_path, "w") as f:
        f.write("dummy content")
        
    return [dummy_path]


# --- Test für gültigen Instrumentnamen ---

def test_download_fits_valid(monkeypatch, tmp_path):
    """
    Testet, ob download_fits bei korrekten Parametern
    eine Liste von FITS-Dateipfaden zurückgibt.
    """

    # Monkeypatch Fido.search und Fido.fetch mit unseren Fake-Funktionen
    monkeypatch.setattr(Fido, "search", fake_search)
    monkeypatch.setattr(Fido, "fetch", fake_fetch)
    
    # Überschreibe os.getcwd(), sodass der Downloadordner im tmp_path angelegt wird.
    monkeypatch.setattr(os, "getcwd", lambda: str(tmp_path))
    
    # Test-Parameter
    start_time = "2023-10-25 03:00:00"
    end_time   = "2023-10-26 00:00:00"
    instrument = "hmi"  # Angenommen, "hmi" ist in a.Instrument enthalten.
    sample_seperation = 4

    # Aufruf der Funktion (es werden die Fake-Funktionen genutzt)
    result_files = download_fits(start_time, end_time, instrument, sample_seperation)

    # Überprüfe, ob der Rückgabewert eine Liste ist
    assert isinstance(result_files, list), "Die Rückgabe sollte eine Liste sein."
    
    # Überprüfe, ob mindestens eine Datei zurückgegeben wird
    assert len(result_files) >= 1, "Mindestens eine Datei sollte zurückgegeben werden."

    # Für jede zurückgegebene Datei: Überprüfe, ob sie mit .fits endet und existiert.
    for file in result_files:
        assert file.endswith(".fits"), f"Die Datei {file} hat nicht die Endung .fits."
        assert os.path.exists(file), f"Die Datei {file} wurde nicht erstellt."


# --- Test für ungültigen Instrumentnamen ---

def test_download_fits_invalid_instrument():
    """
    Testet, ob ein ungültiger Instrumentname einen ValueError auslöst.
    """
    start_time = "2023-10-25 03:00:00"
    end_time   = "2023-10-26 00:00:00"
    invalid_instrument = "ungültig"
    
    with pytest.raises(ValueError) as excinfo:
        download_fits(start_time, end_time, invalid_instrument, sample_seperation=1)
        
    assert "Ungültiges Instrument" in str(excinfo.value)
