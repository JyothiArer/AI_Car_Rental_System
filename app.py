import matplotlib.pyplot as plt
from flask import Flask, render_template, request, send_file
import sqlite3
from datetime import datetime
from reportlab.pdfgen import canvas

app = Flask(__name__)

# ---------------- AI DYNAMIC PRICING ----------------

def calculate_dynamic_price(base_price, demand):

    if demand == "Low":
        return base_price

    elif demand == "Medium":
        return int(base_price * 1.10)

    elif demand == "High":
        return int(base_price * 1.25)

    return base_price


# ---------------- HOME PAGE ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- BOOKING PAGE ----------------

@app.route("/booking")
def booking():

    car = request.args.get("car")
    price = request.args.get("price")

    return render_template(
        "booking.html",
        car=car,
        price=price
    )


# ---------------- BOOKING SUCCESS ----------------

@app.route("/success", methods=["POST"])
def success():

    name = request.form["name"]
    phone = request.form["phone"]
    

    car = request.form["car"]
    price = int(request.form["price"])

    pickup = request.form["pickup"]
    pickup_area = request.form["pickup_area"]

    drop = request.form["drop"]
    drop_area = request.form["drop_area"]

    pickup_date = request.form["pickup_date"]
    drop_date = request.form["drop_date"]

    pickup_time = request.form["pickup_time"]
    drop_time = request.form["drop_time"]

    pickup_obj = datetime.strptime(pickup_date, "%Y-%m-%d")
    drop_obj = datetime.strptime(drop_date, "%Y-%m-%d")

    rental_days = (drop_obj - pickup_obj).days

    if rental_days <= 0:
        rental_days = 1

    # ---------------- AI SMART PRICE ----------------

    ai_price = price

    # Weekend Charges

    pickup_day = pickup_obj.weekday()

    if pickup_day in [5, 6]:
        pricing_type = "Weekend"
        ai_price += 500
    else:
        pricing_type = "Weekday"

# ---------------- AI Demand Prediction ----------------

    demand = "Normal"

    if pickup == "Kempegowda Airport":

        ai_price += 700

        demand = "High"

    elif pickup_area == "Majestic":

        ai_price += 300

        demand = "Medium"

    elif pickup_area == "Electronic City":

        ai_price += 200

        demand = "Medium"

    elif pickup_area == "Whitefield":

        ai_price += 250

        demand = "Medium"

    # Luxury Car Extra Charge

    if car == "Toyota Innova":

        ai_price += 500

    elif car == "Mahindra XUV700":

        ai_price += 1000

        # ---------------- AI DYNAMIC PRICING ----------------
       
        ai_price = calculate_dynamic_price(ai_price, demand)
    
        # ---------------- Long Rental Discount ----------------

    if rental_days >= 5:
        ai_price = int(ai_price * 0.90)

    # ---------------- Final Price ----------------

    total_price = ai_price * rental_days

    # ---------------- Database ----------------

    conn = sqlite3.connect("car_rental.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM bookings")
    count = cursor.fetchone()[0] + 1

    booking_id = f"CRB{1000 + count}"

    cursor.execute("""
    INSERT INTO bookings
    (
        booking_id,
        name,
        phone,
        car,
        pickup,
        drop_location,
        pickup_date,
        drop_date,
        pickup_time,
        drop_time,
        rental_days,
        total_price,
        status
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        booking_id,
        name,
        phone,
        car,
        pickup,
        drop,
        pickup_date,
        drop_date,
        pickup_time,
        drop_time,
        rental_days,
        total_price,
        "Booked"
    ))

    conn.commit()
    conn.close()

    return render_template(
        "success.html",
        booking_id=booking_id,
        name=name,
        phone=phone,
        car=car,
        price=ai_price,
        pricing_type=pricing_type,
        pickup=pickup,
        pickup_area=pickup_area,
        drop=drop,
        drop_area=drop_area,
        pickup_date=pickup_date,
        drop_date=drop_date,
        pickup_time=pickup_time,
        drop_time=drop_time,
        rental_days=rental_days,
        total_price=total_price,
        status="Booked",
        demand=demand
    )
# ---------------- ADMIN PAGE ----------------

@app.route("/admin")
def admin():

    conn = sqlite3.connect("car_rental.db")
    cursor = conn.cursor()

    # ALL bookings - columns in the exact order needed by admin.html
    cursor.execute("""
        SELECT
            booking_id,
            name,
            phone,
            car,
            pickup,
            drop_location,
            pickup_date,
            drop_date,
            rental_days,
            total_price,
            status
        FROM bookings
    """)

    bookings = cursor.fetchall()

    # Total ACTIVE bookings only
    cursor.execute("""
        SELECT COUNT(*)
        FROM bookings
        WHERE status = 'Booked'
    """)

    total_bookings = cursor.fetchone()[0]

    # Total revenue from ACTIVE bookings only
    cursor.execute("""
        SELECT SUM(total_price)
        FROM bookings
        WHERE status = 'Booked'
    """)

    revenue = cursor.fetchone()[0]

    if revenue is None:
        revenue = 0

    # Most booked car from ACTIVE bookings only
    cursor.execute("""
        SELECT car, COUNT(car)
        FROM bookings
        WHERE status = 'Booked'
        GROUP BY car
        ORDER BY COUNT(car) DESC
        LIMIT 1
    """)

    car = cursor.fetchone()

    if car:
        most_booked_car = car[0]
    else:
        most_booked_car = "No Booking"

    conn.close()

    return render_template(
        "admin.html",
        bookings=bookings,
        total_bookings=total_bookings,
        revenue=revenue,
        most_booked_car=most_booked_car
    )

# ---------------- AI RECOMMENDATION ----------------

@app.route("/recommend", methods=["POST"])
def recommend():

    purpose = request.form["purpose"]

    if purpose == "family":
        car = "Toyota Innova"
        reason = "Best for 6-7 members with comfortable seating."

    elif purpose == "budget":
        car = "Maruti Swift"
        reason = "Affordable and fuel efficient."

    elif purpose == "luxury":
        car = "Mahindra XUV700"
        reason = "Premium SUV with luxury features."

    elif purpose == "offroad":
        car = "Mahindra Thar"
        reason = "Perfect for off-road adventures."

    elif purpose == "longdrive":
        car = "Hyundai Creta"
        reason = "Comfortable for long journeys."

    else:
        car = "Hyundai Creta"
        reason = "Recommended for general travel."

    return render_template(
        "recommend.html",
        car=car,
        reason=reason
    )

# ---------------- AI CHATBOT ----------------

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():

    answer = ""

    if request.method == "POST":

        question = request.form["question"]
        question = question.lower()

        if "family" in question:
            answer = "🚗 Toyota Innova is a good choice for family trips because it has spacious seating for 6–7 members."

        elif "cheap" in question or "budget" in question:
            answer = "💰 Maruti Swift is our most budget-friendly car, with a base price of ₹1800 per day."

        elif "luxury" in question:
            answer = "👑 Mahindra XUV700 is our premium SUV with advanced features. Its base price is ₹4200 per day."

        elif "off" in question or "thar" in question:
            answer = "🏔️ Mahindra Thar is suitable for off-road adventures. Its base price is ₹3500 per day."

        elif "car" in question and ("available" in question or "cars" in question):
            answer = "🚗 We currently offer Hyundai Creta, Mahindra Thar, Maruti Swift, Kia Seltos, Tata Nexon, Toyota Innova, Honda City, MG Hector, Hyundai Venue and Mahindra XUV700."

        elif "price" in question or "cost" in question or "rate" in question:
            answer = "💵 Our car prices start from ₹1800 per day for Maruti Swift. The price varies depending on the selected car and rental conditions."

        elif "pickup" in question or "drop" in question or "location" in question:
            answer = "📍 You can select your pickup and drop location while making your booking."

        elif "day" in question or "days" in question or "duration" in question:
            answer = "📅 You can select your pickup date and drop date while booking. The rental price is calculated based on the rental duration."

        elif "passenger" in question or "people" in question or "person" in question:
            answer = "👥 Please select a vehicle that provides enough seating space for the number of people travelling."

        elif "payment" in question or "pay" in question:
            answer = "💳 Payment details can be handled according to the booking process of the rental system."

        elif "receipt" in question or "pdf" in question:
            answer = "🧾 After a successful booking, the system generates a booking receipt in PDF format."

        elif "weekend" in question:
            answer = "🔥 Weekend bookings may have an additional charge because the system applies dynamic pricing based on the booking conditions."

        elif "discount" in question:
            answer = "💰 For longer rentals, the system provides a discount when the rental duration is 5 days or more."

        elif "recommend" in question or "suggest" in question or "best car" in question:
            answer = "🤖 Our system can recommend a suitable car based on your requirement, such as family trip, budget, luxury, off-road adventure or long drive."

        elif "cancel" in question:
            answer = "❌ Yes. You can cancel your booking from the available cancellation option in the system."

        elif "document" in question or "license" in question:
            answer = "📄 A valid Driving License and Aadhaar Card or other Government ID Proof may be required."

        elif "time" in question or "office" in question:
            answer = "🕘 Our booking support is available from 9:00 AM to 9:00 PM every day."

        else:
            answer = "😊 Sorry, I couldn't understand your question. Please ask me about cars, prices, booking, locations, rental duration, documents, cancellation or recommendations."

    return render_template(
        "chatbot.html",
        answer=answer
    )

# ---------------- DOWNLOAD RECEIPT ----------------

@app.route("/download_receipt")
def download_receipt():

    conn = sqlite3.connect("car_rental.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT booking_id,
           name,
           phone,
           car,
           pickup,
           drop_location,
           pickup_date,
           drop_date,
           rental_days,
           total_price
    FROM bookings
    ORDER BY id DESC
    LIMIT 1
    """)

    booking = cursor.fetchone()

    conn.close()

    pdf_file = "Booking_Receipt.pdf"

    c = canvas.Canvas(pdf_file)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(140, 800, "AI Car Rental Booking Receipt")

    c.setFont("Helvetica", 12)

    labels = [
        "Booking ID",
        "Customer Name",
        "Phone Number",
        "Selected Car",
        "Pickup Location",
        "Drop Location",
        "Pickup Date",
        "Drop Date",
        "Rental Days",
        "Total Amount"
    ]

    y = 760

    for i in range(len(labels)):
        c.drawString(50, y, f"{labels[i]} : {booking[i]}")
        y -= 30

    c.drawString(
        50,
        y - 20,
        "Thank you for choosing AI Car Rental Booking System!"
    )

    c.save()

    return send_file(
        pdf_file,
        as_attachment=True
    )
# ---------------- CANCEL BOOKING ----------------

@app.route("/cancel_booking", methods=["POST"])
def cancel_booking():

    booking_id = request.form["booking_id"]

    conn = sqlite3.connect("car_rental.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE bookings SET status=? WHERE booking_id=?",
        ("Cancelled", booking_id)
    )

    conn.commit()
    conn.close()

    return f"""
    <h2 style='color:red;text-align:center;margin-top:80px;'>
    ❌ Booking {booking_id} Cancelled Successfully!
    </h2>

    <center>

    <br>

    <a href="/admin">
        <button style="padding:12px 25px;background:#0d6efd;
        color:white;border:none;border-radius:8px;">
            Open Admin Dashboard
        </button>
    </a>

    <br><br>

    <a href="/">
        <button style="padding:12px 25px;background:green;
        color:white;border:none;border-radius:8px;">
            Back To Home
        </button>
    </a>

    </center>
    """

# ---------------- BOOKINGS CHART ----------------

@app.route("/chart")
def chart():

    conn = sqlite3.connect("car_rental.db")
    cursor = conn.cursor()

    # Count ACTIVE bookings for each car
    cursor.execute("""
        SELECT car, COUNT(*)
        FROM bookings
        WHERE status = 'Booked'
        GROUP BY car
        
    """)

    data = cursor.fetchall()
    print("CHART DATA:",data)

    conn.close()

    cars = [row[0] for row in data]
    counts = [row[1] for row in data]

    # Create chart
    plt.figure(figsize=(10, 6))

    plt.bar(cars, counts)

    plt.title("🚗 Active Bookings by Car")
    plt.xlabel("Car")
    plt.ylabel("Number of Active Bookings")

    plt.xticks(rotation=30)

    plt.tight_layout()

    chart_path = "static/bookings_chart.png"

    plt.savefig(chart_path)
    plt.close()

    return render_template(
        "chart.html",
        chart="bookings_chart.png"
    )
# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app.run(debug=True)