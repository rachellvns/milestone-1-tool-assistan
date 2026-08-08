from tools.files import run


print("TEST 1: Read CSV")
print(run({"path": "expenses.csv"}))


print("\nTEST 2: Read text file")
print(run({"path": "notes.txt"}))


print("\nTEST 3: Missing file")
print(run({"path": "missing.csv"}))


print("\nTEST 4: Path traversal")
print(run({"path": "../secret.txt"}))


print("\nTEST 5: Absolute path")
print(run({"path": "/etc/passwd"}))