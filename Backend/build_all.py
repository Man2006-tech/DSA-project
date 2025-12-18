"""
Veridia Search Engine - Complete Build Script
Runs all indexing steps in sequence
"""
import sys
import time
from build_index_fast import build_indices_optimized
from build_inverted_fast import build_inverted_index_optimized


def main():
    """Run complete indexing pipeline."""
    print("\n" + "="*70)
    print(" "*15 + "VERIDIA SEARCH ENGINE")
    print(" "*20 + "COMPLETE BUILD")
    print("="*70 + "\n")
    
    total_start = time.time()
    
    try:
        # Step 1: Build lexicon, forward index, and metadata
        print("STEP 1: Building Lexicon, Forward Index, and Metadata")
        print("-"*70)
        step1_start = time.time()
        
        stats = build_indices_optimized()
        
        step1_time = time.time() - step1_start
        print(f"\n✓ Step 1 completed in {step1_time:.2f} seconds\n")
        
        # Step 2: Build inverted index
        print("\nSTEP 2: Building Inverted Index")
        print("-"*70)
        step2_start = time.time()
        
        build_inverted_index_optimized()
        
        step2_time = time.time() - step2_start
        print(f"\n✓ Step 2 completed in {step2_time:.2f} seconds\n")
        
        # Final summary
        total_time = time.time() - total_start
        
        print("\n" + "="*70)
        print(" "*20 + "BUILD SUMMARY")
        print("="*70)
        print(f"Total Documents Indexed: {stats['docs']:,}")
        print(f"Unique Words in Lexicon: {stats['words']:,}")
        print(f"Total Build Time: {total_time:.2f} seconds ({total_time/60:.1f} minutes)")
        print(f"Average Speed: {stats['docs']/total_time:.1f} documents/second")
        print("\n✓ All indices built successfully!")
        print("\nYou can now run: python app.py")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ BUILD FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)