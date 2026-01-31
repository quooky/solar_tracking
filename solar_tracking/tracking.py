from pathlib import Path
import os
import cv2
import numpy as np

# Importiere deine bereits existierenden Funktionen aus dem Paket
from solar_tracking.image_processing import image_processing_fits
from solar_tracking.sunspot_detection import sun_infos, find_spots_and_boxes

def run_tracking(trace: int = 1, interactive: bool = True):
    """
    Führt das Tracking von Sonnenflecken in einer gegebenen Trace-Serie aus.
    
    Dabei werden folgende Schritte durchgeführt:
      1. Einlesen der Dateinamen aus 'data/TR_0X/names.txt'
      2. Auslesen der Headerinformationen (z. B. Sonnenmittelpunkt, Bildauflösung)
      3. Vorverarbeitung der FITS-Dateien zu Bildern
      4. Initiale Spot-Detektion im ersten Bild
      5. Verfolgen der Spots in der Bildserie mittels eines OpenCV-Trackers
      6. (Optional) Interaktive Anzeige zur Auswahl, ob der Trace gespeichert wird.
    
    Zusätzlich werden im Tracking:
      - Das aktuelle ROI (Region of Interest) wird vergrößert (Zoom) und eingeblendet.
      - Verschiedene Hilfslinien (z. B. Sonnenmittelpunkt, Startkoordinaten, Bounding-Box-Mittelpunkt) werden gezeichnet.
    
    Parameter
    ----------
    trace : int, optional
        Nummer der Trace-Serie (entspricht dem Ordner 'data/TR_0X'); Standard ist 1.
    interactive : bool, optional
        Wenn True, werden Fenster zur Visualisierung und Tastatureingaben genutzt.
    """
    
    # --- Schritt 1: Dateinamen einlesen ---
    names_file = Path(f"data/TR_0{trace}/names.txt")
    if not names_file.exists():
        raise FileNotFoundError(f"Die Datei {names_file} wurde nicht gefunden.")
    file_paths = np.genfromtxt(str(names_file), dtype=str)
    
    # --- Schritt 2: Headerinformationen aus der ersten Datei auslesen ---
    first_file = Path(f"data/TR_0{trace}") / file_paths[0]
    sun_r, sun_c, image_resolution = sun_infos(first_file)
    
    # --- Schritt 3: Alle FITS-Dateien verarbeiten ---
    images = []
    for fname in file_paths:
        fit_path = Path(f"data/TR_0{trace}") / fname
        processed_fit = image_processing_fits(fit_path)
        images.append(processed_fit)
    
    if not images:
        raise ValueError("Keine Bilder konnten geladen werden.")
    
    # --- Schritt 4: Initiale Spot-Detektion im ersten Bild ---
    prev_image = images[0]
    bbox, centroids = find_spots_and_boxes(prev_image, sun_r, sun_c)
    print('Number of detected spots:', len(bbox))
    
    # Konfiguration: Linienbreite für Zeichnungen
    line_thickness = 3
    
    # Erstelle ein einziges Fenster für die Anzeige, falls interaktiv
    window_name = "Tracking"
    if interactive:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    # --- Schritt 5: Tracking der Spots über die Bildserie ---
    for idx, spot in enumerate(bbox):
        # Startkoordinaten (x,y) aus den Zentroiden
        x1 = int(centroids[idx][0])
        y1 = int(centroids[idx][1])
        
        # Tracker erstellen – hier wird ein MIL-Tracker verwendet (alternativ z.B. CSRT)
        tracker = cv2.TrackerMIL_create()
        oversize = 20  # Erweitert die Bounding-Box für eine bessere Visualisierung
        tracker.init(prev_image, (spot[0]-oversize, spot[1]-oversize, spot[2]+oversize, spot[3]+oversize))
        
        # Variable zur Speicherung der Endkoordinaten initialisieren
        x2, y2 = None, None
        
        # Tracking über die restlichen Bilder der Serie
        for i in range(1, len(images)):
            current_image = images[i]
            # Konvertiere das Bild in BGR, um farbige Zeichnungen zu ermöglichen
            current_disp = cv2.cvtColor(current_image, cv2.COLOR_GRAY2BGR)
            
            # Update des Trackers
            success, new_box = tracker.update(current_disp)
            
            # Zeichne den ursprünglichen Spot als kleinen Kreis (Startpunkt)
            cv2.circle(current_disp, (x1, y1), radius=2, color=(150, 255, 0), thickness=-1)
            
            if success:
                # Berechne den Mittelpunkt der aktuellen Bounding-Box
                center_x = int(new_box[0] + new_box[2] / 2)
                center_y = int(new_box[1] + new_box[3] / 2)
                if i == len(images)-1:
                    x2, y2 = center_x, center_y
                
                # Zeichne die Bounding-Box (inklusive Oversize)
                p1 = (int(new_box[0]-oversize), int(new_box[1]-oversize))
                p2 = (int(new_box[0]+new_box[2]+oversize), int(new_box[1]+new_box[3]+oversize))
                cv2.rectangle(current_disp, p1, p2, (0, 0, 255), 2)
                
                # --- Zoom in das aktuelle Spot-ROI ---
                try:
                    zoom_oversize = 20
                    pos = 50  # Position, wo der Zoom in das Bild eingeblendet wird
                    roi = current_disp[
                        int(new_box[1]-zoom_oversize):int(new_box[1]+new_box[3]+zoom_oversize),
                        int(new_box[0]-zoom_oversize):int(new_box[0]+new_box[2]+zoom_oversize)
                    ]
                    zoomed_roi = cv2.resize(roi, (0,0), fx=10, fy=10)
                    h_roi, w_roi, _ = zoomed_roi.shape
                    # Zeichne Kreuzlinien im vergrößerten ROI
                    cv2.line(zoomed_roi, (int(w_roi/2), 0), (int(w_roi/2), h_roi), (0, 0, 255), line_thickness)
                    cv2.line(zoomed_roi, (0, int(h_roi/2)), (w_roi, int(h_roi/2)), (0, 0, 255), line_thickness)
                    # Stelle sicher, dass das Zoom-Bild in current_disp passt
                    if pos + h_roi <= current_disp.shape[0] and pos + w_roi <= current_disp.shape[1]:
                        current_disp[pos:pos+h_roi, pos:pos+w_roi] = zoomed_roi
                except Exception as e:
                    print("Zoom error:", e)
                
                # --- Zeichne weitere Hilfslinien ---
                # Horizontale Linie durch den Sonnenmittelpunkt
                cv2.line(current_disp, (0, sun_c[1]), (image_resolution, sun_c[1]), (0, 0, 255), line_thickness)
                # Vertikale und horizontale Linien durch den Startpunkt (x1, y1)
                cv2.line(current_disp, (x1, 0), (x1, image_resolution), (255, 0, 0), line_thickness)
                cv2.line(current_disp, (0, y1), (image_resolution, y1), (255, 0, 0), line_thickness)
                # Vertikale und horizontale Linien durch den Mittelpunkt der aktuellen Box
                cv2.line(current_disp, (center_x, 0), (center_x, image_resolution), (0, 0, 255), line_thickness)
                cv2.line(current_disp, (0, center_y), (image_resolution, center_y), (0, 0, 255), line_thickness)
                # Zeichne den Sonnenkreis (Mittelpunkt und Radius)
                cv2.circle(current_disp, sun_c, sun_r, (255, 0, 0), line_thickness)
                cv2.circle(current_disp, sun_c, int(sun_r*0.9), (200, 200, 0), line_thickness)
                # Beschrifte den Spot
                cv2.putText(current_disp, f"Spot ID: {idx}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 0), 2, cv2.LINE_AA)
            else:
                # Falls das Tracking fehlschlägt, wird eine Meldung angezeigt
                cv2.putText(current_disp, "Tracking fehlgeschlagen", (50, 80), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 2, cv2.LINE_AA)
            
            # Anzeige des aktuellen Frames
            if interactive:
                cv2.imshow(window_name, current_disp)
                key = cv2.waitKey(30) & 0xFF
                if key == ord('q'):  # Mit 'q' kann der gesamte Vorgang abgebrochen werden
                    print("Tracking abgebrochen.")
                    cv2.destroyWindow(window_name)
                    return
                elif key == ord('p'):  # Mit 'p' pausiert die Anzeige
                    print("Pausiert. Drücke eine Taste zum Fortfahren.")
                    cv2.waitKey(0)
            else:
                cv2.waitKey(30)
        
        # --- Schritt 6: Optionales Speichern der Ergebnisse ---
        if interactive:
            # Blende am Ende des Trackings für diesen Spot eine Eingabeaufforderung ein
            prompt_img = current_disp.copy()
            cv2.putText(prompt_img, "Druecke y zum Speichern, n zum Ueberspringen", 
                        (150, image_resolution - 50), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (255, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow(window_name, prompt_img)
            
            # Warte auf die Benutzereingabe ('y' oder 'n')
            while True:
                key = cv2.waitKey(0) & 0xFF
                if key == ord('y'):
                    include_trace = True
                    break
                elif key == ord('n'):
                    include_trace = False
                    break
        else:
            include_trace = False
        
        if include_trace and x2 is not None and y2 is not None:
            data_file = Path(f"data/TR_0{trace}/data_points.csv")
            try:
                existing_data = np.genfromtxt(str(data_file), delimiter=',', skip_header=True, dtype=float)
            except IOError:
                existing_data = np.empty((0, 5))
            new_row = np.array([x1, y1, x2, y2, len(images)-1])
            updated_data = np.vstack([existing_data, new_row])
            np.savetxt(str(data_file), updated_data, delimiter=',',
                       header="xcoor[pix],ycorr[pix],x2[pix],y2[pix],delta_time [h]",
                       comments="", fmt="%.8f")
    
    cv2.destroyAllWindows()

if __name__ == '__main__':
    run_tracking(trace=1, interactive=True)
