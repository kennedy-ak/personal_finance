import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib
import sqlite3
import os

# Try to import plotly, with fallback
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Plotly not available. Charts will be disabled. Install with: pip install plotly")

# Set page configuration
st.set_page_config(page_title="Personal Expense Tracker", layout="wide")

# Database file path
DB_PATH = "expense_tracker.db"

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Database initialization functions
def initialize_database():
    """Create necessary database tables if they don't exist"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Create users table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
        """)
        
        # Create accounts table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            balance REAL DEFAULT 0
        )
        """)
        
        # Create transactions table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            account TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date DATE NOT NULL
        )
        """)
        
        # Check if default user exists, if not create it
        cur.execute("SELECT * FROM users WHERE username = ?", ("admin",))
        if cur.fetchone() is None:
            # Default credentials (username: admin, password: admin123)
            default_username = "admin"
            default_password = "admin123"
            
            # Hash the password for storage
            hashed_password = hashlib.sha256(default_password.encode()).hexdigest()
            
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                      (default_username, hashed_password))
        
        # Check if default accounts exist, if not create them
        cur.execute("SELECT COUNT(*) FROM accounts")
        if cur.fetchone()[0] == 0:
            default_accounts = [
                "Fidelity Account 1",
                "Access Account 2",
                "Mobile Money Account 3",
                "Cash"
            ]
            for account in default_accounts:
                cur.execute("INSERT INTO accounts (name, balance) VALUES (?, 0)", (account,))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database initialization error: {e}")
        return False

# Authentication function
def authenticate(username, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Hash the provided password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Check credentials against database
        cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                  (username, hashed_password))
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return result is not None
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return False

# Data functions
def get_accounts():
    """Get all accounts and their balances"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # This makes rows behave like dictionaries
        cur = conn.cursor()
        cur.execute("SELECT name, balance FROM accounts ORDER BY name")
        accounts = {row['name']: float(row['balance']) for row in cur.fetchall()}
        cur.close()
        conn.close()
        return accounts
    except Exception as e:
        st.error(f"Error loading accounts: {e}")
        return {}

def get_transactions():
    """Get all transactions"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
        SELECT type, amount, account, category, description, date
        FROM transactions
        ORDER BY date DESC, id DESC
        """)
        transactions = [dict(row) for row in cur.fetchall()]
        cur.close()
        conn.close()
        return transactions
    except Exception as e:
        st.error(f"Error loading transactions: {e}")
        return []

def add_transaction(transaction_type, amount, account, category, description, date):
    """Add a new transaction and update account balance"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Insert the transaction
        cur.execute("""
        INSERT INTO transactions (type, amount, account, category, description, date)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (transaction_type, amount, account, category, description, date))
        
        # Update account balance
        if transaction_type == "Expense":
            cur.execute("""
            UPDATE accounts SET balance = balance - ? WHERE name = ?
            """, (amount, account))
        else:  # Income
            cur.execute("""
            UPDATE accounts SET balance = balance + ? WHERE name = ?
            """, (amount, account))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error adding transaction: {e}")
        return False

def update_account_balance(account, new_balance):
    """Update an account's balance"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        cur.execute("""
        UPDATE accounts SET balance = ? WHERE name = ?
        """, (new_balance, account))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error updating account balance: {e}")
        return False

# Login Page
def login_page():
    st.title("Login to Personal Expense Tracker")
    
    # Display default credentials info
    st.info("💡 Default login credentials:\n- Username: admin\n- Password: admin123")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again.")

# Main application flow
# Initialize database on startup
db_status = initialize_database()

if not st.session_state.authenticated:
    login_page()
else:
    # Add logout button to sidebar
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
    
    # App title and description
    st.title("Personal Expense Tracker")
    st.markdown("Track your expenses, income, and account balances in one place")
    
    # Sidebar for navigation
    page = st.sidebar.radio("Navigation", ["Dashboard", "Add Transaction", "Transaction History", "Account Management"])
    
    # Dashboard page
    if page == "Dashboard":
        st.header("Financial Dashboard")
        
        # Get accounts and transactions
        accounts = get_accounts()
        transactions = get_transactions()
        
        # Display account balances
        st.subheader("Account Balances")
        account_df = pd.DataFrame({
            'Account': list(accounts.keys()),
            'Balance': list(accounts.values())
        })
        
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.dataframe(account_df, use_container_width=True)
        
        with col2:
            if sum(accounts.values()) > 0:
                if PLOTLY_AVAILABLE:
                    fig = px.pie(account_df, values='Balance', names='Account', title="Balance Distribution")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.bar_chart(account_df.set_index('Account')['Balance'])
        
        # Display recent transactions
        st.subheader("Recent Transactions")
        if transactions:
            recent_transactions = transactions[:5]  # Get the first 5 (since they're already ordered by DESC date)
            recent_df = pd.DataFrame(recent_transactions)
            st.dataframe(recent_df, use_container_width=True)
        else:
            st.info("No transactions recorded yet.")
        
        # Display expense summary by category if there are transactions
        if transactions:
            st.subheader("Expense Summary by Category")
            transactions_df = pd.DataFrame(transactions)
            
            # Filter for expenses only
            expenses_df = transactions_df[transactions_df['type'] == 'Expense']
            
            if not expenses_df.empty:
                category_summary = expenses_df.groupby('category')['amount'].sum().reset_index()
                if PLOTLY_AVAILABLE:
                    fig = px.bar(category_summary, x='category', y='amount', title="Expenses by Category")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.bar_chart(category_summary.set_index('category')['amount'])
            else:
                st.info("No expense transactions recorded yet.")
    
    # Add Transaction page
    elif page == "Add Transaction":
        st.header("Add New Transaction")
        
        # Get accounts
        accounts = get_accounts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Transaction Details")
            transaction_type = st.selectbox("Transaction Type", ["Expense", "Income"])
            amount = st.number_input("Amount", min_value=0.01, format="%.2f")
            account = st.selectbox("Account", list(accounts.keys()))
            category = st.selectbox("Category", 
                                  ["Food", "Transport", "Utilities", "Entertainment", 
                                    "Shopping", "Education", "Salary", "Gift", "Other"])
            description = st.text_area("Description", placeholder="Enter details about the transaction")
            date = st.date_input("Date", datetime.now())
            
            if st.button("Add Transaction"):
                if amount <= 0:
                    st.error("Amount must be greater than zero")
                elif transaction_type == "Expense" and amount > accounts[account]:
                    st.error(f"Insufficient funds in {account}")
                else:
                    if add_transaction(transaction_type, amount, account, category, description, date):
                        st.success(f"{transaction_type} of ${amount:.2f} added successfully!")
                        # Refresh accounts
                        accounts = get_accounts()
        
        with col2:
            st.subheader("Current Account Balances")
            for account, balance in accounts.items():
                st.metric(account, f"${balance:.2f}")
    
    # Transaction History page
    elif page == "Transaction History":
        st.header("Transaction History")
        
        # Get transactions
        transactions = get_transactions()
        transactions_df = pd.DataFrame(transactions) if transactions else pd.DataFrame()
        
        if not transactions_df.empty:
            # Filters
            st.subheader("Filters")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filter_type = st.multiselect("Transaction Type", 
                                          transactions_df['type'].unique().tolist(),
                                          default=transactions_df['type'].unique().tolist())
            
            with col2:
                filter_account = st.multiselect("Account", 
                                             transactions_df['account'].unique().tolist(),
                                             default=transactions_df['account'].unique().tolist())
            
            with col3:
                filter_category = st.multiselect("Category", 
                                              transactions_df['category'].unique().tolist(),
                                              default=transactions_df['category'].unique().tolist())
            
            # Apply filters
            filtered_df = transactions_df[
                (transactions_df['type'].isin(filter_type)) & 
                (transactions_df['account'].isin(filter_account)) & 
                (transactions_df['category'].isin(filter_category))
            ]
            
            if not filtered_df.empty:
                st.dataframe(filtered_df, use_container_width=True)
                
                # Download option
                csv = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download Transaction History",
                    csv,
                    "transaction_history.csv",
                    "text/csv",
                    key='download-csv'
                )
            else:
                st.info("No transactions match your filter criteria.")
        else:
            st.info("No transactions recorded yet.")
    
    # Account Management page
    elif page == "Account Management":
        st.header("Account Management")
        
        # Get accounts
        accounts = get_accounts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Update Account Balances")
            account_to_update = st.selectbox("Select Account", list(accounts.keys()))
            current_balance = accounts[account_to_update]
            st.info(f"Current Balance: ${current_balance:.2f}")
            new_balance = st.number_input("New Balance", min_value=0.0, value=float(current_balance), format="%.2f")
            
            if st.button("Update Balance"):
                if update_account_balance(account_to_update, new_balance):
                    st.success(f"{account_to_update} balance updated to ${new_balance:.2f}")
                    # Refresh accounts
                    accounts = get_accounts()
        
        with col2:
            st.subheader("Account Balances")
            account_data = pd.DataFrame({
                'Account': list(accounts.keys()),
                'Balance': list(accounts.values())
            })
            st.dataframe(account_data, use_container_width=True)
            
            total_balance = sum(accounts.values())
            st.metric("Total Balance", f"${total_balance:.2f}")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info("Personal Expense Tracker - v1.0 (SQLite)")