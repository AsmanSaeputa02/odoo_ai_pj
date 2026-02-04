# Debug setup (comment out ถ้าไม่ต้องการ debug)
try:
    import debugpy
    if not debugpy.is_client_connected():
        debugpy.listen(("0.0.0.0", 5678))
        print("🔍 Debugger listening on port 5678...")
        print("💡 Attach VSCode debugger now!")
except Exception as e:
    print(f"⚠️ Debug setup failed (ignored): {e}")

from . import models