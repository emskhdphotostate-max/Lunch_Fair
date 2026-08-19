"""LedgerFlowPro — Professional Billing System — Streamlit web application.

Configure SUPABASE_URL and SUPABASE_KEY in Streamlit secrets before running.
Developed & Owned By: Shehzad Kazama
"""
from datetime import date
from io import BytesIO

import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph
from supabase import create_client


st.set_page_config(page_title="LedgerFlowPro — Professional Billing System", page_icon="⚡", layout="wide")


def money(value):
    return f"Rs. {float(value or 0):,.0f}"


# ---------------------------------------------------------------------------
# Auth: every browser session gets its own Supabase client stored in
# st.session_state (NOT st.cache_resource — that would be shared across all
# visitors, which would leak one user's login into another user's session).
# ---------------------------------------------------------------------------

def get_client():
    if "sb_client" not in st.session_state:
        st.session_state.sb_client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
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
    st.title("⚡ LedgerFlowPro — Professional Billing System")
    st.caption("Developed & Owned By: Shehzad Kazama")

    login_tab, signup_tab = st.tabs(["Login", "Naya Account Banayein"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", type="primary")
        if submitted:
            if not email.strip() or not password:
                st.error("Email aur password dono zaroori hain.")
            else:
                try:
                    log_in(email.strip(), password)
                    st.rerun()
                except Exception:
                    st.error("Email ya password ghalat hai.")

    with signup_tab:
        with st.form("signup_form"):
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password (kam az kam 6 characters)", type="password", key="signup_pw")
            confirm_password = st.text_input("Password dobara likhein", type="password", key="signup_pw2")
            submitted_signup = st.form_submit_button("Account Banayein", type="primary")
        if submitted_signup:
            if not new_email.strip() or not new_password:
                st.error("Email aur password dono zaroori hain.")
            elif len(new_password) < 6:
                st.error("Password kam az kam 6 characters ka hona chahiye.")
            elif new_password != confirm_password:
                st.error("Dono passwords match nahi kar rahe.")
            else:
                try:
                    status = sign_up(new_email.strip(), new_password)
                    if status == "logged_in":
                        st.success("Account ban gaya! Aap login ho chuke hain.")
                        st.rerun()
                    else:
                        st.success("Account ban gaya. Apni email check karein aur confirmation link par click karein, phir Login tab se sign in karein.")
                except Exception as error:
                    message = str(error)
                    if "already registered" in message.lower() or "already exists" in message.lower():
                        st.error("Ye email pehle se registered hai. Login tab use karein.")
                    else:
                        st.error(f"Account nahi ban saka: {error}")


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
        ["Party", bill["party"], "Launch", bill["launch"]],
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
        "Launch": b["launch"], "Bill Amount": money(b["bill_amt"]),
        "Received": money(b["received"]), "Pending": money(b["pending"]),
        "Status": b["status"], "Remarks": b.get("remarks") or "",
    } for b in bills]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    if include_actions and bills:
        choices = {b["bill_no"]: b for b in bills}
        selected_no = st.selectbox("Invoice download ke liye bill select karein", list(choices), key="invoice_bill")
        selected = choices[selected_no]
        st.download_button("Download Invoice PDF", pdf_invoice(selected),
                           file_name=f"Invoice_{selected_no}.pdf", mime="application/pdf")


def new_bill_page():
    st.header("Naya Bill")
    st.caption("Bill number database se automatic banta hai aur edit nahi ho sakta.")
    names = parties()
    if not names:
        st.warning("Pehle sidebar se party/customer add karein.")
        return
    with st.form("new_bill", clear_on_submit=True):
        col1, col2 = st.columns(2)
        bill_date = col1.date_input("Date", value=date.today())
        party = col2.selectbox("Party / Customer", names)
        launch = col1.text_input("Launch Name")
        amount = col2.number_input("Bill Amount (Rs.)", min_value=0.0, step=100.0)
        remarks = st.text_input("Remarks")
        submitted = st.form_submit_button("Bill Add Karein", type="primary")
    if submitted:
        if not launch.strip() or amount <= 0:
            st.error("Launch Name aur valid Bill Amount zaroori hain.")
            return
        result = get_client().table("bills").insert({
            "date": bill_date.isoformat(), "party": party, "launch": launch.strip(),
            "bill_amt": amount, "remarks": remarks.strip(),
        }).execute()
        st.success(f"Bill {result.data[0]['bill_no']} add ho gaya.")


def bills_page(bills):
    st.header("Tamam Bills")
    term = st.text_input("Search: party, launch ya bill number")
    if term:
        key = term.lower()
        bills = [b for b in bills if key in " ".join(str(b.get(x, "")) for x in ("party", "launch", "bill_no", "remarks")).lower()]
    show_bill_table(bills)


def payments_page(bills):
    st.header("Payment Receive")
    pending_bills = [b for b in bills if b["pending"] > 0.01]
    if not pending_bills:
        st.info("Koi pending bill nahi hai.")
        return
    lookup = {f"{b['bill_no']} — {b['party']} (Pending: {money(b['pending'])})": b for b in pending_bills}
    selected_label = st.selectbox("Bill select karein", list(lookup))
    bill = lookup[selected_label]
    with st.form("payment", clear_on_submit=True):
        col1, col2 = st.columns(2)
        payment_date = col1.date_input("Payment Date", value=date.today())
        amount = col2.number_input("Receive Now (Rs.)", min_value=0.0, max_value=float(bill["pending"]), step=100.0)
        note = st.text_input("Note")
        submitted = st.form_submit_button("Save Payment", type="primary")
    if submitted:
        if amount <= 0:
            st.error("Receive amount zero se zyada honi chahiye.")
            return
        get_client().table("payments").insert({"bill_id": bill["id"], "date": payment_date.isoformat(), "amount": amount, "note": note.strip()}).execute()
        st.success("Payment save ho gayi.")
        st.rerun()


def ledger_page(bills):
    st.header("Party Ledger")
    names = parties()
    if not names:
        return
    party = st.selectbox("Party select karein", names)
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
            name = st.text_input("Nayi party")
            add = st.form_submit_button("Add Party")
        if add:
            try:
                get_client().table("parties").insert({"name": name.strip()}).execute()
                st.success("Party add ho gayi.")
                st.rerun()
            except Exception:
                st.error("Party ka naam blank ya duplicate hai.")


def main():
    if not current_user():
        auth_screen()
        return

    try:
        bills = bills_with_totals()
    except KeyError:
        st.error("Supabase secrets missing hain. README.md mein setup steps dekhein.")
        return
    except Exception as error:
        st.error(f"Database connect nahi ho saka: {error}")
        return

    st.sidebar.markdown("## ⚡ LedgerFlowPro")
    st.sidebar.caption("Professional Billing System")
    st.sidebar.caption("By Shehzad Kazama")
    st.sidebar.markdown(f"**Logged in:** {current_user()['email']}")
    if st.sidebar.button("Logout"):
        log_out()

    page = st.sidebar.radio("Menu", ["Dashboard", "Naya Bill", "Bills", "Payments", "Party Ledger"])
    party_manager()

    st.sidebar.markdown("---")
    st.sidebar.markdown("<p style='font-size: 11px; color: gray;'>© 2026 LedgerFlowPro<br>Owned by Shehzad Kazama</p>", unsafe_allow_html=True)

    if page == "Dashboard":
        dashboard(bills)
    elif page == "Naya Bill":
        new_bill_page()
    elif page == "Bills":
        bills_page(bills)
    elif page == "Payments":
        payments_page(bills)
    else:
        ledger_page(bills)


if __name__ == "__main__":
    main()
