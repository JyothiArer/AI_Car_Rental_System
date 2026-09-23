import sqlite3

conn = sqlite3.connect("car_rental.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE bookings (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    booking_id TEXT,

    name TEXT,

    phone TEXT,

    car TEXT,

    pickup TEXT,

    drop_location TEXT,

    pickup_date TEXT,

    drop_date TEXT,

    pickup_time TEXT,

    drop_time TEXT,

    rental_days INTEGER,

    total_price INTEGER,

    status TEXT

)
""")

conn.commit()
conn.close()

print("✅ Database Created Successfully")