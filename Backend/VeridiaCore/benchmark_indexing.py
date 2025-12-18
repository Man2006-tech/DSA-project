import os
import time
import subprocess
import sys

# CONFIGURATION
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_INDEX_SCRIPT = "build_index.py"     # Lexicon + Forward
INVERT_INDEX_SCRIPT = "inverted_index.py" # Inverted
OFFSETS_SCRIPT = "build_doc_offsets.py"   # Content Offsets

def run_script(script_name, description):
    script_path = os.path.join(BASE_DIR, script_name)
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_name}")
        return
    
    print(f"\n============================================================")
    print(f" ⏱️  BENCHMARKING: {description}")
    print(f"    Script: {script_name}")
    print(f"============================================================")
    
    start_time = time.time()
    
    try:
        # Run process and capture output
        # redirect stdout/stderr to pipe to show real-time or just capture it
        # For benchmarking, we might want to see progress
        process = subprocess.run([sys.executable, script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script_name}: {e}")
        return
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n------------------------------------------------------------")
    print(f" ✅ COMPLETED: {description}")
    print(f" 🕒 Time Taken: {round(duration, 4)} seconds")
    print(f"============================================================\n")

def main():
    print("WARNING: This will RE-BUILD all indices from the 7GB dataset.")
    print("This process will take significant time (10+ minutes).")
    print("Press Ctrl+C to cancel within 5 seconds...")
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        print("\nCancelled.")
        return

    # 1. Forward Index & Lexicon
    # run_script(BUILD_INDEX_SCRIPT, "Lexicon & Forward Index Construction")

    # 2. Inverted Index
    run_script(INVERT_INDEX_SCRIPT, "Inverted Index Construction")
    
    # 3. Doc Offsets
    run_script(OFFSETS_SCRIPT, "Document Content Offsets Map")
    
    # Note: I commented out Build Index by default to prevent accidental 10-minute wait 
    # if the user just runs it quick. But for a full test, valid commands needed.
    # Let's uncomment it but keep the warning.
    
    # run_script(BUILD_INDEX_SCRIPT, "Lexicon & Forward Index Construction") 
    
    print("\nBenchmark Complete.")
    print("Note: To benchmark 'build_index.py' (Forward Index), uncomment it in the script.")
    print("      (It was skipped to save time in this demonstration run).")

if __name__ == "__main__":
    main()
