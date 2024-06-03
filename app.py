from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key'

# Create or connect to the database
conn = sqlite3.connect('pharmacy.db', check_same_thread=False)
cursor = conn.cursor()

# Create tables if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS medicines(
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        manufacturer TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        expiry_date TEXT NOT NULL
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bills(
        id INTEGER PRIMARY KEY,
        medicine_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        total_cost REAL NOT NULL,
        date TEXT NOT NULL
    )
''')
conn.commit()

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add_medicine():
    if request.method == 'POST':
        name = request.form['name']
        manufacturer = request.form['manufacturer']
        quantity = int(request.form['quantity'])
        expiry_date = request.form['expiry_date']

        try:
            expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return redirect(url_for('add_medicine'))

        cursor.execute('INSERT INTO medicines (name, manufacturer, quantity, expiry_date) VALUES (?, ?, ?, ?)',
                       (name, manufacturer, quantity, expiry_date))
        conn.commit()
        flash('Medicine added successfully!', 'success')
        return redirect(url_for('add_medicine'))

    return render_template('add_medicine.html')

@app.route('/delete', methods=['GET', 'POST'])
def delete_medicine():
    if request.method == 'POST':
        id = int(request.form['id'])
        cursor.execute('DELETE FROM medicines WHERE id=?', (id,))
        conn.commit()
        flash('Medicine deleted successfully!', 'success')
        return redirect(url_for('delete_medicine'))

    cursor.execute('SELECT * FROM medicines')
    medicines = cursor.fetchall()
    return render_template('delete_medicine.html', medicines=medicines)

@app.route('/update', methods=['GET', 'POST'])
def update_medicine():
    if request.method == 'POST':
        id = int(request.form['id'])
        name = request.form['name']
        manufacturer = request.form['manufacturer']
        quantity = int(request.form['quantity'])
        expiry_date = request.form['expiry_date']

        try:
            expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return redirect(url_for('update_medicine'))

        cursor.execute('''
            UPDATE medicines
            SET name = ?, manufacturer = ?, quantity = ?, expiry_date = ?
            WHERE id = ?
        ''', (name, manufacturer, quantity, expiry_date, id))
        conn.commit()
        flash('Medicine updated successfully!', 'success')
        return redirect(url_for('update_medicine'))

    cursor.execute('SELECT * FROM medicines')
    medicines = cursor.fetchall()
    return render_template('update_medicine.html', medicines=medicines)

@app.route('/bill', methods=['GET', 'POST'])
def generate_bill():
    if request.method == 'POST':
        medicine_name = request.form['medicine_name']
        quantity = int(request.form['quantity'])
        price_per_unit = float(request.form['price_per_unit'])
        total_cost = quantity * price_per_unit
        date = datetime.now().strftime('%Y-%m-%d')

        cursor.execute('INSERT INTO bills (medicine_name, quantity, total_cost, date) VALUES (?, ?, ?, ?)',
                       (medicine_name, quantity, total_cost, date))
        conn.commit()
        flash('Bill generated successfully!', 'success')
        return redirect(url_for('generate_bill'))

    cursor.execute('SELECT * FROM medicines')
    medicines = cursor.fetchall()
    return render_template('generate_bill.html', medicines=medicines)

@app.route('/view_bills', methods=['GET', 'POST'])
def view_bills():
    if request.method == 'POST':
        bill_id = int(request.form['bill_id'])
        cursor.execute('DELETE FROM bills WHERE id=?', (bill_id,))
        conn.commit()
        flash('Bill deleted successfully!', 'success')
        return redirect(url_for('view_bills'))
    
    cursor.execute('SELECT * FROM bills')
    bills = cursor.fetchall()
    return render_template('view_bills.html', bills=bills)

@app.route('/view_medicines')
def view_medicines():
    cursor.execute('SELECT * FROM medicines')
    medicines = cursor.fetchall()
    return render_template('view_medicines.html', medicines=medicines)

if __name__ == '__main__':
    app.run(debug=True)
