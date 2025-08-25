# ui/main_ui.py

import tkinter as tk
from tkinter import ttk, messagebox
from utils import db_utils, calculator
import pandas as pd
from datetime import datetime
import os

class RestaurantBillingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Billing System")
        self.root.geometry("800x600")

        # Variables
        self.order_items = []
        self.dine_mode = tk.StringVar(value="Dine-In")
        self.payment_method = tk.StringVar(value="Cash")

        # Load menu
        self.menu_items = db_utils.fetch_menu()

        # UI Setup
        self.create_widgets()

    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="Restaurant Billing System",
                         font=("Arial", 20, "bold"), bg="black", fg="white")
        title.pack(fill=tk.X)

        # Dine-in / Takeaway selection
        mode_frame = tk.Frame(self.root, pady=10)
        mode_frame.pack()
        tk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="Dine-In", variable=self.dine_mode, value="Dine-In").pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="Takeaway", variable=self.dine_mode, value="Takeaway").pack(side=tk.LEFT)

        # Menu Tree
        self.tree = ttk.Treeview(self.root, columns=("Price", "GST"), show="headings", height=10)
        self.tree.heading("Price", text="Price (₹)")
        self.tree.heading("GST", text="GST %")
        self.tree.pack(pady=10)

        for item in self.menu_items:
            self.tree.insert("", tk.END, values=(f"{item[2]:.2f}", f"{item[3]}"), text=item[1])

        # Quantity + Add
        control_frame = tk.Frame(self.root, pady=10)
        control_frame.pack()
        tk.Label(control_frame, text="Quantity:").pack(side=tk.LEFT)
        self.qty_var = tk.IntVar(value=1)
        qty_entry = tk.Entry(control_frame, textvariable=self.qty_var, width=5)
        qty_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Add Item", command=self.add_item).pack(side=tk.LEFT)

        # Order List
        self.order_listbox = tk.Listbox(self.root, width=80, height=10)
        self.order_listbox.pack(pady=10)

        # Payment method
        payment_frame = tk.Frame(self.root, pady=10)
        payment_frame.pack()
        tk.Label(payment_frame, text="Payment:").pack(side=tk.LEFT)
        tk.Radiobutton(payment_frame, text="Cash", variable=self.payment_method, value="Cash").pack(side=tk.LEFT)
        tk.Radiobutton(payment_frame, text="Card", variable=self.payment_method, value="Card").pack(side=tk.LEFT)
        tk.Radiobutton(payment_frame, text="UPI", variable=self.payment_method, value="UPI").pack(side=tk.LEFT)

        # Buttons
        btn_frame = tk.Frame(self.root, pady=10)
        btn_frame.pack()
        tk.Button(btn_frame, text="Generate Bill", command=self.generate_bill, bg="green", fg="white").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Clear Order", command=self.clear_order, bg="red", fg="white").pack(side=tk.LEFT, padx=10)

        # Bill Area
        self.bill_text = tk.Text(self.root, width=80, height=15, bg="lightyellow")
        self.bill_text.pack(pady=10)

    def add_item(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a menu item first!")
            return

        item_name = self.tree.item(selected, "text")
        item_values = self.tree.item(selected, "values")
        price = float(item_values[0])
        gst = float(item_values[1])
        qty = self.qty_var.get()

        if qty <= 0:
            messagebox.showwarning("Warning", "Quantity must be at least 1")
            return

        self.order_items.append((item_name, price, gst, qty))
        self.order_listbox.insert(tk.END, f"{item_name} x {qty} — ₹{price*qty:.2f}")

    def clear_order(self):
        self.order_items.clear()
        self.order_listbox.delete(0, tk.END)
        self.bill_text.delete(1.0, tk.END)

    def generate_bill(self):
        if not self.order_items:
            messagebox.showerror("Error", "No items in order!")
            return

        subtotal, gst_amount, discount, total = calculator.calculate_bill(self.order_items)

        # Save order in DB
        order_id = db_utils.save_order(self.dine_mode.get(), self.payment_method.get(),
                                       subtotal, gst_amount, discount, total, self.order_items)

        # Bill Text
        self.bill_text.delete(1.0, tk.END)
        self.bill_text.insert(tk.END, f"Order ID: {order_id}\n")
        self.bill_text.insert(tk.END, f"Mode: {self.dine_mode.get()}\n")
        self.bill_text.insert(tk.END, f"Payment: {self.payment_method.get()}\n")
        self.bill_text.insert(tk.END, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.bill_text.insert(tk.END, "-"*50 + "\n")
        for item in self.order_items:
            self.bill_text.insert(tk.END, f"{item[0]} x {item[3]} = ₹{item[1]*item[3]:.2f}\n")
        self.bill_text.insert(tk.END, "-"*50 + "\n")
        self.bill_text.insert(tk.END, f"Subtotal: ₹{subtotal:.2f}\n")
        self.bill_text.insert(tk.END, f"GST: ₹{gst_amount:.2f}\n")
        self.bill_text.insert(tk.END, f"Discount: -₹{discount:.2f}\n")
        self.bill_text.insert(tk.END, f"Total: ₹{total:.2f}\n")

        messagebox.showinfo("Success", "Bill Generated & Saved!")

if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantBillingApp(root)
    root.mainloop()
