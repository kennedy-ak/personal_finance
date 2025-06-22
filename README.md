# Personal Expense Tracker

This is a personal project to track my spending.

A simple web-based personal finance and expense tracking application built with Streamlit and SQLite.

## Features

- **User Authentication**: Secure login with hashed passwords .
- **Dashboard**: Visualize account balances and recent transactions with charts (Plotly or Streamlit).
- **Add Transactions**: Record expenses and income, categorized by type, account, and category.
- **Transaction History**: Filter, view, and download your transaction history as CSV.
- **Account Management**: View and update balances for multiple accounts (e.g., bank, cash, mobile money).
- **Expense Summary**: Visual breakdown of expenses by category.

## Technologies Used

- [Streamlit](https://streamlit.io/) for the web interface
- [SQLite](https://www.sqlite.org/) for data storage
- [Pandas](https://pandas.pydata.org/) for data manipulation
- [Plotly](https://plotly.com/python/) for interactive charts (optional)

## Getting Started

### Prerequisites
- Python 3.8+
- Recommended: Create and activate a virtual environment

### Installation
1. Clone this repository or download the source code.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the App
```bash
streamlit run main.py
```

The app will open in your browser. Log in with the default credentials:
- **Username**: ``
- **Password**: ``

> **Note:** You can change or add users by editing the SQLite database directly.

### Optional: Enable Plotly Charts
To enable interactive charts, ensure Plotly is installed:
```bash
pip install plotly
```

## File Structure
- `main.py` - Main Streamlit application
- `expense_tracker.db` - SQLite database (auto-created)
- `requirements.txt` - Python dependencies

## Security
- Passwords are stored as SHA-256 hashes.
- For production, use stronger authentication and secure database management.

## License
This project is for personal use and educational purposes.

---
**Personal Expense Tracker - v1.0 (SQLite)**
