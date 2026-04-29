#!/usr/bin/env python3
"""
Load South Portland GIS layers into QGIS with styled layers and
a map canvas zoomed to South Portland.

Saves an uncompressed .qgs project file with map canvas view injected,
so QGIS opens directly showing the right area and layers.

Run:
    /Applications/QGIS-final-4_0_1.app/Contents/MacOS/python load_layers.py
    open -a "QGIS-final-4_0_1" sopo_gis.qgs
"""

import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data", "layers", "2026-04-27")
PROJECT_PATH = os.path.join(SCRIPT_DIR, "sopo_gis.qgs")

SOUTH_PORTLAND_CRS = "EPSG:4326"
CENTER_LON = -70.296
CENTER_LAT = 43.627
EXTENT_WIDTH = 0.050
EXTENT_HEIGHT = 0.035

LAYER_CONFIGS = [
    {
        "file": "parcels.geojson",
        "name": "Parcels",
        "provider": "ogr",
        "color": "#f0a040",
        "fill_alpha": 40,
        "outline_width": 0.4,
    },
    {
        "file": "zoning_districts.geojson",
        "name": "Zoning Districts",
        "provider": "ogr",
        "color": "#4a90d9",
        "fill_alpha": 50,
        "outline_width": 1.0,
    },
    {
        "file": "street_centerlines.geojson",
        "name": "Street Centerlines",
        "provider": "ogr",
        "color": "#333333",
        "fill_alpha": 0,
        "outline_width": 0.8,
        "is_line": True,
    },
]


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def style_polyfill_layer(layer, config):
    from qgis.PyQt.QtGui import QColor
    from qgis.core import (
        QgsFillSymbol,
        QgsSimpleFillSymbolLayer,
        QgsSingleSymbolRenderer,
    )

    r, g, b = hex_to_rgb(config["color"])
    alpha = config["fill_alpha"]

    symbol_layer = QgsSimpleFillSymbolLayer()
    symbol_layer.setFillColor(QColor(r, g, b, alpha))
    symbol_layer.setStrokeColor(QColor(0, 0, 0, 180))
    symbol_layer.setStrokeWidth(config["outline_width"])

    symbol = QgsFillSymbol([symbol_layer])
    renderer = QgsSingleSymbolRenderer(symbol)
    layer.setRenderer(renderer)


def style_line_layer(layer, config):
    from qgis.PyQt.QtGui import QColor
    from qgis.core import (
        QgsLineSymbol,
        QgsSimpleLineSymbolLayer,
        QgsSingleSymbolRenderer,
    )

    r, g, b = hex_to_rgb(config["color"])

    symbol_layer = QgsSimpleLineSymbolLayer()
    symbol_layer.setColor(QColor(r, g, b))
    symbol_layer.setWidth(config["outline_width"])

    symbol = QgsLineSymbol([symbol_layer])
    renderer = QgsSingleSymbolRenderer(symbol)
    layer.setRenderer(renderer)


def style_layer(layer, config):
    is_line = config.get("is_line", False)
    if is_line:
        style_line_layer(layer, config)
    else:
        style_polyfill_layer(layer, config)


def load_standalone():
    qgis_app = "/Applications/QGIS-final-4_0_1.app"
    os.environ["QGIS_PREFIX_PATH"] = os.path.join(qgis_app, "Contents", "Resources")
    os.environ["PROJ_DATA"] = os.path.join(
        qgis_app, "Contents", "Resources", "qgis", "proj"
    )
    python_site = os.path.join(
        qgis_app, "Contents", "Resources", "python3.11", "site-packages"
    )
    python_path = os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = python_site + (":" + python_path if python_path else "")
    sys.path.insert(0, python_site)

    from qgis.core import (
        QgsApplication,
        QgsCoordinateReferenceSystem,
        QgsProject,
        QgsVectorLayer,
    )

    qgs = QgsApplication([a.encode() for a in sys.argv], True)
    qgs.initQgis()

    project = QgsProject.instance()
    crs = QgsCoordinateReferenceSystem(SOUTH_PORTLAND_CRS)
    project.setCrs(crs)

    for config in LAYER_CONFIGS:
        path = os.path.join(DATA_DIR, config["file"])
        if not os.path.exists(path):
            print(f"SKIP: {path} not found")
            continue
        layer = QgsVectorLayer(path, config["name"], config["provider"])
        if not layer.isValid():
            print(f"FAIL: {config['name']} — invalid layer")
            continue

        style_layer(layer, config)
        project.addMapLayer(layer)
        print(f"LOADED: {config['name']} ({layer.featureCount()} features)")

    x_min = CENTER_LON - EXTENT_WIDTH / 2
    x_max = CENTER_LON + EXTENT_WIDTH / 2
    y_min = CENTER_LAT - EXTENT_HEIGHT / 2
    y_max = CENTER_LAT + EXTENT_HEIGHT / 2

    project.write(PROJECT_PATH)
    qgs.exitQgis()

    with open(PROJECT_PATH, "r", encoding="utf-8") as f:
        xml = f.read()

    canvas_xml = (
        '  <mapcanvas name="theMapCanvas" annotationsVisible="1">\n'
        "    <units>degrees</units>\n"
        "    <extent>\n"
        f"      <xmin>{x_min}</xmin>\n"
        f"      <ymin>{y_min}</ymin>\n"
        f"      <xmax>{x_max}</xmax>\n"
        f"      <ymax>{y_max}</ymax>\n"
        "    </extent>\n"
        "    <rotation>0</rotation>\n"
        "    <destinationsrs>\n"
        f'      <spatialrefsys nativeFormat="Wkt">\n'
        '        <wkt>GEOGCRS["WGS 84",ENSEMBLE["World Geodetic System 1984 ensemble",MEMBER["World Geodetic System 1984 (Transit)"],MEMBER["World Geodetic System 1984 (G730)"],MEMBER["World Geodetic System 1984 (G873)"],MEMBER["World Geodetic System 1984 (G1150)"],MEMBER["World Geodetic System 1984 (G1674)"],MEMBER["World Geodetic System 1984 (G1762)"],MEMBER["World Geodetic System 1984 (G2139)"],MEMBER["World Geodetic System 1984 (G2296)"],ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1]],ENSEMBLEACCURACY[2.0]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]],CS[ellipsoidal,2],AXIS["geodetic latitude (Lat)",north,ORDER[1],ANGLEUNIT["degree",0.0174532925199433]],AXIS["geodetic longitude (Lon)",east,ORDER[2],ANGLEUNIT["degree",0.0174532925199433]],USAGE[SCOPE["Horizontal component of 3D system."],AREA["World."],BBOX[-90,-180,90,180]],ID["EPSG",4326]]</wkt>\n'
        "        <proj4>+proj=longlat +datum=WGS84 +no_defs</proj4>\n"
        "        <srsid>3452</srsid>\n"
        "        <srid>4326</srid>\n"
        "        <authid>EPSG:4326</authid>\n"
        "        <description>WGS 84</description>\n"
        "        <projectionacronym>longlat</projectionacronym>\n"
        "        <ellipsoidacronym>EPSG:7030</ellipsoidacronym>\n"
        "        <geographicflag>true</geographicflag>\n"
        "      </spatialrefsys>\n"
        "    </destinationsrs>\n"
        "    <rendermaptile>0</rendermaptile>\n"
        "    <expressionContextScope/>\n"
        "  </mapcanvas>\n"
    )

    xml = re.sub(r"(</projectlayers>)", r"\1\n" + canvas_xml, xml, count=1)

    with open(PROJECT_PATH, "w", encoding="utf-8") as f:
        f.write(xml)

    print(f"Project saved: {PROJECT_PATH}")
    print(f"View: lon=[{x_min}, {x_max}] lat=[{y_min}, {y_max}] — South Portland")


if __name__ == "__main__":
    load_standalone()
