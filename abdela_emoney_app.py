# =====================================================================
# SYSTEM RUN MODULE: FULL-STACK ABDELA E-MONEY SIMULATION PLATFORM
# ARCHITECTURE: STREAMLIT WEB APP | STORAGE: SQLITE RELATIONAL DB
# ANALYTICS ENGINE: PLOTLY GRAPHICS | ALERT LAYER: TWILIO SMS SIMULATOR
# =====================================================================

import datetime
import random
import sqlite3
import pandas as pd
import plotly.express as px
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
# 💬 TWILIO STRUCTURAL INTERFACE: SMS ROUTING DISCLOSURE
# =====================================================================
def simulate_twilio_sms_dispatch(phone_route, text_payload):
    """Simulates programmatic telecom outreach metrics bypassing live API expense

    limits while capturing the structural logs securely.
    """
    st.toast(f"💬 SMS Sent via Twilio Gateway to {phone_route}!", icon="📱")
    with st.expander("📬 Outbound Twilio API SMS Console Log (Debug Network)"):
        st.code(
            f"""
        -------------------------------------------------------------
        TWILIO TELECOM INBOUND SMS GATEWAY ROUTER
        -------------------------------------------------------------
        SID: SM{random.randint(100000, 999999)}ab890cd12345e6789f
        To: {phone_route}
        From: +14155554321 (Twilio Shortcode Proxy)
        Status: Dispatched / Delivered
        Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
        Body: {text_payload}
        -------------------------------------------------------------
        """,
            language="text",
        )


# =====================================================================
# 📱 APP FRAMEWORK INTERFACE INTERACTIVES
# =====================================================================
st.image("https://icons8.com", width=80)

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

# Structural safeguard verification parameters added to auto-inject if out-of-bounds row missing
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

subscriber_name = subscriber_df["subscriber_name"].iloc[0]
wallet_balance = float(subscriber_df["wallet_balance"].iloc[0])
security_pin_stored = str(subscriber_df["security_pin"].iloc[0])

# =====================================================================
# 👤 PROFILE PANEL (SIDEBAR ENVIRONMENT MODULE)
# =====================================================================
with st.sidebar:
    st.header("👤 Platform Profile")
    st.image("https://icons8.com", width=60)
    st.subheader(subscriber_name)
    st.info("📞 Account Line: +251 900 223 344")

    # Render persistent balance metric parameter card
    st.metric(label="Abdela e-money Balance", value=f"{wallet_balance:,.2f} ETB")
    st.write("---")
    st.caption(
        "⚙️ **Engine Config:** Connected to `abdela_emoney_ledger.db` (SQLite3 engine active)."
    )

# =====================================================================
# 💳 WORKSPACE FUNCTIONAL CHANNELS (TAB LAYOUT MATRICES)
# =====================================================================
tab_deposit, tab_transfer, tab_airtime, tab_utility, tab_analytics, tab_db_view = st.tabs(
    [
        "📥 Cash Deposit (Agent)",
        "💸 Send Money",
        "📞 Buy Airtime",
        "🛍️ Utility Settlement",
        "📊 Plotly Analytics",
        "🗄️ Relational Database Ledger",
    ]
)

# NEW TAB MATRIX: SIMULATED AGENT CASH-IN DEPOSIT SYSTEM
with tab_deposit:
    st.subheader("🏦 Simulated Agent Cash-In Terminal")
    
    # NEW INSTRUCTIONAL MODULE: Explains how a user executes a mock deposit
    st.info("""
    📖 **How to Deposit (Simulation Guide):**
    1. Enter any mock **Agent Reference Code** in the box below.
    2. Input the fake **Deposit Value (ETB)** you would like to add to your test balance.
    3. Click the **Confirm Cash Deposit** button.
    4. Your sidebar balance will instantly refresh, your database statement ledger will update, and a simulated Twilio SMS alert receipt will display.
    """)
    
    with st.form("agent_deposit_form", clear_on_submit=True):
        agent_id = st.text_input("Authorized Agent Reference Code", value="AGNT-ADDIS-9912")
        deposit_amount = st.number_input("Deposit Value (ETB)", min_value=10.00, max_value=500000.00, step=100.00)
        
        submit_deposit = st.form_submit_button("Confirm Cash Deposit")
        
        if submit_deposit:
            cursor = conn.cursor()
            new_balance = wallet_balance + deposit_amount
            timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # Commit the newly added balance directly to your SQLite hard drive file
            cursor.execute(
                "UPDATE accounts SET wallet_balance = ? WHERE phone_number = '0900223344'",
                (new_balance,),
            )
            cursor.execute(
                """
                INSERT INTO audit_ledger (timestamp, txn_type, entity_target, amount, execution_status)
                VALUES (?, 'Deposit', ?, ?, 'Success')
                """,
                (timestamp_str, f"Agent Deposit ({agent_id})", deposit_amount),
            )
            conn.commit()
            
            # Fire an automatic Twilio receipt notification text
            sms_payload = f"Abdela e-money Alert: {deposit_amount:.2f} ETB deposited at Agent {agent_id} on {timestamp_str}. New balance: {new_balance:.2f} ETB."
            simulate_twilio_sms_dispatch("0900223344", sms_payload)
            
            st.success(f"Deposit Successful! {deposit_amount:,.2f} ETB has been added to your test wallet.")
            st.rerun()

# CHANNEL 1: PEER-TO-PEER TRANSFER MATRIX
with tab_transfer:
    st.subheader("Secure Peer-to-Peer Transfer Pipeline")
    with st.form("p2p_transfer_form", clear_on_submit=True):
        recipient_phone = st.text_input(
            "Recipient Phone Account String", placeholder="09xxxxxxxx"
        )
        transfer_value = st.number_input(
            "Transaction Volume Scale (ETB)", min_value=5.00, step=5.00
        )
        transaction_pin = st.text_input(
            "Security PIN (Default Setup: 1234)", type="password", max_chars=4
        )

        submit_transfer = st.form_submit_button("Execute Transfer Transaction")

        if submit_transfer:
            if not recipient_phone or len(recipient_phone) < 9:
                st.error(
                    "Operation Aborted: Target recipient network route format invalid."
                )
            elif transfer_value > wallet_balance:
                st.error(
                    "Operation Aborted: Inbound trade metrics exceed wallet balance thresholds."
                )
            elif transaction_pin != security_pin_stored:
                st.error("Authentication Error: Invalid terminal security PIN match.")
            else:
                cursor = conn.cursor()
                new_balance = wallet_balance - transfer_value
                timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

                cursor.execute(
                    "UPDATE accounts SET wallet_balance = ? WHERE phone_number = '0900223344'",
                    (new_balance,),
                )
                cursor.execute(
                    """
                    INSERT INTO audit_ledger (timestamp, txn_type, entity_target, amount, execution_status)
                    VALUES (?, 'Transfer', ?, ?, 'Success')
                    """,
                    (timestamp_str, f"P2P to {recipient_phone}", -transfer_value),
                )

                conn.commit()

                # Fire Automated Abdela e-money Alert System
                sms_text = f"Dear Client, {transfer_value:.2f} ETB transferred to {recipient_phone} on {timestamp_str} via Abdela e-money. New balance: {new_balance:.2f} ETB. Ref: TXN{random.randint(100000,999999)}."
                simulate_twilio_sms_dispatch(
                    "0900223344", sms_text
                )

                st.success(
                    f"Transaction Confirmed! Outbound balance cleanly routed to destination array."
                )
                st.sidebar.markdown(f"**Updated Balance:** {new_balance:,.2f} ETB")
                st.rerun()

# CHANNEL 2: TELECOM AIRTIME TOP-UP SYSTEM
with tab_airtime:
    st.subheader("Ethio Telecom Bundle Recharge Engine")
    with st.form("airtime_form", clear_on_submit=True):
        target_phone = st.text_input("Target Recharge Phone", value="0900223344")
        airtime_tier = st.selectbox(
            "Select Bundle Pack Plan",
            [
                "Voice/Data Micro Pack (100.00 ETB)",
                "Premium Monthly Unlimited Network Combo (500.00 ETB)",
            ],
        )

        submit_airtime = st.form_submit_button("Deploy Top-Up Package")

        if submit_airtime:
            cost = 100.00 if "100.00" in airtime_tier else 500.00
            if cost > wallet_balance:
                st.error(
                    "Aborted: Inbound package value exceeds remaining asset thresholds."
                )
            else:
                cursor = conn.cursor()
                new_balance = wallet_balance - cost
                timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

                cursor.execute(
                    "UPDATE accounts SET wallet_balance = ? WHERE phone_number = '0900223344'",
                    (new_balance,),
                )
                cursor.execute(
                    """
                    INSERT INTO audit_ledger (timestamp, txn_type, entity_target, amount, execution_status)
                    VALUES (?, 'Payment', ?, ?, 'Success')
                    """,
                    (timestamp_str, f"Airtime to {target_phone}", -cost),
                )
                conn.commit()

                # Twilio SMS Event Dispatch
                sms_text = f"Abdela e-money Alert: Airtime package '{airtime_tier}' successfully deployed onto line {target_phone}. Cost: {cost:.2f} ETB."
                simulate_twilio_sms_dispatch(target_phone, sms_text)

                st.success("Airtime profile updated on system logs successfully.")
                st.rerun()

# CHANNEL 3: UTILITY SETTLEMENT INTERACTION PORTAL
with tab_utility:
    st.subheader("Registered Commercial Outbound Bill Settlement Engine")
    with st.form("utility_form", clear_on_submit=True):
        merchant_name = st.selectbox(
            "Select Utility Service Matrix ID",
            [
                "Addis Ababa Water & Sewerage Authority (AAWSA)",
                "Sheger City Trade Office Operational Licensing Fee",
                "Anbessa City Bus Smart-Card Reload Vector",
            ],
        )
        bill_value = st.number_input(
            "Settlement Due Parameters (ETB)", min_value=1.00, step=10.00
        )

        submit_utility = st.form_submit_button("Make Payment via Abdela e-money")

        if submit_utility:
            if bill_value > wallet_balance:
                st.error(
                    "Aborted: Balance limits sit below requested transaction value inputs."
                )
            else:
                cursor = conn.cursor()
                new_balance = wallet_balance - bill_value
                timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

                cursor.execute(
                    "UPDATE accounts SET wallet_balance = ? WHERE phone_number = '0900223344'",
                    (new_balance,),
                )
                cursor.execute(
                    """
                    INSERT INTO audit_ledger (timestamp, txn_type, entity_target, amount, execution_status)
                    VALUES (?, 'Payment', ?, ?, 'Success')
                    """,
                    (timestamp_str, merchant_name, -bill_value),
                )
                conn.commit()

                # Twilio SMS Event Alert
                sms_text = f"Abdela e-money Payment Confirmed: Bill value of {bill_value:.2f} ETB processed for account reference toward {merchant_name}."
                simulate_twilio_sms_dispatch(
                    "0900223344", sms_text
                )

                st.success("Relational invoicing entries closed successfully.")
                st.sidebar.markdown(f"**Updated Balance:** {new_balance:,.2f} ETB")
                st.rerun()

# CHANNEL 4: INTERACTIVE PLOTLY DATA VISUALIZATION ENGINE
with tab_analytics:
    st.subheader("Real-Time Expenditures Portfolio Analytics Dashboard")

    # Query complete historical ledger lines dynamically into dataframes
    df_ledger = pd.read_sql_query(
        "SELECT * FROM audit_ledger WHERE amount < 0", conn
    )

    if not df_ledger.empty:
        # Normalize continuous amounts back to positive scales for relative profile tracking charts
        df_ledger["Absolute_Expenditure"] = df_ledger["amount"].abs()

        col_pie, col_bar = st.columns(2)

        with col_pie:
            st.write("**Expense Allocation Mix by Category Type**")
            fig_pie = px.pie(
                df_ledger,
                values="Absolute_Expenditure",
                names="txn_type",
                color_discrete_sequence=px.colors.sequential.RdBu,
                hole=0.4,
            )
            fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_bar:
            st.write("**Transaction Footprint Matrix Across Targeted Outlets**")
            fig_bar = px.bar(
                df_ledger,
                x="entity_target",
                y="Absolute_Expenditure",
                color="txn_type",
                labels={
                    "entity_target": "Provider / Target Profile",
                    "Absolute_Expenditure": "Volume Spent (ETB)",
                },
                template="seaborn",
            )
            fig_bar.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning(
            "Data Matrix Blank: Run transaction loops first to generate analytical chart tracks."
        )

# CHANNEL 5: LIVE RAW RELATIONAL DATABASE ACCESS VIEW (SQLITE AUDIT LEDGER)
with tab_db_view:
    st.subheader("Live Relational Database Ledger Logs")
    
    # Render the static dataframe log profile
    df_global_audit = pd.read_sql_query(
        "SELECT * FROM audit_ledger ORDER BY txn_id DESC", conn
    )
    st.dataframe(df_global_audit, use_container_width=True, hide_index=True)
    
    # Live Statement Downloader Button Module
    st.write("---")
    st.write("📂 **Account Statement Export Center**")
    csv_data_buffer = df_global_audit.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Official Account Statement (.CSV)",
        data=csv_data_buffer,
        file_name="Abdela_Emoney_Statement_20261005.csv",
        mime="text/csv",
    )
    st.caption(
        f"Displaying {len(df_global_audit)} active logs rows fetched directly from backend relational database schemas."
    )

# Explicitly close relational network lines at the end of runtime compilation loop
conn.close()
