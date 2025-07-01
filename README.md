# 💧 Qatar Water Station Capacity Analysis
This project analyzes water station capacity and operational efficiency in Qatar using **PostgreSQL** for data querying and **Power BI** for visualization.
---
## 📊 Dataset Overview
- Station names and water capacity (installed, operating, non-operating) in both **Million Imperial Gallons (MIG)** and **Cubic Meters (M³)**
- Remarks for stations (e.g., Mega RPS, newly commissioned)
- Null values cleaned (numeric nulls replaced with 0, empty remarks replaced with "No remarks")
---
## 🛠 Tools Used
- **PostgreSQL** — for storing and querying data  
- **pgAdmin / DBeaver** — database GUI tools  
- **Power BI Desktop** — dashboard visualization  
- **Git + GitHub** — version control and project hosting  
---
## 📈 Key SQL Insights
- National and station-wise utilization percentages  
- Identification of underutilized stations (<80%)  
- Stations with special remarks and recent commissioning  
- Top stations by operating capacity
---
## 🚀 How to Use
1. Create the database table by running `sql/create_table.sql`  
2. Import `data/water_stations_qatar_clean.csv` into the table  
3. Run queries in `sql/analysis_queries.sql` to explore insights  
4. Open `dashboards/water_station_dashboard.pbix` in Power BI to visualize data interactively
---
## 📌 Notes
- This is an educational project simulating real-world utility data analysis  
- Feel free to adapt the queries or dashboards for similar datasets
---
## 🙌 Acknowledgements
- [Qatar Open Data Portal](https://www.data.gov.qa/) - Data source
- KAHRAMAA (Qatar General Electricity & Water Corporation) -  Data provider
---
## 📄 License
This project is open-source under the [MIT License](LICENSE).
