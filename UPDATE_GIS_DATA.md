# Updating GIS Data

## How to Update Layers

1. **Download Latest Data**:
   - Visit [South Portland ArcGIS Hub](https://city-of-south-portland-southportland.hub.arcgis.com/).
   - Search for and download the following layers as GeoJSON or Shapefile:
     - Parcels
     - Zoning Districts
     - Street Centerlines

2. **Organize Files**:
   - Create a new directory under `data/layers/` with the current date (e.g., `YYYY-MM-DD`).
   - Place downloaded files in the new directory.

3. **Commit Changes**:
   ```bash
   git lfs track "*.geojson" "*.gpkg" "*.shp" "*.shx" "*.dbf" "*.prj"
   git add data/layers/YYYY-MM-DD/
   git add .gitattributes
   git commit -m "Update GIS data: YYYY-MM-DD"
   git push
   ```

## Notes
- Git LFS is required to track large GIS files. Install it with:
  ```bash
  git lfs install
  ```
- If files exceed GitHub's LFS quota, consider compressing or hosting externally.
