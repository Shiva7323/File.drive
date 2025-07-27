#!/usr/bin/env python3

try:
    print("Testing Flask app import...")
    from app import app
    print("✓ App imported successfully")
    
    print("Testing routes import...")
    import routes
    print("✓ Routes imported successfully")
    
    print("Testing app context...")
    with app.app_context():
        print("✓ App context works")
    
    print("All tests passed! The application should start successfully.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 