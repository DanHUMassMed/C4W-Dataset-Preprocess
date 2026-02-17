# Local Geocoding Setup with Nominatim

This guide explains how to set up a **local geocoding service** using Nominatim and OpenStreetMap data. This allows you to convert addresses into latitude/longitude coordinates and perform reverse geocoding entirely offline.

---

## 📌 Overview

This setup uses:

* **Nominatim** – OpenStreetMap’s official geocoding engine
* **OpenStreetMap (OSM) data** – Map and address data
* **Docker** – Containerized deployment

Once installed, you will have a local API for:

* Forward geocoding (address → coordinates)
* Reverse geocoding (coordinates → address)

---

## 📁 Directory Structure

Recommended project layout:

```
project-root/
├── data/
│   └── massachusetts-latest.osm.pbf
├── README.md
```

All map data and generated files are stored in the `data/` directory.

---

## ✅ Prerequisites

Make sure you have:

* Docker
* wget or curl
* 8+ GB RAM (16 GB recommended)
* 20+ GB free disk space

Verify Docker:

```bash
docker --version
```

---

## 🌍 Download Map Data

Download OpenStreetMap extracts from Geofabrik:

[https://download.geofabrik.de](https://download.geofabrik.de)

For Massachusetts:

```bash
mkdir -p data
cd data

wget https://download.geofabrik.de/north-america/us/massachusetts-latest.osm.pbf
```

This `.osm.pbf` file contains compressed OpenStreetMap data for the region.

---

## 📍 Run Nominatim (Geocoding Server)

### 1️⃣ Pull the Docker Image

```bash
docker pull mediagis/nominatim:5.2
```

---

### 2️⃣ Start the Nominatim Container

Run the container and import the map data:

```bash
docker run -it \
  --shm-size=1g \
  -v ./data:/data \
  -e PBF_PATH=/data/massachusetts-latest.osm.pbf \
  -p 8080:8080 \
  --name nominatim \
  mediagis/nominatim:5.2
```

This command will:

* Import OSM data
* Build PostgreSQL indexes
* Start the geocoding API

⚠️ Initial import may take several hours depending on your hardware.

---

## 🌐 Server Information

Once running, the API is available at:

```
http://localhost:8080
```

---

## 🔍 Test Geocoding

### Forward Geocoding (Address → Coordinates)

```bash
curl "http://localhost:8080/search?q=100+Front+Street+Worcester+MA&format=json"
```

### Reverse Geocoding (Coordinates → Address)

```bash
curl "http://localhost:8080/reverse?lat=42.2626&lon=-71.8023&format=json"
```

---

## ⚙️ Performance Notes

### Memory

* Minimum: 8 GB RAM
* Recommended: 16 GB RAM
* Increase Docker memory limits if imports fail

### Disk Usage

Nominatim generates large databases and indexes.

Expect:

* 5–10× the size of the original `.pbf` file

---

## 🔄 Updating Map Data

To refresh your geocoding data:

```bash
docker rm -f nominatim
rm -rf data/*
wget <new-pbf-url>
```

Then re-run the container import command.

---

## 🐞 Troubleshooting

### Import Fails or Crashes

* Ensure sufficient RAM and disk space
* Increase Docker memory
* Verify `--shm-size` is set

Restart from scratch:

```bash
docker rm -f nominatim
```

---

## 📦 Production Considerations

For long-term or production deployments:

* Use Docker Compose
* Persist PostgreSQL volumes
* Schedule periodic data updates
* Add monitoring and backups
* Configure API rate limits

---

## 📚 References

* Nominatim: [https://nominatim.org](https://nominatim.org)
* Geofabrik: [https://download.geofabrik.de](https://download.geofabrik.de)
* OpenStreetMap: [https://www.openstreetmap.org](https://www.openstreetmap.org)

---

## ✅ Summary

You now have a fully local geocoding service that:

* Runs offline
* Uses OpenStreetMap data
* Supports forward and reverse geocoding
* Integrates easily with GIS and web applications

This setup is well-suited for civic tech, research, and data pipelines requiring reliable address lookup.
