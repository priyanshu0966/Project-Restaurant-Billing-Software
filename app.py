# app.py
# Run: streamlit run app.py

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import io

# Import utils (make sure utils/calculator.py and utils/db_utils.py exist)
from utils.calculator import calculate_totals
from utils.db_utils import init_db, get_menu, add_menu_item, save_order

# Ensure DB and folders exist
init_db()
os.makedirs("bills", exist_ok=True)

st.set_page_config(page_title="Restaurant Billing", page_icon="🍽️", layout="wide")

# ---------- Helper UI functions ----------
def load_menu_dataframe():
    rows = get_menu()
    if not rows:
        return pd.DataFrame(columns=["item_name", "category", "price", "gst"])
    df = pd.DataFrame(rows, columns=["item_name", "category", "price", "gst"])
    return df

def add_csv_to_menu(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        return
    required = {"item_name", "category", "price", "gst"}
    if not required.issubset(set(df.columns)):
        st.error("CSV must contain columns: item_name, category, price, gst")
        return
    # Insert row by row (uses add_menu_item)
    for _, r in df.iterrows():
        try:
            add_menu_item(str(r["item_name"]), str(r["category"]), float(r["price"]), float(r["gst"]))
        except Exception:
            # ignore duplicates/failures
            pass
    st.success("Menu uploaded/merged successfully.")

def export_bill_csv(bill, filename=None):
    df = pd.DataFrame(bill["items"])
    if filename is None:
        filename = f"bill_{bill['order_id'] if 'order_id' in bill else 'temp'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8"), filename

def export_bill_pdf(bill, filename=None):
    try:
        from fpdf import FPDF
    except Exception as e:
        return None, "FPDF not installed. Install with: pip install fpdf"

    if filename is None:
        filename = f"bill_{bill['order_id'] if 'order_id' in bill else 'temp'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    path = os.path.join("bills", filename)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Restaurant Bill", ln=True, align="C")
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, f"Date: {bill.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}", ln=True)
    pdf.cell(0, 8, f"Mode: {bill.get('mode','')}", ln=True)
    pdf.cell(0, 8, f"Payment: {bill.get('payment_method','')}", ln=True)
    pdf.ln(4)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(80, 8, "Item", border=1)
    pdf.cell(20, 8, "Qty", border=1)
    pdf.cell(30, 8, "Price", border=1)
    pdf.cell(20, 8, "GST%", border=1)
    pdf.cell(40, 8, "Line Total", border=1, ln=True)
    pdf.set_font("Arial", size=11)

    for it in bill["items"]:
        pdf.cell(80, 8, str(it["item_name"]), border=1)
        pdf.cell(20, 8, str(it["quantity"]), border=1)
        pdf.cell(30, 8, f"{it['price']:.2f}", border=1)
        pdf.cell(20, 8, f"{it.get('gst',0.0):.1f}", border=1)
        pdf.cell(40, 8, f"{it['line_total']:.2f}", border=1, ln=True)

    pdf.ln(4)
    pdf.cell(0, 8, f"Subtotal: {bill.get('subtotal', 0.0):.2f}", ln=True)
    pdf.cell(0, 8, f"GST: {bill.get('gst', 0.0):.2f}", ln=True)
    pdf.cell(0, 8, f"Grand Total: {bill.get('total', 0.0):.2f}", ln=True)

    pdf.output(path)
    with open(path, "rb") as f:
        data = f.read()
    return data, filename

# ---------- Sidebar: admin ----------
with st.sidebar:
    st.title("Admin")
    st.write("Upload menu CSV (item_name,category,price,gst)")
    uploaded = st.file_uploader("Upload menu.csv to add/replace items", type=["csv"])
    if uploaded:
        add_csv_to_menu(uploaded)

    st.divider()
    if st.button("Reload Menu"):
        st.experimental_rerun()

# ---------- Main layout ----------
st.title("🍽️ Restaurant Billing")

menu_df = load_menu_dataframe()

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Create Order")
    mode = st.radio("Mode", ["Dine-In", "Takeaway"], horizontal=True)
    payment_method = st.selectbox("Payment Method", ["Cash", "Card", "UPI"])
    discount_pct = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)

    # Select item
    if menu_df.empty:
        st.warning("Menu is empty. Upload menu.csv in sidebar.")
    else:
        cats = ["All"] + sorted(menu_df["category"].dropna().unique().tolist())
        cat = st.selectbox("Category", cats)
        filtered = menu_df if cat == "All" else menu_df[menu_df["category"] == cat]
        item_name = st.selectbox("Item", filtered["item_name"].tolist())
        qty = st.number_input("Quantity", min_value=1, value=1, step=1)
        if st.button("Add to Cart"):
            cart = st.session_state.get("cart", [])
            row = filtered[filtered["item_name"] == item_name].iloc[0]
            cart.append({
                "item_name": row["item_name"],
                "category": row.get("category", ""),
                "price": float(row["price"]),
                "gst": float(row.get("gst", 0.0)),
                "quantity": int(qty),
                "line_total": round(float(row["price"]) * int(qty), 2)
            })
            st.session_state["cart"] = cart
            st.success(f"Added {item_name} x {qty} to cart.")

    # show cart with option to remove
    st.markdown("### Cart")
    cart = st.session_state.get("cart", [])
    if not cart:
        st.info("Cart is empty.")
    else:
        cart_df = pd.DataFrame(cart)
        st.dataframe(cart_df[["item_name", "quantity", "price", "gst", "line_total"]])

        # remove last item
        remove_col1, remove_col2 = st.columns([1,1])
        with remove_col1:
            if st.button("Remove Last Item"):
                cart.pop()
                st.session_state["cart"] = cart
                st.experimental_rerun()
        with remove_col2:
            if st.button("Clear Cart"):
                st.session_state["cart"] = []
                st.experimental_rerun()

with col2:
    st.subheader("Summary")
    cart = st.session_state.get("cart", [])
    if not cart:
        st.write("No items yet.")
        subtotal = gst = total = 0.0
    else:
        # calculator expects list of items with price, quantity, gst -> adjust to its API
        calc_input = []
        for it in cart:
            calc_input.append({
                "price": it["price"],
                "quantity": it["quantity"],
                "gst": it["gst"]
            })
        # Our simple calculator returns {'subtotal','gst','total'}
        totals = calculate_totals(calc_input)
        # apply discount
        subtotal = totals["subtotal"]
        gst = totals["gst"]
        discount_amt = subtotal * (discount_pct / 100.0)
        subtotal_after_discount = max(subtotal - discount_amt, 0.0)
        # recompute gst proportionally (simple adjustment)
        if subtotal > 0:
            gst = gst * (subtotal_after_discount / subtotal)
        total = round(subtotal_after_discount + gst, 2)

        st.write(f"Subtotal: ₹{subtotal:.2f}")
        st.write(f"Discount ({discount_pct}%): -₹{discount_amt:.2f}")
        st.write(f"GST: ₹{gst:.2f}")
        st.markdown(f"**Grand Total: ₹{total:.2f}**")

    st.markdown("---")
    if st.button("Complete Order"):
        if not cart:
            st.warning("Cannot complete order with empty cart.")
        else:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Prepare order_items in the format db expects
            order_items_to_save = []
            for it in cart:
                order_items_to_save.append({
                    "item_name": it["item_name"],
                    "quantity": it["quantity"],
                    "price": it["price"],
                    "gst": it["gst"]
                })
            # Save order to DB
            try:
                save_order(mode, payment_method, subtotal_after_discount, gst, total, ts, order_items_to_save)
                # Build bill dict for export/preview
                bill = {
                    "timestamp": ts,
                    "mode": mode,
                    "payment_method": payment_method,
                    "items": [{
                        "item_name": it["item_name"],
                        "quantity": it["quantity"],
                        "price": it["price"],
                        "gst": it["gst"],
                        "line_total": round(it["price"] * it["quantity"], 2)
                    } for it in cart],
                    "subtotal": round(subtotal_after_discount, 2),
                    "gst": round(gst, 2),
                    "total": round(total, 2)
                }
                st.session_state["last_bill"] = bill
                st.session_state["cart"] = []
                st.success("Order completed and saved to DB.")
            except Exception as e:
                st.error(f"Failed to save order: {e}")

    # Export last bill if present
    st.markdown("### Last Bill Export")
    last_bill = st.session_state.get("last_bill")
    if last_bill:
        st.write(f"Bill time: {last_bill['timestamp']}")
        csv_bytes, csv_name = export_bill_csv(last_bill)
        st.download_button("Download Bill CSV", data=csv_bytes, file_name=csv_name, mime="text/csv")

        pdf_data, pdf_msg = export_bill_pdf(last_bill)
        if pdf_data is None:
            st.warning(pdf_msg)
        else:
            st.download_button("Download Bill PDF", data=pdf_data, file_name=pdf_msg, mime="application/pdf")
    else:
        st.info("No recent bill to export.")

# ---------- Footer / quick admin ----------
st.markdown("---")
cols = st.columns([1, 2, 1])
with cols[0]:
    if st.button("Seed Example Menu (quick)"):
        # Add a few sample items if menu is empty
        sample = [
            ("Margherita Pizza", "Food", 250, 5),
            ("Paneer Butter Masala", "Food", 300, 5),
            ("Coke", "Drink", 50, 5),
            ("Ice Cream", "Dessert", 100, 5),
            ("Masala Dosa", "Food", 150, 5)
        ]
        for name, cat, price, gst in sample:
            try:
                add_menu_item(name, cat, price, gst)
            except Exception:
                pass
        st.success("Sample menu items added. Reloading...")
        st.experimental_rerun()

with cols[2]:
    if st.button("Show DB Menu"):
        st.write(load_menu_dataframe())
