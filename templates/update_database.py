import sqlite3

conn = sqlite3.connect("car_rental.db")
cursor = conn.cursor()

try:
    cursor.execute("""
    ALTER TABLE bookings
    ADD COLUMN booking_id TEXT
    """)

    print("✅ booking_id column added successfully!")

except sqlite3.OperationalError:
    print("ℹ️ booking_id column already exists.")

conn.commit()
conn.close()