# GNSS Interference Monitoring Data Download Tool
[![PyPI](https://img.shields.io/pypi/v/rfi-fileparser.svg)](https://pypi.org/project/rfi-fileparser/)
[![License](https://img.shields.io/github/license/liu1322/rfi-fileparser.svg)](./LICENSE)

This repository contains the source code for the Python package **`<rfi_fileparser>`**, which provides utilities to download and visualize JSON files from the GNSS Interference Monitoring Website: http://rfi.stanford.edu/. Users can specify a start date, end date, and data type (`jamming`, `spoofing`, or `dashboard`).


## Installation
### Prerequisites
* Python 3.8+ installed

### Setup

```bash
pip install rfi-fileparser
```

Update periodically to get the latest features:

```bash
pip install --upgrade rfi-fileparser
```



## Usage

### Download JSON data

```python
from rfi_fileparser import downloader

downloader.download_files("2025/04/23", "2025/04/26", "dashboard")
downloader.download_files("2025/04/23", "2025/04/26", "jamming")
downloader.download_files("2025/04/23", "2025/04/26", "spoofing")
```

* HTTPS warnings may appear; these are safe and result from bypassing certificate checks.
* Downloading one week of all data types may take a few minutes.
* Files are saved under the directory `downloaded_json_files/` in the current working path.



### Visualize heatmaps

```python
from rfi_fileparser import plot_daily_heatmap, plot_hourly_heatmap

plot_daily_heatmap("downloaded_json_files", "2025/04/24")
plot_hourly_heatmap("downloaded_json_files", "2025/04/24")
```

### Visualize events

```python
from rfi_fileparser import plot_jamming, plot_spoofing

plot_jamming("downloaded_json_files", "2025/04/24")
plot_spoofing("downloaded_json_files", "2025/04/24")
```




## Data Structure 
```
.downloaded_json_files/
├── dashboard
│   ├──general.json
│   └── 2025
│       └── 04
│           └── statistics.json
├── jamming
│   └── 2025
│       └── 04
│           └── 24
│               ├── events.json
│               ├── heatmap.json
│               ├── 0000
│               │   └── heatmap.json
│               ├── 0100
│               │   └── heatmap.json
│               └── ...
└── spoofing
    └── 2025
        └── 04
            └── 24
                ├── beforeAndDuringSpoofing.json
                ├── duringAndAfterSpoofing.json
                ├── events.json
                └── heatmap.json

```



## Data Information

### 1. `jamming/2025/04/24/heatmap.json`

**→ Daily heatmap data.**


### 2. `jamming/2025/04/24/0000/heatmap.json`

**→ Hourly heatmap data.**

* **`h3Index`**: Unique index for each hexagonal cell (H3 system).
  Use it to get hexgaon boundaries in Python:

  ```python
  from h3 import h3
  from shapely.geometry import Polygon

  def h3_to_polygon(h3_index):
      boundary = h3.h3_to_geo_boundary(h3_index, geo_json=True)
      return Polygon(boundary)
  ```

  *(Functions for this are included in the GitHub repository.)*

* **`lowQualityCount` and `totalAircraftCount`**: Number of low NIC / total aircraft seen within that hexagonal cell.



### 3. `jamming/2025/04/24/event.json`

**→ All jamming events detected on that day.**

* **`latitude` and `longitude`**: Centroid location of each jamming event.
* **`startTime` and `endTime`**: Start and end times of each jamming event.



### 4. `spoofing/2025/04/24/beforeAndDuringSpoofing.json`

**→ For each spoofing event, shows the last known normal position and the first spoofed position observed for each affected flight.**

* **`beforeSpoofing`**: Last known normal position
* **`spoofedInto`**: First spoofed position

Example:

```json
{
  "event_1": [
    {
      "beforeSpoofing": {
        "lat": 53.1131,
        "lon": 49.9999,
        "alt": 9098.28,
        "nic": 7,
        "time": 1740858262.297
      },
      "spoofedInto": {
        "lat": 53.102,
        "lon": 49.9545,
        "alt": 9098.28,
        "nic": 0,
        "time": 1740859918.787
      },
    },
    ...
  ],
  ...
}
```



### 5. `spoofing/2025/04/24/duringAndAfterSpoofing.json`

**→ For each spoofing event, shows the last spoofed position and the first normal position after recovery.**

* **`spoofedInto`**: Last spoofed position
* **`afterRecovering`**: First normal position after spoofing

Example:

```json
{
  "event_1": [
    {
      "spoofedInto": {
        "lat": 53.101,
        "lon": 49.9843,
        "alt": 9098.28,
        "nic": 0,
        "time": 1740867858.763
      },
      "afterRecovering": {
        "lat": 51.7174,
        "lon": 55.0444,
        "alt": 9098.28,
        "nic": 0,
        "time": 1740868558.257
      }
    },
    ...
  ],
  ...
}
```



### 6. `spoofing/2025/04/24/event.json`

**→ All spoofing events detected on that day.**

* **`latitude` and `longitude`**: Centroid location of each spoofing event.
* **`startTime` and `endTime`**: Start and end times of each spoofing event.



### 7. `spoofing/2025/04/24/heatmap.json`

**→ Daily heatmap of spoofing-affected region.**

* **`h3Index`**: Unique index for each hexagonal cell (H3 system).
  *(See usage example above under `jamming/2025/04/24/0000/heatmap.json`.)*

* **`spoofedFlightCount`**: Number of affected aircraft within each cell, based on interpolated true paths.

* **`seenAircraftCount`**: Number of unaffected aircraft in the same cell, based on ADS-B data.

Example:

```json
{
  "event_1": [
    {
      "h3Index": "841f533ffffffff",
      "spoofedFlightCount": 2,
      "seenAircraftCount": 26
    },
    {
      "h3Index": "841f53bffffffff",
      "spoofedFlightCount": 3,
      "seenAircraftCount": 19
    },
    ...
  ],
  ...
}
```


