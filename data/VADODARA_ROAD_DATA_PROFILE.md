# Vadodara Road Network — Dataset Profile

**Generated:** 2026-09-09  
**Source:** OpenStreetMap contributors  
**License:** ODbL (Open Database License)

---

## File Information

| Property | Value |
|---|---|
| Filename | `vadodara_road_network.geojson` |
| File size | ~35 MB |
| Format | GeoJSON FeatureCollection |
| Coordinate System | WGS84 (EPSG:4326) |

---

## Feature Statistics

| Property | Value |
|---|---|
| Total features | 45,909 |
| LineString features | 45,903 |
| Polygon features | 6 |
| Unique OSM IDs | 45,909 (all unique) |

---

## Geographic Coverage

| Dimension | Min | Max |
|---|---|---|
| Longitude | 72.8209°E | 73.5958°E |
| Latitude | 21.8310°N | 22.8146°N |

Coverage area: Vadodara (Baroda) city and surrounding region, Gujarat, India.

---

## Geometry Types

| Type | Count | Notes |
|---|---|---|
| LineString | 45,903 | Road/path segments — imported |
| Polygon | 6 | Pedestrian area outlines — **skipped** during import |

---

## Highway Type Distribution

| Highway Type | Count | % |
|---|---|---|
| residential | 30,752 | 67.0% |
| service | 7,376 | 16.1% |
| track | 2,161 | 4.7% |
| unclassified | 1,980 | 4.3% |
| tertiary | 1,460 | 3.2% |
| primary | 752 | 1.6% |
| secondary | 318 | 0.7% |
| trunk | 312 | 0.7% |
| motorway | 243 | 0.5% |
| primary_link | 110 | 0.2% |
| path | 106 | 0.2% |
| footway | 81 | 0.2% |
| tertiary_link | 52 | 0.1% |
| motorway_link | 49 | 0.1% |
| trunk_link | 44 | 0.1% |
| secondary_link | 37 | 0.1% |
| construction | 25 | 0.1% |
| steps | 20 | 0.0% |
| living_street | 14 | 0.0% |
| pedestrian | 8 | 0.0% |
| (others) | 59 | 0.1% |

---

## Field Presence

Only fields actually present in the dataset are listed. OSM data is extremely sparse — most roads contain only `@id` and `highway`.

| Field | Present | Coverage | Notes |
|---|---|---|---|
| `@id` (OSM ID) | 45,909 | 100% | Format: "way/NNNNNN" |
| `highway` | ~45,909 | ~100% | Road classification |
| `name` | 899 | 2.0% | English road name |
| `name:gu` | 219 | 0.5% | Gujarati name |
| `name:hi` | 219 | 0.5% | Hindi name |
| `ref` | 950 | 2.1% | Road reference number (e.g. NH48) |
| `oneway` | 2,730 | 5.9% | "yes" or "no" |
| `surface` | 2,775 | 6.0% | Road surface type |
| `access` | 2,680 | 5.8% | Access restriction |
| `lanes` | 317 | 0.7% | Number of lanes |
| `maxspeed` | 261 | 0.6% | Speed limit (km/h as string) |
| `bridge` | 1,091 | 2.4% | "yes" if bridge |
| `tunnel` | 99 | 0.2% | "yes" if tunnel |
| `layer` | 1,176 | 2.6% | Elevation layer |
| `junction` | 67 | 0.1% | Junction type |
| `lit` | 2 | 0.0% | Street lighting |
| `cycleway` | 14 | 0.0% | Cycle lane info |
| `sidewalk` | 8 | 0.0% | Sidewalk presence |
| `width` | 5 | 0.0% | Road width (m) |

**Fields NOT present:** traffic volume, vehicle counts, congestion levels, speed measurements, real-time data of any kind.

---

## Value Distributions

### oneway values
| Value | Count |
|---|---|
| yes | 2,698 |
| no | 32 |

### lanes values
| Value | Count |
|---|---|
| 2 | 174 |
| 4 | 78 |
| 1 | 54 |
| 3 | 6 |
| 6 | 4 |
| 5 | 1 |

### maxspeed values (km/h)
| Value | Count |
|---|---|
| 100 | 73 |
| 120 | 71 |
| 20 | 27 |
| 60 | 25 |
| 50 | 20 |
| 30 | 16 |
| 80 | 13 |
| 40 | 9 |
| 15 | 7 |

### surface values
| Value | Count |
|---|---|
| unpaved | 2,142 |
| asphalt | 407 |
| paved | 69 |
| concrete | 66 |
| paving_stones | 41 |
| ground | 36 |
| sand | 9 |
| cobblestone | 3 |
| compacted | 2 |

---

## All OSM Property Keys Present in Dataset

```
@id, abandoned:highway, abandoned:railway, access, addr:city, addr:housenumber,
addr:postcode, addr:street, area, bicycle, bridge, bridge:structure, bus:lanes,
conveying, covered, cutting, cycleway, depth, destination:ref, embankment, fixme,
fixme:maxheight, foot, footway, ford, gauge, handrail:left, handrail:right, hgv:lanes,
highway, horse, imagery_used, incline, informal, junction, lane_markings, lanes,
layer, level, lit, loc_name, maxheight, maxspeed, maxspeed:bus, maxspeed:hgv,
maxspeed:lanes, maxweight:signed, motor_vehicle, motorcar, motorcycle, motorroad,
name, name:etymology:wikidata, name:gu, name:hi, name:ks, name:mr, name:pa, name:ur,
note, old_ref, oneway, opening_date, proposed, railway, ref, ref:old, seasonal,
service, shoulder, sidewalk, source, source:bridge, source:lanes, source:surface,
source:tunnel, start_date, surface, toll, tunnel, width
```

---

## Missing / Not Available

The following fields are **NOT** in the dataset and were **NOT** fabricated:

- Traffic volume
- Vehicle counts
- Congestion levels
- Signal timing data
- Incident data
- Real-time data of any kind

OSM provides **static geographic road network data only**.

---

## Important Notes

1. The dataset covers the broader Vadodara district, not just the city core.
2. OSM data quality varies — many roads have minimal attributes.
3. All 45,909 OSM IDs are unique.
4. The 6 Polygon features are pedestrian area outlines, not road centerlines — skipped during import.
5. `maxspeed` is stored as a string in OSM (e.g., "100") — parsed to integer on import.
6. `oneway=no` (32 records) is treated as `False` (not one-way).

---

## Attribution

> Road network data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright)  
> Available under the Open Database License (ODbL).  
> This dataset does NOT include real-time traffic data.
