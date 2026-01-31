from sunpy.net import Fido, attrs as a
from astropy import units as u
import os
import glob

def download_fits(start_time: str, end_time: str, instrument: str = 'hmi', sample_seperation: int = 1):
    """
    Lädt FITS-Dateien von der Sonne mit SunPy herunter und speichert sie in einem neuen Trace-Ordner.
    
    Für jeden Aufruf wird im aktuellen Arbeitsverzeichnis ein neuer Unterordner im Format "data/TR_XX"
    erstellt (XX = fortlaufende Nummer). In diesem Ordner werden die FITS-Dateien abgelegt und eine 
    "names.txt" erstellt, die die Dateinamen enthält.
    
    Args:
        start_time (str): Startzeit im Format 'YYYY-MM-DD HH:MM:SS'
        end_time (str): Endzeit im Format 'YYYY-MM-DD HH:MM:SS'
        instrument (str): Name des Instruments (z. B. "hmi")
        sample_seperation (int): Intervall in Stunden (wird mit u.hour multipliziert)
        
    Returns:
        list: Liste der heruntergeladenen Dateien (vollständige Pfade)
    """
    # Liste gültiger Instrumente abrufen
    valid_instruments = [name.lower() for name in dir(a.Instrument) if not name.startswith("_")]
    if instrument.lower() not in valid_instruments:
        raise ValueError(f"Ungültiges Instrument: {instrument}. Verfügbare Optionen: {valid_instruments}")

    # Basisordner "data" erstellen (falls nicht vorhanden)
    base_directory = os.path.join(os.getcwd(), "data")
    os.makedirs(base_directory, exist_ok=True)

    # Ermittle den nächsten freien Trace-Ordner (Format: TR_XX, z. B. TR_01)
    existing_traces = glob.glob(os.path.join(base_directory, "TR_*"))
    trace_numbers = []
    for trace_dir in existing_traces:
        basename = os.path.basename(trace_dir)
        # Erwartetes Format: "TR_XX"
        try:
            num = int(basename.replace("TR_", ""))
            trace_numbers.append(num)
        except ValueError:
            continue
    if trace_numbers:
        new_trace = max(trace_numbers) + 1
    else:
        new_trace = 1

    # Neuen Trace-Ordner erstellen (mit führender Null, z. B. TR_01)
    trace_folder = os.path.join(base_directory, f"TR_{new_trace:02d}")
    os.makedirs(trace_folder, exist_ok=True)

    # Suche-Parameter vorbereiten
    instrument_attr = getattr(a.Instrument, instrument, a.Instrument.hmi)
    results = Fido.search(
        a.Time(start_time, end_time),
        instrument_attr,
        a.Physobs.intensity,
        a.Sample(sample_seperation * u.hour)
    )

    # Herunterladen in den neuen Trace-Ordner
    downloaded_files = Fido.fetch(results, path=os.path.join(trace_folder, "{file}"))
    
    # Erstelle die names.txt im neuen Trace-Ordner, die die Dateinamen enthält
    names_path = os.path.join(trace_folder, "names.txt")
    with open(names_path, "w") as f:
        for file_path in downloaded_files:
            # Nur den Dateinamen schreiben (ohne Pfad)
            f.write(os.path.basename(file_path) + "\n")
    
    return downloaded_files
