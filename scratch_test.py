import os
import glob
print("Workspace:", os.getcwd())
# Let's count how many files or items are present
with open("레딧 핵심통증.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
print("Lines in 레딧 핵심통증.txt:", len(lines))
