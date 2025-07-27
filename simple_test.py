print("Starting test...")

try:
    from app import app
    print("✓ App imported")
    
    from models import User
    print("✓ User model imported")
    
    print("✓ All imports successful!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc() 