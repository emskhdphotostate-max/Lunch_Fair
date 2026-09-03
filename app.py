"""LedgerFlowPro — Professional Billing System — Streamlit web application.

Configure SUPABASE_URL and SUPABASE_KEY in Streamlit secrets before running.
Developed & Owned By: Shehzad Kazama
"""

import os
import streamlit as st
from supabase import create_client

supabase_url = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")

supabase = create_client(supabase_url, supabase_key)

from datetime import date
from io import BytesIO

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph



st.set_page_config(page_title="LedgerFlowPro — Professional Billing System", page_icon="⚡", layout="wide")


def money(value):
    return f"Rs. {float(value or 0):,.0f}"


# ---------------------------------------------------------------------------
# Premium visual theme — injected once per run. Pure CSS/HTML on top of the
# existing Streamlit widgets, so none of the app logic above changes.
# Palette: deep midnight navy + champagne gold, glass panels, soft motion.
# ---------------------------------------------------------------------------

def inject_premium_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', 'Poppins', sans-serif;
    }

    :root {
        --gold: #E8C468;
        --gold-soft: #F3DFA0;
        --navy-deep: #0B0F1E;
        --navy-mid: #131a2e;
        --navy-card: rgba(255,255,255,0.045);
        --text-soft: #C9CFE0;
    }

    /* ---------- App background ---------- */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #16203a 0%, #0B0F1E 45%, #060810 100%);
    }

    /* ---------- Headings ---------- */
    h1, h2, h3 {
        font-family: 'Poppins', sans-serif !important;
        color: #F3F5FB !important;
        letter-spacing: 0.2px;
    }
    h1 {
        background: linear-gradient(90deg, #F3DFA0, #E8C468 45%, #C9962E);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800 !important;
    }

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1326 0%, #0a0e1c 100%);
        border-right: 1px solid rgba(232,196,104,0.15);
    }
    [data-testid="stSidebar"] * { color: #DCE1F0 !important; }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] .stMarkdown h2 {
        color: var(--gold) !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] hr { border-color: rgba(232,196,104,0.18) !important; }

    /* Sidebar menu (radio) styled like a premium nav */
    [data-testid="stSidebar"] [role="radiogroup"] {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label {
        padding: 9px 14px !important;
        border-radius: 10px;
        transition: all 0.2s ease;
        border: 1px solid transparent;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(232,196,104,0.08);
        border-color: rgba(232,196,104,0.25);
    }
    [data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"],
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg, rgba(232,196,104,0.22), rgba(232,196,104,0.05));
        border-color: rgba(232,196,104,0.45);
    }

    /* Sidebar buttons (logout, add party) */
    [data-testid="stSidebar"] .stButton > button {
        background: transparent;
        border: 1px solid rgba(232,196,104,0.4);
        color: var(--gold) !important;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(232,196,104,0.12);
        border-color: var(--gold);
    }

    /* Sidebar text inputs (e.g. "New Party") — light field, dark readable text */
    [data-testid="stSidebar"] input {
        background: #F3F5FA !important;
        border: 1px solid rgba(15,23,42,0.15) !important;
        color: #12141C !important;
        caret-color: #12141C !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] input::placeholder { color: #6B7280 !important; opacity: 1 !important; }

    /* ---------- Glass card wrapper for forms ---------- */
    div[data-testid="stForm"] {
        background: var(--navy-card);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border: 1px solid rgba(232,196,104,0.22);
        border-radius: 18px;
        padding: 34px 34px 22px 34px !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.05);
    }

    /* ---------- Inputs everywhere: light field surface, DARK text so typing is visible ---------- */
    .stTextInput input, .stNumberInput input, .stDateInput input, .stTextArea textarea,
    .stSelectbox div[data-baseweb="select"] > div {
        background: #F3F5FA !important;
        border: 1px solid rgba(15,23,42,0.15) !important;
        color: #12141C !important;
        caret-color: #12141C !important;
        border-radius: 10px !important;
    }
    .stTextInput input::placeholder, .stNumberInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #6B7280 !important;
        opacity: 1 !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
        border-color: var(--gold) !important;
        box-shadow: 0 0 0 1px var(--gold) !important;
    }
    /* Dropdown popover list (party / menu selects) */
    div[data-baseweb="popover"] li, ul[role="listbox"] li,
    div[data-baseweb="popover"] div[data-baseweb="menu"] {
        background: #F3F5FA !important;
        color: #12141C !important;
    }
    div[data-baseweb="popover"] li:hover { background: #E8ECF5 !important; }

    label, .stTextInput label, .stNumberInput label, .stDateInput label, .stSelectbox label {
        color: var(--text-soft) !important;
        font-weight: 500 !important;
    }

    /* ---------- Primary buttons ---------- */
    .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
        background: linear-gradient(135deg, #F3DFA0, #E8C468 55%, #C9962E);
        color: #17140a !important;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 0.55em 1.4em;
        box-shadow: 0 8px 24px rgba(232,196,104,0.25);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 28px rgba(232,196,104,0.4);
    }

    /* ---------- Tabs (Login / New Account) ---------- */
    [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid rgba(232,196,104,0.15) !important; }
    [data-baseweb="tab"] {
        color: var(--text-soft) !important;
        font-weight: 600;
    }
    [data-baseweb="tab"][aria-selected="true"] {
        color: var(--gold) !important;
    }
    [data-baseweb="tab-highlight"] { background-color: var(--gold) !important; }

    /* ---------- Metrics ---------- */
    [data-testid="stMetric"] {
        background: var(--navy-card);
        border: 1px solid rgba(232,196,104,0.18);
        border-radius: 14px;
        padding: 14px 16px;
    }
    [data-testid="stMetricValue"] { color: var(--gold) !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: var(--text-soft) !important; }

    /* ---------- Dataframes ---------- */
    [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid rgba(232,196,104,0.15); }

    /* ---------- Alerts ---------- */
    div[data-baseweb="notification"] { border-radius: 10px; }

    /* ---------- Captions / helper text (was invisible — force visible contrast) ---------- */
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p,
    .stCaption, .stMarkdown small, small {
        color: #9AA3BE !important;
        opacity: 1 !important;
    }

    /* ---------- Secondary / plain buttons (e.g. "Add Party", "Logout") ---------- */
    .stButton > button, .stFormSubmitButton > button {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(232,196,104,0.45) !important;
        color: #F3DFA0 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover {
        background: rgba(232,196,104,0.12) !important;
        border-color: var(--gold) !important;
        color: #FFFFFF !important;
    }
    /* Primary buttons stay on the gold-fill treatment (kept readable, dark text on gold) */
    .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
        color: #17140a !important;
    }

    /* ---------- Number input +/- steppers (icons were dark-on-dark) ---------- */
    .stNumberInput button, [data-testid="stNumberInputStepUp"], [data-testid="stNumberInputStepDown"] {
        background: rgba(255,255,255,0.06) !important;
        border-color: rgba(232,196,104,0.35) !important;
    }
    .stNumberInput svg, [data-testid="stNumberInputStepUp"] svg, [data-testid="stNumberInputStepDown"] svg {
        fill: #E8C468 !important;
    }

    /* ---------- General body / markdown / widget label text ---------- */
    p, span, li, .stMarkdown, .stMarkdown p {
        color: #DCE1F0;
    }
    /* Text shown INSIDE the selected value of a dropdown must be dark (light field bg) */
    .stSelectbox div[data-baseweb="select"] * { color: #12141C !important; }
    [data-testid="stWidgetLabel"] p { color: var(--text-soft) !important; }

    /* ---------- Floating ambient orbs (pure decoration, no clicks) ---------- */
    .lfp-orb {
        position: fixed;
        border-radius: 50%;
        filter: blur(70px);
        opacity: 0.35;
        z-index: 0;
        pointer-events: none;
        animation: lfp-float 14s ease-in-out infinite;
    }
    .lfp-orb--gold { width: 340px; height: 340px; background: #E8C468; top: -80px; left: -100px; animation-duration: 16s; }
    .lfp-orb--blue { width: 300px; height: 300px; background: #3E5C9A; bottom: -100px; right: -80px; animation-duration: 18s; animation-delay: 2s; }
    .lfp-orb--teal { width: 220px; height: 220px; background: #2FA48B; top: 40%; right: 10%; animation-duration: 20s; animation-delay: 4s; opacity: 0.22; }

    @keyframes lfp-float {
        0%   { transform: translate(0, 0) scale(1); }
        50%  { transform: translate(30px, -25px) scale(1.08); }
        100% { transform: translate(0, 0) scale(1); }
    }

    /* Make sure real content sits above the decorative orbs */
    section.main > div.block-container { position: relative; z-index: 1; }
    </style>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Auth: every browser session gets its own Supabase client stored in
# st.session_state (NOT st.cache_resource — that would be shared across all
# visitors, which would leak one user's login into another user's session).
# ---------------------------------------------------------------------------

def get_client():
    if "sb_client" not in st.session_state:
        try:
            url = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")
        except Exception:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
        st.session_state.sb_client = create_client(url, key)
    return st.session_state.sb_client


def current_user():
    return st.session_state.get("user")


def log_in(email, password):
    client = get_client()
    result = client.auth.sign_in_with_password({"email": email, "password": password})
    client.postgrest.auth(result.session.access_token)
    st.session_state.user = {"id": result.user.id, "email": result.user.email}


def sign_up(email, password):
    client = get_client()
    result = client.auth.sign_up({"email": email, "password": password})
    if result.session:
        client.postgrest.auth(result.session.access_token)
        st.session_state.user = {"id": result.user.id, "email": result.user.email}
        return "logged_in"
    return "confirm_email"


def log_out():
    try:
        get_client().auth.sign_out()
    except Exception:
        pass
    for key in ("user", "sb_client"):
        st.session_state.pop(key, None)
    st.rerun()


def auth_screen():
    inject_premium_theme()

    # Ambient floating orbs + centered brand header
    st.markdown("""
    <div class="lfp-orb lfp-orb--gold"></div>
    <div class="lfp-orb lfp-orb--blue"></div>
    <div class="lfp-orb lfp-orb--teal"></div>
    <div style="text-align:center; padding-top: 28px; padding-bottom: 6px;">
        <div style="
            display:inline-flex; align-items:center; justify-content:center;
            width:64px; height:64px; border-radius:18px;
            background: linear-gradient(135deg, #F3DFA0, #E8C468 55%, #C9962E);
            box-shadow: 0 10px 30px rgba(232,196,104,0.35);
            font-size: 30px; margin-bottom: 14px;">⚡</div>
        <h1 style="margin-bottom:2px; font-size: 2.4rem;">LedgerFlowPro</h1>
        <div style="
            display:inline-block; margin-top:4px; padding: 4px 14px;
            border: 1px solid rgba(232,196,104,0.4); border-radius: 999px;
            color:#E8C468; font-size:12px; letter-spacing:2px; font-weight:600;
            text-transform:uppercase;">Professional Billing System</div>
        <div style="color:#8B93AC; margin-top:12px; font-size:13px;">Developed &amp; Owned By: Shehzad Kazama</div>
    </div>
    """, unsafe_allow_html=True)

    left, mid, right = st.columns([1, 1.3, 1])
    with mid:
        login_tab, signup_tab = st.tabs(["Login", "New Account"])

        with login_tab:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@company.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Login", type="primary", use_container_width=True)
            if submitted:
                if not email.strip() or not password:
                    st.error("Email and password are both required.")
                else:
                    try:
                        log_in(email.strip(), password)
                        st.rerun()
                    except Exception:
                        st.error("Incorrect email or password.")

        with signup_tab:
            with st.form("signup_form"):
                new_email = st.text_input("Email", key="signup_email", placeholder="you@company.com")
                new_password = st.text_input("Password (at least 6 characters)", type="password", key="signup_pw", placeholder="••••••••")
                confirm_password = st.text_input("Confirm Password", type="password", key="signup_pw2", placeholder="••••••••")
                submitted_signup = st.form_submit_button("Create Account", type="primary", use_container_width=True)
            if submitted_signup:
                if not new_email.strip() or not new_password:
                    st.error("Email and password are both required.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    try:
                        status = sign_up(new_email.strip(), new_password)
                        if status == "logged_in":
                            st.success("Account created! You are now logged in.")
                            st.rerun()
                        else:
                            st.success("Account created. Please check your email and click the confirmation link, then sign in from the Login tab.")
                    except Exception as error:
                        message = str(error)
                        if "already registered" in message.lower() or "already exists" in message.lower():
                            st.error("This email is already registered. Please use the Login tab.")
                        else:
                            st.error(f"Could not create account: {error}")


# ---------------------------------------------------------------------------
# App data functions (unchanged logic — Row Level Security in the database
# now automatically restricts every query below to the logged-in user's own
# rows, so no extra filtering is needed here).
# ---------------------------------------------------------------------------

def bills_with_totals():
    response = get_client().table("bills").select(
        "id,bill_no,date,party,launch,bill_amt,remarks,payments(id,date,amount,note)"
    ).order("id", desc=True).execute()
    bills = response.data or []
    for bill in bills:
        payments = bill.get("payments") or []
        bill["received"] = sum(float(p["amount"] or 0) for p in payments)
        bill["pending"] = max(0, float(bill["bill_amt"] or 0) - bill["received"])
        bill["status"] = "Cleared" if bill["pending"] <= 0.01 else "Partial" if bill["received"] else "Pending"
    return bills


def parties():
    return [row["name"] for row in get_client().table("parties").select("name").order("name").execute().data or []]


def pdf_invoice(bill):
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    story = [Paragraph("LedgerFlowPro — Official Invoice", styles["Title"]), Spacer(1, 4),
             Paragraph("Developed & Owned By: Shehzad Kazama", styles["Normal"]), Spacer(1, 12)]
    data = [
        ["Bill No.", bill["bill_no"], "Date", bill["date"]],
        ["Party", bill["party"], "Product / Item Name", bill["launch"]],
        ["Bill Amount", money(bill["bill_amt"]), "Received", money(bill["received"])],
        ["Pending", money(bill["pending"]), "Status", bill["status"]],
    ]
    table = Table(data, colWidths=[3*cm, 5.5*cm, 3*cm, 5.5*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF2FF")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    story += [table, Spacer(1, 16)]
    if bill.get("remarks"):
        story.append(Paragraph(f"Remarks: {bill['remarks']}", styles["Normal"]))
        story.append(Spacer(1, 16))

    story.append(Paragraph("© 2026 LedgerFlowPro. All rights reserved. Developed & Owned by Shehzad Kazama.", styles["Italic"]))
    doc.build(story)
    return output.getvalue()


def dashboard(bills):
    st.header("Dashboard")
    total = sum(float(b["bill_amt"]) for b in bills)
    received = sum(b["received"] for b in bills)
    pending = sum(b["pending"] for b in bills)
    a, b, c, d = st.columns(4)
    a.metric("Total Bills", len(bills))
    b.metric("Bill Amount", money(total))
    c.metric("Received", money(received))
    d.metric("Pending", money(pending))
    st.subheader("Recent Bills")
    show_bill_table(bills[:10], include_actions=False)


def show_bill_table(bills, include_actions=True):
    rows = [{
        "Bill No.": b["bill_no"], "Date": b["date"], "Party": b["party"],
        "Product / Item Name": b["launch"], "Bill Amount": money(b["bill_amt"]),
        "Received": money(b["received"]), "Pending": money(b["pending"]),
        "Status": b["status"], "Remarks": b.get("remarks") or "",
    } for b in bills]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    if include_actions and bills:
        choices = {b["bill_no"]: b for b in bills}
        selected_no = st.selectbox("Select a bill to download the invoice", list(choices), key="invoice_bill")
        selected = choices[selected_no]
        st.download_button("Download Invoice PDF", pdf_invoice(selected),
                           file_name=f"Invoice_{selected_no}.pdf", mime="application/pdf")


def new_bill_page():
    st.header("New Bill")
    st.caption("The bill number is generated automatically by the database and cannot be edited.")
    names = parties()
    if not names:
        st.warning("Please add a party/customer from the sidebar first.")
        return
    with st.form("new_bill", clear_on_submit=True):
        col1, col2 = st.columns(2)
        bill_date = col1.date_input("Date", value=date.today())
        party = col2.selectbox("Party / Customer", names)
        launch = col1.text_input("Product Name / Item Name")
        amount = col2.number_input("Bill Amount (Rs.)", min_value=0.0, step=100.0)
        remarks = st.text_input("Remarks")
        submitted = st.form_submit_button("Add Bill", type="primary")
    if submitted:
        if not launch.strip() or amount <= 0:
            st.error("Product Name / Item Name and a valid Bill Amount are required.")
            return
        result = get_client().table("bills").insert({
            "date": bill_date.isoformat(), "party": party, "launch": launch.strip(),
            "bill_amt": amount, "remarks": remarks.strip(),
        }).execute()
        st.success(f"Bill {result.data[0]['bill_no']} added.")


def bills_page(bills):
    st.header("All Bills")
    term = st.text_input("Search: party, launch, or bill number")
    if term:
        key = term.lower()
        bills = [b for b in bills if key in " ".join(str(b.get(x, "")) for x in ("party", "launch", "bill_no", "remarks")).lower()]
    show_bill_table(bills)


def payments_page(bills):
    st.header("Receive Payment")
    pending_bills = [b for b in bills if b["pending"] > 0.01]
    if not pending_bills:
        st.info("There are no pending bills.")
        return
    lookup = {f"{b['bill_no']} — {b['party']} (Pending: {money(b['pending'])})": b for b in pending_bills}
    selected_label = st.selectbox("Select a bill", list(lookup))
    bill = lookup[selected_label]
    with st.form("payment", clear_on_submit=True):
        col1, col2 = st.columns(2)
        payment_date = col1.date_input("Payment Date", value=date.today())
        amount = col2.number_input("Receive Now (Rs.)", min_value=0.0, max_value=float(bill["pending"]), step=100.0)
        note = st.text_input("Note")
        submitted = st.form_submit_button("Save Payment", type="primary")
    if submitted:
        if amount <= 0:
            st.error("Receive amount must be greater than zero.")
            return
        get_client().table("payments").insert({"bill_id": bill["id"], "date": payment_date.isoformat(), "amount": amount, "note": note.strip()}).execute()
        st.success("Payment saved.")
        st.rerun()


def ledger_page(bills):
    st.header("Party Ledger")
    names = parties()
    if not names:
        return
    party = st.selectbox("Select a party", names)
    party_bills = [b for b in bills if b["party"] == party]
    total = sum(float(b["bill_amt"]) for b in party_bills)
    received = sum(b["received"] for b in party_bills)
    a, b, c = st.columns(3)
    a.metric("Bill Amount", money(total))
    b.metric("Received", money(received))
    c.metric("Pending", money(total - received))
    show_bill_table(party_bills, include_actions=False)


def party_manager():
    with st.sidebar:
        st.divider()
        st.subheader("Parties / Customers")
        with st.form("add_party", clear_on_submit=True):
            name = st.text_input("New Party")
            add = st.form_submit_button("Add Party")
        if add:
            try:
                get_client().table("parties").insert({"name": name.strip()}).execute()
                st.success("Party added.")
                st.rerun()
            except Exception:
                st.error("Party name is blank or already exists.")


def main():
    inject_premium_theme()

    if not current_user():
        auth_screen()
        return

    try:
        bills = bills_with_totals()
    except KeyError:
        st.error("Supabase secrets are missing. See setup steps in README.md.")
        return
    except Exception as error:
        st.error(f"Could not connect to the database: {error}")
        return

    st.sidebar.markdown("""
        <div style="text-align:center; padding: 6px 0 14px 0;">
            <div style="
                display:inline-flex; align-items:center; justify-content:center;
                width:46px; height:46px; border-radius:13px;
                background: linear-gradient(135deg, #F3DFA0, #E8C468 55%, #C9962E);
                font-size:22px; margin-bottom:8px;">⚡</div>
            <h2 style="margin:0; font-size:1.35rem;">LedgerFlowPro</h2>
            <div style="color:#8B93AC; font-size:11px; letter-spacing:1.5px; text-transform:uppercase; margin-top:2px;">
                Professional Billing System
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.sidebar.caption("By Shehzad Kazama")
    st.sidebar.markdown(
        f"<div style='background:rgba(232,196,104,0.08); border:1px solid rgba(232,196,104,0.25); "
        f"border-radius:10px; padding:8px 12px; font-size:13px; margin-bottom:10px;'>"
        f"👤 <b>{current_user()['email']}</b></div>",
        unsafe_allow_html=True,
    )
    if st.sidebar.button("Logout", use_container_width=True):
        log_out()

    st.sidebar.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
    page = st.sidebar.radio("Menu", ["Dashboard", "New Bill", "Bills", "Payments", "Party Ledger"])
    party_manager()

    st.sidebar.markdown("---")
    st.sidebar.markdown("<p style='font-size: 11px; color: #8B93AC;'>© 2026 LedgerFlowPro<br>Owned by Shehzad Kazama</p>", unsafe_allow_html=True)

    if page == "Dashboard":
        dashboard(bills)
    elif page == "New Bill":
        new_bill_page()
    elif page == "Bills":
        bills_page(bills)
    elif page == "Payments":
        payments_page(bills)
    else:
        ledger_page(bills)


if __name__ == "__main__":
    main()
