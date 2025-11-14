import sys
import os

print("Current directory:", os.getcwd())
print("\nPython path:")
for p in sys.path:
    print(f"  {p}")

print("\nFiles in current directory:")
for f in os.listdir('.'):
    if f.endswith('.py'):
        print(f"  {f}")

print("\nTrying to from src.business import isdoc_service...")
try:
    from src.business import isdoc_service
    print("SUCCESS: isdoc imported")
    print(f"isdoc location: {isdoc_service.__file__}")
except ModuleNotFoundError as e:
    print(f"FAILED: {e}")