import sqlite3

conn = sqlite3.connect("car_rental.db")
cursor = conn.cursor()

try:
    cursor.execute("""
        ALTER TABLE bookings
        ADD COLUMN status TEXT
    """)
    print("✅ Status column added successfully!")

except sqlite3.OperationalError:
    print("ℹ️ Status column already exists.")

conn.commit()
conn.close()