import hid

TARGET_NAME = "VGN F1 MOBA"
TARGET_VID = 13652
TARGET_PID = 62726

print("🔍 Поиск мыши...")

devices = hid.enumerate()
target = None

for d in devices:
    if (
        d.get("vendor_id") == TARGET_VID and
        d.get("product_id") == TARGET_PID and
        TARGET_NAME.lower() in (d.get("product_string") or "").lower()
    ):
        target = d
        break

if not target:
    print("❌ Подходящий интерфейс мыши не найден")
else:
    print(f"✅ Найдена мышь: {target['product_string']}")
    print(f"   VID: 0x{target['vendor_id']:04x}, PID: 0x{target['product_id']:04x}, Interface: {target['interface_number']}")
    
    try:
        h = hid.device()
        h.open_path(target["path"])
        print("✅ Успешно подключено к устройству!")
        h.close()
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

print("\n🔒 Завершено")
