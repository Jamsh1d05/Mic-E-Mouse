import hid
for d in hid.enumerate():
    print(f"VID: {d['vendor_id']:04x}, PID: {d['product_id']:04x}, Interface: {d.get('interface_number')}, Usage Page: {d.get('usage_page')}, Usage: {d.get('usage')}, Product: {d.get('product_string')}")


#VID: 3554, PID: f506, Interface: 2, Usage Page: 1, Usage: 2, Product: VGN F1 MOBA