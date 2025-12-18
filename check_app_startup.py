import sys
import os
import time

print("Diagnostics: Starting...")

# 1. Check Paths
print("Diagnostics: Checking paths...")
print(f"CWD: {os.getcwd()}")
BACKEND_DIR = os.path.join(os.getcwd(), 'Backend')
sys.path.append(BACKEND_DIR)
VERIDIA_CORE_DIR = os.path.join(os.getcwd(), 'VeridiaCore')

if not os.path.exists(VERIDIA_CORE_DIR):
    print(f"ERROR: VeridiaCore not found at {VERIDIA_CORE_DIR}")
    sys.exit(1)

# 2. Check Imports
print("Diagnostics: Importing modules...")
try:
    from VeridiaCore.engine import SearchEngine
    print("  Import SearchEngine: OK")
except Exception as e:
    print(f"  Import SearchEngine: FAILED ({e})")
    sys.exit(1)

# 3. Check Initialization
print("Diagnostics: Initializing SearchEngine...")
try:
    start = time.time()
    engine = SearchEngine(VERIDIA_CORE_DIR)
    print(f"  Initialization took {time.time() - start:.2f}s")
except Exception as e:
    print(f"  Initialization FAILED ({e})")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Diagnostics: Engine Loaded Successfully.")
print("Diagnostics: Attempting imports for App...")
try:
    from flask import Flask
    print("  Import Flask: OK")
except Exception as e:
    print(f"  Import Flask: FAILED ({e})")

print("Diagnostics: All checks passed. The app SHOOULD run.")
