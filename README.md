# ProFinal ISEP - Big Data Analytics and Decision Making

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange.svg)](https://jupyter.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Apache Airflow](https://img.shields.io/badge/Airflow-2.1.0-red.svg)](https://airflow.apache.org/)

Final project for the Big Data Analytics and Decision Making course at ISEP (Instituto Superior de Engenharia do Porto).

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Project Objectives](#project-objectives)
- [Key Features](#key-features)
- [Data Sources](#data-sources)
- [Our Team](#our-team)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running with Docker](#running-with-docker)
- [Usage](#usage)
- [Data Pipeline](#data-pipeline)
- [Data Warehouse Schema](#data-warehouse-schema)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## 🎯 About the Project

This repository contains a comprehensive Big Data analytics solution developed as the final project for the Big Data Analytics and Decision Making course at ISEP. The project implements an **end-to-end data pipeline** for collecting, processing, and analyzing urban mobility and environmental data from Porto, Portugal's Urban Platform.

The system leverages modern data engineering tools and practices to create an automated ETL pipeline that:
- **Extracts** data from multiple sources (APIs and datasets)
- **Transforms** raw data through preprocessing and enrichment
- **Loads** structured data into a data warehouse
- **Orchestrates** workflows using Apache Airflow
- **Stores** data in object storage (MinIO) and relational database (PostgreSQL)

### 🎓 Academic Context

This project was developed as part of the Post-Graduation in Big Data Analytics and Decision Making at ISEP, focusing on practical implementation of big data concepts including distributed storage, workflow orchestration, dimensional modeling, and automated data pipelines.

## 🎯 Project Objectives

### Primary Objectives

1. **Build an Automated Data Pipeline**
   - Design and implement a complete ETL pipeline for urban data
   - Automate data collection from Porto's Urban Platform FIWARE broker
   - Process and transform raw data into analytics-ready formats

2. **Implement Data Lake and Data Warehouse Architecture**
   - Create a data lake using MinIO for raw and preprocessed data storage
   - Design a star schema data warehouse in PostgreSQL
   - Implement dimensional modeling with fact and dimension tables

3. **Orchestrate Workflows with Apache Airflow**
   - Develop DAGs (Directed Acyclic Graphs) for pipeline automation
   - Schedule and monitor data processing tasks
   - Ensure data quality and pipeline reliability

4. **Integrate Multiple Urban Data Sources**
   - Two-wheeled vehicle parking occupancy data
   - Air quality and pollution metrics
   - Public transportation (bus and metro) schedules
   - Demographic data from INE (Instituto Nacional de Estatística)

5. **Enable Analytics and Decision Making**
   - Create a unified view of urban mobility patterns
   - Support data-driven decision making for urban planning
   - Provide insights into environmental and transportation correlations

### Technical Objectives

- Containerize the entire infrastructure using Docker and Docker Compose
- Implement geospatial data processing with coordinate enrichment
- Handle time-series data with proper temporal dimensions
- Apply data preprocessing techniques (aggregation, cleaning, normalization)
- Ensure scalability and maintainability of the pipeline

## 🌟 Key Features

- 📊 **Multi-Source Data Integration**: Combines parking, air quality, transportation, and demographic data
- 🔄 **Automated ETL Pipeline**: Full automation from API calls to data warehouse population
- 🐳 **Containerized Infrastructure**: Complete Docker-based deployment with PostgreSQL, MinIO, and Airflow
- 🗄️ **Data Lake Architecture**: Raw and preprocessed data stored in MinIO object storage
- 🏢 **Star Schema Data Warehouse**: Dimensional modeling with fact and dimension tables
- 📍 **Geospatial Processing**: Location enrichment with administrative boundaries (Concelho, Freguesia)
- ⏱️ **Time-Series Analysis**: Temporal aggregations (hourly, daily) for trend analysis
- 🔁 **Workflow Orchestration**: Apache Airflow DAGs for pipeline scheduling and monitoring
- 📈 **Analytics-Ready Data**: Preprocessed datasets optimized for analysis and visualization

## 📦 Data Sources

### 1. **Two-Wheeled Vehicle Parking (Primary Data Source)**
- **Source**: Porto Urban Platform FIWARE Broker API
- **Type**: Real-time parking occupancy data
- **Endpoint**: `https://broker.fiware.urbanplatform.portodigital.pt/v2/entities`
- **Metrics**: Available spots, occupied spots, total capacity, location coordinates
- **Update Frequency**: Near real-time

### 2. **Air Quality Data**
- **Source**: Porto Urban Platform Air Quality Sensors
- **Variables**: NO2, NOx, O3, Ox, PM1, PM10, PM2.5, CO
- **Format**: Excel dataset (urban-platform-air-quality-2022.xlsx)
- **Temporal Resolution**: Hourly and daily aggregations
- **Locations**: Multiple monitoring stations across Porto

### 3. **Public Transportation Data**
- **Source**: GTFS (General Transit Feed Specification) datasets
- **Providers**: 
  - STCP (Sociedade de Transportes Coletivos do Porto) - Bus network
  - Metro do Porto - Metro network
- **Information**: Stop locations, schedules, routes, service calendars
- **Format**: CSV files (stops.txt, stop_times.txt, calendar.txt)

### 4. **Demographic Data**
- **Source**: INE (Instituto Nacional de Estatística)
- **Type**: Census and administrative boundary data
- **Usage**: Location enrichment with Concelho and Freguesia information

## 👥 Our Team

| Group Members                        | Student ID | Short CV                                                                                                                                               |
| ------------------------------------ | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Daniel Sampaio Osório**           | #1230374   | Former researcher in Cell Biology. Currently Junior Data Scientist at BNP Paribas Personal Finance working on marketing analytics and personalization |
| **Diogo Dias Assunção Serra**        | #1230293   | Former Data Analyst at Sport Zone. Currently working in the textile industry as manager at Sersimalhas, Lda.                                        |
| **Jorge Laginhas**                   | -          | [Background information]                                                                                                                               |
| **Pedro Rodrigues**                  | #1230302   | Graduated in Management (FEP) and currently working as a COBOL programmer.                                                                            |
| **Tiago Fernandes**                  | #1160973   | Recently graduated in Industrial Management. Currently working as a Process Engineer at Amkor Technology Inc., specializing in the semiconductor industry |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                             │
├──────────────┬────────────���─┬──────────────┬───────────────────┤
│  FIWARE API  │ Air Quality  │  GTFS Data   │   INE Census      │
│  (2-Wheel)   │  (Sensors)   │ (STCP/Metro) │  (Demographics)   │
└──────┬───────┴──────┬───────┴──────┬───────┴──────┬────────────┘
       │              │              │              │
       ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APACHE AIRFLOW (Orchestration)                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  DAGs: Scheduling, Monitoring, Error Handling              │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
┌─────────────┐   ┌──────────────────┐   ┌──────────────┐
│   EXTRACT   │   │    TRANSFORM     │   │     LOAD     │
│             │   │                  │   │              │
│ • API Calls │   │ • Data Cleaning  │   │ • PostgreSQL │
│ • JSON Data │──▶│ • Aggregation    │──▶│ • Star Schema│
│             │   │ • Geolocation    │   │ • Fact Tables│
│             │   │ • Normalization  │   │ • Dimensions │
└─────────────┘   └──────────────────┘   └──────────────┘
       │                   │
       ▼                   ▼
┌──────────────────────────────────┐
│         MINIO (Object Storage)    │
│  ┌────────────┐  ┌──────────────┐│
│  │ raw/       │  │ preprocessed/││
│  │ • JSON     │  │ • Parquet    ││
│  └────────────┘  └──────────────┘│
└──────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│   POSTGRESQL (Data Warehouse)    │
│  ┌─────────────────────────────┐ │
│  │  Star Schema:               │ │
│  │  • FactTwoWheel             │ │
│  │  • DimDate                  │ │
│  │  • DimLocation              │ │
│  └─────────────────────────────┘ │
└──────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│    ANALYTICS & VISUALIZATION     │
│  • Business Intelligence Tools   │
│  • Data Science Notebooks        │
│  • Decision Support Systems      │
└──────────────────────────────────┘
```

## 📁 Project Structure

```
proFinal_BDDM_ISEP/
├── Preprocessing_datasets/          # Data preprocessing scripts and notebooks
│   ├── air_polution/               # Air quality data preprocessing
│   │   ├── Pollution_Script.py     # Python script for pollution data cleaning
│   │   └── Legenda_Variáveis.txt   # Variable descriptions
│   ├── bus_metro/                  # Public transportation data preprocessing
│   │   └── bus_metro_complete6.py  # STCP and Metro data processing
│   └── ine/                        # INE demographic data
│
├── full_pipeline_prototype_2wheel/  # Complete ETL pipeline implementation
│   ├── airflow_dags/               # Airflow DAG definitions
│   ├── python_pipeline_tasks/      # Python scripts for ETL tasks
│   │   ├── json_twowheel.py        # API data extraction to MinIO
│   │   ├── Concatenate_preproc.py  # Data preprocessing and transformation
│   │   └── load_populate_table.py  # Load data into PostgreSQL
│   ├── SQL/                        # SQL scripts for data warehouse
│   │   ├── final_dw_create_2.sql   # Create star schema tables
│   │   └── join_all.sql            # Query example for analytics
│   ├── Data_flow_test.ipynb        # Jupyter notebook for pipeline testing
│   └── readme.md                   # Pipeline-specific documentation
│
├── Dockerfile                      # Docker image configuration (Airflow)
├── docker-compose.yaml             # Multi-container orchestration
├── makefile                        # Build and deployment automation
├── .gitignore                      # Git ignore rules
├── LICENSE                         # Apache 2.0 License
└── README.md                       # Project documentation
```

## 🛠️ Technologies Used

### Core Technologies

- **Python 3.8+** - Primary programming language
- **Apache Airflow 2.1.0** - Workflow orchestration and scheduling
- **PostgreSQL 13** - Relational database and data warehouse
- **MinIO** - S3-compatible object storage (data lake)
- **Docker & Docker Compose** - Containerization and orchestration

### Python Libraries

- **pandas** - Data manipulation and analysis
- **requests** - HTTP library for API calls
- **minio** - MinIO Python SDK for object storage
- **geopy** - Geospatial processing and geocoding
- **SQLAlchemy** - SQL toolkit and ORM
- **psycopg2** - PostgreSQL adapter for Python
- **numpy** - Numerical computing

### Data Formats

- **JSON** - Raw data from APIs
- **Parquet** - Columnar storage for preprocessed data
- **CSV** - GTFS transportation data
- **Excel** - Air quality datasets

### Infrastructure

- **Docker** - Container platform
- **Make** - Build automation tool
- **Git** - Version control

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (version 20.10+)
- **Docker Compose** (version 1.29+)
- **Python 3.8 or higher** (for local development)
- **Git**
- **Make** (optional, for using Makefile commands)

Minimum system requirements:
- 8GB RAM
- 10GB free disk space
- Linux/macOS/Windows with WSL2

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/dosorio79/proFinal_BDDM_ISEP.git
cd proFinal_BDDM_ISEP
```

2. **Set environment variables** (Linux/macOS):
```bash
export UID=$(id -u)
export GID=$(id -g)
```

For Windows PowerShell:
```powershell
$env:UID=1000
```

3. **Create required directories:**
```bash
mkdir -p airflow/dags airflow/logs airflow/plugins
mkdir -p postgres_data minio_data
```

### Running with Docker

#### Option 1: Using Docker Compose

1. **Build and start all services:**
```bash
docker-compose up -d
```

2. **Check service status:**
```bash
docker-compose ps
```

3. **View logs:**
```bash
docker-compose logs -f
```

4. **Stop services:**
```bash
docker-compose down
```

#### Option 2: Using Makefile

```bash
# Start services
make up

# Stop services
make stop

# Restart services
make restart

# Remove all containers
make down
```

### Accessing Services

Once the containers are running, you can access:

- **Apache Airflow Web UI**: http://localhost:8080
  - Username: `admin`
  - Password: `admin`

- **MinIO Console**: http://localhost:9001
  - Username: `admin`
  - Password: `password123`

- **PostgreSQL Database**: `localhost:5432`
  - Database: `postgres`
  - Username: `postgres`
  - Password: `password123`

## 💻 Usage

### 1. Data Preprocessing

Navigate to the `Preprocessing_datasets/` directory to explore and run preprocessing notebooks:

```bash
cd Preprocessing_datasets

# For air pollution data
cd air_polution
python Pollution_Script.py

# For bus/metro data
cd ../bus_metro
python bus_metro_complete6.py
```

### 2. Running the Full Pipeline

The complete pipeline is in the `full_pipeline_prototype_2wheel/` directory:

#### Extract Data from API:
```bash
cd full_pipeline_prototype_2wheel/python_pipeline_tasks
python json_twowheel.py
```

This script:
- Fetches two-wheeled parking data from FIWARE API
- Stores raw JSON in MinIO bucket `raw/twowheel/`

#### Transform and Preprocess:
```bash
python Concatenate_preproc.py
```

This script:
- Reads JSON from MinIO
- Performs data cleaning and aggregation
- Enriches with geolocation data (Concelho, Freguesia)
- Saves preprocessed Parquet files to MinIO bucket `preprocessed/`

#### Load to Data Warehouse:
```bash
python load_populate_table.py
```

This script:
- Reads Parquet from MinIO
- Populates PostgreSQL star schema
- Updates fact and dimension tables

### 3. Set Up the Data Warehouse

Run the SQL scripts to create the star schema:

```bash
psql -h localhost -U postgres -d postgres -f full_pipeline_prototype_2wheel/SQL/final_dw_create_2.sql
```

### 4. Query the Data Warehouse

```bash
psql -h localhost -U postgres -d postgres -f full_pipeline_prototype_2wheel/SQL/join_all.sql
```

### 5. Orchestrate with Airflow

1. Access Airflow UI at http://localhost:8080
2. Enable your DAG in the Airflow interface
3. Trigger the DAG manually or wait for scheduled execution
4. Monitor task execution and logs

### Example: Querying the Data Warehouse

```sql
-- Get parking occupancy statistics by location
SELECT 
    dl.Concelho,
    dl.Freguesia,
    AVG(ftw.PercentOccupation) as avg_occupation,
    COUNT(*) as num_observations
FROM testschema1.FactTwoWheel ftw
JOIN testschema1.DimLocation dl ON ftw.LocationID = dl.LocationID
JOIN testschema1.DimDate d ON ftw.Date = d.Date
WHERE d.Year = 2024
GROUP BY dl.Concelho, dl.Freguesia
ORDER BY avg_occupation DESC;
```

## 🔄 Data Pipeline

### Pipeline Workflow

```
1. EXTRACT
   └─ API Call → JSON → MinIO (raw bucket)

2. TRANSFORM
   ├─ Read JSON from MinIO
   ├─ Data Cleaning (remove NaN, duplicates)
   ├─ Aggregation (hourly/daily means, min, max)
   ├─ Geolocation Enrichment (Concelho, Freguesia)
   └─ Save Parquet → MinIO (preprocessed bucket)

3. LOAD
   ├─ Read Parquet from MinIO
   ├─ Dimension Processing (DimLocation, DimDate)
   └─ Fact Table Population (FactTwoWheel)

4. ORCHESTRATION (Airflow)
   ├─ Schedule Tasks
   ├─ Monitor Execution
   ├─ Handle Errors
   └─ Send Alerts
```

### Data Transformations

1. **Time Aggregation**: Raw data aggregated to hourly and daily intervals
2. **Occupancy Metrics**: Calculate mean, min, max occupancy and percentages
3. **Geospatial Enrichment**: Add administrative boundaries (Concelho, Freguesia) using geopy
4. **Data Quality**: Remove duplicates, handle missing values, validate coordinates
5. **Format Conversion**: JSON → Parquet for efficient storage and querying

## 🏢 Data Warehouse Schema

### Star Schema Design

```sql
┌─────────────────────────────────────────────────────────┐
│                    FactTwoWheel                          │
├─────────────────────────────────────────────────────────┤
│ PK: ID                                                   │
│ FK: Date → DimDate                                       │
│ FK: LocationID → DimLocation                             │
│     Latitude, Longitude                                  │
│     MeanOccupation                                       │
│     PercentOccupation                                    │
│     MinOccupation                                        │
│     MaxOccupation                                        │
│     TotalSpotNumber                                      │
└────────────┬────────────────────────────┬───────────────┘
             │                            │
             ▼                            ▼
┌─────────────────────────┐  ┌─────────────────────────────┐
│       DimDate           │  │      DimLocation            │
├─────────────────────────┤  ├─────────────────────────────┤
│ PK: Date                │  │ PK: LocationID              │
│     Year                │  │     Latitude                │
│     Month               │  │     Longitude               │
│     Day                 │  │     Concelho                │
│     DayOfWeek           │  │     Freguesia               │
└─────────────────────────┘  └─────────────────────────────┘
```

### Table Descriptions

**FactTwoWheel** (Fact Table)
- Contains metrics about two-wheeled parking occupancy
- Granularity: One row per location per day
- Measures: Mean, min, max occupancy, total spots

**DimDate** (Dimension Table)
- Temporal dimension with date attributes
- Pre-populated for 2023-2024
- Supports time-based analysis

**DimLocation** (Dimension Table)
- Spatial dimension with geographic attributes
- Unique locations identified by coordinates
- Enriched with administrative boundaries

## 🤝 Contributing

Contributions are welcome! If you'd like to improve this project:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

For questions or feedback about this project, please contact any of the team members through GitHub:

- Daniel Osório: [@dosorio79](https://github.com/dosorio79)

**Project Link**: [https://github.com/dosorio79/proFinal_BDDM_ISEP](https://github.com/dosorio79/proFinal_BDDM_ISEP)

---

## 📚 Additional Resources

### Related Links

- [ISEP - Instituto Superior de Engenharia do Porto](https://www.isep.ipp.pt/)
- [Porto Urban Platform](https://urbanplatform.portodigital.pt/)
- [FIWARE Context Broker](https://fiware-orion.readthedocs.io/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [MinIO Documentation](https://min.io/docs/minio/linux/index.html)
- [GTFS Reference](https://gtfs.org/reference/static/)

### Data Sources Documentation

- [Porto Digital Urban Platform](https://urbanplatform.portodigital.pt/)
- [INE - Instituto Nacional de Estatística](https://www.ine.pt/)
- [STCP - Bus Transportation](https://www.stcp.pt/)
- [Metro do Porto](https://www.metrodoporto.pt/)

### Tools & Technologies

- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## 🙏 Acknowledgments

- **ISEP** - Instituto Superior de Engenharia do Porto for providing the academic framework
- **Course Instructors** - For guidance throughout the project development
- **Porto Digital** - For providing access to the Urban Platform and data APIs
- **Open Source Community** - For the excellent tools and libraries used in this project

## 📊 Project Statistics

- **Lines of Code**: ~1,500+
- **Data Sources**: 4 major sources
- **Docker Services**: 3 (PostgreSQL, MinIO, Airflow)
- **Development Period**: June 2024
- **Python Scripts**: 10+
- **SQL Scripts**: 2

---

## 🔧 Troubleshooting

### Common Issues

**Issue**: Airflow container fails to start
```bash
# Solution: Reset Airflow database
docker-compose down -v
docker-compose up -d
```

**Issue**: MinIO bucket not found
```bash
# Solution: Create buckets manually through MinIO console
# Access http://localhost:9001 and create 'raw' and 'preprocessed' buckets
```

**Issue**: PostgreSQL connection refused
```bash
# Solution: Check if PostgreSQL container is running
docker-compose ps postgres
docker-compose logs postgres
```

**Issue**: Permission denied errors on Linux
```bash
# Solution: Set correct ownership
sudo chown -R $UID:$GID airflow/ postgres_data/ minio_data/
```

---

**Note**: This project was developed as part of the academic curriculum at ISEP's Post-Graduation in Big Data Analytics and Decision Making. It demonstrates practical implementation of modern data engineering concepts including ETL pipelines, data lakes, data warehouses, and workflow orchestration.

**Last Updated**: June 2024
