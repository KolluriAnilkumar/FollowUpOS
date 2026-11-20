
import streamlit as st
import pandas as pd
import sqlite3

# Dashboard configuration
st.set_page_config(
    page_title="FollowUpOS Dashboard",
    page_icon="📊",
    layout="wide"
)
# SQLite Database Setup

def create_database():

    conn = sqlite3.connect("followupos.db")

    cursor = conn.cursor()

    # Reminder Activity Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id TEXT,
            action TEXT,
            message TEXT,
            recorded_at TEXT
        )
    """)

    # Customer Outcome Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS outcome_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id TEXT,
            outcome TEXT,
            notes TEXT,
            promised_payment_date TEXT,
            recorded_at TEXT
        )
    """)
    # Add actor_id to existing tables if it is missing
    for table_name in ["activity_log", "outcome_log"]:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]

        if "actor_id" not in columns:
            cursor.execute(
                f"""
                ALTER TABLE {table_name}
                ADD COLUMN actor_id TEXT NOT NULL DEFAULT 'Demo Owner'
                """
            )

    conn.commit()
    conn.close()


create_database()

# Owner Login
st.sidebar.title("Owner Login")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:

    st.title("🔐 FollowUpOS Owner Login")
    st.write("Please enter your owner password to access the dashboard.")

    owner_password = st.text_input(
        "Enter Owner Password",
        type="password"
    )

    if st.button("Login"):
        if owner_password == "***REMOVED***":
            st.session_state.authenticated = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")

    st.stop()

else:
    st.sidebar.success("Logged in as Demo Owner")

    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# Delete FollowUpOS Demo Records
def delete_all_demo_records():

    conn = sqlite3.connect("followupos.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM activity_log")
    cursor.execute("DELETE FROM outcome_log")

    conn.commit()
    conn.close()
# Professional FollowUpOS Styling

st.markdown("""
<style>
.stApp {
    background-color: #F5F7FB;
}

h1 {
    color: #17365D;
    font-weight: 700;
    font-size: 2.2rem;
    line-height: 1.2;
}

h2, h3 {
    color: #24476B;
    font-weight: 600;
}

[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #DCE3EC;
    padding: 18px;
    border-radius: 10px;
}

[data-testid="stMetricLabel"] {
    color: #526579;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: #17365D;
    font-weight: 700;
}

.stButton button {
    background-color: #17365D;
    color: white;
    border-radius: 7px;
    border: none;
}

hr {
    border-color: #DCE3EC;
}
</style>
""", unsafe_allow_html=True)

# Dashboard title
st.title("FollowUpOS - Sales Follow-up Dashboard")
st.subheader("Deccan Wholesale Mart | Hyderabad")

st.write(
    "An AI-assisted Sales Follow-up and Receivables "
    "Workflow Platform."
)

st.divider()




# Data upload section
st.header("Upload Business Dataset")

uploaded_file = st.file_uploader(
    "Upload your CSV or Excel dataset",
    type=["xlsx", "csv"]
)

# Download Import Template
template_columns = [
    "customer_name",
    "invoice_id",
    "invoice_date",
    "due_date",
    "invoice_amount",
    "amount_paid",
    "payment_status",
    "last_contact_at",
    "next_follow_up_at"
]

template_df = pd.DataFrame(columns=template_columns)

st.download_button(
    label="Download Import Template",
    data=template_df.to_csv(index=False),
    file_name="FollowUpOS_Import_Template.csv",
    mime="text/csv"
)
if uploaded_file is not None:

    # Read uploaded file based on its format
    if uploaded_file.name.lower().endswith(".xlsx"):

        excel_file = pd.ExcelFile(uploaded_file)

        if "Raw_Import" in excel_file.sheet_names:
            sheet_to_read = "Raw_Import"

        elif len(excel_file.sheet_names) > 0:
            sheet_to_read = excel_file.sheet_names[0]
            st.info(f"Reading worksheet: {sheet_to_read}")

        else:
            st.error("The uploaded Excel file contains no worksheets.")
            st.stop()

        df = pd.read_excel(
            excel_file,
            sheet_name=sheet_to_read
        )

    elif uploaded_file.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    st.success("Dataset uploaded successfully!")



    # Column Mapping
    st.subheader("Map Your Dataset Columns")
    st.write("Match your uploaded columns with the required FollowUpOS fields.")

    required_fields = [
        "invoice_id",
        "customer_name",
        "invoice_date",
        "due_date",
        "invoice_amount",
        "amount_paid"
    ]

    column_mapping = {}

    for field in required_fields:

        options = ["-- Not mapped --"] + list(df.columns)

        default_index = 0
        if field in df.columns:
            default_index = options.index(field)

        selected_column = st.selectbox(
            f"Select the column for {field}",
            options,
            index=default_index,
            key=f"mapping_{field}"
        )

        if selected_column != "-- Not mapped --":
            column_mapping[selected_column] = field

    if (
        len(column_mapping) == len(required_fields)
        and len(set(column_mapping.keys())) == len(required_fields)
    ):
        df = df.rename(columns=column_mapping)
        st.success("Column mapping completed successfully!")

    else:
        st.warning("Please map all six required fields before processing.")

        missing_fields = [
            field for field in required_fields
            if field not in column_mapping.values()
        ]

        if missing_fields:
            st.write("Missing required fields:", ", ".join(missing_fields))

        st.stop()






    # Data Validation and Data Preparation

    # Data Validation

    # Keep the original uploaded data
    df = df.copy()

    # Convert financial columns into numbers
    df["invoice_amount"] = pd.to_numeric(
        df["invoice_amount"],
        errors="coerce"
    )

    df["amount_paid"] = pd.to_numeric(
        df["amount_paid"],
        errors="coerce"
    )

    # Convert date columns into dates
    df["invoice_date"] = pd.to_datetime(
        df["invoice_date"],
        errors="coerce"
    )

    df["due_date"] = pd.to_datetime(
        df["due_date"],
        errors="coerce"
    )

        # Data Profiling
    st.header("Data Profiling")

    st.write(
        "Overview of the uploaded dataset, including "
        "record counts, missing values, unique values and data types."
    )

    # Dataset dimensions
    profile_col1, profile_col2 = st.columns(2)

    profile_col1.metric(
        "Total Rows",
        df.shape[0]
    )

    profile_col2.metric(
        "Total Columns",
        df.shape[1]
    )

    # Column-level profiling
    profiling_summary = pd.DataFrame({
        "Column Name": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Missing Values": df.isna().sum().values,
        "Unique Values": df.nunique().values
    })

    st.subheader("Column Profiling Summary")

    st.dataframe(
        profiling_summary,
        use_container_width=True
    )

    # Numerical statistics
    st.subheader("Numerical Data Statistics")

    st.dataframe(
        df.describe(),
        use_container_width=True
    )
        # Data Cleaning - Remove Extra Spaces
    st.header("Data Cleaning")

    text_columns = df.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:
        df[column] = df[column].apply(
            lambda value: value.strip()
            if isinstance(value, str)
            else value
        )

    st.success("Extra spaces removed from text columns.")

    # Calculate outstanding amount
    df["outstanding_amount"] = (
        df["invoice_amount"] - df["amount_paid"]
    )

    # Check each invoice for validation errors
    validation_errors = []

    for index, row in df.iterrows():

        errors = []

        required_fields = [
            "invoice_id",
            "customer_name",
            "invoice_date",
            "due_date",
            "invoice_amount",
            "amount_paid"
        ]

        for field in required_fields:
            if pd.isna(row[field]) or str(row[field]).strip() == "":
                errors.append(f"Missing {field}")

        if pd.isna(row["invoice_date"]):
            if "Missing invoice_date" not in errors:
                errors.append("Invalid invoice date")

        if pd.isna(row["due_date"]):
            if "Missing due_date" not in errors:
                errors.append("Invalid or missing due date")

        if pd.notna(row["invoice_amount"]):
            if row["invoice_amount"] <= 0:
                errors.append("Invoice amount must be greater than zero")

        if pd.notna(row["amount_paid"]):
            if row["amount_paid"] < 0:
                errors.append("Amount paid cannot be negative")

        if pd.notna(row["outstanding_amount"]):
            if row["outstanding_amount"] < 0:
                errors.append("Amount paid exceeds invoice amount")

        validation_errors.append("; ".join(errors))



       # Store validation errors
    df["validation_errors"] = validation_errors

    # Identify duplicate invoice IDs
    duplicate_mask = df.duplicated(
        subset=["invoice_id"],
        keep=False
    )

    df.loc[duplicate_mask, "validation_errors"] = (
        df.loc[duplicate_mask, "validation_errors"].apply(
            lambda error: (
                error + "; Duplicate invoice ID"
                if error else "Duplicate invoice ID"
            )
        )
    )
        # Display Duplicate Invoice Records
    st.subheader("Duplicate Invoice Records")

    duplicate_records = df[duplicate_mask].copy()

    if not duplicate_records.empty:
        st.warning(
            f"Found {len(duplicate_records)} duplicate invoice records."
        )

        st.dataframe(
            duplicate_records,
            use_container_width=True
        )
    else:
        st.success("No duplicate invoice records found.")

        # Separate valid and invalid records
    invalid_data = df[
        df["validation_errors"] != ""
    ].copy()

    # Remove duplicate invoices for financial analysis
    clean_data = df.drop_duplicates(
        subset=["invoice_id"],
        keep="first"
    ).copy()

    # Keep only valid financial records
    finance_data = clean_data[
        (clean_data["validation_errors"] == "") &
        (clean_data["amount_paid"] <= clean_data["invoice_amount"]) &
        (clean_data["invoice_amount"].notna()) &
        (clean_data["amount_paid"].notna())
    ].copy()

    # Import Review Summary
    st.header("Import Review Summary")

    total_records = len(df)
    valid_records = len(finance_data)
    invalid_records = len(invalid_data)

    duplicate_records = int(
        df["invoice_id"].duplicated(keep=False).sum()
    )

    review_cols = st.columns(5)

    review_cols[0].metric(
        "Total Uploaded",
        total_records
    )

    review_cols[1].metric(
        "Valid Records",
        valid_records
    )

    review_cols[2].metric(
        "Invalid Records",
        invalid_records
    )

    review_cols[3].metric(
        "Duplicate Records",
        duplicate_records
    )

    review_cols[4].metric(
        "Ready for Processing",
        valid_records
    )

    st.header("Data Validation Report")

    st.write(
        "The following records contain missing or incorrect data "
        "and require manual correction."
    )

    st.metric(
        "Invalid Records",
        len(invalid_data)
    )
    st.metric(
    "Total Validation Issues",
    invalid_data["validation_errors"].str.count(";").add(1).sum()
)

    if not invalid_data.empty:

        st.dataframe(
            invalid_data[
                [
                    "invoice_id",
                    "customer_name",
                    "invoice_date",
                    "due_date",
                    "invoice_amount",
                    "amount_paid",
                    "validation_errors"
                ]
            ],
            use_container_width=True
        )

    else:
        st.success("All uploaded records passed validation.")


    if not invalid_data.empty:

        invalid_csv = invalid_data.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download Invalid Records",
            data=invalid_csv,
            file_name="FollowUpOS_Invalid_Records.csv",
            mime="text/csv"
        )





    st.header("Outstanding Amount Aging Analysis")

    aging_data = finance_data[
        finance_data["outstanding_amount"] > 0
    ].copy()

    aging_data["due_date"] = pd.to_datetime(
        aging_data["due_date"],
        errors="coerce"
    )

    aging_data = aging_data.dropna(
        subset=["due_date"]
    )

    as_of_date = pd.Timestamp("2026-11-11")

    aging_data["overdue_days"] = (
        as_of_date - aging_data["due_date"]
    ).dt.days

    def assign_aging_bucket(days):

        if days <= 0:
            return "Not Due"

        elif days <= 7:
            return "1-7 Days"

        elif days <= 30:
            return "8-30 Days"

        elif days <= 60:
            return "31-60 Days"

        else:
            return "60+ Days"

    aging_data["aging_bucket"] = (
        aging_data["overdue_days"].apply(
            assign_aging_bucket
        )
    )

    aging_summary = (
        aging_data.groupby("aging_bucket")[
            "outstanding_amount"
        ].sum()
    )

    aging_summary = aging_summary.reindex(
        [
            "Not Due",
            "1-7 Days",
            "8-30 Days",
            "31-60 Days",
            "60+ Days"
        ],
        fill_value=0
    )

    st.subheader("Outstanding Amount by Aging Bucket")

    st.bar_chart(aging_summary)

    st.dataframe(
        aging_summary.reset_index().rename(
            columns={
                "aging_bucket": "Aging Bucket",
                "outstanding_amount": "Outstanding Amount"
            }
        ),
        use_container_width=True
    )

    st.caption(
        "Aging is calculated using 11 November 2026 "
        "as the project date. Invalid or missing due dates "
        "are excluded from this chart."
    )

    st.divider()

    # Top 5 customers analysis
    st.header(
        "Top 5 Customers with Highest Outstanding"
    )

    customer_summary = (
        finance_data.groupby("customer_name")[
            "outstanding_amount"
        ]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )

    st.bar_chart(customer_summary)

    st.subheader("Customer Outstanding Details")

    st.dataframe(
        customer_summary.reset_index().rename(
            columns={
                "customer_name": "Customer Name",
                "outstanding_amount": "Outstanding Amount"
            }
        ),
        use_container_width=True
    )

    st.divider()

    # Invoice follow-up priority analysis
    st.header("Invoice Follow-up Priority Queue")

    followup_data = finance_data.copy()
    followup_data["payment_status"] = (
        followup_data["payment_status"]
        .astype("string")
        .str.strip()
        .str.lower()
    )
    followup_data["last_contact_date"] = pd.to_datetime(
        followup_data["last_contact_date"],
        errors="coerce"
    )
    followup_data["next_follow_up_date"] = pd.to_datetime(
        followup_data["next_follow_up_date"],
        errors="coerce"
    )

    st.write("Payment Status Values:")
    st.write(followup_data["payment_status"].value_counts(dropna=False))

    followup_data["due_date"] = pd.to_datetime(
        followup_data["due_date"],
        errors="coerce"
    )

    as_of_date = pd.Timestamp("2026-11-11")

    followup_data["overdue_days"] = (
        as_of_date - followup_data["due_date"]
        ).dt.days

    def assign_priority(row):

        if row["outstanding_amount"] == 0:
            return "No Follow-up"

        elif row["payment_status"] == "paid":
            return "No Follow-up"

        elif row["payment_status"] == "disputed":
            return "Needs Review"
        elif (
            pd.notna(row["last_contact_date"])
            and (as_of_date - row["last_contact_date"]).days <= 3
            and (as_of_date - row["last_contact_date"]).days >= 0
        ):
            return "Recently Contacted"


        elif pd.isna(row["due_date"]):
            return "Needs Review"
        elif (
            pd.notna(row["next_follow_up_date"])
            and row["next_follow_up_date"] > as_of_date
        ):
            return "Scheduled"

        elif row["overdue_days"] <= 0:
            return "Low"

        elif row["overdue_days"] <= 7:
            return "Medium"

        elif row["overdue_days"] <= 30:
            return "High"

        else:
            return "Critical"

    followup_data["followup_priority"] = (
        followup_data.apply(assign_priority, axis=1)
    )

    priority_order = {
        "Critical": 1,
        "High": 2,
        "Medium": 3,
        "Low": 4
    }

    followup_queue = followup_data[
        followup_data["followup_priority"].isin(
            ["Critical", "High", "Medium", "Low"]
        )
    ].copy()
        # Include disputed and missing due-date invoices
    review_queue = clean_data[
        (
            clean_data["payment_status"]
            .astype("string")
            .str.strip()
            .str.lower()
            == "disputed"
        )
        | clean_data["due_date"].isna()
    ].copy()

    # Exclude duplicate invoice records
    review_queue = review_queue[
        ~review_queue["validation_errors"]
        .astype(str)
        .str.contains("Duplicate invoice ID", case=False)
    ].copy()

    # Prepare manual-review display fields
    review_queue["due_date"] = pd.to_datetime(
        review_queue["due_date"],
        errors="coerce"
    )

    review_queue["overdue_days"] = (
        as_of_date - review_queue["due_date"]
    ).dt.days

    review_queue["followup_priority"] = "Needs Review"







    st.subheader("Invoices Requiring Manual Review")

    if not review_queue.empty:
        st.warning(
            f"{len(review_queue)} invoices require manual review."
        )

        st.dataframe(
            review_queue[
                [
                    "invoice_id",
                    "customer_name",
                    "outstanding_amount",
                    "overdue_days",
                    "followup_priority"
                ]
            ],
            use_container_width=True
        )
    else:
        st.success("No invoices require manual review.")

    followup_queue["priority_order"] = (
        followup_queue["followup_priority"].map(priority_order)
    )

    followup_queue = followup_queue.sort_values(
        ["priority_order", "overdue_days"],
        ascending=[True, False]
    )
    st.subheader("Invoices Requiring Follow-up")

    if not followup_queue.empty:
        st.dataframe(
            followup_queue[
                [
                    "invoice_id",
                    "customer_name",
                    "outstanding_amount",
                    "overdue_days",
                    "followup_priority"
                ]
            ],
            use_container_width=True
        )
    else:
        st.success("No invoices require follow-up.")

    # Recently Contacted Invoices
    recently_contacted = followup_data[
        followup_data["followup_priority"] == "Recently Contacted"
    ].copy()

    st.subheader("Recently Contacted Invoices")

    if not recently_contacted.empty:
        st.info(
            f"{len(recently_contacted)} invoices were contacted recently."
        )

        st.dataframe(
            recently_contacted[
                [
                    "invoice_id",
                    "customer_name",
                    "outstanding_amount",
                    "overdue_days",
                    "followup_priority"
                ]
            ],
            use_container_width=True
        )
    else:
        st.success("No recently contacted invoices found.")
    # Scheduled Invoices
    scheduled_invoices = followup_data[
        followup_data["followup_priority"] == "Scheduled"
    ].copy()

    st.subheader("Scheduled Follow-up Invoices")

    if not scheduled_invoices.empty:
        st.info(
            f"{len(scheduled_invoices)} invoices have future follow-up dates."
        )

        st.dataframe(
            scheduled_invoices[
                [
                    "invoice_id",
                    "customer_name",
                    "outstanding_amount",
                    "next_follow_up_date",
                    "followup_priority"
                ]
            ],
            use_container_width=True
        )
    else:
        st.success("No scheduled follow-up invoices found.")



    st.subheader("Priority Summary")

    priority_counts = followup_queue["followup_priority"].value_counts()

    priority_cols = st.columns(7)

    priority_cols[0].metric(
        "Critical",
        int(priority_counts.get("Critical", 0))
    )

    priority_cols[1].metric(
        "High",
        int(priority_counts.get("High", 0))
    )

    priority_cols[2].metric(
        "Medium",
        int(priority_counts.get("Medium", 0))
    )

    priority_cols[3].metric(
        "Low",
        int(priority_counts.get("Low", 0))
    )
    priority_cols[4].metric(
        "Needs Review",
        int(
            followup_data["followup_priority"]
            .eq("Needs Review")
            .sum()
        )
    )
    priority_cols[5].metric(
        "Recently Contacted",
        int(
            followup_data["followup_priority"]
            .eq("Recently Contacted")
            .sum()
        )
    )
    priority_cols[6].metric(
        "Scheduled",
        int(
            followup_data["followup_priority"]
            .eq("Scheduled")
            .sum()
        )
    )




    st.bar_chart(
        followup_data["followup_priority"].value_counts()
    )

    st.subheader("Invoices Requiring Follow-up")

    selected_priority = st.selectbox(
        "Filter invoices by priority",
        ["All", "Critical", "High", "Medium", "Low", "Needs Review", "Scheduled"]
    )

    if selected_priority == "All":
        filtered_queue = followup_data[
            followup_data["followup_priority"].isin(
                ["Critical", "High", "Medium", "Low"]
            )
        ].copy()

    else:
        filtered_queue = followup_data[
            followup_data["followup_priority"] == selected_priority
        ].copy()

    customer_search = st.text_input(
        "Search Customer Name"
    )

    if customer_search:
        filtered_queue = filtered_queue[
            filtered_queue["customer_name"].str.contains(
                customer_search,
                case=False,
                na=False
            )
        ]



    st.dataframe(
        filtered_queue[
            [
                "invoice_id",
                "customer_name",
                "outstanding_amount",
                "overdue_days",
                "followup_priority"
            ]
        ],
        use_container_width=True
    )


    st.subheader("Download Follow-up Report")


    report_csv = filtered_queue[
        [
            "invoice_id",
            "customer_name",
            "outstanding_amount",
            "overdue_days",
            "followup_priority"
        ]
    ].to_csv(index=False).encode("utf-8")




    st.download_button(
        label="Download Follow-up Report",
        data=report_csv,
        file_name="FollowUpOS_Followup_Report.csv",
        mime="text/csv"
    )


    st.caption(
        "Critical and High priority invoices should be reviewed first. "
        "Invoices with missing due dates require manual verification."
    )


    st.divider()

    # Dataset preview
    st.header("Dataset Preview")

    st.divider()
    st.header("Business Insights & Recommended Actions")

    st.markdown("""
    ### 1. Collection Management
    - Focus on Critical and High priority invoices first.
    - Follow up with customers whose payments are overdue.
    - Review outstanding balances regularly.

    ### 2. Customer Management
    - Identify customers with high outstanding balances.
    - Maintain regular communication with credit customers.
    - Review payment patterns before providing additional credit.

    ### 3. Follow-up Strategy
    - Use the priority queue to organize daily follow-up activities.
    - Review reminder drafts before sending them to customers.
    - Update payment details after receiving payments.

    ### 4. Business Improvement
    - Monitor collection percentage regularly.
    - Reduce long-pending receivables.
    - Maintain accurate invoice and customer records.
    """)
    st.header("Download Complete Invoice Data")

    csv_data = finance_data.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Complete Invoice Data",
        data=csv_data,
        file_name="FollowUpOS_Complete_Invoice_Data.csv",
        mime="text/csv"
    )





    # Customer reminder drafts
    st.header("Customer Payment Reminder Drafts")

    reminder_data = filtered_queue.copy()

    reminder_data["reminder_message"] = reminder_data.apply(
        lambda row: (
            f"Dear {row['customer_name']}, "
            f"our records show that invoice {row['invoice_id']} "
            f"has an outstanding amount of "
            f"Rs. {row['outstanding_amount']:,.2f}. "
            f"Kindly arrange payment at your earliest convenience. "
            f"Thank you."
        ),
        axis=1
    )

    st.dataframe(
        reminder_data[
            [
                "invoice_id",
                "customer_name",
                "outstanding_amount",
                "followup_priority",
                "reminder_message"
            ]
        ],
        use_container_width=True
    )

    # Human Approval Workflow
    st.subheader("Review and Approve Reminder")

    if not reminder_data.empty:

        selected_invoice = st.selectbox(
            "Select Invoice for Review",
            reminder_data["invoice_id"].tolist()
        )

        selected_row = reminder_data[
            reminder_data["invoice_id"] == selected_invoice
        ].iloc[0]

        edited_message = st.text_area(
            "Review or Edit Reminder Message",
            value=selected_row["reminder_message"],
            key="edited_reminder"
        )


        # Store approved reminders in session state
        if "approved_reminders" not in st.session_state:
            st.session_state.approved_reminders = {}

        if "activity_log" not in st.session_state:
            st.session_state.activity_log = []
        if "outcome_log" not in st.session_state:
            st.session_state.outcome_log = []

        if st.button("Approve Reminder"):

            st.session_state.approved_reminders[selected_invoice] = {
                "message": edited_message,
                "status": "Approved"
            }
            st.session_state.activity_log.append({
    "invoice_id": selected_invoice,
    "action": "Reminder Approved",
    "message": edited_message,
    "recorded_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
})
                        # Save approved reminder to SQLite
            conn = sqlite3.connect("followupos.db")
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO activity_log
                (invoice_id, action, message, recorded_at)
                VALUES (?, ?, ?, ?)
            """, (
                selected_invoice,
                "Reminder Approved",
                edited_message,
                pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            conn.commit()
            conn.close()



            st.success(
                f"Invoice {selected_invoice} approved successfully!"
            )

        # Display approval status
        if selected_invoice in st.session_state.approved_reminders:

            approval = st.session_state.approved_reminders[selected_invoice]

            if approval["status"] == "Approved":

                st.success("Status: Approved")
                st.code(
                    approval["message"],
                    language=None
                )

                st.button(
                    "Copy Reminder",
                    key=f"copy_reminder_{selected_invoice}",
                    on_click=lambda message=approval["message"]: st.session_state.update(
                        {"copied_reminder": message}
                    )
                )

                if st.session_state.get("copied_reminder"):
                    st.info(
                        "Reminder text is ready below. Select and copy it."
                    )
                    st.text_area(
                        "Copy your reminder",
                        value=st.session_state["copied_reminder"],
                        height=120,
                        key=f"copy_text_{selected_invoice}"
                    )

                if st.button(
                    "Mark as Sent",
                    key=f"mark_sent_{selected_invoice}"
                ):

                    approval["status"] = "Sent"

                    st.session_state.activity_log.append({
                        "invoice_id": selected_invoice,
                        "action": "Reminder Marked as Sent",
                        "message": approval["message"],
                        "recorded_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

                    # Save sent reminder to SQLite
                    conn = sqlite3.connect("followupos.db")
                    cursor = conn.cursor()

                    cursor.execute("""
                        INSERT INTO activity_log
                        (invoice_id, action, message, recorded_at)
                        VALUES (?, ?, ?, ?)
                    """, (
                        selected_invoice,
                        "Reminder Marked as Sent",
                        approval["message"],
                        pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))

                    conn.commit()
                    conn.close()

                    st.session_state.approved_reminders[selected_invoice] = approval

                    st.success("Reminder marked as sent successfully!")

            elif approval["status"] == "Sent":

                st.success("Status: Sent")

        else:
            st.info("No invoices are currently available for reminder review.")






    reminder_csv = reminder_data[
        [
            "invoice_id",
            "customer_name",
            "outstanding_amount",
            "followup_priority",
            "reminder_message"
        ]
    ].to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Customer Reminder Drafts",
        data=reminder_csv,
        file_name="FollowUpOS_Customer_Reminder_Drafts.csv",
        mime="text/csv"
    )


    # Reminder Activity Log
    st.markdown("---")
    st.header("Reminder Activity Log")

    # Retrieve reminder activities from SQLite
    conn = sqlite3.connect("followupos.db")

    activity_df = pd.read_sql_query("""
        SELECT *
        FROM activity_log
        ORDER BY id DESC
    """, conn)

    conn.close()

    if not activity_df.empty:

        st.dataframe(
            activity_df,
            use_container_width=True
        )

        activity_csv = activity_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download Reminder Activity Log",
            data=activity_csv,
            file_name="FollowUpOS_Reminder_Activity_Log.csv",
            mime="text/csv"
        )

    else:
        st.info("No reminder activities recorded yet.")



    # Customer Outcome Tracking
    st.markdown("---")
    st.header("Customer Outcome Tracking")

    if not finance_data.empty:

        with st.form("customer_outcome_form"):

            outcome_invoice = st.selectbox(
                "Select Invoice",
                finance_data["invoice_id"].astype(str).tolist()
            )

            customer_outcome = st.selectbox(
                "Customer Response",
                [
                    "Payment Promised",
                    "Payment Received",
                    "Dispute Raised",
                    "No Response"
                ]
            )

            outcome_notes = st.text_area(
                "Additional Notes",
                placeholder="Enter customer response details..."
            )

            promised_payment_date = st.date_input(
                "Promised Payment Date (if applicable)",
                value=None
            )

            submit_outcome = st.form_submit_button(
                "Save Customer Outcome"
            )


            if submit_outcome:

                recorded_at = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

                promised_date = (
                    promised_payment_date.strftime("%Y-%m-%d")
                    if promised_payment_date
                    else None
                )

                st.session_state.outcome_log.append({
                    "invoice_id": outcome_invoice,
                    "outcome": customer_outcome,
                    "notes": outcome_notes,
                    "promised_payment_date": promised_date,
                    "recorded_at": recorded_at
                })

                # Save customer outcome to SQLite
                conn = sqlite3.connect("followupos.db")
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO outcome_log
                    (invoice_id, outcome, notes, promised_payment_date, recorded_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    outcome_invoice,
                    customer_outcome,
                    outcome_notes,
                    promised_date,
                    recorded_at
                ))

                conn.commit()
                conn.close()

                st.success("Customer outcome saved successfully!")


    else:
        st.info("No valid invoices available for outcome tracking.")



    # Display Customer Outcome Log
    st.subheader("Customer Outcome History")

    # Retrieve customer outcomes from SQLite
    conn = sqlite3.connect("followupos.db")

    outcome_df = pd.read_sql_query("""
        SELECT *
        FROM outcome_log
        ORDER BY id DESC
    """, conn)

    conn.close()

    if not outcome_df.empty:

        payment_promised_count = (
            outcome_df["outcome"] == "Payment Promised"
        ).sum()

        payment_received_count = (
            outcome_df["outcome"] == "Payment Received"
        ).sum()

        dispute_count = (
            outcome_df["outcome"] == "Dispute Raised"
        ).sum()

        no_response_count = (
            outcome_df["outcome"] == "No Response"
        ).sum()

        st.subheader("Customer Outcome Summary")

        outcome_cols = st.columns(4)

        outcome_cols[0].metric(
            "Payment Promised",
            payment_promised_count
        )

        outcome_cols[1].metric(
            "Payment Received",
            payment_received_count
        )

        outcome_cols[2].metric(
            "Disputes",
            dispute_count
        )

        outcome_cols[3].metric(
            "No Response",
            no_response_count
        )

        st.dataframe(
            outcome_df,
            use_container_width=True
        )

        outcome_csv = outcome_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download Customer Outcome History",
            data=outcome_csv,
            file_name="FollowUpOS_Customer_Outcome_History.csv",
            mime="text/csv"
        )

    else:
        st.info("No customer outcomes recorded yet.")



    # Daily Business Report
    st.markdown("---")
    st.header("Daily Business Report")

    st.write(
        f"Report Date: {as_of_date.strftime('%d-%m-%Y')}"
    )

    # Daily Business Summary
    total_invoices = len(finance_data)

    total_outstanding = finance_data["outstanding_amount"].sum()

    overdue_invoices = len(
        finance_data[
            (finance_data["due_date"] < as_of_date) &
            (finance_data["outstanding_amount"] > 0)
        ]
    )

    overdue_amount = finance_data.loc[
        (finance_data["due_date"] < as_of_date) &
        (finance_data["outstanding_amount"] > 0),
        "outstanding_amount"
    ].sum()

    report_cols = st.columns(4)

    report_cols[0].metric(
        "Valid Invoices",
        total_invoices
    )

    report_cols[1].metric(
        "Outstanding Amount",
        f"₹{total_outstanding:,.2f}"
    )

    report_cols[2].metric(
        "Overdue Invoices",
        overdue_invoices
    )

    report_cols[3].metric(
        "Overdue Amount",
        f"₹{overdue_amount:,.2f}"
    )

    # Retrieve customer outcomes from SQLite
    conn = sqlite3.connect("followupos.db")

    report_outcome_df = pd.read_sql_query("""
        SELECT outcome
        FROM outcome_log
    """, conn)

    conn.close()

    st.subheader("Customer Response Summary")

    payment_promised_count = (
        report_outcome_df["outcome"] == "Payment Promised"
    ).sum()

    payment_received_count = (
        report_outcome_df["outcome"] == "Payment Received"
    ).sum()

    dispute_count = (
        report_outcome_df["outcome"] == "Dispute Raised"
    ).sum()

    no_response_count = (
        report_outcome_df["outcome"] == "No Response"
    ).sum()

    outcome_cols = st.columns(4)

    outcome_cols[0].metric(
        "Payment Promised",
        payment_promised_count
    )

    outcome_cols[1].metric(
        "Payment Received",
        payment_received_count
    )

    outcome_cols[2].metric(
        "Disputes",
        dispute_count
    )

    outcome_cols[3].metric(
        "No Response",
        no_response_count
    )

    # Download Daily Business Report
    daily_report = pd.DataFrame({
        "Metric": [
            "Valid Invoices",
            "Outstanding Amount",
            "Overdue Invoices",
            "Overdue Amount",
            "Payment Promised",
            "Payment Received",
            "Disputes",
            "No Response"
        ],
        "Value": [
            total_invoices,
            total_outstanding,
            overdue_invoices,
            overdue_amount,
            payment_promised_count,
            payment_received_count,
            dispute_count,
            no_response_count
        ]
    })

    daily_report_csv = daily_report.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Daily Business Report",
        data=daily_report_csv,
        file_name="FollowUpOS_Daily_Business_Report.csv",
        mime="text/csv"
    )






    st.dataframe(
        df.head(10),
        use_container_width=True
    )

else:

    st.info(
        "Please upload your FollowUpOS Excel dataset."
    )
    # Data Management
st.markdown("---")

st.subheader("Data Management")

st.warning(
    "This action permanently deletes saved reminder activity "
    "and customer outcome records from the local database."
)

confirm_delete = st.checkbox(
    "I understand and confirm that I want to delete all saved demo records."
)

if st.button(
    "Delete All Demo Records",
    disabled=not confirm_delete
):

    delete_all_demo_records()

    st.success(
        "All saved reminder activity and customer outcome records have been deleted."
)

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; color:#526579; padding:15px;">
        <h4>FollowUpOS | Sales Follow-up & Receivables Management</h4>
        <p>Built to support business analytics, payment tracking and customer follow-ups.</p>
        <p>Project Demonstration | Hyderabad, India</p>
    </div>
    """,
    unsafe_allow_html=True
)




