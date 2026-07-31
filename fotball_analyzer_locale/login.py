
import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter.messagebox as messagebox
import json
import os
import hashlib
from datetime import datetime

base_dir = os.path.dirname(__file__)


# Initialize appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("color_login.json")

# User database file
USER_DB_FILE = os.path.join(base_dir, "users.json")

class AuthSystem:
    def __init__(self):
        self.users = self._load_users()
        
    def _load_users(self):
        if os.path.exists(USER_DB_FILE):
            with open(USER_DB_FILE, 'r') as f:
                return json.load(f)
        return {"users": []}
    
    def _save_users(self):
        with open(USER_DB_FILE, 'w') as f:
            json.dump(self.users, f, indent=4)
    
    def _hash_password(self, password):
        """Secure password hashing with salt"""
        salt = "football_analyzer_salt_2023"
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def register_user(self, email, password):
        """Register a new user with validation"""
        if not email or "@" not in email:
            return False, "Invalid email format"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
            
        if any(user['email'] == email for user in self.users['users']):
            return False, "Email already exists"
        
        self.users['users'].append({
            "email": email,
            "password": self._hash_password(password),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self._save_users()
        return True, "Registration successful!"
    
    def login_user(self, email, password):
        """Authenticate a user"""
        for user in self.users['users']:
            if user['email'] == email and user['password'] == self._hash_password(password):
                return True, "Login successful"
        return False, "Invalid email or password"


def login():
    email = email_entry.get()
    password = password_entry.get()
    
    auth = AuthSystem()
    success, message = auth.login_user(email, password)
    
    if success:
        app.destroy()
        gui_min_app()
    else:
        messagebox.showerror("Login Failed", message)



def show_register():
    register_window = ctk.CTkToplevel(app)
    register_window.title("Register")
    register_window.geometry("800x500")
    
    # Match login page design
    left_frame = ctk.CTkFrame(master=register_window, width=310, corner_radius=0)
    left_frame.pack(side="left", fill="both")
    
    right_frame = ctk.CTkFrame(master=register_window)
    right_frame.pack(side="right", fill="both", expand=True, padx=0, pady=0)
    
    # Same background image
    try:
        bg_image_path = os.path.join(base_dir, "assets", "purple_foot.jpg")
        bg_image = Image.open(bg_image_path)
        bg_image = bg_image.resize((400, 500))
        bg_image = ImageTk.PhotoImage(bg_image)
        bg_label = ctk.CTkLabel(left_frame, image=bg_image, text="")
        bg_label.pack(fill="both", expand=True)
    except Exception as e:
        ctk.CTkLabel(left_frame, text="Create Account").pack(expand=True)
    
    # Right frame content
    title = ctk.CTkLabel(right_frame, text="Create Account", font=ctk.CTkFont(size=24, weight="bold"))
    title.pack(pady=(40, 10))
    
    # Email field
    email_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
    email_frame.pack(pady=(10,0), padx=(100,0), anchor="w")
    
    try:
        email_icon_path = os.path.join(base_dir, "assets", "11908187.png")
        email_icon = ctk.CTkImage(Image.open(email_icon_path), size=(20,20))
        ctk.CTkLabel(email_frame, image=email_icon, text="", width=24).pack(side="left", padx=(0,6))
    except:
        pass
    ctk.CTkLabel(email_frame, text="Email", font=ctk.CTkFont(size=14)).pack(side="left")
    
    reg_email = ctk.CTkEntry(right_frame, width=300, placeholder_text="Email")
    reg_email.pack(pady=(0,10))
    
    # Password field
    password_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
    password_frame.pack(pady=(10,0), padx=(100,0), anchor="w")
    
    try:
        password_icon_path = os.path.join(base_dir, "assets", "7781678.png")
        password_icon = ctk.CTkImage(Image.open(password_icon_path), size=(20,20))
        ctk.CTkLabel(password_frame, image=password_icon, text="", width=24).pack(side="left", padx=(0,6))
    except:
        pass
    ctk.CTkLabel(password_frame, text="Password", font=ctk.CTkFont(size=14)).pack(side="left")
    
    reg_password = ctk.CTkEntry(right_frame, width=300, placeholder_text="Password (min 6 chars)", show="*")
    reg_password.pack(pady=(0,10))
    
    # Confirm Password field
    confirm_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
    confirm_frame.pack(pady=(10,0), padx=(100,0), anchor="w")
    
    try:
        ctk.CTkLabel(confirm_frame, image=password_icon, text="", width=24).pack(side="left", padx=(0,6))
    except:
        pass
    ctk.CTkLabel(confirm_frame, text="Confirm Password", font=ctk.CTkFont(size=14)).pack(side="left")
    
    reg_confirm = ctk.CTkEntry(right_frame, width=300, placeholder_text="Confirm Password", show="*")
    reg_confirm.pack(pady=(0,20))
    
    # Register button (same style as login button)
    def do_register():
        if reg_password.get() != reg_confirm.get():
            messagebox.showerror("Error", "Passwords don't match")
            return
            
        auth = AuthSystem()
        success, message = auth.register_user(reg_email.get(), reg_password.get())
        
        if success:
            messagebox.showinfo("Success", message)
            register_window.destroy()
        else:
            messagebox.showerror("Error", message)
    
    register_btn = ctk.CTkButton(
        right_frame, 
        text="Register", 
        command=do_register,
        hover_color="#8e44ad",
        width=300
    )
    register_btn.pack(pady=10)
    

   
    try:
        google_image_path = os.path.join(base_dir, "assets", "icons8-google-48.png")
        google_image = ctk.CTkImage(light_image=Image.open(google_image_path), size=(24,24))
    except:
        google_image = None
        
    google_btn = ctk.CTkButton(
        right_frame,
        text="Continue With Google",
        image=google_image,
        width=300,
        fg_color="#e0e0e0",
        text_color="black",
        hover_color="#bdc3c7"
    )
    google_btn.pack(pady=(0,10))
    
    # Already have account link
    login_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
    login_frame.pack(pady=(10,0))
    
    ctk.CTkLabel(login_frame, text="Already have an account?", font=ctk.CTkFont(size=12)).pack(side="left")
    login_link = ctk.CTkLabel(
        login_frame, 
        text="Login", 
        font=ctk.CTkFont(size=12, underline=True),
        text_color="#8e44ad",
        cursor="hand2"
    )
    login_link.pack(side="left", padx=5)
    login_link.bind("<Button-1>", lambda e: register_window.destroy())

def gui_min_app():
    import main 
    main.gui()

# Create main window (your original code)
app = ctk.CTk()
app.geometry("800x500")
app.title("Login Page")

# Split frame into left and right
left_frame = ctk.CTkFrame(master=app, width=310, corner_radius=0)
left_frame.pack(side="left", fill="both")

right_frame = ctk.CTkFrame(master=app)
right_frame.pack(side="right", fill="both", expand=True, padx=0, pady=0)

# Background image
try:
    bg_image_path = os.path.join(base_dir, "assets", "purple_foot.jpg")
    bg_image = Image.open(bg_image_path)
    bg_image = bg_image.resize((400, 500))
    bg_image = ImageTk.PhotoImage(bg_image)
    bg_label = ctk.CTkLabel(left_frame, image=bg_image, text="")
    bg_label.pack(fill="both", expand=True)
except Exception as e:
    ctk.CTkLabel(left_frame, text="Image not found").pack()

# Right Frame: Login Content
title = ctk.CTkLabel(right_frame, text="Welcome Back!", font=ctk.CTkFont(size=24, weight="bold"))
title.pack(pady=(20, 10))

subtitle = ctk.CTkLabel(right_frame, text="Sign in to your account", font=ctk.CTkFont(size=14))
subtitle.pack(pady=(0, 20))

# Email field
try:
    email_icon_path = os.path.join(base_dir, "assets", "11908187.png")
    email_icon = ctk.CTkImage(Image.open(email_icon_path), size=(20,20))
    password_icon_path = os.path.join(base_dir, "assets", "7781678.png")
    password_icon = ctk.CTkImage(Image.open(password_icon_path), size=(20,20))
except:
    email_icon = None
    password_icon = None

email_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
email_frame.pack(pady=(10,0), padx=(100,0), anchor="w")

if email_icon:
    ctk.CTkLabel(email_frame, image=email_icon, text="", width=24).pack(side="left", padx=(0,6))
ctk.CTkLabel(email_frame, text="Email", font=ctk.CTkFont(size=14)).pack(side="left")

email_entry = ctk.CTkEntry(right_frame, width=300, placeholder_text="Email")
email_entry.pack(pady=(0,10))

# Password field
password_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
password_frame.pack(pady=(10,0), padx=(100,0), anchor="w")

if password_icon:
    ctk.CTkLabel(password_frame, image=password_icon, text="", width=24).pack(side="left", padx=(0, 6))
ctk.CTkLabel(password_frame, text="Password", font=ctk.CTkFont(size=14)).pack(side="left")

password_entry = ctk.CTkEntry(right_frame, width=300, placeholder_text="Enter your password", show="*")
password_entry.pack(pady=(0, 10))

# Login button
login_button = ctk.CTkButton(right_frame, text="Login", command=login, hover_color="#8e44ad", width=300)
login_button.pack(pady=20)

# Google button
try:
    google_image_path = os.path.join(base_dir, "assets", "icons8-google-48.png")
    google_image = ctk.CTkImage(light_image=Image.open(google_image_path), size=(24,24))
except:
    google_image = None

google_button = ctk.CTkButton(
    right_frame, 
    text="Continue With Google", 
    image=google_image,
    width=300, 
    fg_color="#e0e0e0", 
    text_color="black", 
    hover_color="#bdc3c7"
)

google_button.pack(pady=(0, 10))

# Register link
register_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
register_frame.pack(pady=(10,0))

ctk.CTkLabel(register_frame, text="Don't have an account?", font=ctk.CTkFont(size=12)).pack(side="left")
register_link = ctk.CTkLabel(
    register_frame, 
    text="Register", 
    font=ctk.CTkFont(size=12, underline=True),
    text_color="#8e44ad",
    cursor="hand2"
)
register_link.pack(side="left", padx=5)
register_link.bind("<Button-1>", lambda e: show_register())

app.mainloop()

