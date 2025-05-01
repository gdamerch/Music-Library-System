from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2

# Create a Flask application and specify the template folder path
app = Flask(__name__, template_folder="../templates")
app.secret_key = "this_is_a_key"  # Needed for session usage

# Database connection
def get_connection():
    return psycopg2.connect(
        host="localhost",
        port="8888",
        database="project_demo",
        user="joeyb",
        password="3861"
    )

# Login page is the start page
@app.route("/")
def index():
    return redirect(url_for("login"))

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT u_username FROM users WHERE u_email=%s AND u_password=%s",
            (email, password)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()
        # True, go to home page
        if user:
            session["username"] = user[0]  # Save username in session
            return redirect(url_for("home"))
        else:  # Or print error message
            error = "Invalid email or password"
    return render_template("login.html", error=error)

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        conn = get_connection()
        cur = conn.cursor()
        # Email addresses or user names cannot be repeated
        cur.execute("SELECT * FROM users WHERE u_email=%s OR u_username=%s", (email, username))
        existing_user = cur.fetchone()
        if existing_user:
            error = "Email or Username already exists"
        else:
            # Get the current maximum UID, plus 1
            cur.execute("SELECT MAX(u_uid) FROM users")
            max_id = cur.fetchone()[0] or 0
            new_id = max_id + 1
            # Insert new user
            cur.execute(
                "INSERT INTO users (u_uid, u_username, u_email, u_password) VALUES (%s, %s, %s, %s)",
                (new_id, username, email, password)
            )
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for("login"))
        cur.close()
        conn.close()
    return render_template("register.html", error=error)

# Home
@app.route("/home", methods=["GET"])
def home():
    # Get keyword
    keyword = request.args.get("keyword", "").strip()
    results = []
    # Retrieve the currently username from the session
    username = session.get("username", "Guest")
    message = request.args.get("message", "")
    conn = get_connection()
    cur = conn.cursor()
    # Query the corresponding user ID based on the username
    cur.execute("SELECT u_uid FROM users WHERE u_username = %s", (username,))
    user = cur.fetchone()
    if user:
        user_id = user[0]
        # Query all the playlists created by this user
        cur.execute("SELECT p_playlistid, p_title FROM playlist WHERE p_uid = %s", (user_id,))
        playlists = cur.fetchall()
    else:
        playlists = []
    # Search keyword
    if keyword:
        search = f"%{keyword}%"
        cur.execute("""
            SELECT S.S_Title, AR.AR_Name, AL.A_AlbumName, S.S_Genre, S.S_Duration, S.S_SongID
            FROM Song AS S
            JOIN Artist AS AR ON S.S_ArtistID = AR.AR_ArtistID
            JOIN Album AS AL ON S.S_AlbumID = AL.A_AlbumID
            WHERE S.S_Title ILIKE %s
               OR AR.AR_Name ILIKE %s
               OR S.S_Genre ILIKE %s
               OR Al.A_AlbumName ILIKE %s
        """, (search, search, search, search))
        results = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("home.html",
                           results=results,
                           keyword=keyword,
                           username=username,
                           playlists=playlists,
                           message=message)

@app.route("/add_to_playlist", methods=["POST"])
def add_to_playlist():
    playlist_id = request.form["playlist_id"]
    song_id = request.form["song_id"]
    conn = get_connection()
    cur = conn.cursor()
    # Get current user name (from session)
    username = session.get("username", "Guest")
    message = ""
    # Check whether the song already exists
    cur.execute("""
        SELECT * FROM playlistsong
        WHERE ps_playlistid = %s AND ps_songid = %s
    """, (playlist_id, song_id))
    exists = cur.fetchone()
    # If not exist, add to playlist
    if not exists:
        cur.execute("""
            INSERT INTO playlistsong (ps_playlistid, ps_songid)
            VALUES (%s, %s)
        """, (playlist_id, song_id))
        conn.commit()
        message = "Song added to playlist"
    else:
        message = "Song already exists in playlist"
    cur.close()
    conn.close()
    # Return home
    return redirect(url_for("home", message=message))

# look up user id from session 
def get_current_user_id():
    username = session.get("username")
    if not username:
        return None
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT u_uid FROM users WHERE u_username = %s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else None

@app.route("/playlist", methods=["GET"])
def playlist_index():
    user_id = get_current_user_id()
    if user_id is None:
        return redirect(url_for("login"))
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT p_playlistid, p_title, p_creationdate FROM playlist WHERE p_uid = %s",
                (user_id,))
    raw = cur.fetchall()
    cur.close()
    conn.close()

    playlists = [
        {"id": row[0], "title": row[1], "creation_date": row[2]}
        for row in raw
    ]
    return render_template("playlists.html", playlists=playlists)

@app.route("/playlist/<int:pid>", methods=["GET"])
def playlist_detail(pid):
    user_id = get_current_user_id()
    if user_id is None:
        return redirect(url_for("login"))

    conn = get_connection()
    cur = conn.cursor()

    # Fetch playlist metadata (optionally verify p_uid= user_id)
    cur.execute("SELECT p_title FROM playlist WHERE p_playlistid = %s AND p_uid = %s",
                (pid, user_id))
    p = cur.fetchone()
    if not p:
        cur.close()
        conn.close()
        flash("Playlist not found.", "danger")
        return redirect(url_for("playlist_index"))
    playlist = {"id": pid, "title": p[0]}

    # Fetch the songs currently in this playlist
    cur.execute("""
      SELECT S.S_SongID, S.S_Title, AR.AR_Name, AL.A_Name, S.S_Duration
      FROM playlistsong PS
      JOIN song S     ON PS.ps_songid   = S.S_SongID
      JOIN artist AR  ON S.S_ArtistID   = AR.AR_ArtistID
      JOIN album AL   ON S.S_AlbumID    = AL.A_AlbumID
      WHERE PS.ps_playlistid = %s
    """, (pid,))
    songs = [
      {"id": r[0], "title": r[1], "artist_name": r[2], "album_name": r[3], "duration": r[4]}
      for r in cur.fetchall()
    ]

    # Fetch all songs for the “Add a Song” dropdown
    cur.execute("""
      SELECT S.S_SongID, S.S_Title, AR.AR_Name
      FROM song S
      JOIN artist AR ON S.S_ArtistID = AR.AR_ArtistID
      ORDER BY S.S_Title
    """)
    all_songs = [
      {"id": r[0], "title": r[1], "artist_name": r[2]}
      for r in cur.fetchall()
    ]

    cur.close()
    conn.close()
    return render_template("playlist_detail.html",
                           playlist=playlist,
                           songs=songs,
                           all_songs=all_songs)

# remove a song from a playlist
@app.route("/playlist/<int:pid>/remove/<int:sid>", methods=["POST"])
def remove_song(pid, sid):
    user_id = get_current_user_id()
    if user_id is None:
        return redirect(url_for("login"))
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
      DELETE FROM playlistsong
      WHERE ps_playlistid = %s AND ps_songid = %s
    """, (pid, sid))
    conn.commit()
    cur.close()
    conn.close()
    flash("Song removed.", "info")
    return redirect(url_for("playlist_detail", pid=pid))

# Start the Flask application
if __name__ == "__main__":
    app.run(debug=True)
