# # import streamlit as st
# # import pandas as pd
# # from datetime import datetime
# # import hashlib
# # import psycopg2
# # from psycopg2.extras import RealDictCursor
# # import os
# # from urllib.parse import urlparse

# # from dotenv import load_dotenv
# # load_dotenv()

# # # Try to import plotly, with fallback
# # try:
# #     import plotly.express as px
# #     PLOTLY_AVAILABLE = True
# # except ImportError:
# #     PLOTLY_AVAILABLE = False
# #     st.warning("Plotly not available. Charts will be disabled. Install with: pip install plotly")

# # # Set page configuration
# # st.set_page_config(page_title="Personal Expense Tracker", layout="wide")

# # # Database connection parameters - Updated for Neon
# # DATABASE_URL = os.getenv("DATABASE_URL")

# # # Parse the database URL
# # url = urlparse(DATABASE_URL)
# # DB_CONFIG = {
# #     'host': url.hostname,
# #     'port': url.port,
# #     'database': url.path[1:],  # Remove leading slash
# #     'user': url.username,
# #     'password': url.password,
# #     'sslmode': 'require'
# # }

# # # Initialize session state for authentication
# # if 'authenticated' not in st.session_state:
# #     st.session_state.authenticated = False

# # # Database connection function
# # def get_db_connection():
# #     """Get database connection with error handling"""
# #     try:
# #         conn = psycopg2.connect(**DB_CONFIG)
# #         return conn
# #     except psycopg2.Error as e:
# #         st.error(f"Database connection error: {e}")
# #         return None

# # # Database initialization functions
# # def initialize_database():
# #     """Create necessary database tables if they don't exist"""
# #     try:
# #         conn = get_db_connection()
# #         if not conn:
# #             return False
            
# #         cur = conn.cursor()
        
# #         # Create users table
# #         cur.execute("""
# #         CREATE TABLE IF NOT EXISTS users (
# #             username VARCHAR(50) PRIMARY KEY,
# #             password VARCHAR(64) NOT NULL
# #         )
# #         """)
        
# #         # Create accounts table
# #         cur.execute("""
# #         CREATE TABLE IF NOT EXISTS accounts (
# #             id SERIAL PRIMARY KEY,
# #             name VARCHAR(100) NOT NULL UNIQUE,
# #             balance DECIMAL(10,2) DEFAULT 0
# #         )
# #         """)
        
# #         # Create transactions table
# #         cur.execute("""
# #         CREATE TABLE IF NOT EXISTS transactions (
# #             id SERIAL PRIMARY KEY,
# #             type VARCHAR(10) NOT NULL CHECK (type IN ('Income', 'Expense')),
# #             amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
# #             account VARCHAR(100) NOT NULL,
# #             category VARCHAR(50) NOT NULL,
# #             description TEXT,
# #             date DATE NOT NULL,
# #             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# #         )
# #         """)
        
# #         # Check if default user exists, if not create it
# #         cur.execute("SELECT * FROM users WHERE username = %s", ("admin",))
# #         if cur.fetchone() is None:
# #             # Default credentials (username: admin, password: admin123)
# #             default_username = "admin"
# #             default_password = "admin123"
            
# #             # Hash the password for storage
# #             hashed_password = hashlib.sha256(default_password.encode()).hexdigest()
            
# #             cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
# #                       (default_username, hashed_password))
        
# #         # Check if default accounts exist, if not create them
# #         cur.execute("SELECT COUNT(*) FROM accounts")
# #         if cur.fetchone()[0] == 0:
# #             default_accounts = [
# #                 "Fidelity Account 1",
# #                 "Access Account 2",
# #                 "Mobile Money Account 3",
# #                 "Cash"
# #             ]
# #             for account in default_accounts:
# #                 cur.execute("INSERT INTO accounts (name, balance) VALUES (%s, %s)", (account, 0))
        
# #         conn.commit()
# #         cur.close()
# #         conn.close()
# #         return True
# #     except psycopg2.Error as e:
# #         st.error(f"Database initialization error: {e}")
# #         return False

# # # Authentication function
# # def authenticate(username, password):
# #     try:
# #         conn = get_db_connection()
# #         if not conn:
# #             return False
            
# #         cur = conn.cursor()
        
# #         # Hash the provided password
# #         hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
# #         # Check credentials against database
# #         cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", 
# #                   (username, hashed_password))
# #         result = cur.fetchone()
        
# #         cur.close()
# #         conn.close()
        
# #         return result is not None
# #     except psycopg2.Error as e:
# #         st.error(f"Authentication error: {e}")
# #         return False

# # # Data functions
# # def get_accounts():
# #     """Get all accounts and their balances"""
# #     try:
# #         conn = get_db_connection()
# #         if not conn:
# #             return {}
            
# #         cur = conn.cursor(cursor_factory=RealDictCursor)
# #         cur.execute("SELECT name, balance FROM accounts ORDER BY name")
# #         accounts = {row['name']: float(row['balance']) for row in cur.fetchall()}
# #         cur.close()
# #         conn.close()
# #         return accounts
# #     except psycopg2.Error as e:
# #         st.error(f"Error loading accounts: {e}")
# #         return {}

# # def get_transactions():
# #     """Get all transactions"""
# #     try:
# #         conn = get_db_connection()
# #         if not conn:
# #             return []
            
# #         cur = conn.cursor(cursor_factory=RealDictCursor)
# #         cur.execute("""
# #         SELECT type, amount, account, category, description, date
# #         FROM transactions
# #         ORDER BY date DESC, id DESC
# #         """)
# #         transactions = [dict(row) for row in cur.fetchall()]
# #         # Convert Decimal to float for better compatibility
# #         for transaction in transactions:
# #             transaction['amount'] = float(transaction['amount'])
# #         cur.close()
# #         conn.close()
# #         return transactions
# #     except psycopg2.Error as e:
# #         st.error(f"Error loading transactions: {e}")
# #         return []

# # def add_transaction(transaction_type, amount, account, category, description, date):
# #     """Add a new transaction and update account balance"""
# #     try:
# #         conn = get_db_connection()
# #         if not conn:
# #             return False
            
# #         cur = conn.cursor()
        
# #         # Start transaction
# #         conn.autocommit = False
        
# #         # Insert the transaction
# #         cur.execute("""
# #         INSERT INTO transactions (type, amount, account, category, description, date)
# #         VALUES (%s, %s, %s, %s, %s, %s)
# #         """, (transaction_type, amount, account, category, description, date))
        
# #         # Update account balance
# #         if transaction_type == "Expense":
# #             cur.execute("""
# #             UPDATE accounts SET balance = balance - %s WHERE name = %s
# #             """, (amount, account))
# #         else:  # Income
# #             cur.execute("""
# #             UPDATE accounts SET balance = balance + %s WHERE name = %s
# #             """, (amount, account))
        
# #         conn.commit()
# #         cur.close()
# #         conn.close()
# #         return True
# #     except psycopg2.Error as e:
# #         if conn:
# #             conn.rollback()
# #             conn.close()
# #         st.error(f"Error adding transaction: {e}")
# #         return False

# # def update_account_balance(account, new_balance):
# #     """Update an account's balance"""
# #     try:
# #         conn = get_db_connection()
# #         if not conn:
# #             return False
            
# #         cur = conn.cursor()
        
# #         cur.execute("""
# #         UPDATE accounts SET balance = %s WHERE name = %s
# #         """, (new_balance, account))
        
# #         conn.commit()
# #         cur.close()
# #         conn.close()
# #         return True
# #     except psycopg2.Error as e:
# #         st.error(f"Error updating account balance: {e}")
# #         return False

# # # Login Page
# # def login_page():
# #     st.title("Login to Personal Expense Tracker")
    
# #     # Display default credentials info
# #     st.info("💡 Default login credentials:\n- Username: admin\n- Password: admin123")
    
# #     with st.form("login_form"):
# #         username = st.text_input("Username")
# #         password = st.text_input("Password", type="password")
# #         submit_button = st.form_submit_button("Login")
        
# #         if submit_button:
# #             if authenticate(username, password):
# #                 st.session_state.authenticated = True
# #                 st.success("Login successful!")
# #                 st.rerun()
# #             else:
# #                 st.error("Invalid username or password. Please try again.")

# # # Main application flow
# # # Initialize database on startup
# # db_status = initialize_database()

# # if not st.session_state.authenticated:
# #     login_page()
# # else:
# #     # Add logout button to sidebar
# #     if st.sidebar.button("Logout"):
# #         st.session_state.authenticated = False
# #         st.rerun()
    
# #     # App title and description
# #     st.title("Personal Expense Tracker")
# #     st.markdown("Track your expenses, income, and account balances in one place")
    
# #     # Sidebar for navigation
# #     page = st.sidebar.radio("Navigation", ["Dashboard", "Add Transaction", "Transaction History", "Account Management"])
    
# #     # Dashboard page
# #     if page == "Dashboard":
# #         st.header("Financial Dashboard")
        
# #         # Get accounts and transactions
# #         accounts = get_accounts()
# #         transactions = get_transactions()
        
# #         # Display account balances
# #         st.subheader("Account Balances")
# #         account_df = pd.DataFrame({
# #             'Account': list(accounts.keys()),
# #             'Balance': list(accounts.values())
# #         })
        
# #         col1, col2 = st.columns([2, 3])
        
# #         with col1:
# #             st.dataframe(account_df, use_container_width=True)
        
# #         with col2:
# #             if sum(accounts.values()) > 0:
# #                 if PLOTLY_AVAILABLE:
# #                     fig = px.pie(account_df, values='Balance', names='Account', title="Balance Distribution")
# #                     st.plotly_chart(fig, use_container_width=True)
# #                 else:
# #                     st.bar_chart(account_df.set_index('Account')['Balance'])
        
# #         # Display recent transactions
# #         st.subheader("Recent Transactions")
# #         if transactions:
# #             recent_transactions = transactions[:5]  # Get the first 5 (since they're already ordered by DESC date)
# #             recent_df = pd.DataFrame(recent_transactions)
# #             st.dataframe(recent_df, use_container_width=True)
# #         else:
# #             st.info("No transactions recorded yet.")
        
# #         # Display expense summary by category if there are transactions
# #         if transactions:
# #             st.subheader("Expense Summary by Category")
# #             transactions_df = pd.DataFrame(transactions)
            
# #             # Filter for expenses only
# #             expenses_df = transactions_df[transactions_df['type'] == 'Expense']
            
# #             if not expenses_df.empty:
# #                 category_summary = expenses_df.groupby('category')['amount'].sum().reset_index()
# #                 if PLOTLY_AVAILABLE:
# #                     fig = px.bar(category_summary, x='category', y='amount', title="Expenses by Category")
# #                     st.plotly_chart(fig, use_container_width=True)
# #                 else:
# #                     st.bar_chart(category_summary.set_index('category')['amount'])
# #             else:
# #                 st.info("No expense transactions recorded yet.")
    
# #     # Add Transaction page
# #     elif page == "Add Transaction":
# #         st.header("Add New Transaction")
        
# #         # Get accounts
# #         accounts = get_accounts()
        
# #         col1, col2 = st.columns(2)
        
# #         with col1:
# #             st.subheader("Transaction Details")
# #             transaction_type = st.selectbox("Transaction Type", ["Expense", "Income"])
# #             amount = st.number_input("Amount", min_value=0.01, format="%.2f")
# #             account = st.selectbox("Account", list(accounts.keys()))
# #             category = st.selectbox("Category", 
# #                                   ["Food", "Transport", "Utilities", "Entertainment", 
# #                                     "Shopping", "Education", "Salary", "Gift", "Other"])
# #             description = st.text_area("Description", placeholder="Enter details about the transaction")
# #             date = st.date_input("Date", datetime.now())
            
# #             if st.button("Add Transaction"):
# #                 if amount <= 0:
# #                     st.error("Amount must be greater than zero")
# #                 elif transaction_type == "Expense" and amount > accounts[account]:
# #                     st.error(f"Insufficient funds in {account}")
# #                 else:
# #                     if add_transaction(transaction_type, amount, account, category, description, date):
# #                         st.success(f"{transaction_type} of ${amount:.2f} added successfully!")
# #                         # Refresh accounts
# #                         accounts = get_accounts()
        
# #         with col2:
# #             st.subheader("Current Account Balances")
# #             for account, balance in accounts.items():
# #                 st.metric(account, f"${balance:.2f}")
    
# #     # Transaction History page
# #     elif page == "Transaction History":
# #         st.header("Transaction History")
        
# #         # Get transactions
# #         transactions = get_transactions()
# #         transactions_df = pd.DataFrame(transactions) if transactions else pd.DataFrame()
        
# #         if not transactions_df.empty:
# #             # Filters
# #             st.subheader("Filters")
# #             col1, col2, col3 = st.columns(3)
            
# #             with col1:
# #                 filter_type = st.multiselect("Transaction Type", 
# #                                           transactions_df['type'].unique().tolist(),
# #                                           default=transactions_df['type'].unique().tolist())
            
# #             with col2:
# #                 filter_account = st.multiselect("Account", 
# #                                              transactions_df['account'].unique().tolist(),
# #                                              default=transactions_df['account'].unique().tolist())
            
# #             with col3:
# #                 filter_category = st.multiselect("Category", 
# #                                               transactions_df['category'].unique().tolist(),
# #                                               default=transactions_df['category'].unique().tolist())
            
# #             # Apply filters
# #             filtered_df = transactions_df[
# #                 (transactions_df['type'].isin(filter_type)) & 
# #                 (transactions_df['account'].isin(filter_account)) & 
# #                 (transactions_df['category'].isin(filter_category))
# #             ]
            
# #             if not filtered_df.empty:
# #                 st.dataframe(filtered_df, use_container_width=True)
                
# #                 # Download option
# #                 csv = filtered_df.to_csv(index=False).encode('utf-8')
# #                 st.download_button(
# #                     "Download Transaction History",
# #                     csv,
# #                     "transaction_history.csv",
# #                     "text/csv",
# #                     key='download-csv'
# #                 )
# #             else:
# #                 st.info("No transactions match your filter criteria.")
# #         else:
# #             st.info("No transactions recorded yet.")
    
# #     # Account Management page
# #     elif page == "Account Management":
# #         st.header("Account Management")
        
# #         # Get accounts
# #         accounts = get_accounts()
        
# #         col1, col2 = st.columns(2)
        
# #         with col1:
# #             st.subheader("Update Account Balances")
# #             account_to_update = st.selectbox("Select Account", list(accounts.keys()))
# #             current_balance = accounts[account_to_update]
# #             st.info(f"Current Balance: ${current_balance:.2f}")
# #             new_balance = st.number_input("New Balance", min_value=0.0, value=float(current_balance), format="%.2f")
            
# #             if st.button("Update Balance"):
# #                 if update_account_balance(account_to_update, new_balance):
# #                     st.success(f"{account_to_update} balance updated to ${new_balance:.2f}")
# #                     # Refresh accounts
# #                     accounts = get_accounts()
        
# #         with col2:
# #             st.subheader("Account Balances")
# #             account_data = pd.DataFrame({
# #                 'Account': list(accounts.keys()),
# #                 'Balance': list(accounts.values())
# #             })
# #             st.dataframe(account_data, use_container_width=True)
            
# #             total_balance = sum(accounts.values())
# #             st.metric("Total Balance", f"${total_balance:.2f}")
    
# #     # Footer
# #     st.sidebar.markdown("---")
# #     st.sidebar.info("Personal Expense Tracker - v1.0 (Neon PostgreSQL)")


# import streamlit as st
# import pandas as pd
# from datetime import datetime, timedelta
# import hashlib
# import psycopg2
# from psycopg2.extras import RealDictCursor
# import os
# from urllib.parse import urlparse

# from dotenv import load_dotenv
# load_dotenv()

# # Try to import plotly, with fallback
# try:
#     import plotly.express as px
#     import plotly.graph_objects as go
#     from plotly.subplots import make_subplots
#     PLOTLY_AVAILABLE = True
# except ImportError:
#     PLOTLY_AVAILABLE = False
#     st.warning("Plotly not available. Charts will be disabled. Install with: pip install plotly")

# # Set page configuration
# st.set_page_config(page_title="Personal Expense Tracker", layout="wide")

# # Database connection parameters - Updated for Neon
# DATABASE_URL = os.getenv("DATABASE_URL")

# # Parse the database URL
# url = urlparse(DATABASE_URL)
# DB_CONFIG = {
#     'host': url.hostname,
#     'port': url.port,
#     'database': url.path[1:],  # Remove leading slash
#     'user': url.username,
#     'password': url.password,
#     'sslmode': 'require'
# }

# # Initialize session state for authentication
# if 'authenticated' not in st.session_state:
#     st.session_state.authenticated = False

# # Database connection function
# def get_db_connection():
#     """Get database connection with error handling"""
#     try:
#         conn = psycopg2.connect(**DB_CONFIG)
#         return conn
#     except psycopg2.Error as e:
#         st.error(f"Database connection error: {e}")
#         return None

# # Database initialization functions
# def initialize_database():
#     """Create necessary database tables if they don't exist"""
#     try:
#         conn = get_db_connection()
#         if not conn:
#             return False
            
#         cur = conn.cursor()
        
#         # Create users table
#         cur.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             username VARCHAR(50) PRIMARY KEY,
#             password VARCHAR(64) NOT NULL
#         )
#         """)
        
#         # Create accounts table
#         cur.execute("""
#         CREATE TABLE IF NOT EXISTS accounts (
#             id SERIAL PRIMARY KEY,
#             name VARCHAR(100) NOT NULL UNIQUE,
#             balance DECIMAL(10,2) DEFAULT 0
#         )
#         """)
        
#         # Create transactions table
#         cur.execute("""
#         CREATE TABLE IF NOT EXISTS transactions (
#             id SERIAL PRIMARY KEY,
#             type VARCHAR(10) NOT NULL CHECK (type IN ('Income', 'Expense')),
#             amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
#             account VARCHAR(100) NOT NULL,
#             category VARCHAR(50) NOT NULL,
#             description TEXT,
#             date DATE NOT NULL,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#         """)
        
#         # Check if default user exists, if not create it
#         cur.execute("SELECT * FROM users WHERE username = %s", ("admin",))
#         if cur.fetchone() is None:
#             # Default credentials (username: admin, password: admin123)
#             default_username = "admin"
#             default_password = "admin123"
            
#             # Hash the password for storage
#             hashed_password = hashlib.sha256(default_password.encode()).hexdigest()
            
#             cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
#                       (default_username, hashed_password))
        
#         # Check if default accounts exist, if not create them
#         cur.execute("SELECT COUNT(*) FROM accounts")
#         if cur.fetchone()[0] == 0:
#             default_accounts = [
#                 "Fidelity Account 1",
#                 "Access Account 2",
#                 "Mobile Money Account 3",
#                 "Cash"
#             ]
#             for account in default_accounts:
#                 cur.execute("INSERT INTO accounts (name, balance) VALUES (%s, %s)", (account, 0))
        
#         conn.commit()
#         cur.close()
#         conn.close()
#         return True
#     except psycopg2.Error as e:
#         st.error(f"Database initialization error: {e}")
#         return False

# # Authentication function
# def authenticate(username, password):
#     try:
#         conn = get_db_connection()
#         if not conn:
#             return False
            
#         cur = conn.cursor()
        
#         # Hash the provided password
#         hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
#         # Check credentials against database
#         cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", 
#                   (username, hashed_password))
#         result = cur.fetchone()
        
#         cur.close()
#         conn.close()
        
#         return result is not None
#     except psycopg2.Error as e:
#         st.error(f"Authentication error: {e}")
#         return False

# # Data functions
# def get_accounts():
#     """Get all accounts and their balances"""
#     try:
#         conn = get_db_connection()
#         if not conn:
#             return {}
            
#         cur = conn.cursor(cursor_factory=RealDictCursor)
#         cur.execute("SELECT name, balance FROM accounts ORDER BY name")
#         accounts = {row['name']: float(row['balance']) for row in cur.fetchall()}
#         cur.close()
#         conn.close()
#         return accounts
#     except psycopg2.Error as e:
#         st.error(f"Error loading accounts: {e}")
#         return {}

# def get_transactions():
#     """Get all transactions"""
#     try:
#         conn = get_db_connection()
#         if not conn:
#             return []
            
#         cur = conn.cursor(cursor_factory=RealDictCursor)
#         cur.execute("""
#         SELECT type, amount, account, category, description, date
#         FROM transactions
#         ORDER BY date DESC, id DESC
#         """)
#         transactions = [dict(row) for row in cur.fetchall()]
#         # Convert Decimal to float for better compatibility
#         for transaction in transactions:
#             transaction['amount'] = float(transaction['amount'])
#         cur.close()
#         conn.close()
#         return transactions
#     except psycopg2.Error as e:
#         st.error(f"Error loading transactions: {e}")
#         return []

# def get_weekly_transactions(start_date, end_date):
#     """Get transactions for a specific week"""
#     try:
#         conn = get_db_connection()
#         if not conn:
#             return []
            
#         cur = conn.cursor(cursor_factory=RealDictCursor)
#         cur.execute("""
#         SELECT type, amount, account, category, description, date
#         FROM transactions
#         WHERE date BETWEEN %s AND %s
#         ORDER BY date DESC, id DESC
#         """, (start_date, end_date))
#         transactions = [dict(row) for row in cur.fetchall()]
#         # Convert Decimal to float for better compatibility
#         for transaction in transactions:
#             transaction['amount'] = float(transaction['amount'])
#         cur.close()
#         conn.close()
#         return transactions
#     except psycopg2.Error as e:
#         st.error(f"Error loading weekly transactions: {e}")
#         return []

# def get_weekly_summary_data():
#     """Get weekly summary data for the last 12 weeks"""
#     try:
#         conn = get_db_connection()
#         if not conn:
#             return []
            
#         cur = conn.cursor(cursor_factory=RealDictCursor)
#         cur.execute("""
#         SELECT 
#             DATE_TRUNC('week', date) as week_start,
#             DATE_TRUNC('week', date) + INTERVAL '6 days' as week_end,
#             SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END) as total_expenses,
#             SUM(CASE WHEN type = 'Income' THEN amount ELSE 0 END) as total_income,
#             COUNT(*) as transaction_count
#         FROM transactions
#         WHERE date >= CURRENT_DATE - INTERVAL '12 weeks'
#         GROUP BY DATE_TRUNC('week', date)
#         ORDER BY week_start DESC
#         """)
        
#         weekly_data = []
#         for row in cur.fetchall():
#             weekly_data.append({
#                 'week_start': row['week_start'].date(),
#                 'week_end': row['week_end'].date(),
#                 'total_expenses': float(row['total_expenses']),
#                 'total_income': float(row['total_income']),
#                 'transaction_count': row['transaction_count'],
#                 'net_amount': float(row['total_income']) - float(row['total_expenses'])
#             })
        
#         cur.close()
#         conn.close()
#         return weekly_data
#     except psycopg2.Error as e:
#         st.error(f"Error loading weekly summary: {e}")
#         return []

# def add_transaction(transaction_type, amount, account, category, description, date):
#     """Add a new transaction and update account balance"""
#     try:
#         conn = get_db_connection()
#         if not conn:
#             return False
            
#         cur = conn.cursor()
        
#         # Start transaction
#         conn.autocommit = False
        
#         # Insert the transaction
#         cur.execute("""
#         INSERT INTO transactions (type, amount, account, category, description, date)
#         VALUES (%s, %s, %s, %s, %s, %s)
#         """, (transaction_type, amount, account, category, description, date))
        
#         # Update account balance
#         if transaction_type == "Expense":
#             cur.execute("""
#             UPDATE accounts SET balance = balance - %s WHERE name = %s
#             """, (amount, account))
#         else:  # Income
#             cur.execute("""
#             UPDATE accounts SET balance = balance + %s WHERE name = %s
#             """, (amount, account))
        
#         conn.commit()
#         cur.close()
#         conn.close()
#         return True
#     except psycopg2.Error as e:
#         if conn:
#             conn.rollback()
#             conn.close()
#         st.error(f"Error adding transaction: {e}")
#         return False

# def update_account_balance(account, new_balance):
#     """Update an account's balance"""
#     try:
#         conn = get_db_connection()
#         if not conn:
#             return False
            
#         cur = conn.cursor()
        
#         cur.execute("""
#         UPDATE accounts SET balance = %s WHERE name = %s
#         """, (new_balance, account))
        
#         conn.commit()
#         cur.close()
#         conn.close()
#         return True
#     except psycopg2.Error as e:
#         st.error(f"Error updating account balance: {e}")
#         return False

# def get_week_dates(date_input):
#     """Get the start and end dates for the week containing the given date"""
#     # Get the Monday of the week containing the given date
#     week_start = date_input - timedelta(days=date_input.weekday())
#     week_end = week_start + timedelta(days=6)
#     return week_start, week_end

# # Login Page
# def login_page():
#     st.title("Login to Personal Expense Tracker")
    
#     # Display default credentials info
#     st.info("💡 Default login credentials:\n- Username: admin\n- Password: admin123")
    
#     with st.form("login_form"):
#         username = st.text_input("Username")
#         password = st.text_input("Password", type="password")
#         submit_button = st.form_submit_button("Login")
        
#         if submit_button:
#             if authenticate(username, password):
#                 st.session_state.authenticated = True
#                 st.success("Login successful!")
#                 st.rerun()
#             else:
#                 st.error("Invalid username or password. Please try again.")

# # Weekly Reports Page
# def weekly_reports_page():
#     st.header("Weekly Reports")
    
#     # Tab selection for different report types
#     tab1, tab2, tab3 = st.tabs(["📊 Weekly Summary", "📋 Detailed Weekly Report", "📈 Weekly Trends"])
    
#     with tab1:
#         st.subheader("Weekly Summary Overview")
        
#         # Get weekly summary data
#         weekly_data = get_weekly_summary_data()
        
#         if weekly_data:
#             # Display current week summary
#             current_week = weekly_data[0] if weekly_data else None
#             if current_week:
#                 st.markdown("### Current Week Summary")
#                 col1, col2, col3, col4 = st.columns(4)
                
#                 with col1:
#                     st.metric("Total Expenses", f"${current_week['total_expenses']:.2f}")
#                 with col2:
#                     st.metric("Total Income", f"${current_week['total_income']:.2f}")
#                 with col3:
#                     st.metric("Net Amount", f"${current_week['net_amount']:.2f}",
#                             delta=f"${current_week['net_amount']:.2f}")
#                 with col4:
#                     st.metric("Transactions", current_week['transaction_count'])
                
#                 st.markdown(f"**Week Period:** {current_week['week_start'].strftime('%B %d')} - {current_week['week_end'].strftime('%B %d, %Y')}")
            
#             # Display weekly summary table
#             st.markdown("### Last 12 Weeks Summary")
#             summary_df = pd.DataFrame(weekly_data)
#             summary_df['Week'] = summary_df['week_start'].apply(lambda x: f"{x.strftime('%m/%d')} - {(x + timedelta(days=6)).strftime('%m/%d')}")
            
#             display_df = summary_df[['Week', 'total_expenses', 'total_income', 'net_amount', 'transaction_count']].copy()
#             display_df.columns = ['Week', 'Expenses ($)', 'Income ($)', 'Net ($)', 'Transactions']
            
#             st.dataframe(display_df, use_container_width=True)
            
#             # Weekly trends chart
#             if PLOTLY_AVAILABLE:
#                 fig = make_subplots(
#                     rows=2, cols=1,
#                     subplot_titles=('Weekly Expenses vs Income', 'Weekly Net Amount'),
#                     vertical_spacing=0.1
#                 )
                
#                 # Add expenses and income traces
#                 fig.add_trace(
#                     go.Scatter(x=summary_df['Week'], y=summary_df['total_expenses'],
#                               mode='lines+markers', name='Expenses', line=dict(color='red')),
#                     row=1, col=1
#                 )
#                 fig.add_trace(
#                     go.Scatter(x=summary_df['Week'], y=summary_df['total_income'],
#                               mode='lines+markers', name='Income', line=dict(color='green')),
#                     row=1, col=1
#                 )
                
#                 # Add net amount trace
#                 fig.add_trace(
#                     go.Scatter(x=summary_df['Week'], y=summary_df['net_amount'],
#                               mode='lines+markers', name='Net Amount', line=dict(color='blue')),
#                     row=2, col=1
#                 )
                
#                 fig.update_layout(height=600, title_text="Weekly Financial Trends")
#                 fig.update_xaxes(title_text="Week", row=2, col=1)
#                 fig.update_yaxes(title_text="Amount ($)", row=1, col=1)
#                 fig.update_yaxes(title_text="Net Amount ($)", row=2, col=1)
                
#                 st.plotly_chart(fig, use_container_width=True)
#         else:
#             st.info("No transaction data available for weekly summary.")
    
#     with tab2:
#         st.subheader("Detailed Weekly Report")
        
#         # Week selection
#         col1, col2 = st.columns(2)
#         with col1:
#             selected_date = st.date_input("Select any date in the week", datetime.now().date())
#         with col2:
#             week_start, week_end = get_week_dates(selected_date)
#             st.info(f"Selected week: {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}")
        
#         # Get transactions for the selected week
#         week_transactions = get_weekly_transactions(week_start, week_end)
        
#         if week_transactions:
#             # Weekly summary metrics
#             transactions_df = pd.DataFrame(week_transactions)
#             expenses_df = transactions_df[transactions_df['type'] == 'Expense']
#             income_df = transactions_df[transactions_df['type'] == 'Income']
            
#             total_expenses = expenses_df['amount'].sum() if not expenses_df.empty else 0
#             total_income = income_df['amount'].sum() if not income_df.empty else 0
#             net_amount = total_income - total_expenses
            
#             # Display weekly metrics
#             col1, col2, col3, col4 = st.columns(4)
#             with col1:
#                 st.metric("Total Expenses", f"${total_expenses:.2f}")
#             with col2:
#                 st.metric("Total Income", f"${total_income:.2f}")
#             with col3:
#                 st.metric("Net Amount", f"${net_amount:.2f}", delta=f"${net_amount:.2f}")
#             with col4:
#                 st.metric("Total Transactions", len(week_transactions))
            
#             # Expense breakdown by category
#             if not expenses_df.empty:
#                 st.markdown("### Expenses by Category")
#                 category_expenses = expenses_df.groupby('category')['amount'].sum().reset_index()
#                 category_expenses = category_expenses.sort_values('amount', ascending=False)
                
#                 col1, col2 = st.columns([1, 1])
#                 with col1:
#                     st.dataframe(category_expenses, use_container_width=True)
#                 with col2:
#                     if PLOTLY_AVAILABLE:
#                         fig = px.pie(category_expenses, values='amount', names='category',
#                                    title="Expense Distribution by Category")
#                         st.plotly_chart(fig, use_container_width=True)
            
#             # Account-wise breakdown
#             st.markdown("### Account-wise Breakdown")
#             account_summary = transactions_df.groupby(['account', 'type'])['amount'].sum().reset_index()
#             account_pivot = account_summary.pivot(index='account', columns='type', values='amount').fillna(0)
#             if 'Expense' not in account_pivot.columns:
#                 account_pivot['Expense'] = 0
#             if 'Income' not in account_pivot.columns:
#                 account_pivot['Income'] = 0
#             account_pivot['Net'] = account_pivot['Income'] - account_pivot['Expense']
            
#             st.dataframe(account_pivot, use_container_width=True)
            
#             # Daily breakdown
#             st.markdown("### Daily Breakdown")
#             transactions_df['date'] = pd.to_datetime(transactions_df['date'])
#             daily_summary = transactions_df.groupby([transactions_df['date'].dt.date, 'type'])['amount'].sum().reset_index()
#             daily_pivot = daily_summary.pivot(index='date', columns='type', values='amount').fillna(0)
#             if 'Expense' not in daily_pivot.columns:
#                 daily_pivot['Expense'] = 0
#             if 'Income' not in daily_pivot.columns:
#                 daily_pivot['Income'] = 0
#             daily_pivot['Net'] = daily_pivot['Income'] - daily_pivot['Expense']
            
#             st.dataframe(daily_pivot, use_container_width=True)
            
#             # All transactions for the week
#             st.markdown("### All Transactions")
#             st.dataframe(transactions_df, use_container_width=True)
            
#             # Download option
#             csv = transactions_df.to_csv(index=False).encode('utf-8')
#             st.download_button(
#                 f"Download Week Report ({week_start.strftime('%m-%d')} to {week_end.strftime('%m-%d')})",
#                 csv,
#                 f"weekly_report_{week_start.strftime('%Y%m%d')}_to_{week_end.strftime('%Y%m%d')}.csv",
#                 "text/csv"
#             )
            
#         else:
#             st.info(f"No transactions found for the week of {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}")
    
#     with tab3:
#         st.subheader("Weekly Trends Analysis")
        
#         weekly_data = get_weekly_summary_data()
#         if weekly_data and len(weekly_data) > 1:
#             df = pd.DataFrame(weekly_data)
            
#             # Calculate week-over-week changes
#             df['expense_change'] = df['total_expenses'].pct_change() * 100
#             df['income_change'] = df['total_income'].pct_change() * 100
            
#             # Average weekly spending
#             avg_weekly_expense = df['total_expenses'].mean()
#             avg_weekly_income = df['total_income'].mean()
            
#             col1, col2 = st.columns(2)
#             with col1:
#                 st.metric("Average Weekly Expenses", f"${avg_weekly_expense:.2f}")
#             with col2:
#                 st.metric("Average Weekly Income", f"${avg_weekly_income:.2f}")
            
#             # Trends analysis
#             st.markdown("### Weekly Trends")
#             recent_weeks = df.head(4)  # Last 4 weeks
            
#             if len(recent_weeks) >= 2:
#                 latest_expense_change = recent_weeks.iloc[0]['expense_change']
#                 latest_income_change = recent_weeks.iloc[0]['income_change']
                
#                 col1, col2 = st.columns(2)
#                 with col1:
#                     if not pd.isna(latest_expense_change):
#                         st.metric("Weekly Expense Change", f"{latest_expense_change:.1f}%", 
#                                 delta=f"{latest_expense_change:.1f}%")
#                 with col2:
#                     if not pd.isna(latest_income_change):
#                         st.metric("Weekly Income Change", f"{latest_income_change:.1f}%", 
#                                 delta=f"{latest_income_change:.1f}%")
            
#             # Spending patterns
#             st.markdown("### Spending Patterns")
#             high_expense_weeks = df[df['total_expenses'] > avg_weekly_expense * 1.2]
#             low_expense_weeks = df[df['total_expenses'] < avg_weekly_expense * 0.8]
            
#             col1, col2 = st.columns(2)
#             with col1:
#                 st.markdown(f"**High Expense Weeks:** {len(high_expense_weeks)}")
#                 if not high_expense_weeks.empty:
#                     st.dataframe(high_expense_weeks[['week_start', 'total_expenses']], use_container_width=True)
#             with col2:
#                 st.markdown(f"**Low Expense Weeks:** {len(low_expense_weeks)}")
#                 if not low_expense_weeks.empty:
#                     st.dataframe(low_expense_weeks[['week_start', 'total_expenses']], use_container_width=True)
#         else:
#             st.info("Need at least 2 weeks of data to show trends analysis.")

# # Main application flow
# # Initialize database on startup
# db_status = initialize_database()

# if not st.session_state.authenticated:
#     login_page()
# else:
#     # Add logout button to sidebar
#     if st.sidebar.button("Logout"):
#         st.session_state.authenticated = False
#         st.rerun()
    
#     # App title and description
#     st.title("Personal Expense Tracker")
#     st.markdown("Track your expenses, income, and account balances in one place")
    
#     # Sidebar for navigation
#     page = st.sidebar.radio("Navigation", ["Dashboard", "Add Transaction", "Transaction History", "Weekly Reports", "Account Management"])
    
#     # Dashboard page
#     if page == "Dashboard":
#         st.header("Financial Dashboard")
        
#         # Get accounts and transactions
#         accounts = get_accounts()
#         transactions = get_transactions()
        
#         # Display account balances
#         st.subheader("Account Balances")
#         account_df = pd.DataFrame({
#             'Account': list(accounts.keys()),
#             'Balance': list(accounts.values())
#         })
        
#         col1, col2 = st.columns([2, 3])
        
#         with col1:
#             st.dataframe(account_df, use_container_width=True)
        
#         with col2:
#             if sum(accounts.values()) > 0:
#                 if PLOTLY_AVAILABLE:
#                     fig = px.pie(account_df, values='Balance', names='Account', title="Balance Distribution")
#                     st.plotly_chart(fig, use_container_width=True)
#                 else:
#                     st.bar_chart(account_df.set_index('Account')['Balance'])
        
#         # Display recent transactions
#         st.subheader("Recent Transactions")
#         if transactions:
#             recent_transactions = transactions[:5]  # Get the first 5 (since they're already ordered by DESC date)
#             recent_df = pd.DataFrame(recent_transactions)
#             st.dataframe(recent_df, use_container_width=True)
#         else:
#             st.info("No transactions recorded yet.")
        
#         # Display expense summary by category if there are transactions
#         if transactions:
#             st.subheader("Expense Summary by Category")
#             transactions_df = pd.DataFrame(transactions)
            
#             # Filter for expenses only
#             expenses_df = transactions_df[transactions_df['type'] == 'Expense']
            
#             if not expenses_df.empty:
#                 category_summary = expenses_df.groupby('category')['amount'].sum().reset_index()
#                 if PLOTLY_AVAILABLE:
#                     fig = px.bar(category_summary, x='category', y='amount', title="Expenses by Category")
#                     st.plotly_chart(fig, use_container_width=True)
#                 else:
#                     st.bar_chart(category_summary.set_index('category')['amount'])
#             else:
#                 st.info("No expense transactions recorded yet.")
    
#     # Add Transaction page
#     elif page == "Add Transaction":
#         st.header("Add New Transaction")
        
#         # Get accounts
#         accounts = get_accounts()
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             st.subheader("Transaction Details")
#             transaction_type = st.selectbox("Transaction Type", ["Expense", "Income"])
#             amount = st.number_input("Amount", min_value=0.01, format="%.2f")
#             account = st.selectbox("Account", list(accounts.keys()))
#             category = st.selectbox("Category", 
#                                   ["Food", "Transport", "Utilities", "Entertainment", 
#                                     "Shopping", "Education", "Salary", "Gift", "Other"])
#             description = st.text_area("Description", placeholder="Enter details about the transaction")
#             date = st.date_input("Date", datetime.now())
            
#             if st.button("Add Transaction"):
#                 if amount <= 0:
#                     st.error("Amount must be greater than zero")
#                 elif transaction_type == "Expense" and amount > accounts[account]:
#                     st.error(f"Insufficient funds in {account}")
#                 else:
#                     if add_transaction(transaction_type, amount, account, category, description, date):
#                         st.success(f"{transaction_type} of ${amount:.2f} added successfully!")
#                         # Refresh accounts
#                         accounts = get_accounts()
        
#         with col2:
#             st.subheader("Current Account Balances")
#             for account, balance in accounts.items():
#                 st.metric(account, f"${balance:.2f}")
    
#     # Transaction History page
#     elif page == "Transaction History":
#         st.header("Transaction History")
        
#         # Get transactions
#         transactions = get_transactions()
#         transactions_df = pd.DataFrame(transactions) if transactions else pd.DataFrame()
        
#         if not transactions_df.empty:
#             # Filters
#             st.subheader("Filters")
#             col1, col2, col3 = st.columns(3)
            
#             with col1:
#                 filter_type = st.multiselect("Transaction Type", 
#                                           transactions_df['type'].unique().tolist(),
#                                           default=transactions_df['type'].unique().tolist())
            
#             with col2:
#                 filter_account = st.multiselect("Account", 
#                                              transactions_df['account'].unique().tolist(),
#                                              default=transactions_df['account'].unique().tolist())
            
#             with col3:
#                 filter_category = st.multiselect("Category", 
#                                               transactions_df['category'].unique().tolist(),
#                                               default=transactions_df['category'].unique().tolist())
            
#             # Apply filters
#             filtered_df = transactions_df[
#                 (transactions_df['type'].isin(filter_type)) & 
#                 (transactions_df['account'].isin(filter_account)) & 
#                 (transactions_df['category'].isin(filter_category))
#             ]
            
#             if not filtered_df.empty:
#                 st.dataframe(filtered_df, use_container_width=True)
                
#                 # Download option
#                 csv = filtered_df.to_csv(index=False).encode('utf-8')
#                 st.download_button(
#                     "Download Transaction History",
#                     csv,
#                     "transaction_history.csv",
#                     "text/csv",
#                     key='download-csv'
#                 )
#             else:
#                 st.info("No transactions match your filter criteria.")
#         else:
#             st.info("No transactions recorded yet.")
    
#     # Weekly Reports page
#     elif page == "Weekly Reports":
#         weekly_reports_page()
    
#     # Account Management page
#     elif page == "Account Management":
#         st.header("Account Management")
        
#         # Get accounts
#         accounts = get_accounts()
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             st.subheader("Update Account Balances")
#             account_to_update = st.selectbox("Select Account", list(accounts.keys()))
#             current_balance = accounts[account_to_update]
#             st.info(f"Current Balance: ${current_balance:.2f}")
#             new_balance = st.number_input("New Balance", min_value=0.0, value=float(current_balance), format="%.2f")
            
#             if st.button("Update Balance"):
#                 if update_account_balance(account_to_update, new_balance):
#                     st.success(f"{account_to_update} balance updated to ${new_balance:.2f}")
#                     # Refresh accounts
#                     accounts = get_accounts()
        
#         with col2:
#             st.subheader("Account Balances")
#             account_data = pd.DataFrame({
#                 'Account': list(accounts.keys()),
#                 'Balance': list(accounts.values())
#             })
#             st.dataframe(account_data, use_container_width=True)
            
#             total_balance = sum(accounts.values())
#             st.metric("Total Balance", f"${total_balance:.2f}")
    
#     # Footer
#     st.sidebar.markdown("---")
#     st.sidebar.info("Personal Expense Tracker - v1.1 (Neon PostgreSQL)")

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from urllib.parse import urlparse

from dotenv import load_dotenv
load_dotenv()

# Try to import plotly, with fallback
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Plotly not available. Charts will be disabled. Install with: pip install plotly")

# Try to import OpenAI for AI insights
try:
    import openai
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# Set page configuration
st.set_page_config(page_title="Personal Expense Tracker", layout="wide")

# Database connection parameters - Updated for Neon
DATABASE_URL = os.getenv("DATABASE_URL")

# Parse the database URL
url = urlparse(DATABASE_URL)
DB_CONFIG = {
    'host': url.hostname,
    'port': url.port,
    'database': url.path[1:],  # Remove leading slash
    'user': url.username,
    'password': url.password,
    'sslmode': 'require'
}

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Database connection function
def get_db_connection():
    """Get database connection with error handling"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        st.error(f"Database connection error: {e}")
        return None

# Database initialization functions
def initialize_database():
    """Create necessary database tables if they don't exist"""
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        cur = conn.cursor()
        
        # Create users table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(50) PRIMARY KEY,
            password VARCHAR(64) NOT NULL
        )
        """)
        
        # Create accounts table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            balance DECIMAL(10,2) DEFAULT 0
        )
        """)
        
        # Create transactions table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            type VARCHAR(10) NOT NULL CHECK (type IN ('Income', 'Expense')),
            amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
            account VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL,
            description TEXT,
            date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Check if default user exists, if not create it
        cur.execute("SELECT * FROM users WHERE username = %s", ("admin",))
        if cur.fetchone() is None:
            # Default credentials (username: admin, password: admin123)
            default_username = "admin"
            default_password = "admin123"
            
            # Hash the password for storage
            hashed_password = hashlib.sha256(default_password.encode()).hexdigest()
            
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
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
                cur.execute("INSERT INTO accounts (name, balance) VALUES (%s, %s)", (account, 0))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except psycopg2.Error as e:
        st.error(f"Database initialization error: {e}")
        return False

# Authentication function
def authenticate(username, password):
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        cur = conn.cursor()
        
        # Hash the provided password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Check credentials against database
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", 
                  (username, hashed_password))
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return result is not None
    except psycopg2.Error as e:
        st.error(f"Authentication error: {e}")
        return False

# Data functions
def get_accounts():
    """Get all accounts and their balances"""
    try:
        conn = get_db_connection()
        if not conn:
            return {}
            
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT name, balance FROM accounts ORDER BY name")
        accounts = {row['name']: float(row['balance']) for row in cur.fetchall()}
        cur.close()
        conn.close()
        return accounts
    except psycopg2.Error as e:
        st.error(f"Error loading accounts: {e}")
        return {}

def get_transactions():
    """Get all transactions"""
    try:
        conn = get_db_connection()
        if not conn:
            return []
            
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
        SELECT type, amount, account, category, description, date
        FROM transactions
        ORDER BY date DESC, id DESC
        """)
        transactions = [dict(row) for row in cur.fetchall()]
        # Convert Decimal to float for better compatibility
        for transaction in transactions:
            transaction['amount'] = float(transaction['amount'])
        cur.close()
        conn.close()
        return transactions
    except psycopg2.Error as e:
        st.error(f"Error loading transactions: {e}")
        return []

def get_weekly_transactions(start_date, end_date):
    """Get transactions for a specific week"""
    try:
        conn = get_db_connection()
        if not conn:
            return []
            
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
        SELECT type, amount, account, category, description, date
        FROM transactions
        WHERE date BETWEEN %s AND %s
        ORDER BY date DESC, id DESC
        """, (start_date, end_date))
        transactions = [dict(row) for row in cur.fetchall()]
        # Convert Decimal to float for better compatibility
        for transaction in transactions:
            transaction['amount'] = float(transaction['amount'])
        cur.close()
        conn.close()
        return transactions
    except psycopg2.Error as e:
        st.error(f"Error loading weekly transactions: {e}")
        return []

def get_weekly_summary_data():
    """Get weekly summary data for the last 12 weeks"""
    try:
        conn = get_db_connection()
        if not conn:
            return []
            
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
        SELECT 
            DATE_TRUNC('week', date) as week_start,
            DATE_TRUNC('week', date) + INTERVAL '6 days' as week_end,
            SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END) as total_expenses,
            SUM(CASE WHEN type = 'Income' THEN amount ELSE 0 END) as total_income,
            COUNT(*) as transaction_count
        FROM transactions
        WHERE date >= CURRENT_DATE - INTERVAL '12 weeks'
        GROUP BY DATE_TRUNC('week', date)
        ORDER BY week_start DESC
        """)
        
        weekly_data = []
        for row in cur.fetchall():
            weekly_data.append({
                'week_start': row['week_start'].date(),
                'week_end': row['week_end'].date(),
                'total_expenses': float(row['total_expenses']),
                'total_income': float(row['total_income']),
                'transaction_count': row['transaction_count'],
                'net_amount': float(row['total_income']) - float(row['total_expenses'])
            })
        
        cur.close()
        conn.close()
        return weekly_data
    except psycopg2.Error as e:
        st.error(f"Error loading weekly summary: {e}")
        return []

def add_transaction(transaction_type, amount, account, category, description, date):
    """Add a new transaction and update account balance"""
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        cur = conn.cursor()
        
        # Start transaction
        conn.autocommit = False
        
        # Insert the transaction
        cur.execute("""
        INSERT INTO transactions (type, amount, account, category, description, date)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (transaction_type, amount, account, category, description, date))
        
        # Update account balance
        if transaction_type == "Expense":
            cur.execute("""
            UPDATE accounts SET balance = balance - %s WHERE name = %s
            """, (amount, account))
        else:  # Income
            cur.execute("""
            UPDATE accounts SET balance = balance + %s WHERE name = %s
            """, (amount, account))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
            conn.close()
        st.error(f"Error adding transaction: {e}")
        return False

def update_account_balance(account, new_balance):
    """Update an account's balance"""
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        cur = conn.cursor()
        
        cur.execute("""
        UPDATE accounts SET balance = %s WHERE name = %s
        """, (new_balance, account))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except psycopg2.Error as e:
        st.error(f"Error updating account balance: {e}")
        return False

def get_week_dates(date_input):
    """Get the start and end dates for the week containing the given date"""
    # Get the Monday of the week containing the given date
    week_start = date_input - timedelta(days=date_input.weekday())
    week_end = week_start + timedelta(days=6)
    return week_start, week_end

def get_financial_insights_prompt(weekly_data, recent_transactions, accounts):
    """Generate a comprehensive financial analysis prompt for the AI"""
    
    # Calculate key metrics
    total_balance = sum(accounts.values())
    recent_expenses = [t for t in recent_transactions if t['type'] == 'Expense']
    recent_income = [t for t in recent_transactions if t['type'] == 'Income']
    
    total_recent_expenses = sum(t['amount'] for t in recent_expenses)
    total_recent_income = sum(t['amount'] for t in recent_income)
    
    # Category breakdown
    from collections import defaultdict
    category_spending = defaultdict(float)
    for transaction in recent_expenses:
        category_spending[transaction['category']] += transaction['amount']
    
    # Account usage
    account_activity = defaultdict(float)
    for transaction in recent_transactions:
        if transaction['type'] == 'Expense':
            account_activity[transaction['account']] += transaction['amount']
    
    prompt = f"""
    As a personal financial advisor, analyze the following financial data and provide actionable insights and recommendations:

    ACCOUNT BALANCES:
    {dict(accounts)}
    Total Balance: ${total_balance:.2f}

    RECENT FINANCIAL ACTIVITY (Last 30 days):
    - Total Expenses: ${total_recent_expenses:.2f}
    - Total Income: ${total_recent_income:.2f}
    - Net Cash Flow: ${total_recent_income - total_recent_expenses:.2f}
    - Number of Transactions: {len(recent_transactions)}

    SPENDING BY CATEGORY:
    {dict(category_spending)}

    ACCOUNT USAGE (Expenses):
    {dict(account_activity)}

    WEEKLY TRENDS (Last 4 weeks):
    """
    
    if weekly_data:
        for i, week in enumerate(weekly_data[:4]):
            prompt += f"\nWeek {i+1}: Expenses ${week['total_expenses']:.2f}, Income ${week['total_income']:.2f}, Net ${week['net_amount']:.2f}"
    
    prompt += """

    Please provide a comprehensive financial analysis including:

    1. FINANCIAL HEALTH ASSESSMENT:
    - Overall financial position
    - Cash flow analysis
    - Account balance distribution

    2. SPENDING PATTERNS ANALYSIS:
    - Category-wise spending insights
    - Identify highest expense categories
    - Account usage patterns

    3. PERSONALIZED RECOMMENDATIONS:
    - Budget optimization suggestions
    - Areas to reduce spending
    - Savings opportunities
    - Account management advice

    4. BEST PRACTICES:
    - General financial wellness tips
    - Emergency fund recommendations
    - Investment suggestions (if applicable)

    5. ACTION ITEMS:
    - Specific steps to improve financial health
    - Short-term and long-term goals

    Please format your response in clear sections with bullet points for easy reading. Be specific and actionable in your recommendations.
    """
    
    return prompt

def get_ai_financial_insights(weekly_data, recent_transactions, accounts, api_key=None):
    """Get AI-powered financial insights using OpenAI API"""
    if not AI_AVAILABLE:
        return "AI insights feature requires the 'openai' package. Install with: pip install openai"
    
    if not api_key:
        return "Please provide an OpenAI API key to use AI insights feature."
    
    try:
        # Set up OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Generate the prompt
        prompt = get_financial_insights_prompt(weekly_data, recent_transactions, accounts)
        
        # Make API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional financial advisor with expertise in personal finance, budgeting, and wealth management. Provide helpful, actionable advice based on the user's financial data."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating AI insights: {str(e)}"

def get_simple_financial_insights(weekly_data, recent_transactions, accounts):
    """Generate basic financial insights without AI"""
    insights = []
    
    # Calculate metrics
    total_balance = sum(accounts.values())
    recent_expenses = [t for t in recent_transactions if t['type'] == 'Expense']
    recent_income = [t for t in recent_transactions if t['type'] == 'Income']
    
    total_recent_expenses = sum(t['amount'] for t in recent_expenses)
    total_recent_income = sum(t['amount'] for t in recent_income)
    net_flow = total_recent_income - total_recent_expenses
    
    # Financial Health Assessment
    insights.append("## 💰 Financial Health Assessment")
    if net_flow > 0:
        insights.append(f"✅ **Positive Cash Flow**: You have a positive net cash flow of ${net_flow:.2f}")
    else:
        insights.append(f"⚠️ **Negative Cash Flow**: You're spending ${abs(net_flow):.2f} more than you earn")
    
    if total_balance > total_recent_expenses * 3:
        insights.append("✅ **Good Emergency Buffer**: Your total balance covers 3+ months of expenses")
    elif total_balance > total_recent_expenses:
        insights.append("⚠️ **Moderate Emergency Buffer**: Consider building a larger emergency fund")
    else:
        insights.append("🚨 **Low Emergency Buffer**: Priority should be building emergency savings")
    
    # Spending Analysis
    insights.append("\n## 📊 Spending Analysis")
    if recent_expenses:
        category_spending = {}
        for transaction in recent_expenses:
            category = transaction['category']
            category_spending[category] = category_spending.get(category, 0) + transaction['amount']
        
        top_category = max(category_spending, key=category_spending.get)
        top_amount = category_spending[top_category]
        percentage = (top_amount / total_recent_expenses) * 100
        
        insights.append(f"🔥 **Highest Expense Category**: {top_category} (${top_amount:.2f}, {percentage:.1f}% of total)")
        
        if percentage > 40:
            insights.append(f"💡 **Recommendation**: {top_category} takes up a large portion of your budget. Review if this can be optimized.")
    
    # Account Distribution
    insights.append("\n## 🏦 Account Management")
    if len(accounts) > 1:
        highest_balance_account = max(accounts, key=accounts.get)
        insights.append(f"💳 **Primary Account**: {highest_balance_account} holds ${accounts[highest_balance_account]:.2f}")
        
        low_balance_accounts = [acc for acc, bal in accounts.items() if bal < 100]
        if low_balance_accounts:
            insights.append(f"⚠️ **Low Balance Accounts**: {', '.join(low_balance_accounts)} - Consider consolidating")
    
    # Weekly Trends
    if weekly_data and len(weekly_data) >= 2:
        insights.append("\n## 📈 Weekly Trends")
        current_week = weekly_data[0]
        previous_week = weekly_data[1]
        
        expense_change = ((current_week['total_expenses'] - previous_week['total_expenses']) / previous_week['total_expenses']) * 100
        if expense_change > 20:
            insights.append(f"📈 **Spending Increase**: Expenses increased by {expense_change:.1f}% from last week")
        elif expense_change < -20:
            insights.append(f"📉 **Spending Decrease**: Expenses decreased by {abs(expense_change):.1f}% from last week - Great job!")
    
    # Best Practices
    insights.append("\n## 🎯 Best Practices & Recommendations")
    insights.append("• **50/30/20 Rule**: Aim for 50% needs, 30% wants, 20% savings")
    insights.append("• **Emergency Fund**: Build 3-6 months of expenses in savings")
    insights.append("• **Track Daily**: Record transactions immediately for accuracy")
    insights.append("• **Review Weekly**: Check spending patterns every week")
    insights.append("• **Budget Categories**: Set limits for each spending category")
    
    if net_flow > 0:
        insights.append("• **Invest Surplus**: Consider investing your positive cash flow")
    else:
        insights.append("• **Reduce Expenses**: Focus on cutting unnecessary spending")
    
    return "\n".join(insights)

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

# Weekly Reports Page
def weekly_reports_page():
    st.header("Weekly Reports")
    
    # Tab selection for different report types
    tab1, tab2, tab3 = st.tabs(["📊 Weekly Summary", "📋 Detailed Weekly Report", "📈 Weekly Trends"])
    
    with tab1:
        st.subheader("Weekly Summary Overview")
        
        # Get weekly summary data
        weekly_data = get_weekly_summary_data()
        
        if weekly_data:
            # Display current week summary
            current_week = weekly_data[0] if weekly_data else None
            if current_week:
                st.markdown("### Current Week Summary")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Expenses", f"${current_week['total_expenses']:.2f}")
                with col2:
                    st.metric("Total Income", f"${current_week['total_income']:.2f}")
                with col3:
                    st.metric("Net Amount", f"${current_week['net_amount']:.2f}",
                            delta=f"${current_week['net_amount']:.2f}")
                with col4:
                    st.metric("Transactions", current_week['transaction_count'])
                
                st.markdown(f"**Week Period:** {current_week['week_start'].strftime('%B %d')} - {current_week['week_end'].strftime('%B %d, %Y')}")
            
            # Display weekly summary table
            st.markdown("### Last 12 Weeks Summary")
            summary_df = pd.DataFrame(weekly_data)
            summary_df['Week'] = summary_df['week_start'].apply(lambda x: f"{x.strftime('%m/%d')} - {(x + timedelta(days=6)).strftime('%m/%d')}")
            
            display_df = summary_df[['Week', 'total_expenses', 'total_income', 'net_amount', 'transaction_count']].copy()
            display_df.columns = ['Week', 'Expenses ($)', 'Income ($)', 'Net ($)', 'Transactions']
            
            st.dataframe(display_df, use_container_width=True)
            
            # Weekly trends chart
            if PLOTLY_AVAILABLE:
                fig = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=('Weekly Expenses vs Income', 'Weekly Net Amount'),
                    vertical_spacing=0.1
                )
                
                # Add expenses and income traces
                fig.add_trace(
                    go.Scatter(x=summary_df['Week'], y=summary_df['total_expenses'],
                              mode='lines+markers', name='Expenses', line=dict(color='red')),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=summary_df['Week'], y=summary_df['total_income'],
                              mode='lines+markers', name='Income', line=dict(color='green')),
                    row=1, col=1
                )
                
                # Add net amount trace
                fig.add_trace(
                    go.Scatter(x=summary_df['Week'], y=summary_df['net_amount'],
                              mode='lines+markers', name='Net Amount', line=dict(color='blue')),
                    row=2, col=1
                )
                
                fig.update_layout(height=600, title_text="Weekly Financial Trends")
                fig.update_xaxes(title_text="Week", row=2, col=1)
                fig.update_yaxes(title_text="Amount ($)", row=1, col=1)
                fig.update_yaxes(title_text="Net Amount ($)", row=2, col=1)
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No transaction data available for weekly summary.")
    
    with tab2:
        st.subheader("Detailed Weekly Report")
        
        # Week selection
        col1, col2 = st.columns(2)
        with col1:
            selected_date = st.date_input("Select any date in the week", datetime.now().date())
        with col2:
            week_start, week_end = get_week_dates(selected_date)
            st.info(f"Selected week: {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}")
        
        # Get transactions for the selected week
        week_transactions = get_weekly_transactions(week_start, week_end)
        
        if week_transactions:
            # Weekly summary metrics
            transactions_df = pd.DataFrame(week_transactions)
            expenses_df = transactions_df[transactions_df['type'] == 'Expense']
            income_df = transactions_df[transactions_df['type'] == 'Income']
            
            total_expenses = expenses_df['amount'].sum() if not expenses_df.empty else 0
            total_income = income_df['amount'].sum() if not income_df.empty else 0
            net_amount = total_income - total_expenses
            
            # Display weekly metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Expenses", f"${total_expenses:.2f}")
            with col2:
                st.metric("Total Income", f"${total_income:.2f}")
            with col3:
                st.metric("Net Amount", f"${net_amount:.2f}", delta=f"${net_amount:.2f}")
            with col4:
                st.metric("Total Transactions", len(week_transactions))
            
            # Expense breakdown by category
            if not expenses_df.empty:
                st.markdown("### Expenses by Category")
                category_expenses = expenses_df.groupby('category')['amount'].sum().reset_index()
                category_expenses = category_expenses.sort_values('amount', ascending=False)
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.dataframe(category_expenses, use_container_width=True)
                with col2:
                    if PLOTLY_AVAILABLE:
                        fig = px.pie(category_expenses, values='amount', names='category',
                                   title="Expense Distribution by Category")
                        st.plotly_chart(fig, use_container_width=True)
            
            # Account-wise breakdown
            st.markdown("### Account-wise Breakdown")
            account_summary = transactions_df.groupby(['account', 'type'])['amount'].sum().reset_index()
            account_pivot = account_summary.pivot(index='account', columns='type', values='amount').fillna(0)
            if 'Expense' not in account_pivot.columns:
                account_pivot['Expense'] = 0
            if 'Income' not in account_pivot.columns:
                account_pivot['Income'] = 0
            account_pivot['Net'] = account_pivot['Income'] - account_pivot['Expense']
            
            st.dataframe(account_pivot, use_container_width=True)
            
            # Daily breakdown
            st.markdown("### Daily Breakdown")
            transactions_df['date'] = pd.to_datetime(transactions_df['date'])
            daily_summary = transactions_df.groupby([transactions_df['date'].dt.date, 'type'])['amount'].sum().reset_index()
            daily_pivot = daily_summary.pivot(index='date', columns='type', values='amount').fillna(0)
            if 'Expense' not in daily_pivot.columns:
                daily_pivot['Expense'] = 0
            if 'Income' not in daily_pivot.columns:
                daily_pivot['Income'] = 0
            daily_pivot['Net'] = daily_pivot['Income'] - daily_pivot['Expense']
            
            st.dataframe(daily_pivot, use_container_width=True)
            
            # All transactions for the week
            st.markdown("### All Transactions")
            st.dataframe(transactions_df, use_container_width=True)
            
            # Download option
            csv = transactions_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                f"Download Week Report ({week_start.strftime('%m-%d')} to {week_end.strftime('%m-%d')})",
                csv,
                f"weekly_report_{week_start.strftime('%Y%m%d')}_to_{week_end.strftime('%Y%m%d')}.csv",
                "text/csv"
            )
            
        else:
            st.info(f"No transactions found for the week of {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}")
    
    with tab3:
        st.subheader("Weekly Trends Analysis")
        
        weekly_data = get_weekly_summary_data()
        if weekly_data and len(weekly_data) > 1:
            df = pd.DataFrame(weekly_data)
            
            # Calculate week-over-week changes
            df['expense_change'] = df['total_expenses'].pct_change() * 100
            df['income_change'] = df['total_income'].pct_change() * 100
            
            # Average weekly spending
            avg_weekly_expense = df['total_expenses'].mean()
            avg_weekly_income = df['total_income'].mean()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Average Weekly Expenses", f"${avg_weekly_expense:.2f}")
            with col2:
                st.metric("Average Weekly Income", f"${avg_weekly_income:.2f}")
            
            # Trends analysis
            st.markdown("### Weekly Trends")
            recent_weeks = df.head(4)  # Last 4 weeks
            
            if len(recent_weeks) >= 2:
                latest_expense_change = recent_weeks.iloc[0]['expense_change']
                latest_income_change = recent_weeks.iloc[0]['income_change']
                
                col1, col2 = st.columns(2)
                with col1:
                    if not pd.isna(latest_expense_change):
                        st.metric("Weekly Expense Change", f"{latest_expense_change:.1f}%", 
                                delta=f"{latest_expense_change:.1f}%")
                with col2:
                    if not pd.isna(latest_income_change):
                        st.metric("Weekly Income Change", f"{latest_income_change:.1f}%", 
                                delta=f"{latest_income_change:.1f}%")
            
            # Spending patterns
            st.markdown("### Spending Patterns")
            high_expense_weeks = df[df['total_expenses'] > avg_weekly_expense * 1.2]
            low_expense_weeks = df[df['total_expenses'] < avg_weekly_expense * 0.8]
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**High Expense Weeks:** {len(high_expense_weeks)}")
                if not high_expense_weeks.empty:
                    st.dataframe(high_expense_weeks[['week_start', 'total_expenses']], use_container_width=True)
            with col2:
                st.markdown(f"**Low Expense Weeks:** {len(low_expense_weeks)}")
                if not low_expense_weeks.empty:
                    st.dataframe(low_expense_weeks[['week_start', 'total_expenses']], use_container_width=True)
        else:
            st.info("Not enough data for trend analysis. Need at least 2 weeks of transactions.")

# Dashboard Page
def dashboard_page():
    st.header("Financial Dashboard")
    
    # Get data
    accounts = get_accounts()
    transactions = get_transactions()
    
    if not accounts:
        st.warning("No accounts found. Please check your database connection.")
        return
    
    # Calculate financial metrics
    total_balance = sum(accounts.values())
    
    # Filter recent transactions (last 30 days)
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_transactions = [t for t in transactions if pd.to_datetime(t['date']).date() >= thirty_days_ago]
    
    expenses = [t for t in recent_transactions if t['type'] == 'Expense']
    income = [t for t in recent_transactions if t['type'] == 'Income']
    
    total_expenses = sum(t['amount'] for t in expenses)
    total_income = sum(t['amount'] for t in income)
    net_cash_flow = total_income - total_expenses
    
    # Top row metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Balance", f"${total_balance:.2f}")
    with col2:
        st.metric("Monthly Expenses", f"${total_expenses:.2f}")
    with col3:
        st.metric("Monthly Income", f"${total_income:.2f}")
    with col4:
        delta_color = "normal" if net_cash_flow >= 0 else "inverse"
        st.metric("Net Cash Flow", f"${net_cash_flow:.2f}", delta=f"${net_cash_flow:.2f}")
    
    # Account balances
    st.subheader("Account Balances")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Account balances table
        accounts_df = pd.DataFrame(list(accounts.items()), columns=['Account', 'Balance'])
        accounts_df['Balance'] = accounts_df['Balance'].apply(lambda x: f"${x:.2f}")
        st.dataframe(accounts_df, use_container_width=True, hide_index=True)
    
    with col2:
        # Account balance pie chart
        if PLOTLY_AVAILABLE and len(accounts) > 1:
            fig = px.pie(
                values=list(accounts.values()), 
                names=list(accounts.keys()),
                title="Account Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Expense breakdown
    if expenses:
        st.subheader("Expense Breakdown (Last 30 Days)")
        
        # Group expenses by category
        category_expenses = {}
        for expense in expenses:
            category = expense['category']
            category_expenses[category] = category_expenses.get(category, 0) + expense['amount']
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Category expenses table
            category_df = pd.DataFrame(list(category_expenses.items()), columns=['Category', 'Amount'])
            category_df = category_df.sort_values('Amount', ascending=False)
            category_df['Amount'] = category_df['Amount'].apply(lambda x: f"${x:.2f}")
            st.dataframe(category_df, use_container_width=True, hide_index=True)
        
        with col2:
            # Category expenses pie chart
            if PLOTLY_AVAILABLE:
                fig = px.pie(
                    values=list(category_expenses.values()), 
                    names=list(category_expenses.keys()),
                    title="Expenses by Category"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Recent transactions
    st.subheader("Recent Transactions")
    
    if recent_transactions:
        # Display last 10 transactions
        recent_df = pd.DataFrame(recent_transactions[:10])
        recent_df['Amount'] = recent_df.apply(
            lambda row: f"${row['amount']:.2f}" if row['type'] == 'Income' else f"-${row['amount']:.2f}", 
            axis=1
        )
        display_df = recent_df[['date', 'type', 'Amount', 'account', 'category', 'description']]
        display_df.columns = ['Date', 'Type', 'Amount', 'Account', 'Category', 'Description']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        if len(recent_transactions) > 10:
            st.info(f"Showing 10 of {len(recent_transactions)} recent transactions")
    else:
        st.info("No recent transactions found.")
    
    # Monthly trends (if enough data)
    if PLOTLY_AVAILABLE and len(transactions) > 5:
        st.subheader("Monthly Trends")
        
        # Prepare data for monthly chart
        df = pd.DataFrame(transactions)
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M')
        
        monthly_summary = df.groupby(['month', 'type'])['amount'].sum().reset_index()
        monthly_pivot = monthly_summary.pivot(index='month', columns='type', values='amount').fillna(0)
        
        if 'Expense' not in monthly_pivot.columns:
            monthly_pivot['Expense'] = 0
        if 'Income' not in monthly_pivot.columns:
            monthly_pivot['Income'] = 0
        
        monthly_pivot = monthly_pivot.reset_index()
        monthly_pivot['month_str'] = monthly_pivot['month'].astype(str)
        monthly_pivot['Net'] = monthly_pivot['Income'] - monthly_pivot['Expense']
        
        # Create monthly trends chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=monthly_pivot['month_str'], 
            y=monthly_pivot['Expense'],
            mode='lines+markers',
            name='Expenses',
            line=dict(color='red')
        ))
        
        fig.add_trace(go.Scatter(
            x=monthly_pivot['month_str'], 
            y=monthly_pivot['Income'],
            mode='lines+markers',
            name='Income',
            line=dict(color='green')
        ))
        
        fig.add_trace(go.Scatter(
            x=monthly_pivot['month_str'], 
            y=monthly_pivot['Net'],
            mode='lines+markers',
            name='Net',
            line=dict(color='blue')
        ))
        
        fig.update_layout(
            title="Monthly Financial Trends",
            xaxis_title="Month",
            yaxis_title="Amount ($)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Add Transaction Page
def add_transaction_page():
    st.header("Add New Transaction")
    
    # Get accounts
    accounts = get_accounts()
    
    if not accounts:
        st.warning("No accounts found. Please check your database connection.")
        return
    
    # Transaction form
    with st.form("transaction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            transaction_type = st.selectbox("Type", ["Expense", "Income"])
            amount = st.number_input("Amount", min_value=0.01, step=0.01, format="%.2f")
            account = st.selectbox("Account", list(accounts.keys()))
        
        with col2:
            # Common categories
            expense_categories = [
                "Food & Dining", "Transportation", "Shopping", "Entertainment",
                "Bills & Utilities", "Healthcare", "Education", "Travel",
                "Housing", "Insurance", "Gifts & Donations", "Other"
            ]
            
            income_categories = [
                "Salary", "Business", "Investment", "Gift", "Refund", "Other"
            ]
            
            categories = expense_categories if transaction_type == "Expense" else income_categories
            category = st.selectbox("Category", categories)
            
            date = st.date_input("Date", datetime.now().date())
        
        description = st.text_area("Description (Optional)", placeholder="Enter transaction details...")
        
        submit_button = st.form_submit_button("Add Transaction", use_container_width=True)
        
        if submit_button:
            if amount > 0:
                success = add_transaction(transaction_type, amount, account, category, description, date)
                if success:
                    st.success(f"✅ {transaction_type} of ${amount:.2f} added successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to add transaction. Please try again.")
            else:
                st.error("❌ Amount must be greater than 0.")
    
    # Quick add buttons for common transactions
    st.subheader("Quick Add")
    
    quick_transactions = [
        {"name": "Coffee", "type": "Expense", "amount": 5.0, "category": "Food & Dining"},
        {"name": "Lunch", "type": "Expense", "amount": 15.0, "category": "Food & Dining"},
        {"name": "Gas", "type": "Expense", "amount": 50.0, "category": "Transportation"},
        {"name": "Groceries", "type": "Expense", "amount": 100.0, "category": "Shopping"},
    ]
    
    cols = st.columns(len(quick_transactions))
    
    for i, quick_tx in enumerate(quick_transactions):
        with cols[i]:
            if st.button(f"{quick_tx['name']}\n${quick_tx['amount']:.0f}", key=f"quick_{i}"):
                # Use the first available account for quick transactions
                first_account = list(accounts.keys())[0]
                success = add_transaction(
                    quick_tx['type'], 
                    quick_tx['amount'], 
                    first_account, 
                    quick_tx['category'], 
                    f"Quick add: {quick_tx['name']}", 
                    datetime.now().date()
                )
                if success:
                    st.success(f"✅ Quick {quick_tx['name']} transaction added!")
                    st.rerun()

# View Transactions Page
def view_transactions_page():
    st.header("View Transactions")
    
    # Get transactions
    transactions = get_transactions()
    
    if not transactions:
        st.info("No transactions found.")
        return
    
    # Filters
    st.subheader("Filters")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Date range filter
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now().date() - timedelta(days=30), datetime.now().date()),
            format="YYYY-MM-DD"
        )
    
    with col2:
        # Transaction type filter
        all_types = ["All"] + list(set(t['type'] for t in transactions))
        selected_type = st.selectbox("Type", all_types)
    
    with col3:
        # Category filter
        all_categories = ["All"] + list(set(t['category'] for t in transactions))
        selected_category = st.selectbox("Category", all_categories)
    
    with col4:
        # Account filter
        all_accounts = ["All"] + list(set(t['account'] for t in transactions))
        selected_account = st.selectbox("Account", all_accounts)
    
    # Apply filters
    filtered_transactions = transactions.copy()
    
    # Date filter
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_transactions = [
            t for t in filtered_transactions 
            if start_date <= pd.to_datetime(t['date']).date() <= end_date
        ]
    
    # Type filter
    if selected_type != "All":
        filtered_transactions = [t for t in filtered_transactions if t['type'] == selected_type]
    
    # Category filter
    if selected_category != "All":
        filtered_transactions = [t for t in filtered_transactions if t['category'] == selected_category]
    
    # Account filter
    if selected_account != "All":
        filtered_transactions = [t for t in filtered_transactions if t['account'] == selected_account]
    
    # Display filtered transactions
    if filtered_transactions:
        st.subheader(f"Transactions ({len(filtered_transactions)} found)")
        
        # Calculate totals for filtered transactions
        expenses = [t for t in filtered_transactions if t['type'] == 'Expense']
        income = [t for t in filtered_transactions if t['type'] == 'Income']
        
        total_expenses = sum(t['amount'] for t in expenses)
        total_income = sum(t['amount'] for t in income)
        net_amount = total_income - total_expenses
        
        # Display summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Expenses", f"${total_expenses:.2f}")
        with col2:
            st.metric("Total Income", f"${total_income:.2f}")
        with col3:
            st.metric("Net Amount", f"${net_amount:.2f}", delta=f"${net_amount:.2f}")
        
        # Display transactions table
        df = pd.DataFrame(filtered_transactions)
        df['Amount Display'] = df.apply(
            lambda row: f"${row['amount']:.2f}" if row['type'] == 'Income' else f"-${row['amount']:.2f}", 
            axis=1
        )
        
        display_df = df[['date', 'type', 'Amount Display', 'account', 'category', 'description']].copy()
        display_df.columns = ['Date', 'Type', 'Amount', 'Account', 'Category', 'Description']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Download option
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Transactions CSV",
            csv,
            f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv",
            use_container_width=True
        )
        
    else:
        st.info("No transactions match the selected filters.")

# Account Management Page
def account_management_page():
    st.header("Account Management")
    
    # Get accounts
    accounts = get_accounts()
    
    if not accounts:
        st.warning("No accounts found. Please check your database connection.")
        return
    
    # Display current accounts
    st.subheader("Current Accounts")
    
    # Account balances with edit functionality
    for account_name, balance in accounts.items():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"**{account_name}**")
        with col2:
            st.write(f"${balance:.2f}")
        with col3:
            if st.button("Edit", key=f"edit_{account_name}"):
                st.session_state[f"editing_{account_name}"] = True
        
        # Edit balance form
        if st.session_state.get(f"editing_{account_name}", False):
            with st.form(f"edit_form_{account_name}"):
                new_balance = st.number_input(
                    f"New balance for {account_name}", 
                    value=float(balance), 
                    step=0.01, 
                    format="%.2f"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Update"):
                        success = update_account_balance(account_name, new_balance)
                        if success:
                            st.success(f"✅ {account_name} balance updated!")
                            st.session_state[f"editing_{account_name}"] = False
                            st.rerun()
                        else:
                            st.error("❌ Failed to update balance.")
                
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state[f"editing_{account_name}"] = False
                        st.rerun()
    
    # Total balance
    total_balance = sum(accounts.values())
    st.markdown(f"### Total Balance: ${total_balance:.2f}")
    
    # Account balance chart
    if PLOTLY_AVAILABLE and len(accounts) > 1:
        st.subheader("Account Distribution")
        
        fig = px.bar(
            x=list(accounts.keys()), 
            y=list(accounts.values()),
            title="Account Balances",
            labels={'x': 'Account', 'y': 'Balance ($)'}
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Financial Insights Page
def financial_insights_page():
    st.header("Financial Insights")
    
    # Get data
    accounts = get_accounts()
    transactions = get_transactions()
    weekly_data = get_weekly_summary_data()
    
    if not accounts or not transactions:
        st.warning("Not enough data for insights. Please add some transactions first.")
        return
    
    # Filter recent transactions (last 30 days)
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_transactions = [t for t in transactions if pd.to_datetime(t['date']).date() >= thirty_days_ago]
    
    # Choose between AI insights and simple insights
    st.subheader("Financial Analysis Options")
    
    insight_type = st.radio(
        "Choose insight type:",
        ["Basic Insights (Free)", "AI-Powered Insights (Requires OpenAI API Key)"],
        horizontal=True
    )
    
    if insight_type == "AI-Powered Insights (Requires OpenAI API Key)":
        api_key = st.text_input("Enter your OpenAI API Key:", type="password")
        
        if st.button("Generate AI Insights", use_container_width=True):
            if api_key:
                with st.spinner("Generating AI insights..."):
                    insights = get_ai_financial_insights(weekly_data, recent_transactions, accounts, api_key)
                st.markdown(insights)
            else:
                st.warning("Please enter your OpenAI API key to generate AI insights.")
    
    else:
        # Generate basic insights
        if st.button("Generate Basic Insights", use_container_width=True):
            with st.spinner("Analyzing your financial data..."):
                insights = get_simple_financial_insights(weekly_data, recent_transactions, accounts)
            st.markdown(insights)
    
    # Additional financial metrics
    st.subheader("Key Financial Metrics")
    
    # Calculate metrics
    total_balance = sum(accounts.values())
    recent_expenses = [t for t in recent_transactions if t['type'] == 'Expense']
    recent_income = [t for t in recent_transactions if t['type'] == 'Income']
    
    total_recent_expenses = sum(t['amount'] for t in recent_expenses)
    total_recent_income = sum(t['amount'] for t in recent_income)
    
    # Monthly projections
    days_in_period = 30
    daily_avg_expense = total_recent_expenses / days_in_period if total_recent_expenses > 0 else 0
    daily_avg_income = total_recent_income / days_in_period if total_recent_income > 0 else 0
    
    monthly_projected_expense = daily_avg_expense * 30
    monthly_projected_income = daily_avg_income * 30
    
    # Emergency fund calculation
    months_of_expenses = total_balance / monthly_projected_expense if monthly_projected_expense > 0 else float('inf')
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Average Daily Expenses", f"${daily_avg_expense:.2f}")
        st.metric("Monthly Projection", f"${monthly_projected_expense:.2f}")
    
    with col2:
        st.metric("Average Daily Income", f"${daily_avg_income:.2f}")
        st.metric("Monthly Projection", f"${monthly_projected_income:.2f}")
    
    with col3:
        if months_of_expenses != float('inf'):
            st.metric("Emergency Fund", f"{months_of_expenses:.1f} months")
        else:
            st.metric("Emergency Fund", "∞ months")
        
        savings_rate = ((total_recent_income - total_recent_expenses) / total_recent_income * 100) if total_recent_income > 0 else 0
        st.metric("Savings Rate", f"{savings_rate:.1f}%")

# Main Application
def main():
    # Initialize database
    if not initialize_database():
        st.error("Failed to initialize database. Please check your connection settings.")
        return
    
    # Check authentication
    if not st.session_state.authenticated:
        login_page()
        return
    
    # Sidebar navigation
    st.sidebar.title("Personal Expense Tracker")
    st.sidebar.markdown("---")
    
    # Navigation menu
    pages = {
        "📊 Dashboard": dashboard_page,
        "➕ Add Transaction": add_transaction_page,
        "📋 View Transactions": view_transactions_page,
        "📈 Weekly Reports": weekly_reports_page,
        "🏦 Account Management": account_management_page,
        "💡 Financial Insights": financial_insights_page
    }
    
    selected_page = st.sidebar.radio("Navigation", list(pages.keys()))
    
    # Logout button
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()
    
    # Display selected page
    pages[selected_page]()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Personal Expense Tracker v1.0**")
    st.sidebar.markdown("Built with Streamlit")

if __name__ == "__main__":
    main()
