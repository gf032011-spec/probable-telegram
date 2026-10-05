# =====================================================================
# SYSTEM RUN MODULE: FULL-STACK ABDELA E-MONEY SIMULATION PLATFORM
# ARCHITECTURE: STREAMLIT WEB APP | STORAGE: SQLITE RELATIONAL DB
# ANALYTICS ENGINE: PLOTLY GRAPHICS | ALERT LAYER: LIVE SMARTPHONE SMS
# =====================================================================

import datetime
import random
import sqlite3
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# =====================================================================
# 🗄️ DATABASE ENGINE MAPPING & SCHEMA CONFIGURATIONS
# =====================================================================
def get_db_connection():
    """Establishes thread-safe relational database mapping lines."""
    conn = sqlite3.connect("abdela_emoney_ledger.db", check_same_thread=False)
    return conn


def init_db():
    """Initializes the operational ledger database table schemas."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Accounts Database Layer (Simulating Core Subscriber Vault)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            phone_number TEXT PRIMARY KEY,
            subscriber_name TEXT,
            wallet_balance REAL,
            security_pin TEXT
        )
        """
    )

    # 2. Transaction Audit Ledger (Enforcing Double-Entry Integrity logs)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_ledger (
            txn_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            txn_type TEXT,
            entity_target TEXT,
            amount REAL,
            execution_status TEXT
        )
        """
    )

    # Seed historical baseline datasets if the framework is running fresh
    cursor.execute("SELECT COUNT(*) FROM accounts")
    if cursor.fetchone() == 0:
        cursor.execute(
            """
            INSERT INTO accounts (phone_number, subscriber_name, wallet_balance, security_pin) 
            VALUES ('0900223344', 'Abdela Ayalew Mekonnen', 5450.00, '1234')
            """
        )

        baseline_logs = [
            ("2026-10-01 09:15", "Deposit", "CBE Agent Branch 04", 5000.00, "Success"),
            (
                "2026-10-02 14:22",
                "Payment",
                "Ethio Telecom Airtime",
                -200.00,
                "Success",
            ),
            (
                "2026-10-04 18:45",
                "Transfer",
                "Abebe Kebede (0911223344)",
                -2300.00,
                "Success",
            ),
            (
                "2026-10-05 08:30",
                "Payment",
                "Ethiopian Electric Utility",
                -1050.00,
                "Success",
            ),
        ]
        cursor.executemany(
            """
            INSERT INTO audit_ledger (timestamp, txn_type, entity_target, amount, execution_status)
            VALUES (?, ?, ?, ?, ?)
            """,
            baseline_logs,
        )

    conn.commit()
    conn.close()


# Initialize data directories
init_db()


# =====================================================================
# 💬 REAL TELEGRAM OUTREACH MATRIX: LIVE REAL SMARTPHONE SMS
# =====================================================================
def fire_real_smartphone_alert(message_body):
    """Routes application event data text payloads instantly to the user's

    live physical smartphone device using official Telegram API gateways.
    """
    # 📝 ENTER YOUR TELEGRAM CREDENTIALS HERE TO START RECEIVING REAL TEXTS
    BOT_TOKEN = st.session_state.get("tg_bot_token", "")
    CHAT_ID = st.session_state.get("tg_chat_id", "")
    
    if BOT_TOKEN and CHAT_ID:
        try:
            telegram_url = f"https://telegram.org{BOT_TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": f"📱 [Abdela e-money]\n{message_body}", "parse_mode": "Markdown"}
            requests.post(telegram_url, json=payload, timeout=5)
        except Exception:
            pass


# =====================================================================
# 📱 APP FRAMEWORK INTERFACE INTERACTIVES
# =====================================================================
st.image("https://icons8.com", width=90)

st.title("📱 Abdela e-money FinTech Core Platform")
st.caption(
    "System Operational Matrix: Integrated Relational Storage + Automated Alerts Layer + Expenditure Analytics Dashboard"
)
st.write("---")

# Query subscriber state values dynamically from the SQLite local instance
conn = get_db_connection()
subscriber_df = pd.read_sql_query(
    "SELECT * FROM accounts WHERE phone_number='0900223344'", conn
)

if subscriber_df.empty:
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO accounts (phone_number, subscriber_name, wallet_balance, security_pin) 
        VALUES ('0900223344', 'Abdela Ayalew Mekonnen', 5450.00, '1234')
        """
    )
    conn.commit()
    subscriber_df = pd.read_sql_query(
        "SELECT * FROM accounts WHERE phone_number='0900223344'", conn
    )

subscriber_name = subscriber_df["subscriber_name"].iloc
wallet_balance = float(subscriber_df["wallet_balance"].iloc)
security_pin_stored = str(subscriber_df["security_pin"].iloc)

# =====================================================================
# 👤 PROFILE PANEL (SIDEBAR ENVIRONMENT MODULE)
# =====================================================================
with st.sidebar:
    st.header("👤 Platform Profile")
    st.image("https://icons8.com", width=65)
    st.subheader(subscriber_name)
    st.info("📞 Account Line: +251 900 223 344")
    st.metric(label="Abdela e-money Balance", value=f"{wallet_balance:,.2f} ETB")
    
    st.write("---")
    st.write("⚙️ **Live Phone SMS Setup**")
    st.caption("Paste your free Telegram configuration parameters here to start seeing real, instant transaction text alerts on your physical phone device screen!")
    st.text_input("Enter Telegram Bot Token", key="tg_bot_token", type="password", placeholder="123456789:ABC...")
    st.text_input("Enter Telegram Chat ID", key="tg_chat_id", placeholder="987654321")
    
    st.write("---")
    st.caption(
        "⚙️ **Engine Config:** Connected to `abdela_emoney_ledger.db` (SQLite3 engine active)."
    )

# =====================================================================
# 💳 WORKSPACE FUNCTIONAL CHANNELS (TAB LAYOUT MATRICES)
# =====================================================================
tabs = st.tabs(
    [
        "👥 Customer Registration",
        "📥 Cash Deposit",
        "💸 Send Money",
        "📞 Buy Airtime",
        "🛍️ Utility Settlement",
        "📈 Savings Estimator",
        "🔒 Change PIN",
        "💱 Currency Exchange",
        "📄 Invoice Builder",
        "📊 Plotly Analytics",
        "🗄️ Relational Database",
    ]
)
tab_register, tab_deposit, tab_transfer, tab_airtime, tab_utility, tab_interest, tab_pin, tab_exchange, tab_invoice, tab_analytics, tab_db_view = tabs

# NEW CHANNEL: DYNAMIC CUSTOMER REGISTRATION ENGAGEMENT INTERFACE
with tab_register:
    st.subheader("👥 Core Subscriber Registration Portal")
    st.write("Provision new accounts vectors cleanly inside the master relational ledger system tables maps.")
    
    with st.form("customer_registration_form", clear_on_submit=True):
        reg_name = st.text_input("Full Legal Subscriber Name", placeholder="Abebe Kebede")
        reg_phone = st.text_input("Mobile Account String (Phone Number)", placeholder="09xxxxxxxx")
        reg_pin = st.text_input("Set 4-Digit Security Authorization PIN", type="password", max_chars=4)
        reg_deposit = st.number_input("Opening Capital Baseline Deposit (ETB)", min_value=0.00, value=500.00, step=50.00)
        
        submit_registration = st.form_submit_button("Register New Subscriber")
        
        if submit_registration:
            if not reg_name or len(reg_phone) < 9 or len(reg_pin) != 4:
                st.error("Registration Aborted: Empty data inputs or invalid parameter scale metrics provided.")
            else:
                try:
                    cursor = conn.cursor()
                    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    
                    # Write the brand new customer account into your database files records logs
                    cursor.execute("INSERT INTO accounts (phone_number, subscriber_name, wallet_balance, security_pin) VALUES (?, ?, ?, ?)", (reg_phone, reg_name, reg_deposit, reg_pin))
                    cursor.execute("INSERT INTO audit_ledger (timestamp, txn_type, entity_target, amount, execution_status) VALUES (?, 'Registration', ?, ?, 'Success')", (timestamp_str, f"New User: {reg_name}", reg_deposit))
                    conn.commit()
                    
                    # FIRE REAL TELEGRAM PHONE OUTREACH TEXT
                    real_text = f"New Customer Registration Confirmed!\nName: {reg_name}\nPhone: +251 {reg_phone[1:]}\nOpening Balance: {reg_deposit:.2f} ETB\nTimestamp: {timestamp_str}."
                    fire_real_smartphone_alert(real_text)
                    
                    st.success(f"Success! Account for '{reg_name}' provisioned cleanly inside local ledger files.")
                except sqlite3.IntegrityError:
                    st.error("Exception: A subscriber line matching that phone string parameters is already logged.")

# CHANNEL 0: SIMULATED AGENT CASH-IN DEPOSIT SYSTEM
with tab_deposit:
    st.subheader("🏦 Simulated Agent Cash-In Terminal")
    st.info("""
    📖 **How to Deposit (Simulation Guide):**
    1. Enter any mock **Agent Reference Code** in the box below.
    2. Input the fake **Deposit Value (ETB)** you would like to add to your test balance.
    3. Click the **Confirm Cash Deposit** button.
    """)
    
    with st.form("agent_deposit_form", clear_on_submit=True):
        agent_id = st.text_input("Authorized Agent Reference Code", value="AGNT-ADDIS-9912")
        deposit_amount = st.number_input("Deposit Value (ETB)", min_value=10.00, max_value=500000.00, step=100.00)
        
        submit_deposit = st.form_submit_button("Confirm Cash Deposit")
        
        if submit_deposit:
            cursor = conn.cursor()
            new_balance = wallet_balance + deposit_amount
            timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            
            cursor.execute("UPDATE accounts SET wallet_balance = ? WHERE phone_number = '0900223344'", (new_balance,))
            cursor.execute("INSERT INTO audit_ledger (timestamp, txn_type, entity_target, amount, execution_status) VALUES (?, 'Deposit', ?, ?, 'Success')", (timestamp_str, f"Agent Deposit ({agent_id})", deposit_amount))
            conn.commit()
            
            # FIRE REAL TELEGRAM PHONE OUTREACH TEXT
            real_text = f"Cash Deposit Confirmed!\nAgent ID: {agent_id}\nAmount: +{deposit_amount:,.2f} ETB\nNew Wallet Balance: {new_balance:,.2f} ETB."
            fire_real_smartphone_alert(real_text)
            
            st.success(f"Deposit Successful! {deposit_amount:,.2f} ETB has been added to your test wallet.")
            st.rerun()

# CHANNEL 1: PEER-TO-PEER TRANSFER MATRIX
with tab_transfer:
    st.subheader("Secure Peer-to-Peer Transfer Pipeline")
    with st.form("p2p_transfer_form", clear_on_submit=True):
        recipient_phone = st.text_input("Recipient Phone Account String", placeholder="09xxxxxxxx")
        transfer_value = st.number_input("Transaction Volume Scale (ETB)", min_value=5.00, step=5.00)
        transaction_pin = st.text_input("Security PIN", type="password", max_chars=4)

        submit_transfer = st.form_submit_button("Execute Transfer Transaction")

        if submit_transfer:
            if not recipient_phone or len(recipient_phone) < 9:
                st.error("Operation Aborted: Target recipient network route format invalid.")
            elif transfer_value > wallet_balance:
                st.error("Operation Aborted: Inbound trade metrics exceed wallet balance thresholds.")
            elif transaction_pin != security_pin_stored:
                st.error("Authentication Error: Invalid terminal security PIN match.")
            else:
                cursor = conn.cursor()
                new_balance = wallet_balance - transfer_value
                timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

                cursor.execute("UPDATE accounts SET wallet_balance = ? WHERE phone_number = '0900223344'", (new_balance,))
                cursor.execute("INSERT INTO audit_ledger (timestamp, txn_type, entity_target, amount, execution_status) VALUES (?, 'Transfer', ?, ?, 'Success')", (timestamp_str, f"P2P to {recipient_phone}", -transfer_value))
                conn.commit()

                # FIRE REAL TELEGRAM PHONE OUTREACH TEXT
                real_text = f"Outbound Transfer Sent!\nRecipient Line: {recipient_phone}\nVolume Sent: -{transfer_value:.2f} ETB\nRemaining Asset Threshold: {new_balance:.2f} ETB."
                fire_real_smartphone_alert(real_text)

                st.success(f"Transaction Confirmed! Outbound balance cleanly routed.")
                st.rerun()

# CHANNEL 2: TELECOM AIRTIME TOP-UP SYSTEM
with tab_airtime:
    st.subheader("Ethio Telecom Bundle Recharge Engine")
    with st.form("airtime_form", clear_on_submit=True):
        target_phone = st.text_input("Target Recharge Phone", value="0900223344")
        airtime_tier = st.selectbox("Select Bundle Pack Plan", ["Voice/Data Micro Pack (100.00 ETB)", "Premium Monthly Unlimited Network Combo (500.00 ETB)"])

        submit_airtime = st.form_submit_button("Deploy Top-Up Package")

        if submit_airtime:
            cost = 100.00 if "100.00" in airtime_tier else 500.00
            if cost > wallet_balance:
                st.error("Aborted: Inbound package value exceeds remaining asset thresholds.")
            else:
                cursor = conn.cursor()
                new_balance = wallet_balance - cost
                timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

                cursor.execute("UPDATE accounts SET wallet_balance = ? WHERE phone_number = '0900223344'", (new_balance,))
                cursor.execute("INSERT INTO audit_ledger (timestamp, txn_type, entity_target, amount, execution_status) VALUES (?, 'Payment', ?, ?, 'Success')", (timestamp_str, f"Airtime to {target_phone}", -cost))
                conn.commit()

                # FIRE REAL TELEGRAM PHONE OUTREACH TEXT
                real_text = f"Telecom Airtime Deployment Complete!\nTarget Line: {target_phone}\nPackage Pack Selection: {airtime_tier}\nCost: {cost:.2f} ETB."
                fire_real_smartphone_alert(real_text)

                st.success("Airtime profile updated on system logs successfully.")
                st.rerun()

# CHANNEL 3: UTILITY SETTLEMENT INTERACTION PORTAL
with tab_utility:
    st.subheader("Registered Commercial Outbound Bill Settlement Engine")
    with st.form("utility_form", clear_on_submit=True):
        merchant_name = st.selectbox("Select Utility Service Matrix ID", ["Addis Ababa Water & Sewerage Authority (AAWSA)", "Sheger City Trade Office Operational Licensing Fee", "Anbessa City Bus Smart-Card Reload Vector"])
        bill_value = st.number_input("Settlement Due Parameters (ETB)", min_value=1.00, step=10.00)

        submit_utility = st.form_submit_button("Make Payment via Abdela e-money")

        if submit_utility:
            if bill_value > wallet_balance:
                st.error("Aborted: Balance limits sit below requested transaction value inputs.")
            else:
                cursor = conn.cursor()
                new_balance = wallet_balance - bill_value
                timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

                cursor.execute("UPDATE accounts SET wallet_balance = ? WHERE phone_number = '0900223344'", (new_balance,))
                cursor.execute("INSERT INTO audit_ledger (timestamp, txn_type, entity_target, amount, execution_status) VALUES (?, 'Payment', ?, ?, 'Success')", (timestamp_str, merchant_name, -bill_value))
                conn.commit()

                # FIRE REAL TELEGRAM PHONE OUTREACH TEXT
                real_text = f"Commercial Bill Settlement Processed!\nMerchant: {merchant_name}\nSettlement Invoiced: -{bill_value:.2f} ETB\nRemaining Wallet Account Balance: {new_balance:.2f} ETB."
                fire_real_smartphone_alert(real_text)

                st.success("Relational invoicing entries closed successfully.")
                st.rerun()

# CHANNEL 4: MOCK SAVINGS INTEREST ESTIMATOR CALCULATOR
with tab_interest:
    st.subheader("📈 Sandbox Savings Growth Forecasting Engine")
    st.write("Predict your simulated compound interest returns based on your active play balance parameters.")
    
    col1, col2 = st.columns(2)
    with col1:
        annual_yield = st.slider("Simulated Annual Interest Rate (Yield %)", min_value=4.0, max_value=15.0, value=7.5, step=0.5)
        forecast_years = st.slider("Investment Horizon Timeline (Years)", min_value=1, max_value=10, value=5)
    
    years_list = list(range(0, forecast_years + 1))
    balance_projections = [wallet_balance * ((1 + (annual_yield / 100)) ** year) for year in years_list]
    
    df_projection = pd.DataFrame({"Timeline (Years)": years_list, "Projected Value (ETB)": balance_projections})
    
    with col2:
        final_yield = balance_projections[-1]
        interest_earned = final_yield - wallet_balance
        st.metric(label="Estimated Value (Horizon End)", value=f"{final_yield:,.2f} ETB", delta=f"+{interest_earned:,.2f} ETB Earned")
    
    fig_line = px.line(df_projection, x="Timeline (Years)", y="Projected Value (ETB)", title="Compounding Asset Balance Over Time", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

# CHANNEL 5: DYNAMIC RELATIONAL SECURITY PIN RESET VAULT
with tab_pin:
    st.subheader("🔒 Dynamic Credentials PIN Crypt Vault")
    st.write("Modify your security terminal passcode credentials cleanly within the backend relational database.")
    
    with st.form("pin_modification_form", clear_on_submit=True):
        current_pin_input = st.text_input("Enter Current 4-Digit Security PIN", type="password", max_chars=4)
        new_pin_input = st.text_input("Enter New 4-Digit Passcode", type="password", max_chars=4)
        confirm_pin_input = st.text_input("Confirm New Passcode Entry", type="password", max_chars=4)
        
        submit_pin_change = st.form_submit_button("Commit Security Parameter Changes")
        
        if submit_pin_change:
            if current_pin_input != security_pin_stored:
                st.error("Authentication Exception: Active password token matrix mismatch.")
            elif len(new_pin_input) != 4 or not new_pin_input.isdigit():
                st.error("Validation Exception: Passcode format constraint requires exactly 4 numerical tokens.")
            elif new_pin_input != confirm_pin_input:
                st.error("Mismatch Error: Confirmation token string maps away from parent vector entry.")
            else:
                cursor = conn.cursor()
                cursor.execute("UPDATE accounts SET security_pin = ? WHERE phone_number = '0900223344'", (new_pin_input,))
                conn.commit()
                
                # FIRE REAL TELEGRAM PHONE OUTREACH TEXT
                real_text = "Security Warning: Your 4-digit transaction verification authorization passcode credentials were modified inside the core database files successfully."
                fire_real_smartphone_alert(real_text)
                
                st.success("Security configuration profile modified cleanly inside local database matrices.")
                st.rerun()

# CHANNEL 6: SIMULATED FOREX CURRENCY EXCHANGE CONVERTER
with tab_exchange:
    st.subheader("💱 Real-Time Foreign Exchange Valuation Engine")
    
    usd_index_rate = 124.50
    eur_index_rate = 135.25
    
    st.write("📈 **Active Simulated Index Reference Ratios:**")
    exc_col1, exc_col2 = st.columns(2)
    exc_col1.metric("🇺🇸 USD / ETB Index Pair", f"{usd_index_rate:.2f} ETB")
    exc_col2.metric("🇪🇺 EUR / ETB Index Pair", f"{eur_index_rate:.2f} ETB")
    st.write("---")
    
    st.write("🌎 **Your Net Wallet Asset Valuation Matrix:**")
    converted_usd = wallet_balance / usd_index_rate
    converted_eur = wallet_balance / eur_index_rate
    
    res_col1, res_col2 = st.columns(2)
    res_col1.metric("Net Valuation Scale (US Dollars)", f"\${converted_usd:,.2f} USD")
    res_col2.metric("Net Valuation Scale (Euros)", f"€{converted_eur:,.2f} EUR")

# CHANNEL 7: PRINTABLE COMMERCIAL INVOICE GENERATOR ENGINE
with tab_invoice:
    st.subheader("📄 Automated Outbound Commercial Invoice Builder")
    inv_col1, inv_col2 = st.columns()
    
    with inv_col1:
        st.write("**Invoicing Parameter Configurations:**")
        client_org = st.text_input("Billed Customer / Corporate Entity Name", value="Ethio-Somali Logistics Corp")
        invoice_item = st.text_input("Rendered Service Line Description", value="Enterprise FinTech System Integration Fee")
        item_cost = st.number_input("Service Settlement Value (ETB)", min_value=10.00, value=25000.00, step=500.00)
        invoice_notes = st.text_area("Invoicing Memo Terms / Notes", value="Net 30 settlement parameters applied. Remit transfer via core Abdela e-money network rails.")
    
    with inv_col2:
        st.write("**📄 Live Generated Order Receipt Preview:**")
        st.markdown(f"""
        <div style="border: 2px dashed #9E9E9E; padding: 20px; background-color: #FAFAFA; border-radius: 8px; color: #212121;">
            <h3 style="text-align: center; color: #1E88E5; margin-bottom: 5px;">ABDELA E-MONEY RECEIPT ORDER</h3>
            <p style="text-align: center; font-size: 11px; color: #757575; margin-top: 0px;">Reference ID: INV-{random.randint(10000, 99999)}</p>
            <hr style="border-top: 1px solid #BDBDBD;">
            <p><strong>Billing Date:</strong> {datetime.datetime.now().strftime('%B %d, %Y')}</p>
            <p><strong>Client Target:</strong> {client_org}</p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                <tr style="border-bottom: 2px solid #757575;">
                    <th style="text-align: left;">Line Description</th>
                    <th style="text-align: right;">Total Amount</th>
                </tr>
                <tr style="border-bottom: 1px solid #E0E0E0;">
                    <td style="padding: 10px 0px; font-size: 13px;">{invoice_item}</td>
                    <td style="text-align: right; padding: 10px 0px;">{item_cost:,.2f} ETB</td>
                </tr>
            </table>
            <h4 style="text-align: right; margin-top: 20px; color: #2E7D32;">Total Balance Due: {item_cost:,.2f} ETB</h4>
            <hr style="border-top: 1px dashed #BDBDBD; margin-top: 25px;">
            <p style="font-size: 11px; color: #616161; line-height: 1.4;"><strong>Memo Notes:</strong> {invoice_notes}</p>
        </div>
        """, unsafe_allow_html=True)
        st.caption("💡 **Tip:** Press **`Ctrl + P`** on your keyboard to instantly print this receipt box directly to your hardware printer or save it as a digital PDF file on your computer!")

# CHANNEL 8: INTERACTIVE PLOTLY DATA VISUALIZATION ENGINE
with tab_analytics:
    st.subheader("Real-Time Expenditures Portfolio Analytics Dashboard")
    df_ledger = pd.read_sql_query("SELECT * FROM audit_ledger WHERE amount < 0", conn)

    if not df_ledger.empty:
        df_ledger["Absolute_Expenditure"] = df_ledger["amount"].abs()
        col_pie, col_bar = st.columns(2)

        with col_pie:
            st.write("**Expense Allocation Mix by Category Type**")
            fig_pie = px.pie(df_ledger, values="Absolute_Expenditure", names="txn_type", color_discrete_sequence=px.colors.sequential.RdBu, hole=0.4)
            fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_bar:
            st.write("**Transaction Footprint Matrix Across Targeted Outlets**")
            fig_bar = px.bar(df_ledger, x="entity_target", y="Absolute_Expenditure", color="txn_type", labels={"entity_target": "Provider / Target Profile", "Absolute_Expenditure": "Volume Spent (ETB)"}, template="seaborn")
            fig_bar.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("Data Matrix Blank: Run transaction loops first to generate analytical chart tracks.")

# CHANNEL 9: LIVE RAW RELATIONAL DATABASE ACCESS VIEW (SQLITE AUDIT LEDGER)
with tab_db_view:
    st.subheader("Live Relational Database Ledger Logs")
    df_global_audit = pd.read_sql_query("SELECT * FROM audit_ledger ORDER BY txn_id DESC", conn)
    st.dataframe(df_global_audit, use_container_width=True, hide_index=True)
    
    st.write("---")
    st.write("📂 **Account Statement Export Center**")
    csv_data_buffer = df_global_audit.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Official Account Statement (.CSV)",
        data=csv_data_buffer,
        file_name="Abdela_Emoney_Statement_20261005.csv",
        mime="text/csv",
    )
    st.caption(f"Displaying {len(df_global_audit)} active logs rows fetched directly from backend relational database schemas.")

conn.close()
