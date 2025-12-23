# 🌱 UP Secondary Schools Eco Club Monitoring Dashboard

A professional Streamlit-based monitoring dashboard for tracking Eco Club activities across Uttar Pradesh secondary schools.

## 📊 Features

- **Dual Report System**
  - 📋 Notification Upload Status Report
  - 🌳 Tree Plantation Report

- **Advanced Filtering**
  - District-wise filtering
  - School Type filtering (Private/Government)
  - Status-based filtering (Uploaded/Not Uploaded)

- **Real-time Metrics**
  - Total schools count
  - Upload status tracking
  - Tree plantation statistics
  - Auto-updating summaries

- **User-Friendly Interface**
  - Mobile responsive design
  - Tabbed navigation
  - Downloadable CSV reports
  - Loading indicators

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/alokkmohan/ECO-Club.git
cd ECO-Club
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Prepare data files**

Place the following Excel files in the project root:
- `School Master.xlsx`
- `All_Schools_with_Notifications_UTTAR PRADESH.xlsx`
- `UTTAR PRADESH.xlsx`

5. **(Optional) Convert to CSV for faster loading**
```bash
python convert_to_csv.py
```

6. **Run the dashboard**
```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

## 📁 Project Structure

```
eco-club-dashboard/
├── app.py                      # Main Streamlit application
├── data_service.py             # Data processing logic
├── convert_to_csv.py           # Excel to CSV converter
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── .gitignore                  # Git ignore rules
```

## 📋 Data Files Required

### School Master.xlsx
Contains all secondary schools with columns:
- District Name
- School Name
- UDISE Code
- School Management
- School Category

### All_Schools_with_Notifications_UTTAR PRADESH.xlsx
Contains UDISE codes of schools that uploaded notifications

### UTTAR PRADESH.xlsx
Contains tree plantation data with columns:
- UDISE ID
- Saplings (tree count)

## 🎨 Dashboard Sections

### Notification Report Tab
- Filter by district and school type
- View upload status
- Download filtered reports
- Track notification compliance

### Tree Planted Report Tab
- Filter by district and school type
- View plantation statistics
- Download tree reports
- Monitor tree count across schools

## 🔧 Configuration

The dashboard uses:
- **Caching**: 10-minute cache for faster performance
- **Auto-reload**: Updates when data files change
- **CSV Support**: Automatically uses CSV if available (10-20x faster than Excel)

## 📱 Mobile Support

Fully responsive design that works on:
- Desktop computers
- Tablets
- Mobile phones

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 👨‍💻 Developer

**Alok Mohan**  
📧 alokmohann@gmail.com  
🔗 [GitHub](https://github.com/alokkmohan)

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built for Eco Club monitoring in Uttar Pradesh
- Designed for DIOS, DC, and School Principals
- Streamlit framework for rapid dashboard development
