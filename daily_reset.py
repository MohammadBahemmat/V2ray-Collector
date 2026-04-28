import os
if os.path.exists("checkpoint.json"):
    os.remove("checkpoint.json")
    print("Checkpoint reset for daily full scan.")
else:
    print("No checkpoint to reset.")
