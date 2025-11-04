import hid
import json

def make_json_safe(obj):
    """Convert all non-serializable types (bytes, enums, etc.) to strings"""
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_safe(i) for i in obj]
    elif isinstance(obj, bytes):
        try:
            return obj.decode("utf-8", errors="ignore")
        except Exception:
            return str(obj)
    elif not isinstance(obj, (str, int, float, bool, type(None))):
        return str(obj)
    else:
        return obj

devices = hid.enumerate()
for d in devices:
    clean = make_json_safe(d)
    print(json.dumps(clean, indent=2, ensure_ascii=False))
    print("-" * 70)
