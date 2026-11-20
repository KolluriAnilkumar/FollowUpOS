# FollowUpOS – Invoice Data Processing & Follow-up Priority Dashboard

FollowUpOS is a Python-based invoice data processing and follow-up priority dashboard developed for a wholesale business case study, **Deccan Wholesale Mart, Hyderabad**.

The application helps organize invoice records, identify outstanding payments, prioritize customer follow-ups, and generate useful business reports through an interactive Streamlit dashboard.

## Project Objectives

- Process and clean invoice data.
- Identify missing, duplicate, and invalid records.
- Calculate outstanding amounts.
- Categorize invoices based on follow-up priority.
- Display useful business insights.
- Generate downloadable reports.

## Key Features

- **Invoice Upload:** Upload invoice data for processing.
- **Data Cleaning:** Handle missing values, duplicates, and data inconsistencies.
- **Data Validation:** Identify invalid and exceptional records.
- **Outstanding Amount Calculation:** Calculate pending payment amounts.
- **Follow-up Priority:** Categorize invoices using rule-based conditions.
- **Interactive Dashboard:** View invoice summaries, filters, and business insights.
- **Report Generation:** Download processed data and business reports in Excel format.
- **Owner Login:** Restrict dashboard access through a configurable owner password.
- **Activity Logging:** Use SQLite for local activity and outcome logging.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application development |
| Pandas | Data processing and analysis |
| Streamlit | Interactive dashboard |
| SQLite | Local database and activity logging |
| Excel / CSV | Data input and report output |

## Project Workflow

1. Upload invoice dataset.
2. Read and inspect the invoice records.
3. Clean and preprocess the data.
4. Validate records and identify exceptions.
5. Calculate outstanding amounts.
6. Assign follow-up priorities using business rules.
7. Display results through the dashboard.
8. Generate and download reports.

## Repository Contents

- `app.py` – Main Streamlit application.
- `FollowUpOS_Hyderabad_Synthetic_Dataset.xlsx` – Sample synthetic invoice dataset.
- `FollowUpOS_Cleaned_Dataset.xlsx` – Cleaned invoice data.
- `FollowUpOS_Followup_Queue.xlsx` – Follow-up priority report.
- `FollowUpOS_Business_KPI_Summary.xlsx` – Business KPI summary.
- Other Excel files – Supporting financial, exception, data-quality, reminder, and consolidated reports.

## Sample Dataset

This project uses a synthetic dataset created for demonstration and learning purposes. It represents a wholesale business scenario and does not contain actual customer or business transaction records.

## How to Run the Application

### 1. Clone the repository

```bash
git clone https://github.com/KolluriAnilkumar/FollowUpOS.git
cd FollowUpOS
```

### 2. Install dependencies

```bash
pip install streamlit pandas openpyxl
```

### 3. Configure the owner password

Create a folder named `.streamlit` in the project directory.

Inside it, create a file named `secrets.toml`:

```toml
OWNER_PASSWORD = "your-own-password"
```

Replace the example with your own password. Keep this file private and never upload it to GitHub.

### 4. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## Project Limitations

- This is a demonstration project and not a production-ready financial system.
- Follow-up priority is assigned using predefined business rules, not a trained AI/ML model.
- The sample dataset is synthetic.
- The owner login is a basic demonstration authentication mechanism and should be strengthened before production use.

## Future Improvements

- Integrate a production-grade authentication system.
- Connect to a centralized database.
- Add automated customer reminder notifications.
- Improve analytics and reporting capabilities.
- Deploy the application to a cloud hosting platform.

## Author

**Anil Kumar Kolluri**

GitHub: [KolluriAnilkumar](https://github.com/KolluriAnilkumar)

---

*FollowUpOS – Making invoice processing and customer follow-ups more organized and efficient.*
