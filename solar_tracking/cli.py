import argparse
import matplotlib.pyplot as plt
import sunpy.map
from solar_tracking.downloader import download_fits
from solar_tracking.tracking import run_tracking  # Falls dein Tracking-Tool so heißt

def view_fits(file_path):
    """Zeigt eine FITS-Datei als Bild an."""
    try:
        smap = sunpy.map.Map(file_path)
        smap.plot()
        plt.colorbar()
        plt.title(f"FITS-Datei: {file_path}")
        plt.show()
    except Exception as e:
        print(f"Fehler beim Öffnen der FITS-Datei: {e}")

def main():
    parser = argparse.ArgumentParser(description="CLI-Tool für Solar Tracking")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 📌 Downloader-Befehl
    parser_download = subparsers.add_parser("downloader", help="Lädt FITS-Dateien herunter")
    parser_download.add_argument("--start", required=True, help="Startzeit (YYYY-MM-DD HH:MM:SS)")
    parser_download.add_argument("--end", required=True, help="Endzeit (YYYY-MM-DD HH:MM:SS)")
    parser_download.add_argument("--instrument", default="hmi", help="Instrument (Standard: hmi)")
    parser_download.add_argument("--sample", type=int, default=1, help="Zeitintervall in Stunden")

    # 📌 Tracking-Befehl
    parser_tracking = subparsers.add_parser("run_tracking", help="Führt Sonnenflecken-Tracking aus")
    parser_tracking.add_argument("--trace", type=int, default=1, help="Nummer der Trace-Serie (z. B. 1 für data/TR_01)")
    parser_tracking.add_argument("--no-interactive", action="store_true", help="Tracking ohne Benutzerinteraktion ausführen")

    # 📌 `view_fits`-Befehl
    parser_view = subparsers.add_parser("view_fits", help="Zeigt eine FITS-Datei an")
    parser_view.add_argument("file", help="Pfad zur FITS-Datei")

    args = parser.parse_args()

    # 🛰️ Downloader ausführen
    if args.command == "downloader":
        print(f"Lade Daten von {args.start} bis {args.end} mit {args.instrument} herunter...")
        downloaded_files = download_fits(args.start, args.end, args.instrument, args.sample)
        print(f"Heruntergeladene Dateien: {downloaded_files}")

    # 🌞 Tracking starten
    elif args.command == "run_tracking":
        interactive_mode = not args.no_interactive  # Invertiert den `--no-interactive`-Flag
        print(f"Starte Tracking für Trace {args.trace}...")
        run_tracking(trace=args.trace, interactive=interactive_mode)
        print("Tracking abgeschlossen.")

    # 🔍 FITS-Datei anzeigen
    elif args.command == "view_fits":
        print(f"Öffne FITS-Datei: {args.file}")
        view_fits(args.file)

if __name__ == "__main__":
    main()
