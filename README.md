# 🍴 Restaurant Billing System

A Python-based **Restaurant Billing Software** with **Streamlit UI** and **SQLite database**.  
This system handles order entry, bill generation (with GST & discounts), dine-in/takeaway modes, payment tracking, and reporting.

---

## 📂 Project Structure

restaurant_billing/ #folder name
│
├── app.py # Main Streamlit app entry point
├── menu.csv # Menu file (editable or uploadable in the app)
│
├── db/
│ └── restaurant.db # Auto-created SQLite database on first run
│
├── utils/
│ ├── calculator.py # Billing, GST, and discount calculation utilities
│ └── db_utils.py # Database helper functions (menu, orders, reports)
│
├── ui/
│ └── main_ui.py # Streamlit UI components
│
├── reports/
│ └── sales_report.csv # Exported reports will be saved here
│
└── README.md # Project documentation

## ⚙️ Features

- ✅ **Menu Management** – Add, update, and fetch menu items  
- ✅ **Order Management** – Dine-in / Takeaway, multiple items, payment modes  
- ✅ **Billing** – Auto-calculate total, GST, discount, and grand total  
- ✅ **Reports Module** – Sales reports exportable to CSV  
- ✅ **Error Handling** – Handles empty orders, invalid entries, missing files

## 🚀 Setup & Installation

# Web App Framework
streamlit==1.37.0

# Data Handling
pandas==2.2.2

# Database (SQLite is built-in, but SQLAlchemy can be used for easier handling)
sqlalchemy==2.0.32

###  Run the Application

streamlit run app.py

## 📝 Usage Guide 

1. **Menu Setup**  
   - Upload or edit `menu.csv` to update restaurant items  

2. **Place Orders**  
   - Choose **Dine-in** or **Takeaway**  
   - Add items, set quantity, select payment mode (Cash/UPI/Card)  

3. **Bill Generation**  
   - Auto-calculated bill with GST & discount  
   - Option to download invoice  

4. **Reports**  
   - Generate daily/weekly/monthly sales reports  
   - Export reports to CSV

## 🔮 Future Enhancements

- 🔑 User login system  
- 🖨 Auto-print bill support  
- ⏰ Table management for dine-in  
