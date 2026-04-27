---
source-id: sopo-axisgis-viewer
url: "https://www.axisgis.com/South_PortlandME/"
---

# AxisGIS - South Portland, ME (CAI Technologies)

**System:** CAI Technologies AxisGIS (hosted viewer)
**URL:** https://www.axisgis.com/South_PortlandME/
**Maintainer:** City of South Portland Assessor / CAI Technologies

## Layers available

The viewer provides the following interactive map layers (toggleable in the layer list):

| Layer | Use for setback QA |
|-------|--------------------|
| **Tax Parcels** | Cross-check lot geometry and MBLU against downloaded GeoJSON |
| **Aerial Imagery** | Ground-truth irregular parcels, shoreland boundaries, and building footprints |
| **Streets** | Verify street centerline positions for front-yard classification |
| **Topography** | Useful for understanding slope-related buildability (not directly a setback factor, but affects constructability) |
| **City Infrastructure** | Water, sewer, storm drains — relevant for utility setback rules |
| **FEMA Flood Zones** | Buildable area may be further restricted independent of zoning setbacks |
| **Shoreland Zoning Overlay** | Critical overlay — supersedes base-district setbacks within 75–100 ft of high-water mark |

## Technical notes

- **Disclaimer:** The landing page states: *"These maps are not designed or intended to be used as a substitute for an accurate field survey, as performed by a Registered Land Surveyor."*
- **Data source:** The parcel attributes in AxisGIS are the same as those exported via the ArcGIS Hub *Parcels for download* dataset, because the Hub items are derived from AxisGIS.
- **No direct download:** AxisGIS is a *viewer*, not a download portal. For bulk data, use the ArcGIS Hub or contact the Assessor's office.
- **Print capability:** The viewer supports printing maps with user-selected layers.

## Why it matters for setback analysis

AxisGIS is the **visual QA tool** for the `sopo-setbacks` overlay workflow:

1. Load `setback_strips.geojson` and `envelopes.geojson` in QGIS.
2. Compare parcel edges and setback classifications against the AxisGIS aerial + parcel + street layers.
3. Use the Shoreland Zoning Overlay layer to flag parcels where the shoreland setback would supersede the base-district rules.

## Related URLs

- Next-gen viewer: https://next.axisgis.com/South_PortlandME/ (updated interface, same underlying data)
- Vision Government Solutions assessor database: https://gis.vgsi.com/southportlandme/ (search by MBLU or address)

## Citation

City of South Portland / CAI Technologies. *AxisGIS Property Maps — South Portland, Maine*. Hosted viewer. Accessed 2026-04-27.
