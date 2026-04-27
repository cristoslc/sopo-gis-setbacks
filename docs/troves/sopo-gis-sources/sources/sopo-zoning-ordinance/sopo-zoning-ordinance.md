---
source-id: sopo-zoning-ordinance
url: "https://southportland.gov/DocumentCenter/View/1510/CH-27--Zoning-with-New-TOC-format"
---

# South Portland Code — Chapter 27 (Zoning Ordinance)

**Document:** Chapter 27 — Zoning Ordinance
**Format:** PDF (Document Center)
**URL:** https://southportland.gov/DocumentCenter/View/1510/CH-27--Zoning-with-New-TOC-format
**Publisher:** City of South Portland
**Table of Contents URL:** https://www.southportland.gov/DocumentCenter/View/1451/Table-of-Contents

## Structure

Chapter 27 is organized by Articles:

| Article | Content |
|---------|---------|
| Article I — In General | Definitions, applicability, interpretation |
| Article II — Definitions | Sec. 27-201 et seq. — lot, front yard, side yard, rear yard, height, story, accessory structure, etc. |
| Article III — General Provisions | Applicability, nonconformities, variances, special exceptions |
| Article IV — Planned Development | PD district rules |
| Article V — Residential Districts | **AA**, **A**, **G**, **RF** — space and bulk regulations (setbacks, height, lot coverage) |
| Article VI — Business Districts | **LB**, **C**, **VC**, **VE** — commercial setback rules |
| Article VII — Industrial Districts | **IL**, **IH** — industrial setback and buffering rules |
| Article VIII — Conditional Zones | **CAZ**, **CBZ**, **ILZ**, etc. — property-specific contract zones |
| Article IX — Signs | Sign regulations (less relevant to setback tool) |
| Article X — Parking & Loading | Parking and loading standards |
| Article XI — Landscaping & Screening | Buffering rules (abutting residential triggers) |
| Article XII — Historic Preservation | Historic overlay |
| Article XIII — Appeals | Board of Appeals procedures |
| Article XIV — Special Exceptions | Special exception criteria |

## Setback-relevant sections (known mapping to `districts.yaml`)

| District | Section | Status in `districts.yaml` |
|----------|---------|---------------------------|
| AA | Sec. 27-524 | Partially transcribed — verify against current PDF |
| A | Sec. 27-534 | Partially transcribed — verify |
| G | Sec. 27-554 | Partially transcribed — verify |
| C | Sec. 27-780 | Partially transcribed — verify |
| VC | Sec. 27-7xx / 27-8xx | Needs transcription |
| VE | Sec. 27-7xx / 27-8xx | Needs transcription |
| RF | Sec. 27-5xx | Needs transcription |

## Key setback rules (high-level, not exhaustive)

- **Base residential setbacks:** Typically 30 ft front, 15 ft side, 25 ft rear (varies by district).
- **Height-conditional setbacks:** Several districts require side/rear yards of "50% of building height" when the building exceeds 30 ft. This cannot be modeled from parcel data alone (no building height attribute).
- **Shoreland Overlay:** Supersedes base setbacks within the Resource Protection zone (typically 75 ft or 100 ft from the high-water mark).
- **Secondary Front Yard:** On corner lots, one street is Primary Front Yard (full setback) and the other is Secondary Front Yard (median of nearby setbacks or the side yard, whichever is greater). The `sopo-setbacks` tool currently treats all street-facing edges as full front yards (conservative approximation).
- **Abutting residential:** Several commercial districts (C, VC, VE) have 0-ft side/rear setbacks unless they abut a residential district, in which case they jump to 15 ft. Modeling this requires a parcel-to-parcel adjacency check (not yet implemented).

## Related amendments and updates

- **ADU Amendments (Ordinance #4):** Modified Chapter 27 sections related to accessory dwelling units — may affect accessory structure setbacks.
- **Historic Preservation Ordinance:** Adaptive reuse and historic preservation rules may affect setback requirements for pre-1940 structures.

## Citation

City of South Portland. *Code of Ordinances — Chapter 27. Zoning*. Document Center. Accessed 2026-04-27.
