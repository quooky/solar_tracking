import cv2
import numpy as np
import pytest

# Importiere die Funktion; passe den Modulpfad gegebenenfalls an.
from solar_tracking.sunspot_detection import find_spots_and_boxes

def test_find_spots_and_boxes_separate_spots():
    """
    Testet die Funktion mit zwei weit auseinander liegenden Spots.
    Es wird erwartet, dass zwei separate Gruppen zurückgegeben werden.
    """
    # Erstelle ein synthetisches Graustufenbild (300x300) mit weißem Hintergrund (Wert 255)
    image = np.full((300, 300), 255, dtype=np.uint8)
    
    # Zeichne zwei separate schwarze Kreise (ausgefüllt) als Spots
    cv2.circle(image, (100, 100), 20, 0, thickness=-1)  # Spot 1
    cv2.circle(image, (200, 200), 20, 0, thickness=-1)  # Spot 2

    # Definiere den Sonnenmittelpunkt und -radius
    sun_center = (150, 150)
    sun_radius = 150  # Damit ist der erlaubte Abstand 0.9 * 150 = 135; beide Spots liegen innerhalb.

    grouped_boxes, grouped_centroids = find_spots_and_boxes(
        image, sun_radius, sun_center,
        max_area=5000, min_area=1000,
        max_distance_ratio=0.9, min_distance_between_clusters=100
    )

    # Es sollten zwei Gruppen (Boxes und Centroids) erkannt werden
    assert len(grouped_boxes) == 2, f"Erwartet 2 gruppierte Boxen, aber erhalten: {len(grouped_boxes)}"
    assert len(grouped_centroids) == 2, f"Erwartet 2 gruppierte Zentroiden, aber erhalten: {len(grouped_centroids)}"

    # Prüfe, ob die Zentroiden ungefähr in der Nähe der ursprünglichen Kreiszentren liegen
    # Da die Vorverarbeitung leichte Verschiebungen verursachen kann, wird ein Toleranzwert von 10 Pixeln genutzt.
    centroid1 = grouped_centroids[0]
    centroid2 = grouped_centroids[1]

    # Es ist nicht vorgegeben, in welcher Reihenfolge die Spots zurückgeliefert werden.
    # Wir prüfen, ob einer der Zentroiden in der Nähe von (100,100) und der andere in der Nähe von (200,200) liegt.
    d1 = np.linalg.norm(np.array(centroid1) - np.array([100, 100]))
    d2 = np.linalg.norm(np.array(centroid1) - np.array([200, 200]))
    if d1 < d2:
        assert d1 < 10, f"Zentroid 1 liegt nicht nahe genug bei (100,100): Abstand = {d1}"
        d = np.linalg.norm(np.array(centroid2) - np.array([200, 200]))
        assert d < 10, f"Zentroid 2 liegt nicht nahe genug bei (200,200): Abstand = {d}"
    else:
        assert d2 < 10, f"Zentroid 1 liegt nicht nahe genug bei (200,200): Abstand = {d2}"
        d = np.linalg.norm(np.array(centroid2) - np.array([100, 100]))
        assert d < 10, f"Zentroid 2 liegt nicht nahe genug bei (100,100): Abstand = {d}"



def test_find_spots_and_boxes_merged_spots():
    """
    Testet die Funktion mit zwei sehr nah beieinander liegenden Spots.
    Es wird erwartet, dass diese zu einer einzigen Gruppe zusammengefasst werden.
    """
    # Erstelle ein synthetisches Graustufenbild (300x300) mit weißem Hintergrund (Wert 255)
    image = np.full((300, 300), 255, dtype=np.uint8)
    
    # Zeichne zwei nahe beieinander liegende schwarze Kreise (ausgefüllt) als Spots
    cv2.circle(image, (100, 100), 20, 0, thickness=-1)  # Spot 1
    cv2.circle(image, (110, 110), 20, 0, thickness=-1)  # Spot 2 (sehr nah zu Spot 1)

    # Definiere den Sonnenmittelpunkt und -radius
    sun_center = (150, 150)
    sun_radius = 150

    grouped_boxes, grouped_centroids = find_spots_and_boxes(
        image, sun_radius, sun_center,
        max_area=5000, min_area=1000,
        max_distance_ratio=0.9, min_distance_between_clusters=100
    )

    # Da die Spots nahe beieinander liegen, sollten sie zu einer einzigen Gruppe zusammengefasst werden.
    assert len(grouped_boxes) == 1, f"Erwartet 1 gruppierte Box, aber erhalten: {len(grouped_boxes)}"
    assert len(grouped_centroids) == 1, f"Erwartet 1 gruppierten Zentroid, aber erhalten: {len(grouped_centroids)}"

    # Der erwartete Zentroid entspricht in etwa dem Durchschnitt der beiden ursprünglichen Zentren: (105,105)
    expected_centroid = np.array([105, 105])
    d = np.linalg.norm(np.array(grouped_centroids[0]) - expected_centroid)
    assert d < 10, f"Der gruppierte Zentroid weicht zu stark vom erwarteten Wert ab: Abstand = {d}"
