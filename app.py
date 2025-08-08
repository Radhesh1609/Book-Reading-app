# book_tracker_remember_me.py

import streamlit as st
import json
import os
import base64
from datetime import date

USERS_FILE = "users.json"
BOOKS_FILE = "reading.json"
CONFIG_FILE = "config.json"

# Password Helpers
def encode_password(password):
    return base64.b64encode(password.encode()).decode()

def decode_password(encoded):
    return base64.b64decode(encoded.encode()).decode()

# JSON Helpers
def load_json(file, default):
    if os.path.exists(file):
        try:
            with open(file, "r") as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# Book Data
def get_user_books(username):
    all_books = load_json(BOOKS_FILE, [])
    return [b for b in all_books if b.get("user") == username]

def save_user_books(username, books):
    all_books = load_json(BOOKS_FILE, [])
    all_books = [b for b in all_books if b.get("user") != username]
    all_books.extend(books)
    save_json(BOOKS_FILE, all_books)

# Styling
def apply_custom_style():
    st.markdown("""
        <style>
            body {
                background: linear-gradient(to right, #fceabb, #f8b500);
            }
            .stButton>button {
                font-size: 16px;
                border-radius: 10px;
                padding: 10px;
                background-color: #4CAF50;
                color: white;
            }
            .stButton>button:hover {
                background-color: #45a049;
            }
            .stTextInput>div>div>input,
            .stNumberInput>div>div>input,
            .stSelectbox>div>div>div,
            .stDateInput>div>div>input {
                font-size: 16px;
                border-radius: 8px;
                padding: 8px;
            }
        </style>
    """, unsafe_allow_html=True)

# Pages
def signup_page():
    st.header("🔐 Sign Up")
    username = st.text_input("Create Username")
    password = st.text_input("Create Password", type="password")
    if st.button("Create Account"):
        users = load_json(USERS_FILE, {})
        if username in users:
            st.error("Username already exists.")
        elif not username.strip() or not password:
            st.warning("Please enter both username and password.")
        else:
            users[username] = encode_password(password)
            save_json(USERS_FILE, users)
            st.success("Account created. Please login.")
            st.session_state.page = "login"
            st.rerun()

def login_page():
    st.header("🔑 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    remember = st.checkbox("Remember Me")

    if st.button("Login"):
        users = load_json(USERS_FILE, {})
        encoded_pwd = users.get(username)
        if encoded_pwd and decode_password(encoded_pwd) == password:
            st.session_state.user = username
            st.session_state.page = "language"
            save_json(CONFIG_FILE, {
                "username": username,
                "remember": remember
            })
            st.rerun()
        else:
            st.error("Invalid credentials.")
    if st.button("Go to Sign Up"):
        st.session_state.page = "signup"
        st.rerun()

def language_selection_page():
    st.header("🌐 Choose Language / भाषा चुनें")
    col1, col2 = st.columns(2)
    if col1.button("English"):
        st.session_state.lang = "English"
        st.session_state.page = "welcome"
        st.rerun()
    if col2.button("हिन्दी"):
        st.session_state.lang = "Hindi"
        st.session_state.page = "welcome"
        st.rerun()

def welcome_page():
    lang = st.session_state.get("lang", "English")
    username = st.session_state.get("user", "User")
    if lang == "Hindi":
        st.title(f"👋 स्वागत है, {username}!")
        st.write("आप सफलतापूर्वक लॉगिन हो गए हैं। अपनी लाइब्रेरी देखें 📚")
        if st.button("मेनू पर जाएं"):
            st.session_state.page = "menu"
            st.rerun()
    else:
        st.title(f"👋 Welcome, {username}!")
        st.write("You are now logged in. Let’s explore your library 📚")
        if st.button("Continue to Menu"):
            st.session_state.page = "menu"
            st.rerun()

def menu_page():
    lang = st.session_state.get("lang", "English")
    st.header("📋 मेनू" if lang == "Hindi" else "📋 Main Menu")
    col1, col2 = st.columns(2)
    if col1.button("📚 पुस्तक ट्रैकर" if lang == "Hindi" else "📚 Book Tracker"):
        st.session_state.page = "tracker"
        st.session_state.tracker_subpage = "home"
        st.rerun()
    if col2.button("🚪 लॉगआउट" if lang == "Hindi" else "🚪 Logout"):
        st.session_state.clear()
        save_json(CONFIG_FILE, {})
        st.session_state.page = "login"
        st.rerun()

def tracker_router():
    subpage = st.session_state.get("tracker_subpage", "home")
    if subpage == "home":
        book_tracker_home()
    elif subpage == "add":
        book_add_page()
    elif subpage == "list":
        book_list_page()

def book_tracker_home():
    st.title("📖 Book Tracker Menu")
    col1, col2 = st.columns(2)
    if col1.button("➕ Add New Book"):
        st.session_state.tracker_subpage = "add"
        st.rerun()
    if col2.button("📚 View Your Books"):
        st.session_state.tracker_subpage = "list"
        st.rerun()
    if st.button("⬅️ Back to Main Menu"):
        st.session_state.page = "menu"
        st.rerun()

def book_add_page():
    st.header("➕ Add New Book")
    books = get_user_books(st.session_state.user)

    with st.form("add_book_form"):
        title = st.text_input("Book Title")
        page = st.number_input("Pages Read", min_value=0, step=1)
        total = st.number_input("Total Pages", min_value=1, step=1)
        status = st.selectbox("Status", ["To Read", "Reading", "Completed"])
        deadline = st.date_input("Deadline", value=date.today())
        favorite = st.checkbox("Favorite ⭐")
        submitted = st.form_submit_button("Add Book")
        if submitted:
            if not title.strip():
                st.warning("Enter a book title.")
            else:
                books.append({
                    "title": title.strip(),
                    "page": page,
                    "total": total,
                    "status": status,
                    "deadline": str(deadline),
                    "favorite": favorite,
                    "user": st.session_state.user
                })
                save_user_books(st.session_state.user, books)
                st.success(f"Book '{title}' added!")
                st.rerun()

    if st.button("⬅️ Back"):
        st.session_state.tracker_subpage = "home"
        st.rerun()

def book_list_page():
    st.header("📚 Your Book List")
    books = get_user_books(st.session_state.user)

    search = st.text_input("Search by Title")
    status_filter = st.selectbox("Filter by Status", ["All", "To Read", "Reading", "Completed"])
    only_fav = st.checkbox("⭐ Show Only Favorites")

    filtered = []
    for book in books:
        match_title = search.lower() in book["title"].lower()
        match_status = (status_filter == "All") or (book["status"] == status_filter)
        match_fav = (not only_fav) or book["favorite"]
        if match_title and match_status and match_fav:
            filtered.append(book)

    for idx, book in enumerate(filtered):
        st.markdown(f"### {'⭐' if book['favorite'] else ''} {book['title']}")
        st.write(f"Status: {book['status']} | Pages: {book['page']}/{book['total']}")
        progress = int((book['page'] / book['total']) * 100)
        st.progress(progress)
        st.write(f"📅 Deadline: {book['deadline']}")

        with st.expander("✏️ Edit or 🗑️ Delete"):
            with st.form(f"edit_form_{idx}"):
                new_title = st.text_input("Edit Title", value=book["title"])
                new_page = st.number_input("Edit Pages Read", value=book["page"], min_value=0)
                new_total = st.number_input("Edit Total Pages", value=book["total"], min_value=1)
                new_status = st.selectbox("Edit Status", ["To Read", "Reading", "Completed"], index=["To Read", "Reading", "Completed"].index(book["status"]))
                new_deadline = st.date_input("Edit Deadline", value=date.fromisoformat(book["deadline"]))
                new_fav = st.checkbox("Favorite ⭐", value=book["favorite"])
                col1, col2 = st.columns(2)
                if col1.form_submit_button("Save Changes"):
                    book.update({
                        "title": new_title,
                        "page": new_page,
                        "total": new_total,
                        "status": new_status,
                        "deadline": str(new_deadline),
                        "favorite": new_fav
                    })
                    save_user_books(st.session_state.user, books)
                    st.success("Book updated.")
                    st.rerun()
                if col2.form_submit_button("Delete Book"):
                    books.remove(book)
                    save_user_books(st.session_state.user, books)
                    st.success("Book deleted.")
                    st.rerun()

    if st.button("⬅️ Back"):
        st.session_state.tracker_subpage = "home"
        st.rerun()

def app():
    apply_custom_style()

    if "page" not in st.session_state:
        st.session_state.page = "login"

    if "user" not in st.session_state:
        cfg = load_json(CONFIG_FILE, {})
        if cfg.get("remember") and cfg.get("username"):
            st.session_state.user = cfg["username"]
            st.session_state.page = "language"

    page = st.session_state.page

    if page == "signup":
        signup_page()
    elif page == "login":
        login_page()
    elif page == "language":
        language_selection_page()
    elif page == "welcome":
        welcome_page()
    elif page == "menu":
        menu_page()
    elif page == "tracker":
        tracker_router()
    else:
        st.session_state.page = "login"

if __name__ == "__main__":
    app()
