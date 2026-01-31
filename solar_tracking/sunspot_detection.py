from astropy.io import fits
import cv2
import numpy as np

def sun_infos(fits_path:str, data_layer: int = 1):
    """
    Extract all need inforamtion from the header of the fits file. and also 
    calculte the sun_radius in pix.

    Assumtions:
    - Header of the data on second position 
    - 'RSUN_OBS': observed radius of the sun in in arcsec
    - 'CDELT1': scale in arcsec per pix 
    - 'CRPIX1','CRPIX1': x and y corrdinate of the reference pix, here the
                        centerpoint of the solardisk
    - 'NAXIS2': resolution of the image assumed symmetrical 

    Args:
        fits_path (str): path to the fits file 
        data_layer int): the index of the data layer in the fits file

    Returns:
        sun_r_pix (int): sun radius in pix on the image
        sun_c (int): position of the sun center (x,y)
        res (int): resolution of the used image
    """
    
    with fits.open(fits_path) as hdul:
        header = hdul[1].header 
       # global sun_r  
        sun_r = int(header['RSUN_OBS']/ header['CDELT1'])
        sun_c = (int(header['CRPIX1']),int(header['CRPIX2']))
        res = int(header['NAXIS2'])
    
    return sun_r, sun_c, res



def find_spots_and_boxes(image: np.ndarray,
                         sun_radius: int,
                         sun_center: tuple,
                         max_area: int = 5000,
                         min_area: int = 1000,
                         max_distance_ratio: float = 0.9,
                         min_distance_between_clusters: int = 20):
    """
    Findet die Position von Sonnenflecken im vorverarbeiteten Bild und gruppiert benachbarte Spots.
    
    Das Bild muss bereits normalisiert vorliegen (Werte zwischen 0 und 255). Zunächst wird das
    Bild vorverarbeitet (Blur, adaptive Schwellenwertbildung, Dilation und Erosion) und mittels
    Connected Component Labeling werden potenzielle Spots identifiziert. Anschließend werden die Spots
    nach Fläche und Entfernung vom Sonnenmittelpunkt gefiltert. Zum Schluss werden nahe beieinander liegende
    Spots mithilfe eines Clustering-Algorithmus (DBSCAN) zu Gruppen zusammengefasst.
    
    Parameter
    ----------
    image : np.ndarray
        Das Eingabebild (normalisiert zwischen 0 und 255).
    sun_radius : int
        Der Sonnenradius in Pixeln.
    sun_center : tuple
        Die (x, y)-Koordinate des Sonnenmittelpunkts.
    max_area : int, optional
        Maximale Fläche eines Spots in Pixeln (Standard: 5000).
    min_area : int, optional
        Minimale Fläche eines Spots in Pixeln (Standard: 1000).
    max_distance_ratio : float, optional
        Maximaler Abstand (als Anteil des Sonnenradius) vom Sonnenmittelpunkt, bis zu dem Spots berücksichtigt werden (Standard: 0.9).
    min_distance_between_clusters : int, optional
        Minimaler Abstand in Pixeln zwischen Spots, damit diese nicht in verschiedene Cluster eingeordnet werden (Standard: 100).
    
    Returns
    -------
    grouped_boxes : list of tuples
        Liste von Bounding-Boxen für die gruppierten Spots, jeweils als (x, y, w, h), wobei (x, y) die obere linke Ecke ist.
    grouped_centroids : list of np.ndarray
        Liste der Zentroiden der gruppierten Spots als (x, y)-Werte.
    """
    
    # Vorverarbeitung des Bildes
    image_blur = cv2.GaussianBlur(image, (13, 13), 0)
    binary_img = cv2.adaptiveThreshold(image_blur, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV,
                                       301, 30)
    binary_img = cv2.dilate(binary_img, None, iterations=1)
    binary_img = cv2.erode(binary_img, None, iterations=1)
    
    # Verbundene Komponenten (Connected Components) ermitteln
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_img)
    
    # Spots nach Fläche und Entfernung filtern
    filtered_boxes = []
    filtered_centroids = []
    
    for label in range(1, num_labels):  # Hintergrund (Label 0) überspringen
        area = stats[label, cv2.CC_STAT_AREA]
        if not (min_area < area < max_area):
            continue
        
        centroid = centroids[label]
        # Abstand vom Spot-Zentroid zum Sonnenmittelpunkt
        distance = np.linalg.norm(np.array(centroid) - np.array(sun_center))
        if distance > max_distance_ratio * sun_radius:
            continue
        
        x = stats[label, cv2.CC_STAT_LEFT]
        y = stats[label, cv2.CC_STAT_TOP]
        w = stats[label, cv2.CC_STAT_WIDTH]
        h = stats[label, cv2.CC_STAT_HEIGHT]
        filtered_boxes.append((x, y, w, h))
        filtered_centroids.append(centroid)
    
    # Falls keine Spots gefunden wurden, leere Listen zurückgeben
    if not filtered_boxes:
        return [], []
    
    # Gruppierung der Spots mittels Clustering (DBSCAN)
    try:
        from sklearn.cluster import DBSCAN
        filtered_centroids_array = np.array(filtered_centroids)
        clustering = DBSCAN(eps=min_distance_between_clusters, min_samples=1).fit(filtered_centroids_array)
        cluster_labels = clustering.labels_
    except ImportError:
        # Fallback: Jeder Spot ist ein eigener Cluster
        cluster_labels = np.arange(len(filtered_centroids))
    
    unique_labels = np.unique(cluster_labels)
    grouped_boxes = []
    grouped_centroids = []
    
    # Für jeden Cluster: Bestimme die umschließende Bounding-Box und den Mittelwert der Zentroiden
    for cluster in unique_labels:
        indices = np.where(cluster_labels == cluster)[0]
        
        # Sammle alle Bounding-Boxen und Zentroiden des Clusters
        cluster_boxes = [filtered_boxes[i] for i in indices]
        cluster_centroids = [filtered_centroids[i] for i in indices]
        
        # Berechne die minimale und maximale Koordinate für die Bounding-Box
        x_min = min(box[0] for box in cluster_boxes)
        y_min = min(box[1] for box in cluster_boxes)
        x_max = max(box[0] + box[2] for box in cluster_boxes)
        y_max = max(box[1] + box[3] for box in cluster_boxes)
        grouped_boxes.append((x_min, y_min, x_max - x_min, y_max - y_min))
        
        # Berechne den Mittelwert der Zentroiden
        avg_centroid = np.mean(cluster_centroids, axis=0)
        grouped_centroids.append(avg_centroid)
    
    return grouped_boxes, grouped_centroids
