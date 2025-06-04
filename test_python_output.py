import sys
print("Test: Standard output from Python script.")
print("Test: Error output from Python script.", file=sys.stderr)
sys.exit(0)
