# utils/calculator.py
def calculate_totals(order_items):
    subtotal = 0
    gst_amount = 0
    for item in order_items:
        subtotal += item['price'] * item['quantity']
        gst_amount += (item['price'] * item['quantity']) * (item['gst'] / 100)

    total = subtotal + gst_amount
    return {
        'subtotal': round(subtotal, 2),
        'gst': round(gst_amount, 2),
        'total': round(total, 2)
    }
