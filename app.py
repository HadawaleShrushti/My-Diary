from flask import Flask, render_template, request, redirect, session, jsonify
from datetime import datetime
import sqlite3
from datetime import datetime
app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# 🛠️ Database setup
def init_db():
    conn = sqlite3.connect("diary.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS entries 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, created_at TEXT)''')
    # Add test user only once
    c.execute("SELECT * FROM users WHERE username=?", ("shru",))
    if not c.fetchone():
        c.execute("INSERT INTO users VALUES (?, ?)", ("shru", "mypinkdiary"))
    conn.commit()
    conn.close()

init_db()

# 🏠 Home (Show titles only)
@app.route('/')
@app.route('/')
def index():
    if 'username' in session:
        today = datetime.now().strftime("%Y-%m-%d")  # e.g. "2025-07-28"
        conn = sqlite3.connect("diary.db")
        c = conn.cursor()
        c.execute("SELECT id, title, content, created_at FROM entries ORDER BY created_at DESC")
        entries = c.fetchall()
        conn.close()

        # Filter entries for today
        today_entries = []
        for entry in entries:
            entry_date = entry[3][:10]  # '2025-07-28 14:30:00' → '2025-07-28'
            if entry_date == today:
                created_at = datetime.strptime(entry[3], "%Y-%m-%d %H:%M:%S")
                formatted_time = created_at.strftime("%b %d, %Y — %I:%M %p")
                today_entries.append((entry[0], entry[1], entry[2], formatted_time))

        return render_template("home.html", entries=today_entries)
    
    return redirect('/login')


# 🔐 Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        conn = sqlite3.connect("diary.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (uname, pwd))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = uname
            return redirect('/')
    return render_template("login.html")

# ✍ Write
@app.route('/write', methods=['GET', 'POST'])
def write():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect("diary.db")
        c = conn.cursor()
        c.execute("INSERT INTO entries (title, content, created_at) VALUES (?, ?, ?)", 
                  (title, content, now))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template("write.html")

# 🔓 Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

# 📅 For calendar (return just the dates)
@app.route('/entry-dates')
def entry_dates():
    conn = sqlite3.connect("diary.db")
    c = conn.cursor()
    c.execute("SELECT created_at FROM entries")
    rows = c.fetchall()
    conn.close()
    dates = [datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d") for r in rows]
    return jsonify(dates)


# 👁 View single entry
@app.route('/view/<int:entry_id>')
def view_entry(entry_id):
    conn = sqlite3.connect('diary.db')
    c = conn.cursor()
    c.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
    entry = c.fetchone()
    conn.close()
    if entry:
        return render_template('view.html', entry=entry)
    else:
        return "Entry not found", 404


@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    conn = sqlite3.connect("diary.db")
    c = conn.cursor()

    if request.method == 'POST':
        new_title = request.form['title']
        new_content = request.form['content']
        c.execute("UPDATE entries SET title = ?, content = ? WHERE id = ?", 
                  (new_title, new_content, entry_id))
        conn.commit()
        conn.close()
        return redirect(f'/view/{entry_id}')
    
    c.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
    entry = c.fetchone()
    conn.close()
    if entry:
        return render_template("edit.html", entry=entry)
    else:
        return "Entry not found", 404

@app.route('/delete/<int:entry_id>')
def delete_entry(entry_id):
    conn = sqlite3.connect("diary.db")
    c = conn.cursor()
    c.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    return redirect('/')

#for db

# ✅ Run the app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)  

