from flask import Flask, render_template, request
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
import MySQLdb

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'  # Change if your MySQL host is different
app.config['MYSQL_USER'] = 'root'       # Your MySQL username
app.config['MYSQL_PASSWORD'] = '12345678'  # Your MySQL password
app.config['MYSQL_DB'] = 'classroom_booking'  # The name of your database

# Initialize MySQL
mysql = MySQL(app)

# Home Page Route
@app.route('/')
def home():
    return render_template('home.html')  # This will render the home page

# Booking Page Route
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # Use DictCursor for better access
    cur.execute("SELECT id, room_name, capacity, projector_available, status FROM classrooms WHERE status = 'Empty' OR status = 'Available'")
    classrooms = cur.fetchall()
    cur.close()
    return render_template('booking.html', classrooms=classrooms)

# Book a Classroom Route
@app.route('/book/<int:classroom_id>', methods=['GET', 'POST'])
def book_classroom(classroom_id):
    if request.method == 'POST':
        # Get the booking details
        branch = request.form['branch']
        duration = int(request.form['duration'])
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration)

        # Convert to string for query
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

        # Check if the classroom is already booked during this time
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT * FROM bookings
            WHERE classroom_id = %s
              AND (
                (start_time < %s AND end_time > %s)
                OR
                (start_time < %s AND end_time > %s)
                OR
                (start_time >= %s AND end_time <= %s)
            );
        """, (classroom_id, start_time_str, start_time_str, end_time_str, end_time_str, start_time_str, end_time_str))

        existing_booking = cur.fetchone()
        if existing_booking:
            return "Classroom is already booked during the requested time. Please choose a different time."

        # Proceed with the booking if the classroom is available
        cur.execute("""
            INSERT INTO bookings (classroom_id, branch, start_time, end_time)
            VALUES (%s, %s, %s, %s);
        """, (classroom_id, branch, start_time_str, end_time_str))

        # Update the classroom status to 'Occupied' after booking
        cur.execute("""
            UPDATE classrooms 
            SET status = 'Occupied'
            WHERE id = %s;
        """, (classroom_id,))

        mysql.connection.commit()
        cur.close()

        return "Classroom successfully booked!"

    return render_template('book_classroom.html')

# Complaints Page Route
@app.route('/complaints', methods=['GET', 'POST'])
def complaints():
    if request.method == 'POST':
        classroom = request.form['classroom']
        issue = request.form['issue']
        contact = request.form['contact']

        # Store the complaint in the database
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO complaints (classroom, issue, contact)
            VALUES (%s, %s, %s)
        """, (classroom, issue, contact))
        mysql.connection.commit()
        cur.close()

        return "Your complaint has been submitted successfully!"

    # Fetch technician contact details
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT name, contact_number FROM technicians")
    technicians = cur.fetchall()
    cur.close()

    return render_template('complaints.html', technicians=technicians)

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM teachers WHERE phone_number = %s", [phone_number])
        teacher = cur.fetchone()
        cur.close()

        if teacher:
            return f"Logged in as {teacher[1]} with phone number: {phone_number}"
        else:
            return "Phone number not registered, please register first."
    return render_template('login.html')

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        phone_number = request.form['phone_number']
        subject = request.form['subject']

        # Logic to insert teacher data into the database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO teachers (name, phone_number, subject) VALUES (%s, %s, %s)", 
                    (name, phone_number, subject))
        mysql.connection.commit()
        cur.close()

        return f"Teacher {name} registered successfully!"

    return render_template('register.html')

# Run the app
if __name__ == "__main__":
    app.run(debug=True)