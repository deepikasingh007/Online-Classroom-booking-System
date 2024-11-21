from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
import MySQLdb

app = Flask(__name__)
app.secret_key = 'this_is_a_secret_key'

# Initialize MySQL
app.config['MYSQL_HOST'] = 'localhost' 
app.config['MYSQL_USER'] = 'root'       
app.config['MYSQL_PASSWORD'] = '543212345'  
app.config['MYSQL_DB'] = 'classroom_booking'  

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        teacher_name = session.get('teacher_name', 'User')
        phone_number = session.get('phone_number')
        return render_template('dashboard.html', teacher_name=teacher_name, phone_number=phone_number)
    else:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM teachers WHERE phone_number = %s", [phone_number])
        teacher = cur.fetchone()
        cur.close()

        if teacher:
            session['loggedin'] = True
            session['phone_number'] = teacher[2]  # Storing the phone number in session
            session['teacher_name'] = teacher[1]  # Storing teacher name
            session['teacher_id'] = teacher[0]  # Storing teacher ID
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Phone number not registered, please register first.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM classrooms")
    classrooms = cur.fetchall()

    now = datetime.now()
    for classroom in classrooms:
        cur.execute(""" 
            SELECT * FROM bookings 
            WHERE classroom_id = %s 
              AND start_time <= %s 
              AND end_time > %s
        """, (classroom['id'], now, now))
        
        booking = cur.fetchone()
        if booking:
            classroom['status'] = 'Occupied'
        else:
            classroom['status'] = 'Available'

        cur.execute(""" 
            UPDATE classrooms SET status = %s WHERE id = %s 
        """, (classroom['status'], classroom['id']))
    
    mysql.connection.commit()
    cur.close()

    return render_template('booking.html', classrooms=classrooms)

@app.route('/book/<int:classroom_id>', methods=['GET', 'POST'])
def book_classroom(classroom_id):
    if request.method == 'POST':
        branch = request.form['branch']
        duration = int(request.form['duration'])
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration)
        phone_number = session.get('phone_number')  
        teacher_id = session.get('teacher_id')  

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM teachers WHERE id = %s", (teacher_id,))
        teacher = cur.fetchone()

        if not teacher:
            return "Teacher not found."

        cur.execute(""" 
            SELECT * FROM bookings 
            WHERE classroom_id = %s 
              AND ((start_time < %s AND end_time > %s) 
                   OR (start_time < %s AND end_time > %s))
        """, (classroom_id, start_time, start_time, end_time, end_time))

        existing_booking = cur.fetchone()
        if existing_booking:
            cur.close()
            return "Classroom is already booked during the requested time."

        cur.execute(""" 
            INSERT INTO bookings (classroom_id, branch, start_time, end_time, teacher_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (classroom_id, branch, start_time, end_time, teacher_id))

        cur.execute(""" 
            UPDATE classrooms SET status = 'Occupied' WHERE id = %s 
        """, (classroom_id,))
        
        mysql.connection.commit()
        cur.close()

        return render_template('success.html', message="Classroom booked successfully!")

    return render_template('book_classroom.html')

@app.route('/view_bookings')
def view_bookings():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT
            bookings.id AS booking_id,
            bookings.classroom_id,
            teachers.name AS teacher_name,
            classrooms.room_name,
            bookings.branch,
            bookings.start_time,
            bookings.end_time
        FROM
            bookings
        JOIN
            teachers ON bookings.teacher_id = teachers.id
        JOIN
            classrooms ON bookings.classroom_id = classrooms.id
    """)
    bookings = cur.fetchall()
    cur.close()
    return render_template('view_bookings.html', bookings=bookings)

@app.route('/my_bookings')
def my_bookings():
    if 'loggedin' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('login'))
    
    teacher_id = session.get('teacher_id')  
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Using JOIN to retrieve room_name from classrooms
    cur.execute("""
        SELECT bookings.*, classrooms.room_name 
        FROM bookings 
        JOIN classrooms ON bookings.classroom_id = classrooms.id
        WHERE bookings.teacher_id = %s
    """, (teacher_id,))
    bookings = cur.fetchall()
    cur.close()
    return render_template('my_bookings.html', bookings=bookings)


@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 'loggedin' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('login'))
    
    teacher_id = session['teacher_id']  
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(""" 
        SELECT * FROM bookings 
        WHERE id = %s
    """, (booking_id,))
    booking = cur.fetchone()

    if booking and booking['teacher_id'] == teacher_id:
        cur.execute(""" 
            DELETE FROM bookings 
            WHERE id = %s 
        """, (booking_id,))

        if 'classroom_id' in booking:
            cur.execute(""" 
                UPDATE classrooms 
                SET status = 'Available' 
                WHERE id = %s
            """, (booking['classroom_id'],))
        
        mysql.connection.commit()
        flash("Booking canceled successfully!", "success")
    else:
        flash("Booking not found or you don't have permission to cancel it.", "danger")
    
    cur.close()
    return redirect(url_for('my_bookings'))


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

@app.route('/profile')
def profile():
    if 'loggedin' not in session:
        flash("Please log in to view your profile.", "warning")
        return redirect(url_for('login'))

    teacher_id = session.get('teacher_id')  # Get teacher's ID from the session
    if not teacher_id:
        flash("Teacher ID not found in session.", "danger")
        return redirect(url_for('login'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT name, phone_number, subject FROM teachers WHERE id = %s", (teacher_id,))
    teacher = cur.fetchone()
    cur.close()

    if teacher:
        return render_template('profile.html', teacher=teacher)
    else:
        flash("Teacher not found.", "danger")
        return redirect(url_for('login'))


@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'loggedin' not in session:
        flash("Please log in to update your profile.", "warning")
        return redirect(url_for('login'))

    teacher_id = session.get('teacher_id')
    if not teacher_id:
        flash("Teacher ID not found in session.", "danger")
        return redirect(url_for('login'))

    new_phone_number = request.form['phone_number']
    new_subject = request.form['subject']

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE teachers
        SET phone_number = %s, subject = %s
        WHERE id = %s
    """, (new_phone_number, new_subject, teacher_id))
    mysql.connection.commit()
    cur.close()

    flash("Profile updated successfully!", "success")
    return redirect(url_for('profile'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        phone_number = request.form['phone_number']
        subject = request.form['subject']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO teachers (name, phone_number, subject) VALUES (%s, %s, %s)", 
                    (name, phone_number, subject))
        mysql.connection.commit()
        cur.close()
        flash(f"Teacher {name} registered successfully!")
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
