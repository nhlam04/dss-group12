"""
Quick Start Script - Charity Fund Decision Support System
Run this to see the system in action immediately
"""

print("""
================================================================================
                                                                            
         CHARITY FUND DECISION SUPPORT SYSTEM - QUICK START                
                                                                            
================================================================================

This system helps you allocate limited charity funds to grant requests
using multi-criteria decision analysis and optimization.

WHAT IT DOES:
* Ranks grant requests using 7 weighted criteria (TOPSIS algorithm)
* Optimizes fund allocation using multiple strategies
* Maximizes impact while respecting budget constraints
* Provides transparent, explainable decisions

NEXT STEPS:
1. Review the sample output below
2. Try 'python interactive_cli.py' for custom data input
3. Read USER_GUIDE.md for detailed instructions
4. Modify example_usage.py for your own scenarios

--------------------------------------------------------------------------------

RUNNING DEMONSTRATION WITH SAMPLE DATA...

""")

# Import and run the example
from example_usage import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[STOP] Demo interrupted by user.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("\nPlease ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
