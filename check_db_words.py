"""Check database for specific words to understand lemma forms."""
import sys
import io
import sqlite3

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect('src/marathi_pratham/data/dictionary.db')
cursor = conn.cursor()

# Check for water-related words
print("Searching for water-related words:")
cursor.execute("SELECT Key, Meaning1 FROM MarathiEnglish WHERE Meaning1 LIKE '%पाण%' OR Key LIKE '%pan%' LIMIT 10")
for row in cursor.fetchall():
    print(f"  {row[0]} → {row[1]}")

# Check for boy-related words
print("\nSearching for boy-related words:")
cursor.execute("SELECT Key, Meaning1 FROM MarathiEnglish WHERE Meaning1 LIKE '%मुल%' OR Key LIKE '%mul%' LIMIT 10")
for row in cursor.fetchall():
    print(f"  {row[0]} → {row[1]}")

# Check what "pani" maps to
print("\nChecking 'pani' key:")
cursor.execute("SELECT Key, Meaning1, Meaning2 FROM MarathiEnglish WHERE Key = 'pani'")
row = cursor.fetchone()
if row:
    print(f"  {row[0]} → {row[1]} ({row[2]})")
else:
    print("  Not found")

# Check what "mul" maps to
print("\nChecking 'mul' key:")
cursor.execute("SELECT Key, Meaning1, Meaning2 FROM MarathiEnglish WHERE Key = 'mul'")
row = cursor.fetchone()
if row:
    print(f"  {row[0]} → {row[1]} ({row[2]})")
else:
    print("  Not found")

# Check for पाणी directly
print("\nChecking for 'पाणी' in Meaning1:")
cursor.execute("SELECT Key, Meaning1, Meaning2 FROM MarathiEnglish WHERE Meaning1 = 'पाणी'")
for row in cursor.fetchall():
    print(f"  {row[0]} → {row[1]} ({row[2]})")

conn.close()
