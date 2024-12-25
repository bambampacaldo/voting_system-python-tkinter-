import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import json
from pathlib import Path
from datetime import datetime
import hashlib
from tkinter import simpledialog
import re
import os
import random
import math
import sys
import subprocess
from PIL import Image, ImageTk
import time

# Initialize darkdetect
darkdetect_module = None
try:
    import darkdetect as darkdetect_module
except ImportError:
    def install_darkdetect():
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'darkdetect'])
            return True
        except subprocess.CalledProcessError:
            return False
    
    if install_darkdetect():
        try:
            import darkdetect as darkdetect_module
        except ImportError:
            # Create dummy darkdetect if import still fails
            class DarkDetect:
                @staticmethod
                def isDark():
                    return False
            darkdetect_module = DarkDetect()
    else:
        # Create dummy darkdetect if installation fails
        class DarkDetect:
            @staticmethod
            def isDark():
                return False
        darkdetect_module = DarkDetect()

# Create global reference
darkdetect = darkdetect_module

class VotingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Voting System")
        self.root.geometry("1080x720")
        
        # Detect system theme
        self.is_dark_mode = darkdetect.isDark()
        
        # Update style dictionary based on system theme
        if self.is_dark_mode:
            self.style = {
                'bg': '#1A1A1A',  # Dark background
                'fg': '#FFFFFF',  # White text
                'font': ('Arial', 12),
                'button_bg': '#4CAF50',  # Keep green buttons
                'button_fg': 'white',
                'entry_bg': '#2C2C2C',  # Dark entry background
                'entry_fg': '#FFFFFF',  # White entry text
                'highlight_bg': '#2C2C2C',  # Dark highlight
                'border_color': '#4CAF50',  # Keep green border
                'frame_relief': tk.RIDGE,
                'entry_relief': tk.SOLID,
                'button_relief': tk.RAISED,
                'secondary_bg': '#2C2C2C',  # Dark secondary background
                'secondary_fg': '#888888'  # Gray secondary text
            }
        else:
            self.style = {
                'bg': '#FFFFFF',  # White background
                'fg': '#2E7D32',  # Dark green text
                'font': ('Arial', 12),
                'button_bg': '#4CAF50',  # Material green
                'button_fg': 'white',
                'entry_bg': '#F5F5F5',  # Light gray for inputs
                'entry_fg': '#1B5E20',  # Darker green for input text
                'highlight_bg': '#E8F5E9',  # Very light green for highlights
                'border_color': '#4CAF50',  # Green border
                'frame_relief': tk.RIDGE,
                'entry_relief': tk.SOLID,
                'button_relief': tk.RAISED,
                'secondary_bg': '#F5F5F5',  # Light secondary background
                'secondary_fg': '#666666'  # Gray secondary text
            }
        
        self.root.configure(bg=self.style['bg'])
        
        # Load or initialize data
        self.votes_file = Path("votes.json")
        self.admin_file = Path("admin.json")
        self.voters_file = Path("voters.json")
        self.load_votes()
        self.load_admin()
        self.load_voters()
        self.current_user = None
        
        self.is_admin = False
        
        self.show_login_screen()
        
    def load_votes(self):
        if self.votes_file.exists():
            with open(self.votes_file, 'r') as f:
                data = json.load(f)
                self.candidates = data.get('candidates', {})
                self.voting_history = data.get('history', [])
        else:
            self.candidates = {}
            self.voting_history = []
            
    def load_admin(self):
        if self.admin_file.exists():
            try:
                with open(self.admin_file, 'r') as f:
                    self.admin_data = json.load(f)
                    print(f"Loaded admin data: {self.admin_data}")
            except:
                # If there's any error loading the file, reset to default
                self.admin_data = {}
        
        # Always ensure default admin exists
        default_password = "admin123".encode('utf-8')
        default_hash = hashlib.sha256(default_password).hexdigest()
        
        # Set or reset admin credentials
        self.admin_data = {"admin": default_hash}
        print(f"Setting admin data: {self.admin_data}")
        self.save_admin()
        
    def load_voters(self):
        if self.voters_file.exists():
            with open(self.voters_file, 'r') as f:
                self.voters = json.load(f)
        else:
            self.voters = {}
            self.save_voters()
            
    def save_admin(self):
        with open(self.admin_file, 'w') as f:
            json.dump(self.admin_data, f)
            
    def save_voters(self):
        with open(self.voters_file, 'w') as f:
            json.dump(self.voters, f)
            
    def show_login_screen(self):
        # Clear current window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Main container with gradient effect
        main_frame = tk.Frame(self.root, bg=self.style['bg'])
        main_frame.pack(expand=True, fill='both')
        
        # Create background canvas for animated elements
        self.bg_canvas = tk.Canvas(main_frame, bg=self.style['bg'], highlightthickness=0)
        self.bg_canvas.place(relwidth=1, relheight=1)
        
        # Function to arrange symbols based on current window size
        def arrange_symbols():
            # Clear existing symbols
            for item in self.bg_canvas.find_all():
                self.bg_canvas.delete(item)
            
            # Draw background pattern
            create_pattern()
            
            # Calculate window width for proper symbol distribution
            window_width = max(self.root.winfo_width(), 800)  # Use minimum width of 800
            spacing = window_width / (len(symbols) + 1)
            
            # Add floating symbols to background with proper spacing
            for i, (symbol, _) in enumerate(symbols):
                x = spacing * (i + 1)  # Position symbols with equal spacing
                y = 50 + (i % 3) * 100  # Stagger vertical positions
                text_id = self.bg_canvas.create_text(
                    x, y,
                    text=symbol,
                    font=('Arial', 24),
                    fill='#81C784'  # Light green for symbols
                )
                # Start floating animation with random speed
                speed = random.uniform(0.5, 1.5)
                float_symbol(text_id, x, y, speed=speed)
        
        # Draw background pattern
        def create_pattern():
            # Create hexagonal pattern
            hex_size = 40
            hex_points = []
            window_width = max(self.root.winfo_width(), 800)  # Use minimum width of 800
            window_height = max(self.root.winfo_height(), 600)  # Use minimum height of 600
            
            for x in range(-50, window_width + 50, hex_size * 2):
                for y in range(-50, window_height + 50, hex_size * 2):
                    points = []
                    for angle in range(0, 360, 60):
                        rad = math.radians(angle)
                        px = x + hex_size * math.cos(rad)
                        py = y + hex_size * math.sin(rad)
                        points.extend([px, py])
                    hex_points.append(points)
            
            # Draw hexagons with different opacities
            for points in hex_points:
                self.bg_canvas.create_polygon(
                    points,
                    fill='#E8F5E9',  # Very light green
                    outline='#C8E6C9',  # Light green
                    width=1
                )
        
        # Add floating election symbols
        symbols = [
            ("🗳️", "Vote"),
            ("✓", "Check"),
            ("⭐", "Star"),
            ("🏛️", "Government"),
            ("📜", "Constitution"),
            ("⚖️", "Justice"),
            ("🎗️", "Ribbon"),
            ("🌟", "Success"),
            ("🔔", "Alert"),
            ("🎯", "Target")
        ]
        
        # Function to create floating animation
        def float_symbol(symbol, x, y, direction=1, speed=1):
            try:
                # Check if canvas still exists
                if self.bg_canvas.winfo_exists():
                    # Move symbol up and down
                    new_y = y + (direction * speed)
                    if new_y > self.bg_canvas.winfo_height() - 20:
                        direction = -1
                        new_y = self.bg_canvas.winfo_height() - 20
                    elif new_y < 20:
                        direction = 1
                        new_y = 20
                        
                    # Update symbol position
                    self.bg_canvas.coords(symbol, x, new_y)
                    
                    # Schedule next movement
                    self.root.after(50, lambda: float_symbol(symbol, x, new_y, direction, speed))
            except tk.TclError:
                pass  # Canvas was destroyed
        
        # Update symbol positions when window is resized
        def update_symbol_positions(event=None):
            try:
                if self.bg_canvas.winfo_exists():
                    arrange_symbols()
            except tk.TclError:
                pass  # Canvas was destroyed
        
        # Bind resize event
        self.root.bind('<Configure>', update_symbol_positions)
        
        # Initial arrangement after a short delay to ensure window is ready
        self.root.after(100, arrange_symbols)
        
        # Create semi-transparent overlay for login container
        overlay_frame = tk.Frame(main_frame, bg='#FFFFFF')
        overlay_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Login container with glass morphism effect
        login_frame = tk.Frame(
            overlay_frame,
            bg='white',
            padx=50,  # Increased padding
            pady=40,  # Increased padding
            relief=tk.RIDGE,
            bd=2,
            highlightbackground=self.style['border_color'],
            highlightthickness=1
        )
        login_frame.pack(padx=30, pady=30)  # Increased outer padding
        
        # Create title frame first
        title_frame = tk.Frame(login_frame, bg='white')
        title_frame.pack(fill='x', pady=(0, 40))  # Increased bottom padding
        
        # Logo/Title section with enhanced design
        logo_canvas = tk.Canvas(
            title_frame,
            width=120,  # Slightly larger logo
            height=120,
            bg='white',
            highlightthickness=0
        )
        logo_canvas.pack(pady=(0, 20))  # Added padding below logo
        
        # Title with green color
        title_label = tk.Label(
            title_frame,
            text="Secure Voting System",
            font=('Arial', 28, 'bold'),  # Larger font
            bg='white',
            fg='#2E7D32'
        )
        title_label.pack(pady=(0, 10))  # Adjusted padding
        
        # Subtitle
        tk.Label(
            title_frame,
            text="Your Voice, Your Choice",
            font=('Arial', 14, 'italic'),  # Larger subtitle
            bg='white',
            fg='#2E7D32'
        ).pack()
        
        # Login type selection with improved style
        login_type_frame = tk.Frame(login_frame, bg='white')
        login_type_frame.pack(fill='x', pady=(0, 25))  # Increased bottom padding
        
        tk.Label(
            login_type_frame,
            text="Select Access Type:",
            font=('Arial', 12, 'bold'),  # Made bold
            bg='white',
            fg='#2E7D32'
        ).pack(pady=(0, 8))  # Added padding below label
        
        # Style the combobox
        style = ttk.Style()
        style.configure(
            'Custom.TCombobox',
            fieldbackground='white',
            background='white',
            foreground='#2E7D32',
            arrowcolor='#4CAF50',
            selectbackground='#4CAF50',
            selectforeground='white',
            borderwidth=1,
            relief=tk.SOLID
        )
        
        self.login_type = ttk.Combobox(
            login_type_frame,
            values=["Voter", "Candidate", "Admin"],
            font=('Arial', 12),  # Increased font size
            style='Custom.TCombobox',
            state="readonly",
            width=25  # Wider combobox
        )
        self.login_type.set("Voter")
        self.login_type.pack(ipady=5)  # Added internal padding
        
        # Credentials section with improved styling
        credentials_frame = tk.Frame(login_frame, bg='white')
        credentials_frame.pack(fill='x', pady=(0, 25))  # Increased bottom padding
        
        # Username field with icon
        username_frame = tk.Frame(credentials_frame, bg='white')
        username_frame.pack(fill='x', pady=(0, 15))  # Increased spacing between fields
        
        tk.Label(
            username_frame,
            text="👤",
            font=('Arial', 18),  # Larger icon
            bg='white',
            fg='#2E7D32'
        ).pack(side=tk.LEFT, padx=(0, 15))  # Increased spacing between icon and field
        
        self.username_entry = tk.Entry(
            username_frame,
            font=('Arial', 12),  # Increased font size
            bg='white',
            fg='#2E7D32',
            insertbackground='#2E7D32',
            relief=tk.SOLID,
            bd=1,
            highlightbackground=self.style['border_color'],
            highlightthickness=1,
            width=30  # Wider entry field
        )
        self.username_entry.pack(fill='x', ipady=8)  # Increased internal padding
        
        # Password field with icon
        password_frame = tk.Frame(credentials_frame, bg='white')
        password_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            password_frame,
            text="🔒",
            font=('Arial', 18),  # Larger icon
            bg='white',
            fg='#2E7D32'
        ).pack(side=tk.LEFT, padx=(0, 15))  # Increased spacing between icon and field
        
        self.password_entry = tk.Entry(
            password_frame,
            font=('Arial', 12),  # Increased font size
            bg='white',
            fg='#2E7D32',
            insertbackground='#2E7D32',
            relief=tk.SOLID,
            bd=1,
            highlightbackground=self.style['border_color'],
            highlightthickness=1,
            width=30,  # Wider entry field
            show="•"
        )
        self.password_entry.pack(fill='x', ipady=8)  # Increased internal padding
        
        # Show/Hide password
        show_password_frame = tk.Frame(password_frame, bg='white')
        show_password_frame.pack(fill='x', pady=(8, 0))  # Added top padding
        
        self.show_password_var = tk.BooleanVar()
        tk.Checkbutton(
            show_password_frame,
            text="Show password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility,
            font=('Arial', 10),
            bg='white',
            fg='#2E7D32',
            selectcolor='#E8F5E9',  # Light green background when selected
            activebackground='white',
            activeforeground='#2E7D32'
        ).pack(anchor='w')
        
        # Login button with enhanced style
        self.login_button = tk.Button(
            login_frame,
            text="LOGIN",
            command=self.process_login,
            font=('Arial', 14, 'bold'),
            bg='#4CAF50',
            fg='white',
            activebackground='#66BB6A',
            activeforeground='white',
            relief=tk.RAISED,
            bd=0,
            width=20,
            height=2,
            cursor='hand2'
        )
        self.login_button.pack(pady=(20, 30))  # Increased padding around button
        
        # Add hover animation for login button
        def on_enter(e):
            e.widget.configure(bg='#66BB6A')
            # Create ripple effect
            x = e.x
            y = e.y
            ripple = tk.Canvas(
                e.widget,
                width=20,
                height=20,
                bg='#4CAF50',
                highlightthickness=0
            )
            ripple.place(x=x-10, y=y-10)
            ripple.create_oval(0, 0, 20, 20, fill='#A5D6A7')
            
            def fade_ripple():
                ripple.destroy()
            
            e.widget.after(200, fade_ripple)
        
        def on_leave(e):
            e.widget.configure(bg='#4CAF50')
        
        self.login_button.bind('<Enter>', on_enter)
        self.login_button.bind('<Leave>', on_leave)
        self.login_button.bind('<Button-1>', lambda e: on_enter(e))
        
        # Registration section with improved styling
        register_frame = tk.Frame(login_frame, bg='white')
        register_frame.pack(pady=(0, 10))
        
        tk.Label(
            register_frame,
            text="Don't have an account? ",
            font=('Arial', 11),  # Slightly larger font
            bg='white',
            fg='#2E7D32'
        ).pack(side=tk.LEFT)
        
        register_link = tk.Label(
            register_frame,
            text="Register here",
            font=('Arial', 11, 'underline'),  # Slightly larger font
            bg='white',
            fg='#2E7D32',
            cursor='hand2'
        )
        register_link.pack(side=tk.LEFT)
        
        # Add hover effect for register link
        register_link.bind('<Button-1>', self.show_registration_options)
        register_link.bind('<Enter>', lambda e: e.widget.configure(fg='#66BB6A'))
        register_link.bind('<Leave>', lambda e: e.widget.configure(fg='#2E7D32'))

    def on_entry_click(self, entry, placeholder):
        """Handle entry field focus in"""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            if entry == self.password_entry:
                entry.configure(show="���")
                
    def on_focus_out(self, entry, placeholder):
        """Handle entry field focus out"""
        if entry.get() == "":
            entry.insert(0, placeholder)
            if entry == self.password_entry and entry.get() == placeholder:
                entry.configure(show="")

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="•")

    def on_login_type_change(self, event=None):
        """Handle login type change"""
        login_type = self.login_type.get()
        if login_type == "Admin":
            self.login_button.configure(text="ADMIN LOGIN")
        elif login_type == "Candidate":
            self.login_button.configure(text="CANDIDATE LOGIN")
        else:
            self.login_button.configure(text="VOTER LOGIN")

    def process_login(self):
        login_type = self.login_type.get()
        if login_type == "Admin":
            self.admin_login()
        elif login_type == "Candidate":
            self.candidate_login()
        else:
            self.voter_login()
            
    def show_registration_options(self, event=None):
        registration_menu = tk.Menu(self.root, tearoff=0, bg=self.style['bg'], fg=self.style['fg'])
        registration_menu.add_command(
            label="Register as Voter",
            command=self.show_voter_registration,
            font=self.style['font']
        )
        registration_menu.add_command(
            label="Register as Candidate",
            command=self.show_candidate_registration,
            font=self.style['font']
        )
        
        # Get the widget that triggered the event
        widget = event.widget
        # Get the widget's position
        x = widget.winfo_rootx()
        y = widget.winfo_rooty() + widget.winfo_height()
        
        # Show the menu at the calculated position
        registration_menu.post(x, y)
        
    def admin_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        # Use the exact same hashing process
        input_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        
        # Debug prints
        print(f"Attempting login with username: {username}")
        print(f"Admin data: {self.admin_data}")
        print(f"Input password hash: {input_hash}")
        print(f"Stored password hash: {self.admin_data.get(username, 'Not found')}")
        
        if username in self.admin_data and self.admin_data[username] == input_hash:
            self.is_admin = True
            self.create_main_interface()
        else:
            messagebox.showerror("Error", "Invalid admin credentials!")
            
    def candidate_login(self):
        """Handle candidate login"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        if (username in self.voters and 
            self.voters[username]['password'] == hashed_password and 
            self.voters[username].get('is_candidate', False)):
            self.is_admin = False
            self.current_user = username
            self.create_candidate_interface()
        else:
            messagebox.showerror("Error", "Invalid candidate credentials!")
            
    def voter_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        if username in self.voters and self.voters[username]['password'] == hashed_password:
            self.is_admin = False
            self.current_user = username
            self.create_main_interface()
        else:
            messagebox.showerror("Error", "Invalid credentials!")
            
    def create_main_interface(self):
        # Clear current window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Main container
        main_container = tk.Frame(self.root, bg=self.style['bg'])
        main_container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title with login status
        status = "Admin Mode" if self.is_admin else "Voter Mode"
        title = tk.Label(
            main_container,
            text=f"Voting System ({status})",
            font=('Arial', 24, 'bold'),
            bg=self.style['bg'],
            fg=self.style['fg']
        )
        title.pack(pady=20)
        
        if self.is_admin:
            self.create_admin_interface(main_container)
        else:
            self.create_voter_interface(main_container)
            
        # Logout button
        tk.Button(
            main_container,
            text="Logout",
            command=self.show_login_screen,
            font=self.style['font'],
            bg='red',
            fg='white'
        ).pack(pady=10)
        
    def create_admin_interface(self, container):
        # Add header frame with settings and back buttons
        header_frame = tk.Frame(container, bg=self.style['bg'])
        header_frame.pack(fill='x', pady=(0, 10))
        
        # Back to Login button (left side) with updated styling
        back_btn = tk.Button(
            header_frame,
            text="← Back to Login",
            command=self.show_login_screen,
            font=self.style['font'],
            bg='#4CAF50',  # Material green to match theme
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        back_btn.pack(side=tk.LEFT, padx=10)
        
        # Settings button (right side) with updated styling
        settings_btn = tk.Button(
            header_frame,
            text="⚙️ Settings",
            command=self.show_admin_settings,
            font=self.style['font'],
            bg='#4CAF50',  # Material green to match theme
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        settings_btn.pack(side=tk.RIGHT, padx=10)
        
        # Add hover effects for both buttons
        def on_enter(e):
            e.widget.configure(bg='#66BB6A')  # Lighter green on hover
            
        def on_leave(e):
            e.widget.configure(bg='#4CAF50')  # Return to original green
            
        for btn in [back_btn, settings_btn]:
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
            # Add click effect
            btn.bind('<Button-1>', lambda e: e.widget.configure(relief=tk.SUNKEN))
            btn.bind('<ButtonRelease-1>', lambda e: e.widget.configure(relief=tk.FLAT))
        
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(container)
        notebook.pack(fill='both', expand=True, pady=10)
        
        # Style for tabs
        style = ttk.Style()
        style.configure('Custom.TFrame', background=self.style['bg'])
        
        # Create tabs
        voters_tab = ttk.Frame(notebook, style='Custom.TFrame')
        candidates_tab = ttk.Frame(notebook, style='Custom.TFrame')
        results_tab = ttk.Frame(notebook, style='Custom.TFrame')
        
        notebook.add(voters_tab, text='Manage Voters')
        notebook.add(candidates_tab, text='Manage Candidates')
        notebook.add(results_tab, text='View Results')
        
        # Setup each tab
        self.setup_voters_tab(voters_tab)
        self.setup_candidates_tab(candidates_tab)
        self.setup_results_tab(results_tab)

    def setup_voters_tab(self, container):
        # Search and filter section
        search_frame = tk.Frame(container, bg=self.style['bg'])
        search_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            search_frame,
            text="Search Voters:",
            font=self.style['font'],
            bg=self.style['bg'],
            fg=self.style['fg']
        ).pack(side=tk.LEFT, padx=5)
        
        search_entry = tk.Entry(
            search_frame,
            font=self.style['font'],
            bg=self.style['entry_bg'],
            fg=self.style['entry_fg'],
            width=30
        )
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Voters list with scrollbar
        list_frame = tk.Frame(container, bg=self.style['bg'])
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create Treeview with style
        style = ttk.Style()
        style.configure(
            "Treeview",
            background=self.style['bg'],
            foreground=self.style['fg'],
            fieldbackground=self.style['bg'],
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            background=self.style['highlight_bg'],
            foreground=self.style['fg'],
            relief='flat'
        )
        # Configure selection colors
        style.map('Treeview',
            background=[('selected', '#00BFFF')],
            foreground=[('selected', 'white')]
        )
        
        # Create Treeview
        columns = ('Username', 'Full Name', 'Email', 'Phone', 'Registration Date')
        self.voters_tree = ttk.Treeview(list_frame, columns=columns, show='headings', selectmode='browse')
        
        # Configure columns
        for col in columns:
            self.voters_tree.heading(col, text=col)
            self.voters_tree.column(col, width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.voters_tree.yview)
        self.voters_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.voters_tree.pack(fill='both', expand=True)
        
        # Add row selection event
        def on_select(event):
            selected = self.voters_tree.selection()
            if selected:
                item = selected[0]
                values = self.voters_tree.item(item)['values']
                print(f"Selected voter: {values[0]}")  # Print selected username for debugging
        
        self.voters_tree.bind('<<TreeviewSelect>>', on_select)
        
        # Buttons frame
        btn_frame = tk.Frame(container, bg=self.style['bg'])
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Button(
            btn_frame,
            text="Add Voter",
            command=self.show_voter_registration,
            font=self.style['font'],
            bg='#00BFFF',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Edit Voter",
            command=lambda: self.edit_voter(self.voters_tree.selection()),
            font=self.style['font'],
            bg='#00BFFF',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Delete Voter",
            command=lambda: self.delete_voter(self.voters_tree.selection()),
            font=self.style['font'],
            bg='red',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        # Populate voters list
        self.update_voters_list()
        
        # Bind search functionality
        search_entry.bind('<KeyRelease>', lambda e: self.search_voters(search_entry.get()))

    def setup_candidates_tab(self, container):
        # Similar structure to voters tab but for candidates
        search_frame = tk.Frame(container, bg=self.style['bg'])
        search_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            search_frame,
            text="Search Candidates:",
            font=self.style['font'],
            bg=self.style['bg'],
            fg=self.style['fg']
        ).pack(side=tk.LEFT, padx=5)
        
        search_entry = tk.Entry(
            search_frame,
            font=self.style['font'],
            bg=self.style['entry_bg'],
            fg=self.style['entry_fg'],
            width=30
        )
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Candidates list with scrollbar
        list_frame = tk.Frame(container, bg=self.style['bg'])
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('Full Name', 'Party', 'Votes', 'Registration Date')
        self.candidates_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.candidates_tree.heading(col, text=col)
            self.candidates_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.candidates_tree.yview)
        self.candidates_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.candidates_tree.pack(fill='both', expand=True)
        
        # Buttons frame
        btn_frame = tk.Frame(container, bg=self.style['bg'])
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Button(
            btn_frame,
            text="Add Candidate",
            command=self.show_candidate_registration,
            font=self.style['font'],
            bg='#00BFFF',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="View Details",
            command=lambda: self.view_candidate_details(self.candidates_tree.selection()),
            font=self.style['font'],
            bg='#00BFFF',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Delete Candidate",
            command=lambda: self.delete_candidate(self.candidates_tree.selection()),
            font=self.style['font'],
            bg='red',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        # Populate candidates list
        self.update_candidates_list()
        
        # Bind search functionality
        search_entry.bind('<KeyRelease>', lambda e: self.search_candidates(search_entry.get()))

    def setup_results_tab(self, container):
        """Setup the results tab"""
        # Results visualization
        chart_frame = tk.Frame(container, bg=self.style['bg'])
        chart_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create results frame
        self.results_frame = tk.Frame(chart_frame, bg=self.style['bg'])
        self.results_frame.pack(fill='both', expand=True)
        
        # Results in table format
        columns = ('Candidate', 'Party', 'Votes', 'Percentage')
        self.results_tree = ttk.Treeview(self.results_frame, columns=columns, show='headings')
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_tree.pack(fill='both', expand=True)
        
        # Control buttons
        btn_frame = tk.Frame(container, bg=self.style['bg'])
        btn_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Button(
            btn_frame,
            text="Export Results",
            command=self.export_results,
            font=self.style['font'],
            bg='#00BFFF',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Reset All Votes",
            command=self.reset_votes,
            font=self.style['font'],
            bg='red',
            fg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        # Update results
        self.update_results_display()

    def create_voter_interface(self, container):
        # Main container with padding
        main_frame = tk.Frame(container, bg=self.style['bg'], padx=30, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Header section with welcome message and user info
        header_frame = tk.Frame(main_frame, bg=self.style['secondary_bg'], pady=20)
        header_frame.pack(fill='x', padx=20)
        
        user_data = self.voters[self.current_user]
        
        # Welcome message with user's name
        tk.Label(
            header_frame,
            text=f"Welcome, {user_data['full_name']}!",
            font=('Arial', 24, 'bold'),
            bg=self.style['secondary_bg'],
            fg=self.style['fg']
        ).pack(pady=(0, 10))
        
        tk.Label(
            header_frame,
            text="Cast your vote by selecting a candidate below",
            font=('Arial', 12),
            bg=self.style['secondary_bg'],
            fg=self.style['secondary_fg']
        ).pack()
        
        # Quick actions bar
        actions_frame = tk.Frame(main_frame, bg=self.style['bg'])
        actions_frame.pack(fill='x', pady=(20, 20))
        
        # Action buttons with updated colors
        buttons = [
            ("👤 My Profile", self.show_profile),
            ("🔒 Change Password", self.change_password),
            ("📊 View Results", self.show_results)
        ]
        
        for text, command in buttons:
            btn = tk.Button(
                actions_frame,
                text=text,
                command=command,
                font=self.style['font'],
                bg=self.style['secondary_bg'],
                fg=self.style['fg'],
                relief=tk.FLAT,
                padx=15,
                pady=8,
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=5)
            
            # Add hover effects
            btn.bind('<Enter>', lambda e: e.widget.configure(
                bg=self.style['highlight_bg']
            ))
            btn.bind('<Leave>', lambda e: e.widget.configure(
                bg=self.style['secondary_bg']
            ))
        
        # Candidates section
        candidates_label = tk.Label(
            main_frame,
            text="Available Candidates",
            font=('Arial', 18, 'bold'),
            bg=self.style['bg'],
            fg=self.style['fg']
        )
        candidates_label.pack(pady=(20, 10))
        
        # Create scrollable candidates frame
        canvas = tk.Canvas(main_frame, bg=self.style['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.candidates_frame = tk.Frame(canvas, bg=self.style['bg'])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill='both', expand=True, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas_frame = canvas.create_window((0, 0), window=self.candidates_frame, anchor='nw')
        
        # Update candidates display
        self.update_candidates_display(False)
        
        # Configure canvas scrolling
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        self.candidates_frame.bind('<Configure>', configure_scroll_region)
        
        # Make canvas expand with window
        def configure_canvas(event):
            canvas.itemconfig(canvas_frame, width=event.width)
        
        canvas.bind('<Configure>', configure_canvas)
        
        # Logout button at the bottom
        logout_btn = tk.Button(
            main_frame,
            text="🚪 Logout",
            command=self.show_login_screen,
            font=self.style['font'],
            bg='#FF4444',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        logout_btn.pack(pady=20)
        
        # Add hover effect for logout button
        logout_btn.bind('<Enter>', lambda e: e.widget.configure(bg='#FF6666'))
        logout_btn.bind('<Leave>', lambda e: e.widget.configure(bg='#FF4444'))

    def create_candidates_list(self, container, is_admin):
        # Candidates Frame with Scrollbar
        candidates_container = tk.Frame(container, bg=self.style['bg'])
        candidates_container.pack(fill='both', expand=True, pady=20)
        
        self.canvas = tk.Canvas(candidates_container, bg=self.style['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(candidates_container, orient="vertical", command=self.canvas.yview)
        self.candidates_frame = tk.Frame(self.canvas, bg=self.style['bg'])
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill='both', expand=True)
        
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.candidates_frame, anchor='nw')
        self.candidates_frame.bind('<Configure>', self.on_frame_configure)
        
        self.update_candidates_display(is_admin)
        
    def edit_candidate(self, candidate):
        new_name = tk.simpledialog.askstring("Edit Candidate", 
                                           f"Enter new name for {candidate}:",
                                           parent=self.root)
        if new_name and new_name != candidate:
            votes = self.candidates.pop(candidate)
            self.candidates[new_name] = votes
            self.save_votes()
            # Pass True since this is called from admin interface
            self.update_candidates_display(True)
            
    def delete_candidate(self, selection):
        """Delete selected candidate"""
        if not selection:
            messagebox.showwarning("Warning", "Please select a candidate first!")
            return
        
        item = selection[0]
        candidate_name = self.candidates_tree.item(item)['values'][0]  # Get candidate name from first column
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {candidate_name}?"):
            if candidate_name in self.candidates:
                # Remove from candidates list
                del self.candidates[candidate_name]
                
                # Remove candidate flag from voters
                for username, data in self.voters.items():
                    if data.get('is_candidate', False) and data['full_name'] == candidate_name:
                        data['is_candidate'] = False
                        break
                
                self.save_votes()
                self.save_voters()
                self.update_candidates_list()
                messagebox.showinfo("Success", f"Candidate {candidate_name} deleted successfully!")
            else:
                messagebox.showerror("Error", "Candidate not found!")
            
    def update_candidates_display(self, is_admin):
        # Clear existing candidates
        for widget in self.candidates_frame.winfo_children():
            widget.destroy()
        
        if not self.candidates:
            # Show message if no candidates
            tk.Label(
                self.candidates_frame,
                text="No candidates available at this time",
                font=('Arial', 12, 'italic'),
                bg=self.style['bg'],
                fg='#888888'
            ).pack(pady=20)
            return
        
        # Create a card for each candidate
        for candidate in self.candidates:
            # Find candidate data
            candidate_data = None
            for voter in self.voters.values():
                if voter.get('is_candidate', False) and voter['full_name'] == candidate:
                    candidate_data = voter
                    break
            
            if not candidate_data:
                continue
            
            # Card frame with border effect
            card = tk.Frame(
                self.candidates_frame,
                bg='#1A1A1A',
                padx=20,
                pady=15,
                relief=tk.GROOVE,
                bd=1
            )
            card.pack(fill='x', padx=10, pady=5)
            
            # Left side: Candidate info
            info_frame = tk.Frame(card, bg='#1A1A1A')
            info_frame.pack(side=tk.LEFT, fill='both', expand=True)
            
            # Candidate name
            tk.Label(
                info_frame,
                text=candidate,
                font=('Arial', 14, 'bold'),
                bg='#1A1A1A',
                fg='#00BFFF'
            ).pack(anchor='w')
            
            # Party and Position
            party = candidate_data.get('party', 'Independent')
            position = candidate_data.get('desired_position', 'Not specified')
            
            tk.Label(
                info_frame,
                text=f"Party: {party} | Running for: {position}",
                font=('Arial', 10),
                bg='#1A1A1A',
                fg='#888888'
            ).pack(anchor='w')
            
            # View Details button
            details_btn = tk.Button(
                info_frame,
                text="View Details",
                command=lambda c=candidate_data: self.show_candidate_details_popup(c),
                font=('Arial', 10),
                bg='#2C2C2C',
                fg='white',
                relief=tk.FLAT,
                padx=10,
                pady=2,
                cursor='hand2'
            )
            details_btn.pack(anchor='w', pady=5)
            
            # Add hover effect for details button
            details_btn.bind('<Enter>', lambda e: e.widget.configure(bg='#404040'))
            details_btn.bind('<Leave>', lambda e: e.widget.configure(bg='#2C2C2C'))
            
            # Right side: Vote button or vote count
            if is_admin:
                tk.Label(
                    card,
                    text=f"Votes: {self.candidates[candidate]}",
                    font=self.style['font'],
                    bg='#1A1A1A',
                    fg='#00BFFF'
                ).pack(side=tk.RIGHT, padx=10)
            else:
                vote_btn = tk.Button(
                    card,
                    text="🗳️ Vote",
                    command=lambda c=candidate: self.vote(c),
                    font=self.style['font'],
                    bg='#00BFFF',
                    fg='white',
                    relief=tk.FLAT,
                    padx=20,
                    pady=5,
                    cursor='hand2'
                )
                vote_btn.pack(side=tk.RIGHT, padx=10)
                
                # Add hover effect
                vote_btn.bind('<Enter>', lambda e: e.widget.configure(bg='#33CCFF'))
                vote_btn.bind('<Leave>', lambda e: e.widget.configure(bg='#00BFFF'))

    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def add_candidate(self):
        name = self.candidate_entry.get().strip()
        if name:
            if name not in self.candidates:
                self.candidates[name] = 0
                self.save_votes()
                # Pass True since this is called from admin interface
                self.update_candidates_display(True)
                self.update_results_display()
                self.candidate_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Warning", "Candidate already exists!")
        else:
            messagebox.showwarning("Warning", "Please enter a candidate name!")
            
    def vote(self, candidate):
        """Cast a vote for a candidate"""
        # Get candidate's role
        candidate_role = None
        for voter in self.voters.values():
            if voter.get('is_candidate', False) and voter['full_name'] == candidate:
                candidate_role = voter.get('desired_position')
                break
        
        if not candidate_role:
            messagebox.showerror("Error", "Could not determine candidate's role!")
            return
        
        # Check if voter has already voted for this role
        for vote in self.voting_history:
            if vote['voter'] == self.current_user:
                voted_candidate = None
                # Find the role of the candidate they voted for
                for voter in self.voters.values():
                    if voter.get('is_candidate', False) and voter['full_name'] == vote['candidate']:
                        voted_role = voter.get('desired_position')
                        if voted_role == candidate_role:
                            messagebox.showwarning(
                                "Warning", 
                                f"You have already voted for a {candidate_role}!\n"
                                f"Your vote was cast for {vote['candidate']}"
                            )
                            return
        
        # If not voted for this role before, proceed with voting
        self.candidates[candidate] += 1
        self.voting_history.append({
            'candidate': candidate,
            'voter': self.current_user,
            'role': candidate_role,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self.save_votes()
        self.update_candidates_display(False)
        messagebox.showinfo("Success", f"Vote cast for {candidate} as {candidate_role}")
        
    def update_results_display(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        sorted_candidates = sorted(
            self.candidates.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for candidate, votes in sorted_candidates:
            frame = tk.Frame(self.results_frame, bg=self.style['highlight_bg'])
            frame.pack(fill='x', pady=2)
            
            tk.Label(
                frame,
                text=f"{candidate}:",
                font=self.style['font'],
                bg=self.style['highlight_bg'],
                fg=self.style['fg']
            ).pack(side=tk.LEFT, padx=5)
            
            tk.Label(
                frame,
                text=str(votes),
                font=self.style['font'],
                bg=self.style['highlight_bg'],
                fg=self.style['fg']
            ).pack(side=tk.RIGHT, padx=5)
            
    def reset_votes(self):
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all votes?"):
            self.candidates = {candidate: 0 for candidate in self.candidates}
            self.voting_history = []
            self.save_votes()
            
            # Update results display first
            self.update_results_display()
            
            # Only update candidates display if we're in admin view
            if self.is_admin:
                self.update_candidates_list()  # Update the admin candidates list instead
            messagebox.showinfo("Success", "All votes have been reset successfully!")

    def export_results(self):
        """Export voting results as PDF"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
        except ImportError:
            # If reportlab is not installed, fall back to text file export
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"voting_results_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write("Voting Results Summary\n")
                f.write("=====================\n\n")
                
                sorted_candidates = sorted(
                    self.candidates.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                total_votes = sum(self.candidates.values())
                
                for candidate, votes in sorted_candidates:
                    percentage = (votes / total_votes * 100) if total_votes > 0 else 0
                    f.write(f"{candidate}: {votes} votes ({percentage:.1f}%)\n")
                
                f.write("\n\nVoting History\n")
                f.write("==============\n\n")
                
                for vote in self.voting_history:
                    f.write(f"{vote['timestamp']}: {vote['voter']} voted for {vote['candidate']}\n")
                
            messagebox.showinfo("Success", f"Results exported to {filename}")
            
            # Open the file with the default text editor
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(filename)
                elif os.name == 'posix':  # macOS and Linux
                    import subprocess
                    subprocess.call(('open' if sys.platform == 'darwin' else 'xdg-open', filename))
            except Exception as e:
                messagebox.showwarning("Warning", f"File created but could not be opened automatically.\nLocation: {os.path.abspath(filename)}")
            return

        # Rest of the PDF export code...
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"voting_results_{timestamp}.pdf"
        
        # Create the PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        
        # ... (rest of the existing PDF export code)
        
        # Build PDF
        try:
            doc.build(elements)
            messagebox.showinfo("Success", f"Results exported to {filename}")
            # Open the PDF file
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(filename)
                elif os.name == 'posix':  # macOS and Linux
                    import subprocess
                    subprocess.call(('open' if sys.platform == 'darwin' else 'xdg-open', filename))
            except Exception as e:
                messagebox.showwarning("Warning", f"PDF created but could not be opened automatically.\nLocation: {os.path.abspath(filename)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create PDF: {str(e)}")

    def show_results(self):
        result_text = "Voting Results:\n\n"
        if not self.candidates:
            result_text += "No candidates yet!"
        else:
            sorted_candidates = sorted(
                self.candidates.items(),
                key=lambda x: x[1],
                reverse=True
            )
            for candidate, votes in sorted_candidates:
                result_text += f"{candidate}: {votes} votes\n"
            
        messagebox.showinfo("Results", result_text)

    def show_voter_registration(self):
        registration_window = tk.Toplevel(self.root)
        registration_window.title("Voter Registration")
        registration_window.configure(bg=self.style['bg'])
        registration_window.geometry("800x900")  # Wider window
        
        # Create main canvas with scrollbar
        main_canvas = tk.Canvas(registration_window, bg=self.style['bg'])
        scrollbar = ttk.Scrollbar(registration_window, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg=self.style['bg'])
        
        main_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        main_canvas.pack(side=tk.LEFT, fill="both", expand=True)
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Title
        title_frame = tk.Frame(scrollable_frame, bg=self.style['bg'])
        title_frame.pack(fill='x', pady=20)
        
        tk.Label(
            title_frame,
            text="Voter Registration Form",
            font=('Arial', 24, 'bold'),
            bg=self.style['bg'],
            fg=self.style['fg']
        ).pack()
        
        tk.Label(
            title_frame,
            text="Please fill in all required fields",
            font=('Arial', 12, 'italic'),
            bg=self.style['bg'],
            fg='#888888'
        ).pack(pady=5)
        
        # Create sections
        sections = {
            'Account Information': ['Username', 'Password', 'Confirm Password'],
            'Personal Information': [
                'Full Name',
                {'name': 'Date of Birth', 'type': 'date'},  # Changed from 'Date of Birth (YYYY-MM-DD)'
                {'name': 'Gender', 'type': 'combo', 'values': ['Male', 'Female', 'Other']},  # Added gender combo
                'National ID Number',
                'Occupation'
            ],
            'Contact Information': ['Phone Number', 'Email Address'],
            'Address Details': [
                'Residential Address',
                'City',
                'State/Province',
                'Postal Code',
                {'name': 'Country', 'type': 'combo', 'values': [  # Added country combo
                    'Brunei',
                    'Cambodia',
                    'Indonesia',
                    'Laos',
                    'Malaysia',
                    'Myanmar',
                    'Philippines',
                    'Singapore',
                    'Thailand',
                    'Timor-Leste',
                    'Vietnam',
                    'Other'
                ]}
            ]
        }
        
        entries = {}
        
        # Style for section frames
        section_style = {
            'bg': '#1A1A1A',
            'pady': 15,
            'padx': 20,
            'relief': tk.GROOVE,
            'bd': 1
        }
        
        # Create sections with fields
        for section_title, fields in sections.items():
            # Section frame
            section_frame = tk.Frame(scrollable_frame, **section_style)
            section_frame.pack(fill='x', padx=20, pady=10)
            
            # Section title
            tk.Label(
                section_frame,
                text=section_title,
                font=('Arial', 14, 'bold'),
                bg=section_style['bg'],
                fg='#00BFFF'
            ).pack(anchor='w', pady=(0, 10))
            
            # Create two-column layout for fields
            for i in range(0, len(fields), 2):
                row_frame = tk.Frame(section_frame, bg=section_style['bg'])
                row_frame.pack(fill='x', pady=5)
                
                # First field in row
                field_frame = tk.Frame(row_frame, bg=section_style['bg'])
                field_frame.pack(side=tk.LEFT, expand=True, fill='x', padx=(0, 10))
                
                # Extract field name and type for first field
                if isinstance(fields[i], dict):
                    field_name = fields[i]['name']
                    field_type = fields[i]['type']
                else:
                    field_name = fields[i]
                    field_type = 'entry'
                
                # Create label using f-string
                tk.Label(
                    field_frame,
                    text=f"{field_name}:",  # Changed to use f-string
                    font=self.style['font'],
                    bg=section_style['bg'],
                    fg=self.style['fg']
                ).pack(anchor='w')
                
                if field_type == 'combo':
                    entry = ttk.Combobox(
                        field_frame,
                        values=fields[i]['values'],
                        font=self.style['font'],
                        state='readonly',
                        width=30
                    )
                    entry.set("Select...")
                elif field_type == 'date':
                    # Create date picker frame
                    date_frame = tk.Frame(field_frame, bg=section_style['bg'])
                    date_frame.pack(fill='x')
                    
                    # Year
                    year_values = list(range(1900, datetime.now().year + 1))
                    year = ttk.Combobox(
                        date_frame,
                        values=year_values,
                        font=self.style['font'],
                        width=6
                    )
                    year.set("Year")
                    year.pack(side=tk.LEFT, padx=2)
                    
                    # Month
                    month_values = list(range(1, 13))
                    month = ttk.Combobox(
                        date_frame,
                        values=month_values,
                        font=self.style['font'],
                        width=4
                    )
                    month.set("MM")
                    month.pack(side=tk.LEFT, padx=2)
                    
                    # Day
                    day_values = list(range(1, 32))
                    day = ttk.Combobox(
                        date_frame,
                        values=day_values,
                        font=self.style['font'],
                        width=4
                    )
                    day.set("DD")
                    day.pack(side=tk.LEFT, padx=2)
                    
                    entry = (year, month, day)  # Store tuple of comboboxes
                else:
                    entry = tk.Entry(
                        field_frame,
                        font=self.style['font'],
                        bg=self.style['entry_bg'],
                        fg=self.style['entry_fg'],
                        relief=self.style['entry_relief'],
                        width=30
                    )
                    if 'password' in field_name.lower():
                        entry.configure(show="*")
                
                if field_type != 'date':
                    entry.pack(fill='x', padx=5)
                entries[field_name] = entry
                
                # Second field in row (if exists)
                if i + 1 < len(fields):
                    field_frame = tk.Frame(row_frame, bg=section_style['bg'])
                    field_frame.pack(side=tk.LEFT, expand=True, fill='x')
                    
                    # Extract field name and type for second field
                    if isinstance(fields[i + 1], dict):
                        field_name = fields[i + 1]['name']
                        field_type = fields[i + 1]['type']
                    else:
                        field_name = fields[i + 1]
                        field_type = 'entry'
                    
                    # Create label using f-string
                    tk.Label(
                        field_frame,
                        text=f"{field_name}:",  # Changed to use f-string
                        font=self.style['font'],
                        bg=section_style['bg'],
                        fg=self.style['fg']
                    ).pack(anchor='w')
                    
                    if field_type == 'combo':
                        entry = ttk.Combobox(
                            field_frame,
                            values=fields[i + 1]['values'],
                            font=self.style['font'],
                            state='readonly',
                            width=30
                        )
                        entry.set("Select...")
                    elif field_type == 'date':
                        # Create date picker frame
                        date_frame = tk.Frame(field_frame, bg=section_style['bg'])
                        date_frame.pack(fill='x')
                        
                        # Year
                        year_values = list(range(1900, datetime.now().year + 1))
                        year = ttk.Combobox(
                            date_frame,
                            values=year_values,
                            font=self.style['font'],
                            width=6
                        )
                        year.set("Year")
                        year.pack(side=tk.LEFT, padx=2)
                        
                        # Month
                        month_values = list(range(1, 13))
                        month = ttk.Combobox(
                            date_frame,
                            values=month_values,
                            font=self.style['font'],
                            width=4
                        )
                        month.set("MM")
                        month.pack(side=tk.LEFT, padx=2)
                        
                        # Day
                        day_values = list(range(1, 32))
                        day = ttk.Combobox(
                            date_frame,
                            values=day_values,
                            font=self.style['font'],
                            width=4
                        )
                        day.set("DD")
                        day.pack(side=tk.LEFT, padx=2)
                        
                        entry = (year, month, day)  # Store tuple of comboboxes
                    else:
                        entry = tk.Entry(
                            field_frame,
                            font=self.style['font'],
                            bg=self.style['entry_bg'],
                            fg=self.style['entry_fg'],
                            relief=self.style['entry_relief'],
                            width=30
                        )
                        if 'password' in field_name.lower():
                            entry.configure(show="*")
                    
                    if field_type != 'date':
                        entry.pack(fill='x', padx=5)
                    entries[field_name] = entry
        
        # Terms and Conditions
        terms_frame = tk.Frame(scrollable_frame, bg=self.style['bg'])
        terms_frame.pack(fill='x', padx=20, pady=10)

        self.terms_var = tk.BooleanVar()
        
        terms_check_frame = tk.Frame(terms_frame, bg=self.style['bg'])
        terms_check_frame.pack(fill='x')
        
        tk.Checkbutton(
            terms_check_frame,
            text="I agree to the ",
            variable=self.terms_var,
            font=self.style['font'],
            bg=self.style['bg'],
            fg=self.style['fg'],
            selectcolor='black',
            activebackground=self.style['bg'],
            activeforeground=self.style['fg']
        ).pack(side=tk.LEFT)

        terms_link = tk.Label(
            terms_check_frame,
            text="Terms and Conditions",
            font=('Arial', 11, 'underline'),
            bg=self.style['bg'],
            fg='#00BFFF',
            cursor='hand2'
        )
        terms_link.pack(side=tk.LEFT)

        # Bind click event to terms link
        terms_link.bind('<Button-1>', lambda e: self.show_terms_and_conditions())

        # Add hover effect for terms link
        terms_link.bind('<Enter>', lambda e: e.widget.configure(fg='#33CCFF'))
        terms_link.bind('<Leave>', lambda e: e.widget.configure(fg='#00BFFF'))
        
        # Register button
        button_frame = tk.Frame(scrollable_frame, bg=self.style['bg'])
        button_frame.pack(pady=20)
        
        register_btn = tk.Button(
            button_frame,
            text="Register",
            command=lambda: self.process_voter_registration(entries, registration_window),
            font=('Arial', 12, 'bold'),
            bg='#00BFFF',
            fg='white',
            width=20,
            height=2,
            cursor='hand2'
        )
        register_btn.pack()
        
        # Configure the scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
    def process_voter_registration(self, entries, window):
        if not self.terms_var.get():
            messagebox.showerror("Error", "Please accept the Terms and Conditions!")
            return
        
        # Get all field values
        data = {}
        for field, entry in entries.items():
            if isinstance(entry, tuple):  # Date field
                year, month, day = entry
                try:
                    # Validate and format date
                    date_str = f"{year.get()}-{int(month.get()):02d}-{int(day.get()):02d}"
                    # Verify it's a valid date
                    datetime.strptime(date_str, '%Y-%m-%d')
                    data[field] = date_str
                except (ValueError, TypeError):
                    messagebox.showerror("Error", f"Invalid date format for {field}")
                    return
            else:
                data[field] = entry.get().strip()
        
        # Validation
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        if data['Password'] != data['Confirm Password']:
            messagebox.showerror("Error", "Passwords do not match!")
            return
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['Email Address']):
            messagebox.showerror("Error", "Invalid email address!")
            return
        
        # Validate date format
        try:
            year, month, day = entries['Date of Birth']  # Get the tuple of year, month, day comboboxes
            try:
                # Construct date string
                date_str = f"{year.get()}-{int(month.get()):02d}-{int(day.get()):02d}"
                birth_date = datetime.strptime(date_str, '%Y-%m-%d')
                age = (datetime.now() - birth_date).days // 365
                if age < 18:
                    messagebox.showerror("Error", "Must be 18 or older to register!")
                    return
            except (ValueError, TypeError):
                messagebox.showerror("Error", "Invalid date format! Please select valid date.")
                return
        except KeyError:
            messagebox.showerror("Error", "Date of Birth is required!")
            return
        
        if data['Username'] in self.voters or data['Username'] in self.admin_data:
            messagebox.showerror("Error", "Username already exists!")
            return
        
        # Add voter with extended information
        self.voters[data['Username']] = {
            'password': hashlib.sha256(data['Password'].encode()).hexdigest(),
            'full_name': data['Full Name'],
            'date_of_birth': date_str,
            'national_id': data['National ID Number'],
            'phone': data['Phone Number'],
            'email': data['Email Address'],
            'address': {
                'street': data['Residential Address'],
                'city': data['City'],
                'state': data['State/Province'],
                'postal_code': data['Postal Code'],
                'country': data['Country']
            },
            'occupation': data['Occupation'],
            'gender': data['Gender'],  # Changed from 'Gender (M/F/Other)'
            'is_candidate': False,
            'registration_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.save_voters()
        messagebox.showinfo("Success", "Registration successful! You can now login.")
        window.destroy()

    def show_candidate_registration(self):
        registration_window = tk.Toplevel(self.root)
        registration_window.title("Candidate Registration")
        registration_window.configure(bg=self.style['bg'])
        registration_window.geometry("800x900")  # Wider window
        
        # Create main canvas with scrollbar
        main_canvas = tk.Canvas(registration_window, bg=self.style['bg'])
        scrollbar = ttk.Scrollbar(registration_window, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg=self.style['bg'])
        
        main_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        main_canvas.pack(side=tk.LEFT, fill="both", expand=True)
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Title
        title_frame = tk.Frame(scrollable_frame, bg=self.style['bg'])
        title_frame.pack(fill='x', pady=20)
        
        tk.Label(
            title_frame,
            text="Candidate Registration Form",
            font=('Arial', 24, 'bold'),
            bg=self.style['bg'],
            fg=self.style['fg']
        ).pack()
        
        tk.Label(
            title_frame,
            text="Please fill in all required fields",
            font=('Arial', 12, 'italic'),
            bg=self.style['bg'],
            fg='#888888'
        ).pack(pady=5)
        
        # Create sections
        sections = {
            'Account Information': [
                'Username', 'Password', 'Confirm Password'
            ],
            'Personal Information': [
                'Full Name', 
                {'name': 'Date of Birth', 'type': 'date'},
                {'name': 'Gender', 'type': 'combo', 'values': ['Male', 'Female', 'Other']},
                'National ID Number'
            ],
            'Contact Information': [
                'Phone Number', 'Email Address'
            ],
            'Address Details': [
                'Residential Address',
                {'name': 'City', 'type': 'combo', 'values': [
                    'Manila', 'Jakarta', 'Bangkok', 'Singapore', 'Kuala Lumpur',
                    'Ho Chi Minh City', 'Hanoi', 'Phnom Penh', 'Yangon', 'Vientiane',
                    'Bandar Seri Begawan', 'Dili', 'Other'
                ]},
                {'name': 'State/Province', 'type': 'combo', 'values': [
                    # Philippines
                    'Metro Manila', 'Cebu', 'Davao', 'Rizal', 'Cavite',
                    # Indonesia
                    'Jakarta', 'West Java', 'East Java', 'Central Java', 'Bali',
                    # Thailand
                    'Bangkok', 'Chiang Mai', 'Phuket', 'Nonthaburi', 'Songkhla',
                    # Malaysia
                    'Selangor', 'Johor', 'Penang', 'Sabah', 'Sarawak',
                    # Vietnam
                    'Ho Chi Minh', 'Hanoi', 'Da Nang', 'Hai Phong', 'Can Tho',
                    'Other'
                ]},
                'Postal Code',
                {'name': 'Country', 'type': 'combo', 'values': [
                    'Philippines', 'Indonesia', 'Thailand', 'Singapore', 'Malaysia',
                    'Vietnam', 'Cambodia', 'Myanmar', 'Laos', 'Brunei',
                    'Timor-Leste', 'Other'
                ]}
            ],
            'Political Information': [
                {'name': 'Party Affiliation', 'type': 'combo', 'values': [
                    # Philippines
                    'PDP-Laban', 'Liberal Party', 'Nacionalista Party', 'NPC', 'NUP',
                    # Indonesia
                    'PDI-P', 'Golkar', 'Gerindra', 'PKB', 'Demokrat',
                    # Thailand
                    'Pheu Thai', 'Move Forward', 'Bhumjaithai', 'Democrat Party',
                    # Malaysia
                    'UMNO', 'PKR', 'DAP', 'PAS', 'Bersatu',
                    # Singapore
                    'PAP', 'WP', 'PSP',
                    'Independent', 'Other'
                ]},
                'Current Position',
                {'name': 'Application Type', 'type': 'combo', 'values': [
                    'New Role Application', 'Re-election Application'
                ]}
            ],
            'Role Application': [
                {'name': 'Desired Position', 'type': 'combo', 'values': [
                    'President', 'Prime Minister', 'Vice President', 'Deputy Prime Minister',
                    'Senator', 'Member of Parliament', 'Governor', 'Mayor',
                    'Provincial Council Member', 'City Council Member',
                    'Barangay Captain', 'District Representative', 'Other'
                ]},
                {'name': 'Term Length', 'type': 'combo', 'values': [
                    '3 Years', '4 Years', '5 Years', '6 Years'
                ]},
                'Previous Position (if re-election)'
            ],
            'Qualifications': [
                'Educational Background'
            ],
            'Professional Background': [
                'Professional Experience'
            ],
            'Campaign Information': [
                'Campaign Platform',
                'Campaign Promises'
            ],
            'Additional Information': [
                'Political Experience',
                'Vision Statement'
            ]
        }
        
        entries = {}
        text_fields = ['Educational Background', 'Professional Experience', 
                       'Campaign Platform', 'Campaign Promises', 
                       'Political Experience', 'Vision Statement']
        
        # Style for section frames
        section_style = {
            'bg': '#1A1A1A',
            'pady': 15,
            'padx': 20,
            'relief': tk.GROOVE,
            'bd': 1
        }
        
        # Create sections with two-column layout
        for section_title, fields in sections.items():
            # Section frame
            section_frame = tk.Frame(scrollable_frame, **section_style)
            section_frame.pack(fill='x', padx=20, pady=10)
            
            # Section title
            tk.Label(
                section_frame,
                text=section_title,
                font=('Arial', 14, 'bold'),
                bg=section_style['bg'],
                fg='#00BFFF'
            ).pack(anchor='w', pady=(0, 10))
            
            # Create two-column layout for fields
            for i in range(0, len(fields), 2):
                row_frame = tk.Frame(section_frame, bg=section_style['bg'])
                row_frame.pack(fill='x', pady=5)
                
                # Process first field
                field = fields[i]
                field_frame = tk.Frame(row_frame, bg=section_style['bg'])
                field_frame.pack(side=tk.LEFT, expand=True, fill='x', padx=(0, 10))
                
                if isinstance(field, dict):
                    field_name = field['name']
                    field_type = field['type']
                else:
                    field_name = field
                    field_type = 'entry'
                
                tk.Label(
                    field_frame,
                    text=f"{field_name}:",
                    font=self.style['font'],
                    bg=section_style['bg'],
                    fg=self.style['fg']
                ).pack(anchor='w')
                
                if field_type == 'combo':
                    entry = ttk.Combobox(
                        field_frame,
                        values=field['values'],
                        font=self.style['font'],
                        state='readonly',
                        width=27
                    )
                    entry.set("Select...")
                elif field_type == 'date':
                    # Create date picker frame
                    date_frame = tk.Frame(field_frame, bg=section_style['bg'])
                    date_frame.pack(fill='x')
                    
                    # Year
                    year_values = list(range(1900, datetime.now().year + 1))
                    year = ttk.Combobox(
                        date_frame,
                        values=year_values,
                        font=self.style['font'],
                        width=6
                    )
                    year.set("Year")
                    year.pack(side=tk.LEFT, padx=2)
                    
                    # Month
                    month_values = list(range(1, 13))
                    month = ttk.Combobox(
                        date_frame,
                        values=month_values,
                        font=self.style['font'],
                        width=4
                    )
                    month.set("MM")
                    month.pack(side=tk.LEFT, padx=2)
                    
                    # Day
                    day_values = list(range(1, 32))
                    day = ttk.Combobox(
                        date_frame,
                        values=day_values,
                        font=self.style['font'],
                        width=4
                    )
                    day.set("DD")
                    day.pack(side=tk.LEFT, padx=2)
                    
                    entry = (year, month, day)
                else:
                    if field_name in text_fields:
                        entry = tk.Text(
                            field_frame,
                            font=self.style['font'],
                            bg=self.style['entry_bg'],
                            fg=self.style['entry_fg'],
                            height=4,
                            width=30
                        )
                    else:
                        entry = tk.Entry(
                            field_frame,
                            font=self.style['font'],
                            bg=self.style['entry_bg'],
                            fg=self.style['entry_fg'],
                            width=30
                        )
                        if 'password' in field_name.lower():
                            entry.configure(show="*")
                
                if field_type != 'date':
                    entry.pack(fill='x', pady=2)
                entries[field_name] = entry
                
                # Process second field if it exists
                if i + 1 < len(fields):
                    field_frame = tk.Frame(row_frame, bg=section_style['bg'])
                    field_frame.pack(side=tk.LEFT, expand=True, fill='x')
                    
                    field = fields[i + 1]
                    if isinstance(field, dict):
                        field_name = field['name']
                        field_type = field['type']
                    else:
                        field_name = field
                        field_type = 'entry'
                    
                    tk.Label(
                        field_frame,
                        text=f"{field_name}:",
                        font=self.style['font'],
                        bg=section_style['bg'],
                        fg=self.style['fg']
                    ).pack(anchor='w')
                    
                    if field_type == 'combo':
                        entry = ttk.Combobox(
                            field_frame,
                            values=field['values'],
                            font=self.style['font'],
                            state='readonly',
                            width=27
                        )
                        entry.set("Select...")
                    elif field_type == 'date':
                        # Create date picker frame
                        date_frame = tk.Frame(field_frame, bg=section_style['bg'])
                        date_frame.pack(fill='x')
                        
                        # Year
                        year_values = list(range(1900, datetime.now().year + 1))
                        year = ttk.Combobox(
                            date_frame,
                            values=year_values,
                            font=self.style['font'],
                            width=6
                        )
                        year.set("Year")
                        year.pack(side=tk.LEFT, padx=2)
                        
                        # Month
                        month_values = list(range(1, 13))
                        month = ttk.Combobox(
                            date_frame,
                            values=month_values,
                            font=self.style['font'],
                            width=4
                        )
                        month.set("MM")
                        month.pack(side=tk.LEFT, padx=2)
                        
                        # Day
                        day_values = list(range(1, 32))
                        day = ttk.Combobox(
                            date_frame,
                            values=day_values,
                            font=self.style['font'],
                            width=4
                        )
                        day.set("DD")
                        day.pack(side=tk.LEFT, padx=2)
                        
                        entry = (year, month, day)
                    else:
                        entry = tk.Entry(
                            field_frame,
                            font=self.style['font'],
                            bg=self.style['entry_bg'],
                            fg=self.style['entry_fg'],
                            relief=self.style['entry_relief'],
                            width=30
                        )
                        if 'password' in field_name.lower():
                            entry.configure(show="*")
                    
                    if field_type != 'date':
                        entry.pack(fill='x', pady=2)
                    entries[field_name] = entry
        
        # Terms and Conditions
        terms_frame = tk.Frame(scrollable_frame, bg=self.style['bg'])
        terms_frame.pack(fill='x', padx=20, pady=10)

        self.terms_var = tk.BooleanVar()
        
        terms_check_frame = tk.Frame(terms_frame, bg=self.style['bg'])
        terms_check_frame.pack(fill='x')
        
        tk.Checkbutton(
            terms_check_frame,
            text="I agree to the ",
            variable=self.terms_var,
            font=self.style['font'],
            bg=self.style['bg'],
            fg=self.style['fg'],
            selectcolor='black',
            activebackground=self.style['bg'],
            activeforeground=self.style['fg']
        ).pack(side=tk.LEFT)

        terms_link = tk.Label(
            terms_check_frame,
            text="Terms and Conditions",
            font=('Arial', 11, 'underline'),
            bg=self.style['bg'],
            fg='#00BFFF',
            cursor='hand2'
        )
        terms_link.pack(side=tk.LEFT)

        # Bind click event to terms link
        terms_link.bind('<Button-1>', lambda e: self.show_terms_and_conditions())

        # Add hover effect for terms link
        terms_link.bind('<Enter>', lambda e: e.widget.configure(fg='#33CCFF'))
        terms_link.bind('<Leave>', lambda e: e.widget.configure(fg='#00BFFF'))
        
        # Register button
        button_frame = tk.Frame(scrollable_frame, bg=self.style['bg'])
        button_frame.pack(pady=20)
        
        register_btn = tk.Button(
            button_frame,
            text="Submit Candidacy",
            command=lambda: self.process_candidate_registration(entries, registration_window),
            font=('Arial', 12, 'bold'),
            bg='#00BFFF',
            fg='white',
            width=20,
            height=2,
            cursor='hand2'
        )
        register_btn.pack()
        
        # Configure the scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

    def process_candidate_registration(self, entries, window):
        """Process candidate registration form"""
        if not self.terms_var.get():
            messagebox.showerror("Error", "Please accept the Terms and Conditions!")
            return
        
        # Get all field values
        data = {}
        for field, entry in entries.items():
            if isinstance(entry, tuple):  # Date field
                year, month, day = entry
                try:
                    # Validate and format date
                    date_str = f"{year.get()}-{int(month.get()):02d}-{int(day.get()):02d}"
                    # Verify it's a valid date
                    datetime.strptime(date_str, '%Y-%m-%d')
                    data[field] = date_str
                except (ValueError, TypeError):
                    messagebox.showerror("Error", f"Invalid date format for {field}")
                    return
            elif isinstance(entry, tk.Text):
                data[field] = entry.get("1.0", tk.END).strip()
            else:
                data[field] = entry.get().strip()
        
        # Validation
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        if data['Password'] != data['Confirm Password']:
            messagebox.showerror("Error", "Passwords do not match!")
            return
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['Email Address']):
            messagebox.showerror("Error", "Invalid email address!")
            return
        
        # Validate age
        try:
            birth_date = datetime.strptime(data['Date of Birth'], '%Y-%m-%d')
            age = (datetime.now() - birth_date).days // 365
            if age < 25:
                messagebox.showerror("Error", "Must be 25 or older to register as a candidate!")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
            return
        
        if data['Username'] in self.voters or data['Username'] in self.admin_data:
            messagebox.showerror("Error", "Username already exists!")
            return
        
        # Add candidate with extended information
        self.voters[data['Username']] = {
            'password': hashlib.sha256(data['Password'].encode()).hexdigest(),
            'full_name': data['Full Name'],
            'date_of_birth': data['Date of Birth'],
            'national_id': data['National ID Number'],
            'phone': data['Phone Number'],
            'email': data['Email Address'],
            'address': {
                'street': data['Residential Address'],
                'city': data['City'],
                'state': data['State/Province'],
                'postal_code': data['Postal Code'],
                'country': data['Country']
            },
            'gender': data['Gender'],
            'is_candidate': True,
            'party': data['Party Affiliation'],
            'current_position': data['Current Position'],
            'desired_position': data['Desired Position'],
            'term_length': data['Term Length'],
            'education': data['Educational Background'],
            'experience': data['Professional Experience'],
            'platform': data['Campaign Platform'],
            'promises': data['Campaign Promises'],
            'political_experience': data['Political Experience'],
            'vision': data['Vision Statement'],
            'registration_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Add to candidates list
        self.candidates[data['Full Name']] = 0
        
        self.save_voters()
        self.save_votes()
        messagebox.showinfo("Success", "Candidate registration successful! You can now login.")
        window.destroy()

    def show_profile(self):
        """Show user profile and voting history"""
        profile_window = tk.Toplevel(self.root)
        profile_window.title("User Profile")
        profile_window.configure(bg=self.style['bg'])
        profile_window.geometry("600x800")
        
        user_data = self.voters[self.current_user]
        
        # Create scrollable frame
        canvas = tk.Canvas(profile_window, bg=self.style['bg'])
        scrollbar = ttk.Scrollbar(profile_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.style['bg'])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill="both", expand=True)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Profile Header
        tk.Label(
            scrollable_frame,
            text="Profile Information",
            font=('Arial', 20, 'bold'),
            bg=self.style['bg'],
            fg='#00BFFF'
        ).pack(pady=20)
        
        # User Details
        details_frame = tk.Frame(scrollable_frame, bg='#1A1A1A', padx=20, pady=20)
        details_frame.pack(fill='x', padx=20)
        
        details = [
            ('Full Name', user_data['full_name']),
            ('Email', user_data['email']),
            ('Phone', user_data['phone']),
            ('Date of Birth', user_data['date_of_birth']),
            ('Gender', user_data.get('gender', 'Not specified')),
            ('Occupation', user_data.get('occupation', 'Not specified')),
            ('Registration Date', user_data['registration_date'])
        ]  # Add closing bracket here
        
        for label, value in details:
            row = tk.Frame(details_frame, bg='#1A1A1A')
            row.pack(fill='x', pady=2)
            
            tk.Label(
                row,
                text=f"{label}:",
                font=self.style['font'],
                bg='#1A1A1A',
                fg='#00BFFF',
                width=15,
                anchor='w'
            ).pack(side=tk.LEFT)
            
            tk.Label(
                row,
                text=value,
                font=self.style['font'],
                bg='#1A1A1A',
                fg=self.style['fg'],
                anchor='w'
            ).pack(side=tk.LEFT, padx=10)
        
        # Address Information
        tk.Label(
            scrollable_frame,
            text="Address Information",
            font=('Arial', 16, 'bold'),
            bg=self.style['bg'],
            fg='#00BFFF'
        ).pack(pady=20)
        
        address_frame = tk.Frame(scrollable_frame, bg='#1A1A1A', padx=20, pady=20)
        address_frame.pack(fill='x', padx=20)
        
        address = user_data['address']
        for field in ['street', 'city', 'state', 'postal_code', 'country']:
            row = tk.Frame(address_frame, bg='#1A1A1A')
            row.pack(fill='x', pady=2)
            
            tk.Label(
                row,
                text=f"{field.title()}:",
                font=self.style['font'],
                bg='#1A1A1A',
                fg='#00BFFF',
                width=15,
                anchor='w'
            ).pack(side=tk.LEFT)
            
            tk.Label(
                row,
                text=address[field],
                font=self.style['font'],
                bg='#1A1A1A',
                fg=self.style['fg'],
                anchor='w'
            ).pack(side=tk.LEFT, padx=10)
        
        # Voting History
        tk.Label(
            scrollable_frame,
            text="Voting History",
            font=('Arial', 16, 'bold'),
            bg=self.style['bg'],
            fg='#00BFFF'
        ).pack(pady=20)
        
        history_frame = tk.Frame(scrollable_frame, bg='#1A1A1A', padx=20, pady=20)
        history_frame.pack(fill='x', padx=20)
        
        # Group votes by role
        user_votes = {}
        for vote in self.voting_history:
            if vote.get('voter') == self.current_user:
                role = vote.get('role', 'Unknown Role')
                if role not in user_votes:
                    user_votes[role] = []
                user_votes[role].append(vote)
        
        if user_votes:
            for role, votes in user_votes.items():
                # Role header
                tk.Label(
                    history_frame,
                    text=f"{role}:",
                    font=('Arial', 12, 'bold'),
                    bg='#1A1A1A',
                    fg='#00BFFF'
                ).pack(anchor='w', pady=(10, 5))
                
                for vote in votes:
                    tk.Label(
                        history_frame,
                        text=f"{vote['timestamp']}: Voted for {vote['candidate']}",
                        font=self.style['font'],
                        bg='#1A1A1A',
                        fg=self.style['fg']
                    ).pack(anchor='w', padx=20, pady=2)
        else:
            tk.Label(
                history_frame,
                text="No voting history",
                font=('Arial', 12, 'italic'),
                bg='#1A1A1A',
                fg='#888888'
            ).pack(pady=10)
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

    def change_password(self):
        """Allow users to change their password"""
        # Check if password change window already exists
        for window in self.root.winfo_children():
            if isinstance(window, tk.Toplevel) and window.title() == "Change Password":
                window.lift()  # Bring existing window to front
                return
        
        change_window = tk.Toplevel(self.root)
        change_window.title("Change Password")
        change_window.configure(bg=self.style['bg'])
        change_window.geometry("400x400")  # Made window taller to accommodate new field
        
        # Make window modal
        change_window.transient(self.root)
        change_window.grab_set()
        
        tk.Label(
            change_window,
            text="Change Password",
            font=('Arial', 16, 'bold'),
            bg=self.style['bg'],
            fg=self.style['fg']
        ).pack(pady=20)
        
        # Current password
        tk.Label(
            change_window,
            text="Current Password:",
            font=self.style['font'],
            bg=self.style['bg'],
            fg=self.style['fg']
        ).pack()
        
        current_pass = tk.Entry(
            change_window,
            font=self.style['font'],
            bg=self.style['entry_bg'],
            fg=self.style['entry_fg'],
            show="•"
        )
        current_pass.pack(pady=5)
        
        # New password
        tk.Label(
            change_window,
            text="New Password:",
            font=self.style['font'],
            bg=self.style['bg'],
            fg=self.style['fg']
        ).pack()
        
        new_pass = tk.Entry(
            change_window,
            font=self.style['font'],
            bg=self.style['entry_bg'],
            fg=self.style['entry_fg'],
            show="•"
        )
        new_pass.pack(pady=5)
        
        # Confirm new password
        tk.Label(
            change_window,
            text="Confirm New Password:",
            font=self.style['font'],
            bg=self.style['bg'],
            fg=self.style['fg']
        ).pack()
        
        confirm_pass = tk.Entry(
            change_window,
            font=self.style['font'],
            bg=self.style['entry_bg'],
            fg=self.style['entry_fg'],
            show="•"
        )
        confirm_pass.pack(pady=5)
        
        # Show/Hide password checkboxes
        show_pass_frame = tk.Frame(change_window, bg=self.style['bg'])
        show_pass_frame.pack(pady=5)
        
        # Show current password
        show_current = tk.BooleanVar()
        tk.Checkbutton(
            show_pass_frame,
            text="Show Current",
            variable=show_current,
            command=lambda: current_pass.configure(show='' if show_current.get() else '•'),
            bg=self.style['bg'],
            fg=self.style['fg'],
            selectcolor='#E8F5E9'  # Light green background when selected
        ).pack(side=tk.LEFT, padx=5)
        
        # Show new password
        show_new = tk.BooleanVar()
        tk.Checkbutton(
            show_pass_frame,
            text="Show New",
            variable=show_new,
            command=lambda: new_pass.configure(show='' if show_new.get() else '•'),
            bg=self.style['bg'],
            fg=self.style['fg'],
            selectcolor='#E8F5E9'  # Light green background when selected
        ).pack(side=tk.LEFT, padx=5)
        
        # Show confirm password
        show_confirm = tk.BooleanVar()
        tk.Checkbutton(
            show_pass_frame,
            text="Show Confirm",
            variable=show_confirm,
            command=lambda: confirm_pass.configure(show='' if show_confirm.get() else '•'),
            bg=self.style['bg'],
            fg=self.style['fg'],
            selectcolor='#E8F5E9'  # Light green background when selected
        ).pack(side=tk.LEFT, padx=5)
        
        def update_password():
            current = current_pass.get()
            new = new_pass.get()
            confirm = confirm_pass.get()
            
            # Validate current password
            if hashlib.sha256(current.encode()).hexdigest() != self.voters[self.current_user]['password']:
                messagebox.showerror("Error", "Current password is incorrect!")
                return
            
            if new != confirm:
                messagebox.showerror("Error", "New passwords do not match!")
                return
            
            if len(new) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters!")
                return
            
            # Update password
            self.voters[self.current_user]['password'] = hashlib.sha256(new.encode()).hexdigest()
            self.save_voters()
            messagebox.showinfo("Success", "Password changed successfully!")
            change_window.destroy()
        
        # Buttons frame
        btn_frame = tk.Frame(change_window, bg=self.style['bg'])
        btn_frame.pack(pady=20)
        
        # Update button
        update_btn = tk.Button(
            btn_frame,
            text="Update Password",
            command=update_password,
            font=self.style['font'],
            bg='#00BFFF',
            fg='white',
            width=15,
            cursor='hand2'
        )
        update_btn.pack(side=tk.LEFT, padx=5)
        
        # Cancel button
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            command=change_window.destroy,
            font=self.style['font'],
            bg='red',
            fg='white',
            width=15,
            cursor='hand2'
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Add hover effects
        update_btn.bind('<Enter>', lambda e: e.widget.configure(bg='#33CCFF'))
        update_btn.bind('<Leave>', lambda e: e.widget.configure(bg='#00BFFF'))
        
        cancel_btn.bind('<Enter>', lambda e: e.widget.configure(bg='#FF6666'))
        cancel_btn.bind('<Leave>', lambda e: e.widget.configure(bg='#FF4444'))

    def update_voters_list(self):
        """Update the voters treeview"""
        for item in self.voters_tree.get_children():
            self.voters_tree.delete(item)
        
        for username, data in self.voters.items():
            if not data.get('is_candidate', False):  # Show only voters
                self.voters_tree.insert('', 'end', values=(
                    username,
                    data['full_name'],
                    data['email'],
                    data['phone'],
                    data['registration_date']
                ))

    def update_candidates_list(self):
        """Update the candidates treeview"""
        for item in self.candidates_tree.get_children():
            self.candidates_tree.delete(item)
        
        for username, data in self.voters.items():
            if data.get('is_candidate', False):  # Show only candidates
                self.candidates_tree.insert('', 'end', values=(
                    data['full_name'],
                    data.get('party', 'Independent'),
                    self.candidates.get(data['full_name'], 0),
                    data['registration_date']
                ))

    def search_voters(self, query):
        """Search voters by name or username"""
        for item in self.voters_tree.get_children():
            self.voters_tree.delete(item)
        
        for username, data in self.voters.items():
            if not data.get('is_candidate', False):
                if (query.lower() in username.lower() or 
                    query.lower() in data['full_name'].lower()):
                    self.voters_tree.insert('', 'end', values=(
                        username,
                        data['full_name'],
                        data['email'],
                        data['phone'],
                        data['registration_date']
                    ))

    def search_candidates(self, query):
        """Search candidates by name or party"""
        for item in self.candidates_tree.get_children():
            self.candidates_tree.delete(item)
        
        for username, data in self.voters.items():
            if data.get('is_candidate', False):
                if (query.lower() in data['full_name'].lower() or 
                    query.lower() in data.get('party', '').lower()):
                    self.candidates_tree.insert('', 'end', values=(
                        data['full_name'],
                        data.get('party', 'Independent'),
                        self.candidates.get(data['full_name'], 0),
                        data['registration_date']
                    ))

    def view_candidate_details(self, selection):
        """Show detailed information about selected candidate"""
        if not selection:
            messagebox.showwarning("Warning", "Please select a candidate first!")
            return
        
        item = selection[0]
        candidate_name = self.candidates_tree.item(item)['values'][0]
        
        # Find candidate data
        candidate_data = None
        candidate_username = None
        for username, data in self.voters.items():
            if data.get('is_candidate') and data['full_name'] == candidate_name:
                candidate_data = data
                candidate_username = username
                break
        
        if candidate_data:
            details_window = tk.Toplevel(self.root)
            details_window.title(f"Candidate Details - {candidate_name}")
            details_window.geometry("800x600")
            details_window.configure(bg=self.style['bg'])
            
            # Create scrollable frame for details
            canvas = tk.Canvas(details_window, bg=self.style['bg'])
            scrollbar = ttk.Scrollbar(details_window, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=self.style['bg'])
            
            canvas.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            canvas.pack(side=tk.LEFT, fill="both", expand=True)
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            
            # Title
            tk.Label(
                scrollable_frame,
                text="Candidate Information",
                font=('Arial', 20, 'bold'),
                bg=self.style['bg'],
                fg='#00BFFF'
            ).pack(pady=20)
            
            # Create sections with editable fields
            sections = {
                'Login Credentials': [
                    'username',
                    {'name': 'new_password', 'type': 'password', 'label': 'New Password (leave blank to keep current)'}
                ],
                'Personal Information': [
                    'full_name',
                    {'name': 'date_of_birth', 'type': 'date'},
                    {'name': 'gender', 'type': 'combo', 'values': ['Male', 'Female', 'Other']},
                    'national_id'
                ],
                'Contact Information': [
                    'email',
                    'phone'
                ],
                'Address Details': [
                    'address.street',
                    {'name': 'address.city', 'type': 'combo', 'values': [
                        'Manila', 'Jakarta', 'Bangkok', 'Singapore', 'Kuala Lumpur',
                        'Ho Chi Minh City', 'Hanoi', 'Phnom Penh', 'Yangon', 'Vientiane',
                        'Bandar Seri Begawan', 'Dili', 'Other'
                    ]},
                    {'name': 'address.state', 'type': 'combo', 'values': [
                        'Metro Manila', 'Cebu', 'Davao', 'Rizal', 'Cavite',
                        'Jakarta', 'West Java', 'East Java', 'Central Java', 'Bali',
                        'Bangkok', 'Chiang Mai', 'Phuket', 'Nonthaburi', 'Songkhla',
                        'Selangor', 'Johor', 'Penang', 'Sabah', 'Sarawak',
                        'Ho Chi Minh', 'Hanoi', 'Da Nang', 'Hai Phong', 'Can Tho',
                        'Other'
                    ]},
                    'address.postal_code',
                    {'name': 'address.country', 'type': 'combo', 'values': [
                        'Philippines', 'Indonesia', 'Thailand', 'Singapore', 'Malaysia',
                        'Vietnam', 'Cambodia', 'Myanmar', 'Laos', 'Brunei',
                        'Timor-Leste', 'Other'
                    ]}
                ],
                'Political Information': [
                    {'name': 'party', 'type': 'combo', 'values': [
                        'PDP-Laban', 'Liberal Party', 'Nacionalista Party', 'NPC', 'NUP',
                        'PDI-P', 'Golkar', 'Gerindra', 'PKB', 'Demokrat',
                        'Pheu Thai', 'Move Forward', 'Bhumjaithai', 'Democrat Party',
                        'UMNO', 'PKR', 'DAP', 'PAS', 'Bersatu',
                        'PAP', 'WP', 'PSP',
                        'Independent', 'Other'
                    ]},
                    'current_position',
                    {'name': 'application_type', 'type': 'combo', 'values': [
                        'New Role Application', 'Re-election Application'
                    ]}
                ],
                'Role Application': [
                    {'name': 'desired_position', 'type': 'combo', 'values': [
                        'President', 'Prime Minister', 'Vice President', 'Deputy Prime Minister',
                        'Senator', 'Member of Parliament', 'Governor', 'Mayor',
                        'Provincial Council Member', 'City Council Member',
                        'Barangay Captain', 'District Representative', 'Other'
                    ]},
                    {'name': 'term_length', 'type': 'combo', 'values': [
                        '3 Years', '4 Years', '5 Years', '6 Years'
                    ]},
                    'previous_position'
                ],
                'Qualifications': [
                    'education',
                    'experience'
                ],
                'Campaign Information': [
                    'platform',
                    'promises',
                    'vision'
                ]
            }
            
            entries = {}
            text_fields = ['education', 'experience', 'platform', 'promises', 'vision']
            
            # Create editable fields
            for section_title, fields in sections.items():
                # Section frame
                section_frame = tk.Frame(scrollable_frame, bg='#1A1A1A', padx=20, pady=15)
                section_frame.pack(fill='x', padx=20, pady=10)
                
                # Section title
                tk.Label(
                    section_frame,
                    text=section_title,
                    font=('Arial', 14, 'bold'),
                    bg='#1A1A1A',
                    fg='#00BFFF'
                ).pack(anchor='w', pady=(0, 10))
                
                # Create fields
                for field in fields:
                    field_frame = tk.Frame(section_frame, bg='#1A1A1A')
                    field_frame.pack(fill='x', pady=5)
                    
                    if isinstance(field, dict):
                        field_name = field['name']
                        field_type = field['type']
                    else:
                        field_name = field
                        field_type = 'entry'
                    
                    # Get the display name
                    display_name = field_name.replace('_', ' ').replace('.', ' ').title()
                    
                    tk.Label(
                        field_frame,
                        text=f"{display_name}:",
                        font=self.style['font'],
                        bg='#1A1A1A',
                        fg=self.style['fg']
                    ).pack(anchor='w')
                    
                    # Get current value
                    if '.' in field_name:  # Handle nested address fields
                        parts = field_name.split('.')
                        current_value = candidate_data.get(parts[0], {}).get(parts[1], '')
                    else:
                        current_value = candidate_data.get(field_name, '')
                    
                    if field_type == 'combo':
                        entry = ttk.Combobox(
                            field_frame,
                            values=field['values'],
                            font=self.style['font'],
                            state='readonly',
                            width=30
                        )
                        entry.set(current_value if current_value else "Select...")
                    elif field_type == 'password':
                        entry = tk.Entry(
                            field_frame,
                            font=self.style['font'],
                            bg=self.style['entry_bg'],
                            fg=self.style['entry_fg'],
                            show="•",
                            width=30
                        )
                        if current_value:
                            entry.insert(0, current_value)
                        
                        # Add show/hide password toggle
                        show_var = tk.BooleanVar()
                        tk.Checkbutton(
                            field_frame,
                            text="Show password",
                            variable=show_var,
                            command=lambda e=entry, v=show_var: e.configure(show='' if v.get() else '•'),
                            font=('Arial', 10),
                            bg='#1A1A1A',
                            fg='#888888',
                            selectcolor='black',
                            activebackground='#1A1A1A',
                            activeforeground='#888888'
                        ).pack(anchor='w')
                    elif field_type == 'date':
                        # Create date picker frame
                        date_frame = tk.Frame(field_frame, bg='#1A1A1A')
                        date_frame.pack(fill='x')
                        
                        # Parse current date
                        try:
                            current_date = datetime.strptime(current_value, '%Y-%m-%d')
                            current_year = current_date.year
                            current_month = current_date.month
                            current_day = current_date.day
                        except:
                            current_year = ''
                            current_month = ''
                            current_day = ''
                        
                        # Year
                        year_values = list(range(1900, datetime.now().year + 1))
                        year = ttk.Combobox(
                            date_frame,
                            values=year_values,
                            font=self.style['font'],
                            width=6
                        )
                        year.set(current_year or "Year")
                        year.pack(side=tk.LEFT, padx=2)
                        
                        # Month
                        month_values = list(range(1, 13))
                        month = ttk.Combobox(
                            date_frame,
                            values=month_values,
                            font=self.style['font'],
                            width=4
                        )
                        month.set(current_month or "MM")
                        month.pack(side=tk.LEFT, padx=2)
                        
                        # Day
                        day_values = list(range(1, 32))
                        day = ttk.Combobox(
                            date_frame,
                            values=day_values,
                            font=self.style['font'],
                            width=4
                        )
                        day.set(current_day or "DD")
                        day.pack(side=tk.LEFT, padx=2)
                        
                        entry = (year, month, day)
                    else:
                        if field_name in text_fields:
                            entry = tk.Text(
                                field_frame,
                                font=self.style['font'],
                                bg=self.style['entry_bg'],
                                fg=self.style['entry_fg'],
                                height=4,
                                width=30
                            )
                            entry.insert('1.0', current_value)
                        else:
                            entry = tk.Entry(
                                field_frame,
                                font=self.style['font'],
                                bg=self.style['entry_bg'],
                                fg=self.style['entry_fg'],
                                width=30
                            )
                            entry.insert(0, current_value)
                    
                    if field_type != 'date':
                        entry.pack(fill='x', pady=2)
                    entries[field_name] = entry
            
            def save_changes():
                # Collect all updated values
                updated_data = {}
                for field_name, entry in entries.items():
                    if isinstance(entry, tuple):  # Date field
                        year, month, day = entry
                        try:
                            date_str = f"{year.get()}-{int(month.get()):02d}-{int(day.get()):02d}"
                            datetime.strptime(date_str, '%Y-%m-%d')  # Validate date
                            if '.' in field_name:
                                parts = field_name.split('.')
                                if parts[0] not in updated_data:
                                    updated_data[parts[0]] = {}
                                updated_data[parts[0]][parts[1]] = date_str
                            else:
                                updated_data[field_name] = date_str
                        except:
                            messagebox.showerror("Error", f"Invalid date format for {field_name}")
                            return
                    elif isinstance(entry, tk.Text):
                        value = entry.get('1.0', tk.END).strip()
                        if '.' in field_name:
                            parts = field_name.split('.')
                            if parts[0] not in updated_data:
                                updated_data[parts[0]] = {}
                            updated_data[parts[0]][parts[1]] = value
                        else:
                            updated_data[field_name] = value
                    else:
                        value = entry.get().strip()
                        if '.' in field_name:
                            parts = field_name.split('.')
                            if parts[0] not in updated_data:
                                updated_data[parts[0]] = {}
                            updated_data[parts[0]][parts[1]] = value
                        else:
                            updated_data[field_name] = value
                
                # Update the voter data
                self.voters[candidate_username].update(updated_data)
                
                # Update password if new one is provided
                new_password = entries.get('new_password')
                if new_password and new_password.get().strip():
                    self.voters[candidate_username]['password'] = hashlib.sha256(
                        new_password.get().strip().encode()
                    ).hexdigest()
                
                # Update candidates list if name changed
                if updated_data['full_name'] != candidate_name:
                    votes = self.candidates.pop(candidate_name)
                    self.candidates[updated_data['full_name']] = votes
                
                self.save_voters()
                self.save_votes()
                self.update_candidates_list()
                details_window.destroy()
                messagebox.showinfo("Success", "Candidate information updated successfully!")
            
            # Buttons frame
            btn_frame = tk.Frame(scrollable_frame, bg=self.style['bg'])
            btn_frame.pack(pady=20)
            
            tk.Button(
                btn_frame,
                text="Save Changes",
                command=save_changes,
                font=self.style['font'],
                bg='#00BFFF',
                fg='white',
                width=15
            ).pack(side=tk.LEFT, padx=5)
            
            tk.Button(
                btn_frame,
                text="Cancel",
                command=details_window.destroy,
                font=self.style['font'],
                bg='red',
                fg='white',
                width=15
            ).pack(side=tk.LEFT, padx=5)
            
            # Configure scrolling
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

    def show_admin_settings(self):
        """Show admin settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Admin Settings")
        settings_window.configure(bg=self.style['bg'])
        settings_window.geometry("600x700")
        
        # Create scrollable frame
        canvas = tk.Canvas(settings_window, bg=self.style['bg'])
        scrollbar = ttk.Scrollbar(settings_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.style['bg'])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill="both", expand=True)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Title
        tk.Label(
            scrollable_frame,
            text="Admin Settings",
            font=('Arial', 24, 'bold'),
            bg=self.style['bg'],
            fg='#00BFFF'
        ).pack(pady=20)
        
        # Current Admin Info
        current_admin = next(iter(self.admin_data.keys()))
        info_frame = tk.Frame(scrollable_frame, bg='#1A1A1A', padx=30, pady=20)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            info_frame,
            text="Current Admin Information",
            font=('Arial', 16, 'bold'),
            bg='#1A1A1A',
            fg='#00BFFF'
        ).pack(anchor='w', pady=(0, 15))
        
        tk.Label(
            info_frame,
            text=f"Username: {current_admin}",
            font=self.style['font'],
            bg='#1A1A1A',
            fg=self.style['fg']
        ).pack(anchor='w')
        
        # Change Username Section
        username_frame = tk.Frame(scrollable_frame, bg='#1A1A1A', padx=30, pady=20)
        username_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            username_frame,
            text="Change Username",
            font=('Arial', 16, 'bold'),
            bg='#1A1A1A',
            fg='#00BFFF'
        ).pack(anchor='w', pady=(0, 15))
        
        tk.Label(
            username_frame,
            text="New Username:",
            font=self.style['font'],
            bg='#1A1A1A',
            fg=self.style['fg']
        ).pack(anchor='w', pady=(0, 5))
        
        new_username = tk.Entry(
            username_frame,
            font=self.style['font'],
            bg=self.style['entry_bg'],
            fg=self.style['entry_fg'],
            width=30
        )
        new_username.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            username_frame,
            text="Current Password (to confirm):",
            font=self.style['font'],
            bg='#1A1A1A',
            fg=self.style['fg']
        ).pack(anchor='w', pady=(0, 5))
        
        username_confirm_pass = tk.Entry(
            username_frame,
            font=self.style['font'],
            bg=self.style['entry_bg'],
            fg=self.style['entry_fg'],
            show="•",
            width=30
        )
        username_confirm_pass.pack(fill='x', pady=(0, 10))
        
        tk.Button(
            username_frame,
            text="Change Username",
            command=lambda: self.change_admin_username(
                new_username.get(),
                username_confirm_pass.get(),
                settings_window
            ),
            font=('Arial', 12, 'bold'),
            bg='#00BFFF',
            fg='white',
            width=20,
            cursor='hand2'
        ).pack(pady=10)
        
        # Change Password Section
        password_frame = tk.Frame(scrollable_frame, bg='#1A1A1A', padx=30, pady=20)
        password_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            password_frame,
            text="Change Password",
            font=('Arial', 16, 'bold'),
            bg='#1A1A1A',
            fg='#00BFFF'
        ).pack(anchor='w', pady=(0, 15))
        
        tk.Label(
            password_frame,
            text="Current Password:",
            font=self.style['font'],
            bg='#1A1A1A',
            fg=self.style['fg']
        ).pack(anchor='w', pady=(0, 5))
        
        current_pass = tk.Entry(
            password_frame,
            font=self.style['font'],
            bg=self.style['entry_bg'],
            fg=self.style['entry_fg'],
            show="•",
            width=30
        )
        current_pass.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            password_frame,
            text="New Password:",
            font=self.style['font'],
            bg='#1A1A1A',
            fg=self.style['fg']
        ).pack(anchor='w', pady=(0, 5))
        
        new_pass = tk.Entry(
            password_frame,
            font=self.style['font'],
            bg=self.style['entry_bg'],
            fg=self.style['entry_fg'],
            show="•",
            width=30
        )
        new_pass.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            password_frame,
            text="Confirm New Password:",
            font=self.style['font'],
            bg='#1A1A1A',
            fg=self.style['fg']
        ).pack(anchor='w', pady=(0, 5))
        
        confirm_pass = tk.Entry(
            password_frame,
            font=self.style['font'],
            bg=self.style['entry_bg'],
            fg=self.style['entry_fg'],
            show="•",
            width=30
        )
        confirm_pass.pack(fill='x', pady=(0, 10))
        
        tk.Button(
            password_frame,
            text="Change Password",
            command=lambda: self.update_admin_password(
                current_pass.get(),
                new_pass.get(),
                confirm_pass.get(),
                settings_window
            ),
            font=('Arial', 12, 'bold'),
            bg='#00BFFF',
            fg='white',
            width=20,
            cursor='hand2'
        ).pack(pady=10)
        
        # Create New Admin Section
        new_admin_frame = tk.Frame(scrollable_frame, bg='#1A1A1A', padx=30, pady=20)
        new_admin_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            new_admin_frame,
            text="Create New Admin",
            font=('Arial', 16, 'bold'),
            bg='#1A1A1A',
            fg='#00BFFF'
        ).pack(anchor='w', pady=(0, 15))
        
        tk.Label(
            new_admin_frame,
            text="New Admin Username:",
            font=self.style['font'],
            bg='#1A1A1A',
            fg=self.style['fg']
        ).pack(anchor='w', pady=(0, 5))
        
        new_admin_username = tk.Entry(
            new_admin_frame,
            font=self.style['font'],
            bg=self.style['entry_bg'],
            fg=self.style['entry_fg'],
            width=30
        )
        new_admin_username.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            new_admin_frame,
            text="New Admin Password:",
            font=self.style['font'],
            bg='#1A1A1A',
            fg=self.style['fg']
        ).pack(anchor='w', pady=(0, 5))
        
        new_admin_password = tk.Entry(
            new_admin_frame,
            font=self.style['font'],
            bg=self.style['entry_bg'],
            fg=self.style['entry_fg'],
            show="•",
            width=30
        )
        new_admin_password.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            new_admin_frame,
            text="Your Current Password (to confirm):",
            font=self.style['font'],
            bg='#1A1A1A',
            fg=self.style['fg']
        ).pack(anchor='w', pady=(0, 5))
        
        admin_confirm_pass = tk.Entry(
            new_admin_frame,
            font=self.style['font'],
            bg=self.style['entry_bg'],
            fg=self.style['entry_fg'],
            show="•",
            width=30
        )
        admin_confirm_pass.pack(fill='x', pady=(0, 10))
        
        tk.Button(
            new_admin_frame,
            text="Create New Admin",
            command=lambda: self.create_new_admin(
                new_admin_username.get(),
                new_admin_password.get(),
                admin_confirm_pass.get(),
                settings_window
            ),
            font=('Arial', 12, 'bold'),
            bg='#00BFFF',
            fg='white',
            width=20,
            cursor='hand2'
        ).pack(pady=10)
        
        # Show/Hide password toggles
        for entry, label in [
            (current_pass, "Show current password"),
            (new_pass, "Show new password"),
            (confirm_pass, "Show confirm password"),
            (username_confirm_pass, "Show password"),
            (new_admin_password, "Show new admin password"),
            (admin_confirm_pass, "Show confirm password")
        ]:
            frame = entry.master
            show_var = tk.BooleanVar()
            tk.Checkbutton(
                frame,
                text=label,
                variable=show_var,
                command=lambda e=entry, v=show_var: e.configure(show='' if v.get() else '•'),
                font=('Arial', 10),
                bg='#1A1A1A',
                fg='#888888',
                selectcolor='black',
                activebackground='#1A1A1A',
                activeforeground='#888888'
            ).pack(anchor='w')
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
    def change_admin_username(self, new_username, current_password, window):
        """Change admin username"""
        if not new_username or not current_password:
            messagebox.showerror("Error", "All fields are required!")
            return
            
        current_admin = next(iter(self.admin_data.keys()))
        
        # Verify current password
        if hashlib.sha256(current_password.encode()).hexdigest() != self.admin_data[current_admin]:
            messagebox.showerror("Error", "Current password is incorrect!")
            return
            
        # Validate new username
        if len(new_username) < 4:
            messagebox.showerror("Error", "Username must be at least 4 characters!")
            return
            
        if new_username in self.voters:
            messagebox.showerror("Error", "Username already exists!")
            return
            
        # Update admin username
        self.admin_data[new_username] = self.admin_data.pop(current_admin)
        self.save_admin()
        
        messagebox.showinfo("Success", "Admin username updated successfully!")
        window.destroy()
        self.show_admin_settings()
        
    def create_new_admin(self, username, password, current_password, window):
        """Create a new admin account"""
        if not username or not password or not current_password:
            messagebox.showerror("Error", "All fields are required!")
            return
            
        current_admin = next(iter(self.admin_data.keys()))
        
        # Verify current admin's password
        if hashlib.sha256(current_password.encode()).hexdigest() != self.admin_data[current_admin]:
            messagebox.showerror("Error", "Your current password is incorrect!")
            return
            
        # Validate new admin credentials
        if len(username) < 4:
            messagebox.showerror("Error", "Username must be at least 4 characters!")
            return
            
        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters!")
            return
            
        if username in self.admin_data or username in self.voters:
            messagebox.showerror("Error", "Username already exists!")
            return
            
        # Create new admin account
        self.admin_data[username] = hashlib.sha256(password.encode()).hexdigest()
        self.save_admin()
        
        messagebox.showinfo("Success", f"New admin account '{username}' created successfully!")
        window.destroy()
        self.show_admin_settings()

    def show_admin_management_interface(self, container):
        """Show admin management interface"""
        management_frame = tk.Frame(container, bg=self.style['bg'])
        management_frame.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(
            management_frame,
            text="Admin Management",
            font=('Arial', 24, 'bold'),
            bg=self.style['bg'],
            fg=self.style['fg']
        ).pack(pady=20)

        # Create new admin user
        tk.Button(
            management_frame,
            text="Create New Admin User",
            command=self.prompt_create_admin_user,
            font=self.style['font'],
            bg='#00BFFF',
            fg='white'
        ).pack(pady=10)

        # View voters
        tk.Button(
            management_frame,
            text="View Voters",
            command=self.update_voters_list,
            font=self.style['font'],
            bg='#00BFFF',
            fg='white'
        ).pack(pady=10)

        # View candidates
        tk.Button(
            management_frame,
            text="View Candidates",
            command=self.update_candidates_list,
            font=self.style['font'],
            bg='#00BFFF',
            fg='white'
        ).pack(pady=10)

    def prompt_create_admin_user(self):
        """Prompt for new admin user details"""
        new_admin_window = tk.Toplevel(self.root)
        new_admin_window.title("Create New Admin User")
        new_admin_window.configure(bg=self.style['bg'])
        
        tk.Label(
            new_admin_window,
            text="Username:",
            font=self.style['font'],
            bg=self.style['bg'],
            fg=self.style['fg']
        ).pack(pady=5)
        
        username_entry = tk.Entry(new_admin_window, font=self.style['font'])
        username_entry.pack(pady=5)

        tk.Label(
            new_admin_window,
            text="Password:",
            font=self.style['font'],
            bg=self.style['bg'],
            fg=self.style['fg']
        ).pack(pady=5)
        
        password_entry = tk.Entry(new_admin_window, font=self.style['font'], show="*")
        password_entry.pack(pady=5)

        tk.Button(
            new_admin_window,
            text="Create Admin",
            command=lambda: self.create_admin_user(username_entry.get(), password_entry.get()),
            font=self.style['font'],
            bg='#00BFFF',
            fg='white'
        ).pack(pady=10)

    def voter_change_password(self):
        """Allow voters to change their password"""
        change_window = tk.Toplevel(self.root)
        change_window.title("Change Password")
        change_window.configure(bg=self.style['bg'])
        change_window.geometry("400x300")
        
        tk.Label(
            change_window,
            text="Change Password",
            font=('Arial', 16, 'bold'),
            bg=self.style['bg'],
            fg=self.style['fg']
        ).pack(pady=20)
        
        # Current password
        tk.Label(
            change_window,
            text="Current Password:",
            font=self.style['font'],
            bg=self.style['bg'],
            fg=self.style['fg']
        ).pack()
        
        current_pass = tk.Entry(
            change_window,
            font=self.style['font'],
            bg=self.style['entry_bg'],
            fg=self.style['entry_fg'],
            show="*"
        )
        current_pass.pack(pady=5)
        
        # New password
        tk.Label(
            change_window,
            text="New Password:",
            font=self.style['font'],
            bg=self.style['bg'],
            fg=self.style['fg']
        ).pack()
        
        new_pass = tk.Entry(
            change_window,
            font=self.style['font'],
            bg=self.style['entry_bg'],
            fg=self.style['entry_fg'],
            show="*"
        )
        new_pass.pack(pady=5)
        
        # Confirm new password
        tk.Label(
            change_window,
            text="Confirm New Password:",
            font=self.style['font'],
            bg=self.style['bg'],
            fg=self.style['fg']
        ).pack()
        
        confirm_pass = tk.Entry(
            change_window,
            font=self.style['font'],
            bg=self.style['entry_bg'],
            fg=self.style['entry_fg'],
            show="*"
        )
        confirm_pass.pack(pady=5)
        
        def update_password():
            current = current_pass.get()
            new = new_pass.get()
            confirm = confirm_pass.get()
            
            # Validate current password
            if hashlib.sha256(current.encode()).hexdigest() != self.voters[self.current_user]['password']:
                messagebox.showerror("Error", "Current password is incorrect!")
                return
            
            if new != confirm:
                messagebox.showerror("Error", "New passwords do not match!")
                return
            
            if len(new) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters!")
                return
            
            # Update password
            self.voters[self.current_user]['password'] = hashlib.sha256(new.encode()).hexdigest()
            self.save_voters()
            messagebox.showinfo("Success", "Password changed successfully!")
            change_window.destroy()
        
        tk.Button(
            change_window,
            text="Update Password",
            command=update_password,
            font=self.style['font'],
            bg='#00BFFF',
            fg='white',
            width=15,
            height=2
        ).pack(pady=20)

    def show_candidate_profile(self):
        """Show candidate profile"""
        candidate_data = self.voters[self.current_user]
        profile_window = tk.Toplevel(self.root)
        profile_window.title("Candidate Profile")
        profile_window.configure(bg=self.style['bg'])
        
        tk.Label(
            profile_window,
            text=f"Candidate Profile: {candidate_data['full_name']}",
            font=('Arial', 20, 'bold'),
            bg=self.style['bg'],
            fg='#00BFFF'
        ).pack(pady=20)

        # Display candidate details
        details = [
            ('Full Name', candidate_data['full_name']),
            ('Party', candidate_data.get('party', 'Independent')),
            ('Current Position', candidate_data.get('current_position', 'N/A')),
            ('Email', candidate_data['email']),
            ('Phone', candidate_data['phone']),
            ('Registration Date', candidate_data['registration_date'])
        ]  # Added missing closing bracket
        
        for label, value in details:
            tk.Label(
                profile_window,
                text=f"{label}: {value}",
                font=self.style['font'],
                bg=self.style['bg'],
                fg=self.style['fg']
            ).pack(anchor='w', padx=20, pady=5)

    def show_voter_profile(self):
        """Show voter profile"""
        voter_data = self.voters[self.current_user]
        profile_window = tk.Toplevel(self.root)
        profile_window.title("Voter Profile")
        profile_window.configure(bg=self.style['bg'])
        
        tk.Label(
            profile_window,
            text=f"Voter Profile: {voter_data['full_name']}",
            font=('Arial', 20, 'bold'),
            bg=self.style['bg'],
            fg='#00BFFF'
        ).pack(pady=20)

        # Display voter details
        details = [
            ('Full Name', voter_data['full_name']),
            ('Email', voter_data['email']),
            ('Phone', voter_data['phone']),
            ('Registration Date', voter_data['registration_date'])
        ]  # Add closing bracket here
        
        for label, value in details:
            tk.Label(
                profile_window,
                text=f"{label}: {value}",
                font=self.style['font'],
                bg=self.style['bg'],
                fg=self.style['fg']
            ).pack(anchor='w', padx=20, pady=5)

    def edit_voter(self, selection):
        """Edit selected voter"""
        if not selection:
            messagebox.showwarning("Warning", "Please select a voter to edit!")
            return
        
        item = selection[0]
        username = self.voters_tree.item(item)['values'][0]
        
        if username not in self.voters:
            messagebox.showerror("Error", "Voter not found!")
            return
        
        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit Voter - {username}")
        edit_window.configure(bg=self.style['bg'])
        edit_window.geometry("500x600")  # Make window larger
        
        voter_data = self.voters[username]
        
        # Create scrollable frame
        canvas = tk.Canvas(edit_window, bg=self.style['bg'])
        scrollbar = ttk.Scrollbar(edit_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.style['bg'])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill="both", expand=True)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Title
        tk.Label(
            scrollable_frame,
            text="Edit Voter Information",
            font=('Arial', 16, 'bold'),
            bg=self.style['bg'],
            fg='#00BFFF'
        ).pack(pady=20)
        
        # Create entry fields for editable data
        fields = {
            'Username': username,
            'Password': '',  # Empty for security
            'Full Name': voter_data['full_name'],
            'Email': voter_data['email'],
            'Phone': voter_data['phone']
        }
        
        entries = {}
        for field, value in fields.items():
            frame = tk.Frame(scrollable_frame, bg=self.style['bg'])
            frame.pack(fill='x', padx=20, pady=5)
            
            tk.Label(
                frame,
                text=f"{field}:",
                font=self.style['font'],
                bg=self.style['bg'],
                fg=self.style['fg'],
                width=15,
                anchor='w'
            ).pack(side=tk.LEFT)
            
            if field == 'Password':
                entry = tk.Entry(frame, font=self.style['font'], show="•")
                # Add show/hide password checkbox
                show_password_var = tk.BooleanVar()
                tk.Checkbutton(
                    frame,
                    text="Show",
                    variable=show_password_var,
                    command=lambda e=entry, v=show_password_var: e.configure(show='' if v.get() else '•'),
                    bg=self.style['bg'],
                    fg=self.style['fg'],
                    selectcolor='black'
                ).pack(side=tk.RIGHT)
            else:
                entry = tk.Entry(frame, font=self.style['font'])
                entry.insert(0, value)
                if field == 'Username':
                    entry.configure(state='readonly')  # Make username read-only
            
            entry.pack(side=tk.LEFT, padx=5, expand=True, fill='x')
            entries[field] = entry
        
        # Add note about password
        tk.Label(
            scrollable_frame,
            text="Note: Leave password empty to keep current password",
            font=('Arial', 10, 'italic'),
            bg=self.style['bg'],
            fg='#888888'
        ).pack(pady=5)
        
        def save_changes():
            # Get new username and password
            new_password = entries['Password'].get().strip()
            
            # Validate email
            email = entries['Email'].get().strip()
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                messagebox.showerror("Error", "Invalid email address!")
                return
            
            # Update voter data
            updated_data = {
                'full_name': entries['Full Name'].get().strip(),
                'email': email,
                'phone': entries['Phone'].get().strip()
            }
            
            # Only update password if a new one is provided
            if new_password:
                updated_data['password'] = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
            
            # Update the voter's data
            self.voters[username].update(updated_data)
            self.save_voters()
            self.update_voters_list()
            edit_window.destroy()
            messagebox.showinfo("Success", "Voter information updated!")
        
        # Buttons frame
        btn_frame = tk.Frame(scrollable_frame, bg=self.style['bg'])
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="Save Changes",
            command=save_changes,
            font=self.style['font'],
            bg='#00BFFF',
            fg='white',
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            command=edit_window.destroy,
            font=self.style['font'],
            bg='red',
            fg='white',
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Configure the scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

    def delete_voter(self, selection):
        """Delete selected voter"""
        if not selection:
            messagebox.showwarning("Warning", "Please select a voter to delete!")
            return
        
        item = selection[0]
        username = self.voters_tree.item(item)['values'][0]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete voter {username}?"):
            if username in self.voters:
                del self.voters[username]
                self.save_voters()
                self.update_voters_list()
                messagebox.showinfo("Success", "Voter deleted successfully!")
            else:
                messagebox.showerror("Error", "Voter not found!")

    def export_results_as_pdf(self):
        """Export voting results as PDF"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
        except ImportError:
            if messagebox.askyesno("Missing Library", "The reportlab library is required for PDF export. Would you like to install it?"):
                self.install_reportlab()
                messagebox.showinfo("Success", "Please try exporting again now that reportlab is installed.")
            return

        # Create timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"voting_results_{timestamp}.pdf"
        
        # Create the PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        
        # Add title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        elements.append(Paragraph("Voting Results Report", title_style))
        elements.append(Spacer(1, 20))
        
        # Add timestamp
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
        elements.append(Spacer(1, 20))
        
        # Prepare results data
        total_votes = sum(self.candidates.values())
        data = [['Candidate', 'Party', 'Votes', 'Percentage']]
        
        # Sort candidates by votes (descending)
        sorted_candidates = sorted(
            self.candidates.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Add candidate data
        for candidate_name, votes in sorted_candidates:
            # Find candidate's party from voters data
            party = "Independent"
            for voter in self.voters.values():
                if voter.get('is_candidate', False) and voter['full_name'] == candidate_name:
                    party = voter.get('party', 'Independent')
                    break
            
            percentage = (votes / total_votes * 100) if total_votes > 0 else 0
            data.append([
                candidate_name,
                party,
                str(votes),
                f"{percentage:.2f}%"
            ])
        
        # Create table
        table = Table(data, colWidths=[2.5*inch, 2*inch, 1*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # Add voting history
        elements.append(Paragraph("Voting History", styles["Heading2"]))
        elements.append(Spacer(1, 10))
        
        history_data = [['Time', 'Candidate']]
        for vote in self.voting_history:
            history_data.append([
                vote['timestamp'],
                vote['candidate']
            ])
        
        history_table = Table(history_data, colWidths=[3*inch, 4*inch])
        history_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(history_table)
        
        # Build PDF
        try:
            doc.build(elements)
            messagebox.showinfo("Success", f"Results exported to {filename}")
            # Open the PDF file
            import os
            os.startfile(filename)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create PDF: {str(e)}")

    def install_reportlab(self):
        """Install the reportlab library"""
        try:
            import subprocess
            subprocess.check_call(['pip', 'install', 'reportlab'])
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install reportlab: {str(e)}")
            return False

    def save_votes(self):
        """Save votes and voting history to file"""
        data = {
            'candidates': self.candidates,
            'history': self.voting_history
        }
        with open(self.votes_file, 'w') as f:
            json.dump(data, f)

    def create_candidate_interface(self):
        """Create interface for candidate users"""
        # Clear current window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Main container with padding
        main_frame = tk.Frame(self.root, bg=self.style['bg'], padx=30, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Header section with welcome message and user info
        header_frame = tk.Frame(main_frame, bg='#1A1A1A', pady=20)
        header_frame.pack(fill='x', padx=20)
        
        user_data = self.voters[self.current_user]
        
        # Welcome message with candidate's name
        tk.Label(
            header_frame,
            text=f"Welcome, {user_data['full_name']}!",
            font=('Arial', 24, 'bold'),
            bg='#1A1A1A',
            fg='#00BFFF'
        ).pack(pady=(0, 10))
        
        tk.Label(
            header_frame,
            text=f"Running for: {user_data.get('desired_position', 'Not specified')}",
            font=('Arial', 16),
            bg='#1A1A1A',
            fg='white'
        ).pack(pady=5)
        
        tk.Label(
            header_frame,
            text=f"Party: {user_data.get('party', 'Independent')}",
            font=('Arial', 14),
            bg='#1A1A1A',
            fg='#888888'
        ).pack()
        
        # Create notebook for tabbed interface
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, pady=20)
        
        # Dashboard Tab
        dashboard_frame = tk.Frame(notebook, bg='#1A1A1A')
        notebook.add(dashboard_frame, text='Dashboard')
        
        # Campaign Stats
        stats_frame = tk.Frame(dashboard_frame, bg='#1A1A1A', padx=20, pady=20)
        stats_frame.pack(fill='x', pady=10)
        
        votes = self.candidates.get(user_data['full_name'], 0)
        total_votes = sum(self.candidates.values())
        vote_percentage = (votes / total_votes * 100) if total_votes > 0 else 0
        
        # Stats in a grid layout
        stats_grid = tk.Frame(stats_frame, bg='#1A1A1A')
        stats_grid.pack(fill='x')
        
        # Votes Received
        votes_frame = tk.Frame(stats_grid, bg='#2C2C2C', padx=20, pady=15)
        votes_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        
        tk.Label(
            votes_frame,
            text="Votes Received",
            font=('Arial', 12),
            bg='#2C2C2C',
            fg='#888888'
        ).pack()
        
        tk.Label(
            votes_frame,
            text=str(votes),
            font=('Arial', 24, 'bold'),
            bg='#2C2C2C',
            fg='#00BFFF'
        ).pack()
        
        # Vote Percentage
        percentage_frame = tk.Frame(stats_grid, bg='#2C2C2C', padx=20, pady=15)
        percentage_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        
        tk.Label(
            percentage_frame,
            text="Vote Share",
            font=('Arial', 12),
            bg='#2C2C2C',
            fg='#888888'
        ).pack()
        
        tk.Label(
            percentage_frame,
            text=f"{vote_percentage:.1f}%",
            font=('Arial', 24, 'bold'),
            bg='#2C2C2C',
            fg='#00BFFF'
        ).pack()
        
        # Configure grid
        stats_grid.grid_columnconfigure(0, weight=1)
        stats_grid.grid_columnconfigure(1, weight=1)
        
        # Campaign Information
        tk.Label(
            dashboard_frame,
            text="Campaign Overview",
            font=('Arial', 16, 'bold'),
            bg='#1A1A1A',
            fg='#00BFFF'
        ).pack(pady=(20, 10), padx=20, anchor='w')
        
        info_frame = tk.Frame(dashboard_frame, bg='#2C2C2C', padx=20, pady=20)
        info_frame.pack(fill='x', padx=20)
        
        # Platform preview
        tk.Label(
            info_frame,
            text="Campaign Platform:",
            font=('Arial', 12, 'bold'),
            bg='#2C2C2C',
            fg='white'
        ).pack(anchor='w')
        
        tk.Label(
            info_frame,
            text=user_data.get('platform', 'No platform specified')[:200] + "...",
            font=self.style['font'],
            bg='#2C2C2C',
            fg='#888888',
            wraplength=500,
            justify='left'
        ).pack(anchor='w', pady=(0, 10))
        
        # Profile Tab
        profile_frame = tk.Frame(notebook, bg='#1A1A1A')
        notebook.add(profile_frame, text='Profile')
        
        self.setup_candidate_profile_tab(profile_frame)
        
        # Campaign Tab
        campaign_frame = tk.Frame(notebook, bg='#1A1A1A')
        notebook.add(campaign_frame, text='Campaign')
        
        self.setup_campaign_tab(campaign_frame)
        
        # Quick Action Buttons
        actions_frame = tk.Frame(main_frame, bg=self.style['bg'])
        actions_frame.pack(fill='x', pady=20)
        
        buttons = [
            ("🔄 Update Profile", self.show_profile_editor),
            ("🔒 Change Password", self.change_password),
            ("📊 View Results", self.show_results),
            ("🚪 Logout", self.show_login_screen)
        ]
        
        for text, command in buttons:
            btn = tk.Button(
                actions_frame,
                text=text,
                command=command,
                font=self.style['font'],
                bg='#2C2C2C' if 'Logout' not in text else '#FF4444',
                fg='white',
                relief=tk.FLAT,
                padx=15,
                pady=8,
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=5)
            
            # Add hover effects
            if 'Logout' not in text:
                btn.bind('<Enter>', lambda e: e.widget.configure(bg='#404040'))
                btn.bind('<Leave>', lambda e: e.widget.configure(bg='#2C2C2C'))
            else:
                btn.bind('<Enter>', lambda e: e.widget.configure(bg='#FF6666'))
                btn.bind('<Leave>', lambda e: e.widget.configure(bg='#FF4444'))

    def setup_candidate_profile_tab(self, container):
        """Setup the profile tab in candidate interface"""
        user_data = self.voters[self.current_user]
        
        # Create scrollable frame
        canvas = tk.Canvas(container, bg='#1A1A1A')
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1A1A1A')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill="both", expand=True)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Profile Photo Section
        photo_frame = tk.Frame(scrollable_frame, bg='#1A1A1A', padx=20, pady=15)
        photo_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            photo_frame,
            text="Profile Photo",
            font=('Arial', 14, 'bold'),
            bg='#1A1A1A',
            fg='#00BFFF'
        ).pack(anchor='w', pady=(0, 10))
        
        # Create a container frame for the photo to control its size
        photo_container = tk.Frame(photo_frame, bg='#2C2C2C', width=150, height=150)
        photo_container.pack(pady=10)
        photo_container.pack_propagate(False)  # Prevent the frame from shrinking
        
        # Profile photo display
        photo_display = tk.Label(
            photo_container,
            bg='#2C2C2C',
            text="No profile photo"
        )
        photo_display.pack(expand=True, fill='both')
        
        # Load and display profile photo if it exists
        if 'profile_photo' in user_data:
            try:
                image = Image.open(user_data['profile_photo'])
                # Calculate dimensions to maintain aspect ratio within 150x150
                width, height = image.size
                ratio = min(150/width, 150/height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(image)
                photo_display.configure(image=photo)
                photo_display.image = photo  # Keep reference
                self.profile_image_path = user_data['profile_photo']
            except Exception as e:
                photo_display.configure(text="Unable to load photo")
        
        # Rest of the profile sections...
        # Personal Information Section
        self.create_profile_section(scrollable_frame, "Personal Information", [
            ("Full Name", user_data['full_name']),
            ("Date of Birth", user_data['date_of_birth']),
            ("Gender", user_data.get('gender', 'Not specified')),
            ("National ID", user_data['national_id'])
        ])
        
        # Contact Information Section
        self.create_profile_section(scrollable_frame, "Contact Information", [
            ("Email", user_data['email']),
            ("Phone", user_data['phone'])
        ])
        
        # Address Section
        address = user_data.get('address', {})
        self.create_profile_section(scrollable_frame, "Address", [
            ("Street", address.get('street', 'Not specified')),
            ("City", address.get('city', 'Not specified')),
            ("State/Province", address.get('state', 'Not specified')),
            ("Postal Code", address.get('postal_code', 'Not specified')),
            ("Country", address.get('country', 'Not specified'))
        ])
        
        # Political Information Section
        self.create_profile_section(scrollable_frame, "Political Information", [
            ("Party Affiliation", user_data.get('party', 'Independent')),
            ("Current Position", user_data.get('current_position', 'Not specified')),
            ("Desired Position", user_data.get('desired_position', 'Not specified')),
            ("Term Length", user_data.get('term_length', 'Not specified'))
        ])
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

    def setup_campaign_tab(self, container):
        """Setup the campaign tab in candidate interface"""
        user_data = self.voters[self.current_user]
        
        # Create scrollable frame
        canvas = tk.Canvas(container, bg='#1A1A1A')
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1A1A1A')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill="both", expand=True)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Campaign Platform Section
        self.create_campaign_section(scrollable_frame, "Campaign Platform", 
                                   user_data.get('platform', 'No platform specified'))
        
        # Campaign Promises Section
        self.create_campaign_section(scrollable_frame, "Campaign Promises", 
                                   user_data.get('promises', 'No promises specified'))
        
        # Vision Statement Section
        self.create_campaign_section(scrollable_frame, "Vision Statement", 
                                   user_data.get('vision', 'No vision statement specified'))
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

    def create_profile_section(self, container, title, fields):
        """Create a section in the profile tab"""
        section_frame = tk.Frame(container, bg='#2C2C2C', padx=20, pady=15)
        section_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            section_frame,
            text=title,
            font=('Arial', 14, 'bold'),
            bg='#2C2C2C',
            fg='#00BFFF'
        ).pack(anchor='w', pady=(0, 10))
        
        for label, value in fields:
            field_frame = tk.Frame(section_frame, bg='#2C2C2C')
            field_frame.pack(fill='x', pady=2)
            
            tk.Label(
                field_frame,
                text=f"{label}:",
                font=self.style['font'],
                bg='#2C2C2C',
                fg='white',
                width=15,
                anchor='w'
            ).pack(side=tk.LEFT)
            
            tk.Label(
                field_frame,
                text=value,
                font=self.style['font'],
                bg='#2C2C2C',
                fg='#888888',
                anchor='w'
            ).pack(side=tk.LEFT, padx=10)

    def create_campaign_section(self, container, title, content):
        """Create a section in the campaign tab"""
        section_frame = tk.Frame(container, bg='#2C2C2C', padx=20, pady=15)
        section_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            section_frame,
            text=title,
            font=('Arial', 14, 'bold'),
            bg='#2C2C2C',
            fg='#00BFFF'
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            section_frame,
            text=content,
            font=self.style['font'],
            bg='#2C2C2C',
            fg='#888888',
            wraplength=500,
            justify='left'
        ).pack(anchor='w')

    def show_profile_editor(self):
        """Enhanced profile editor for candidates"""
        editor_window = tk.Toplevel(self.root)
        editor_window.title("Edit Profile")
        editor_window.configure(bg=self.style['bg'])
        editor_window.geometry("900x800")
        
        # Create main canvas with scrollbar
        canvas = tk.Canvas(editor_window, bg=self.style['bg'])
        scrollbar = ttk.Scrollbar(editor_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.style['bg'])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill="both", expand=True)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Title and progress bar
        title_frame = tk.Frame(scrollable_frame, bg=self.style['bg'])
        title_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            title_frame,
            text="Edit Profile",
            font=('Arial', 24, 'bold'),
            bg=self.style['bg'],
            fg='#00BFFF'
        ).pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        ttk.Progressbar(
            title_frame,
            variable=self.progress_var,
            maximum=100,
            length=200,
            mode='determinate'
        ).pack(side=tk.RIGHT, padx=20)
        
        user_data = self.voters[self.current_user]
        entries = {}
        
        # Profile Photo Section
        photo_section = self.create_collapsible_section(
            scrollable_frame,
            "Profile Photo",
            self.create_image_upload
        )
        
        # Personal Information Section
        def create_personal_info(container):
            fields = [
                ('Full Name', 'full_name'),
                ('Date of Birth', 'date_of_birth'),
                ('Gender', 'gender', ['Male', 'Female', 'Other']),
                ('National ID', 'national_id')
            ]
            
            for field in fields:
                label, key = field[:2]
                field_type = field[2] if len(field) > 2 else None
                
                frame = tk.Frame(container, bg='#1A1A1A')
                frame.pack(fill='x', pady=5)
                
                tk.Label(
                    frame,
                    text=f"{label}:",
                    font=self.style['font'],
                    bg='#1A1A1A',
                    fg=self.style['fg']
                ).pack(anchor='w')
                
                if isinstance(field_type, list):
                    entry = ttk.Combobox(
                        frame,
                        values=field_type,
                        font=self.style['font'],
                        state='readonly'
                    )
                    entry.set(user_data.get(key, field_type[0]))
                else:
                    entry = tk.Entry(
                        frame,
                        font=self.style['font'],
                        bg=self.style['entry_bg'],
                        fg=self.style['entry_fg']
                    )
                    entry.insert(0, user_data.get(key, ''))
                
                entry.pack(fill='x', pady=2)
                entries[key] = entry
        
        personal_section = self.create_collapsible_section(
            scrollable_frame,
            "Personal Information",
            create_personal_info
        )
        
        # Contact Information Section
        def create_contact_info(container):
            fields = [
                ('Email', 'email'),
                ('Phone', 'phone')
            ]
            
            for label, key in fields:
                frame = tk.Frame(container, bg='#1A1A1A')
                frame.pack(fill='x', pady=5)
                
                tk.Label(
                    frame,
                    text=f"{label}:",
                    font=self.style['font'],
                    bg='#1A1A1A',
                    fg=self.style['fg']
                ).pack(anchor='w')
                
                entry = tk.Entry(
                    frame,
                    font=self.style['font'],
                    bg=self.style['entry_bg'],
                    fg=self.style['entry_fg']
                )
                entry.insert(0, user_data.get(key, ''))
                entry.pack(fill='x', pady=2)
                entries[key] = entry
        
        contact_section = self.create_collapsible_section(
            scrollable_frame,
            "Contact Information",
            create_contact_info
        )
        
        # Campaign Information Section (for candidates only)
        if user_data.get('is_candidate', False):
            def create_campaign_info(container):
                # Party and Position
                fields = [
                    ('Party Affiliation', 'party', [
                        'PDP-Laban', 'Liberal Party', 'Nacionalista Party',
                        'Independent', 'Other'
                    ]),
                    ('Current Position', 'current_position'),
                    ('Desired Position', 'desired_position', [
                        'President', 'Vice President', 'Senator',
                        'Representative', 'Governor', 'Mayor'
                    ])
                ]
                
                for field in fields:
                    label, key = field[:2]
                    field_type = field[2] if len(field) > 2 else None
                    
                    frame = tk.Frame(container, bg='#1A1A1A')
                    frame.pack(fill='x', pady=5)
                    
                    tk.Label(
                        frame,
                        text=f"{label}:",
                        font=self.style['font'],
                        bg='#1A1A1A',
                        fg=self.style['fg']
                    ).pack(anchor='w')
                    
                    if isinstance(field_type, list):
                        entry = ttk.Combobox(
                            frame,
                            values=field_type,
                            font=self.style['font'],
                            state='readonly'
                        )
                        entry.set(user_data.get(key, field_type[0]))
                    else:
                        entry = tk.Entry(
                            frame,
                            font=self.style['font'],
                            bg=self.style['entry_bg'],
                            fg=self.style['entry_fg']
                        )
                        entry.insert(0, user_data.get(key, ''))
                    
                    entry.pack(fill='x', pady=2)
                    entries[key] = entry
                
                # Rich text fields
                entries['platform'] = self.create_rich_text_field(
                    container,
                    "Campaign Platform",
                    user_data.get('platform', '')
                )
                
                entries['promises'] = self.create_rich_text_field(
                    container,
                    "Campaign Promises",
                    user_data.get('promises', '')
                )
                
                entries['vision'] = self.create_rich_text_field(
                    container,
                    "Vision Statement",
                    user_data.get('vision', '')
                )
            
            campaign_section = self.create_collapsible_section(
                scrollable_frame,
                "Campaign Information",
                create_campaign_info
            )
        
        # Preview Changes Button
        def preview_changes():
            preview_window = tk.Toplevel(editor_window)
            preview_window.title("Preview Changes")
            preview_window.configure(bg=self.style['bg'])
            preview_window.geometry("600x800")
            
            # Create scrollable preview
            preview_canvas = tk.Canvas(preview_window, bg=self.style['bg'])
            preview_scrollbar = ttk.Scrollbar(preview_window, orient="vertical", command=preview_canvas.yview)
            preview_frame = tk.Frame(preview_canvas, bg=self.style['bg'])
            
            preview_canvas.configure(yscrollcommand=preview_scrollbar.set)
            preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            preview_canvas.pack(side=tk.LEFT, fill="both", expand=True)
            preview_canvas.create_window((0, 0), window=preview_frame, anchor="nw")
            
            # Show changes
            tk.Label(
                preview_frame,
                text="Profile Preview",
                font=('Arial', 20, 'bold'),
                bg=self.style['bg'],
                fg='#00BFFF'
            ).pack(pady=20)
            
            for key, entry in entries.items():
                frame = tk.Frame(preview_frame, bg='#1A1A1A', padx=20, pady=10)
                frame.pack(fill='x', padx=20, pady=5)
                
                # Format key for display
                display_key = key.replace('_', ' ').title()
                
                tk.Label(
                    frame,
                    text=f"{display_key}:",
                    font=('Arial', 12, 'bold'),
                    bg='#1A1A1A',
                    fg='#00BFFF'
                ).pack(anchor='w')
                
                # Get new value
                if isinstance(entry, tk.Text):
                    new_value = entry.get('1.0', tk.END).strip()
                else:
                    new_value = entry.get().strip()
                
                # Show old and new values
                old_value = user_data.get(key, 'Not set')
                
                if new_value != old_value:
                    tk.Label(
                        frame,
                        text=f"Current: {old_value}",
                        font=self.style['font'],
                        bg='#1A1A1A',
                        fg='#888888'
                    ).pack(anchor='w')
                    
                    tk.Label(
                        frame,
                        text=f"New: {new_value}",
                        font=self.style['font'],
                        bg='#1A1A1A',
                        fg='white'
                    ).pack(anchor='w')
                else:
                    tk.Label(
                        frame,
                        text=str(new_value),
                        font=self.style['font'],
                        bg='#1A1A1A',
                        fg='white'
                    ).pack(anchor='w')
            
            # Configure preview scrolling
            preview_frame.bind(
                "<Configure>",
                lambda e: preview_canvas.configure(scrollregion=preview_canvas.bbox("all"))
            )
        
        # Buttons frame
        btn_frame = tk.Frame(scrollable_frame, bg=self.style['bg'])
        btn_frame.pack(pady=20)
        
        preview_btn = tk.Button(
            btn_frame,
            text="Preview Changes",
            command=preview_changes,
            font=self.style['font'],
            bg='#2C2C2C',
            fg='white',
            width=15,
            cursor='hand2'
        )
        preview_btn.pack(side=tk.LEFT, padx=5)
        
        def save_changes():
            # Validate required fields
            required_fields = ['full_name', 'email', 'phone']
            for field in required_fields:
                if not entries[field].get().strip():
                    messagebox.showerror("Error", f"{field.replace('_', ' ').title()} is required!")
                    return
            
            # Validate email format
            email = entries['email'].get().strip()
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                messagebox.showerror("Error", "Invalid email address!")
                return
            
            # Collect updated values
            updated_data = {}
            for key, entry in entries.items():
                if isinstance(entry, tk.Text):
                    value = entry.get('1.0', tk.END).strip()
                else:
                    value = entry.get().strip()
                updated_data[key] = value
            
            # Update the voter data
            self.voters[self.current_user].update(updated_data)
            
            # Update candidates list if name changed
            if user_data.get('is_candidate', False):
                old_name = user_data['full_name']
                new_name = updated_data['full_name']
                if new_name != old_name:
                    votes = self.candidates.pop(old_name)
                    self.candidates[new_name] = votes
            
            self.save_voters()
            self.save_votes()
            
            messagebox.showinfo("Success", "Profile updated successfully!")
            editor_window.destroy()
            
            # Refresh the interface
            if user_data.get('is_candidate', False):
                self.create_candidate_interface()
            else:
                self.create_main_interface()
        
        save_btn = tk.Button(
            btn_frame,
            text="Save Changes",
            command=save_changes,
            font=self.style['font'],
            bg='#00BFFF',
            fg='white',
            width=15,
            cursor='hand2'
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            command=editor_window.destroy,
            font=self.style['font'],
            bg='red',
            fg='white',
            width=15,
            cursor='hand2'
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Add hover effects
        for btn in [preview_btn, save_btn]:
            btn.bind('<Enter>', lambda e: e.widget.configure(bg='#404040'))
            btn.bind('<Leave>', lambda e: e.widget.configure(
                bg='#2C2C2C' if e.widget == preview_btn else '#00BFFF'
            ))
        
        cancel_btn.bind('<Enter>', lambda e: e.widget.configure(bg='#FF6666'))
        cancel_btn.bind('<Leave>', lambda e: e.widget.configure(bg='red'))
        
        # Configure the scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Setup autosave
        def autosave():
            # Save to temporary storage
            temp_data = {}
            for key, entry in entries.items():
                if isinstance(entry, tk.Text):
                    temp_data[key] = entry.get('1.0', tk.END).strip()
                else:
                    temp_data[key] = entry.get().strip()
            
            # Update progress bar
            filled_fields = sum(1 for v in temp_data.values() if v.strip())
            progress = (filled_fields / len(entries)) * 100
            self.progress_var.set(progress)
            
            # Schedule next autosave
            editor_window.after(30000, autosave)  # Autosave every 30 seconds
        
        # Start autosave
        autosave()

    def create_collapsible_section(self, container, title, content_creator):
        """Create a collapsible section for profile editing"""
        frame = tk.Frame(container, bg='#1A1A1A', padx=20, pady=10)
        frame.pack(fill='x', padx=10, pady=5)
        
        # Header frame with toggle button
        header = tk.Frame(frame, bg='#1A1A1A')
        header.pack(fill='x')
        
        # Toggle button (arrow)
        self.toggle_btn = tk.Label(
            header,
            text="▼",  # Down arrow
            font=('Arial', 12),
            bg='#1A1A1A',
            fg='#00BFFF',
            cursor='hand2'
        )
        self.toggle_btn.pack(side=tk.LEFT, padx=5)
        
        # Section title
        tk.Label(
            header,
            text=title,
            font=('Arial', 14, 'bold'),
            bg='#1A1A1A',
            fg='#00BFFF'
        ).pack(side=tk.LEFT, padx=5)
        
        # Content frame
        content_frame = tk.Frame(frame, bg='#1A1A1A')
        content_frame.pack(fill='x', pady=(10, 0))
        
        # Create content
        content_creator(content_frame)
        
        # Toggle function
        def toggle_section():
            if content_frame.winfo_viewable():
                content_frame.pack_forget()
                self.toggle_btn.configure(text="▶")  # Right arrow
            else:
                content_frame.pack(fill='x', pady=(10, 0))
                self.toggle_btn.configure(text="▼")  # Down arrow
        
        # Bind toggle function to both arrow and title
        self.toggle_btn.bind('<Button-1>', lambda e: toggle_section())
        header.bind('<Button-1>', lambda e: toggle_section())
        
        return frame

    def create_rich_text_field(self, container, label, initial_text=""):
        """Create a rich text editing field with formatting options"""
        frame = tk.Frame(container, bg='#1A1A1A')
        frame.pack(fill='x', pady=5)
        
        # Label
        tk.Label(
            frame,
            text=label,
            font=self.style['font'],
            bg='#1A1A1A',
            fg=self.style['fg']
        ).pack(anchor='w')
        
        # Toolbar frame
        toolbar = tk.Frame(frame, bg='#2C2C2C')
        toolbar.pack(fill='x', pady=2)
        
        # Formatting buttons
        buttons = [
            ("B", "bold"), 
            ("I", "italic"),
            ("U", "underline"),
            ("•", "bullet")
        ]
        
        for text, cmd in buttons:
            btn = tk.Button(
                toolbar,
                text=text,
                command=lambda c=cmd: self.apply_format(text_widget, c),
                font=('Arial', 10, 'bold'),
                bg='#2C2C2C',
                fg='white',
                bd=0,
                padx=10,
                pady=2,
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=2)
            
            # Hover effects
            btn.bind('<Enter>', lambda e: e.widget.configure(bg='#404040'))
            btn.bind('<Leave>', lambda e: e.widget.configure(bg='#2C2C2C'))
        
        # Text widget
        text_widget = tk.Text(
            frame,
            font=self.style['font'],
            bg=self.style['entry_bg'],
            fg=self.style['entry_fg'],
            height=4,
            width=40,
            wrap=tk.WORD
        )
        text_widget.pack(fill='x', pady=2)
        text_widget.insert('1.0', initial_text)
        
        return text_widget

    def apply_format(self, text_widget, format_type):
        """Apply formatting to selected text in rich text editor"""
        try:
            selection = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            text_widget.tag_add(format_type, tk.SEL_FIRST, tk.SEL_LAST)
            
            if format_type == "bold":
                text_widget.tag_configure(format_type, font=('Arial',12, 'bold'))
            elif format_type == "italic":
                text_widget.tag_configure(format_type, font=('Arial',12, 'italic'))
            elif format_type == "underline":
                text_widget.tag_configure(format_type, underline=True)
            elif format_type == "bullet":
                text_widget.insert(tk.SEL_FIRST, "• ")
        except tk.TclError:
            pass  # No selection

    def create_image_upload(self, container):
        """Create an image upload section for profile photo"""
        frame = tk.Frame(container, bg='#1A1A1A')
        frame.pack(fill='x', pady=10)
        
        # Image preview
        preview_frame = tk.Frame(frame, bg='#1A1A1A')
        preview_frame.pack(pady=5)
        
        self.preview_label = tk.Label(
            preview_frame,
            text="No image selected",
            bg='#2C2C2C',
            fg='#888888',
            width=20,
            height=10
        )
        self.preview_label.pack()
        
        # Load existing profile photo if available
        user_data = self.voters[self.current_user]
        if 'profile_photo' in user_data:
            try:
                image = Image.open(user_data['profile_photo'])
                # Calculate dimensions to maintain aspect ratio within 150x150
                width, height = image.size
                ratio = min(150/width, 150/height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(image)
                self.preview_label.configure(image=photo, width=new_width, height=new_height)
                self.preview_label.image = photo  # Keep reference
                self.profile_image_path = user_data['profile_photo']
            except Exception as e:
                self.preview_label.configure(text="Unable to load photo")  # Changed from photo_display to self.preview_label
        
        def upload_image():
            try:
                file_types = [
                    ('Image files', '*.png *.jpg *.jpeg *.gif *.bmp'),
                    ('All files', '*.*')
                ]
                filename = filedialog.askopenfilename(filetypes=file_types)
                
                if filename:
                    # Create a copy of the image in the application's directory
                    image = Image.open(filename)
                    # Calculate dimensions to maintain aspect ratio within 150x150
                    width, height = image.size
                    ratio = min(150/width, 150/height)
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Create unique filename using timestamp
                    new_filename = f"profile_photos/{self.current_user}_{int(time.time())}.png"
                    
                    # Ensure directory exists
                    os.makedirs("profile_photos", exist_ok=True)
                    
                    # Save the image
                    image.save(new_filename)
                    
                    # Update preview
                    photo = ImageTk.PhotoImage(image)
                    self.preview_label.configure(image=photo, width=new_width, height=new_height)
                    self.preview_label.image = photo
                    
                    # Save image path
                    self.profile_image_path = new_filename
                    
                    # Update voter data
                    self.voters[self.current_user]['profile_photo'] = new_filename
                    self.save_voters()
                    
                    messagebox.showinfo("Success", "Image uploaded successfully!")
                    
                    # Refresh the candidate interface to show the new photo
                    self.create_candidate_interface()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
        
        # Upload button
        upload_btn = tk.Button(
            frame,
            text="Upload Photo",
            command=upload_image,
            font=self.style['font'],
            bg='#00BFFF',
            fg='white',
            cursor='hand2'
        )
        upload_btn.pack(pady=5)
        
        # Remove button
        def remove_image():
            self.preview_label.configure(image="", text="No image selected")
            self.preview_label.image = None
            if hasattr(self, 'profile_image_path'):
                # Remove the file if it exists
                if os.path.exists(self.profile_image_path):
                    try:
                        os.remove(self.profile_image_path)
                    except Exception:
                        pass
                del self.profile_image_path
                # Remove from voter data
                if 'profile_photo' in self.voters[self.current_user]:
                    del self.voters[self.current_user]['profile_photo']
                    self.save_voters()
        
        remove_btn = tk.Button(
            frame,
            text="Remove Photo",
            command=remove_image,
            font=self.style['font'],
            bg='#FF4444',
            fg='white',
            cursor='hand2'
        )
        remove_btn.pack(pady=5)

    def show_candidate_details_popup(self, candidate_data):
        """Show detailed candidate information in a popup window"""
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Candidate Details - {candidate_data['full_name']}")
        details_window.configure(bg=self.style['bg'])
        details_window.geometry("800x600")
        
        # Create scrollable frame
        canvas = tk.Canvas(details_window, bg=self.style['bg'])
        scrollbar = ttk.Scrollbar(details_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.style['bg'])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill="both", expand=True)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Header with candidate photo and basic info
        header_frame = tk.Frame(scrollable_frame, bg='#1A1A1A', padx=30, pady=20)
        header_frame.pack(fill='x', padx=20, pady=10)
        
        # Create a container for photo and name side by side
        info_container = tk.Frame(header_frame, bg='#1A1A1A')
        info_container.pack(fill='x')
        
        # Photo container on the left
        photo_container = tk.Frame(info_container, bg='#2C2C2C', width=150, height=150)
        photo_container.pack(side=tk.LEFT, padx=(0, 20))
        photo_container.pack_propagate(False)
        
        # Profile photo display
        photo_display = tk.Label(
            photo_container,
            bg='#2C2C2C',
            text="No photo"
        )
        photo_display.pack(expand=True, fill='both')
        
        # Load and display profile photo if it exists
        if 'profile_photo' in candidate_data:
            try:
                image = Image.open(candidate_data['profile_photo'])
                # Calculate dimensions to maintain aspect ratio within 150x150
                width, height = image.size
                ratio = min(150/width, 150/height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(image)
                photo_display.configure(image=photo)
                photo_display.image = photo  # Keep reference
            except Exception as e:
                photo_display.configure(text="Unable to load photo")
        
        # Name and role on the right
        text_container = tk.Frame(info_container, bg='#1A1A1A')
        text_container.pack(side=tk.LEFT, fill='x', expand=True)
        
        tk.Label(
            text_container,
            text=candidate_data['full_name'],
            font=('Arial', 24, 'bold'),
            bg='#1A1A1A',
            fg='#00BFFF'
        ).pack(anchor='w')
        
        tk.Label(
            text_container,
            text=f"Running for {candidate_data.get('desired_position', 'Not specified')}",
            font=('Arial', 16),
            bg='#1A1A1A',
            fg='white'
        ).pack(anchor='w', pady=5)
        
        # Rest of the existing code remains the same...
        # Basic Information Section
        info_frame = tk.Frame(scrollable_frame, bg='#1A1A1A', padx=30, pady=20)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            info_frame,
            text="Basic Information",
            font=('Arial', 16, 'bold'),
            bg='#1A1A1A',
            fg='#00BFFF'
        ).pack(anchor='w', pady=(0, 10))
        
        basic_info = [
            ("Party Affiliation", candidate_data.get('party', 'Independent')),
            ("Current Position", candidate_data.get('current_position', 'Not specified')),
            ("Political Experience", candidate_data.get('political_experience', 'Not specified')),
            ("Education", candidate_data.get('education', 'Not specified'))
        ]
        
        for label, value in basic_info:
            info_row = tk.Frame(info_frame, bg='#1A1A1A')
            info_row.pack(fill='x', pady=2)
            
            tk.Label(
                info_row,
                text=f"{label}:",
                font=('Arial', 12, 'bold'),
                bg='#1A1A1A',
                fg='white',
                width=20,
                anchor='w'
            ).pack(side=tk.LEFT)
            
            tk.Label(
                info_row,
                text=value,
                font=('Arial', 12),
                bg='#1A1A1A',
                fg='#888888',
                wraplength=400,
                justify='left'
            ).pack(side=tk.LEFT, padx=10)
        
        # Campaign Platform Section
        platform_frame = tk.Frame(scrollable_frame, bg='#1A1A1A', padx=30, pady=20)
        platform_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            platform_frame,
            text="Campaign Platform",
            font=('Arial', 16, 'bold'),
            bg='#1A1A1A',
            fg='#00BFFF'
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            platform_frame,
            text=candidate_data.get('platform', 'No platform specified'),
            font=('Arial', 12),
            bg='#1A1A1A',
            fg='white',
            wraplength=700,
            justify='left'
        ).pack(anchor='w')
        
        # Campaign Promises Section
        promises_frame = tk.Frame(scrollable_frame, bg='#1A1A1A', padx=30, pady=20)
        promises_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            promises_frame,
            text="Campaign Promises",
            font=('Arial', 16, 'bold'),
            bg='#1A1A1A',
            fg='#00BFFF'
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            promises_frame,
            text=candidate_data.get('promises', 'No promises specified'),
            font=('Arial', 12),
            bg='#1A1A1A',
            fg='white',
            wraplength=700,
            justify='left'
        ).pack(anchor='w')
        
        # Vision Statement Section
        vision_frame = tk.Frame(scrollable_frame, bg='#1A1A1A', padx=30, pady=20)
        vision_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            vision_frame,
            text="Vision Statement",
            font=('Arial', 16, 'bold'),
            bg='#1A1A1A',
            fg='#00BFFF'
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            vision_frame,
            text=candidate_data.get('vision', 'No vision statement specified'),
            font=('Arial', 12),
            bg='#1A1A1A',
            fg='white',
            wraplength=700,
            justify='left'
        ).pack(anchor='w')
        
        # Close button
        tk.Button(
            scrollable_frame,
            text="Close",
            command=details_window.destroy,
            font=self.style['font'],
            bg='#FF4444',
            fg='white',
            width=15,
            cursor='hand2'
        ).pack(pady=20)
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

    def update_admin_password(self, current_password, new_password, confirm_password, settings_window):
        """Update admin password"""
        # Check if password change window already exists
        for window in self.root.winfo_children():
            if isinstance(window, tk.Toplevel) and window.title() == "Change Admin Password":
                window.lift()  # Bring existing window to front
                return
        
        if not current_password or not new_password or not confirm_password:
            messagebox.showerror("Error", "All fields are required!")
            return
        
        current_admin = next(iter(self.admin_data.keys()))
        
        # Verify current password
        if hashlib.sha256(current_password.encode()).hexdigest() != self.admin_data[current_admin]:  # Fixed variable name
            messagebox.showerror("Error", "Current password is incorrect!")
            return
        
        if new_password != confirm_password:
            messagebox.showerror("Error", "New passwords do not match!")
            return
        
        if len(new_password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters!")
            return
        
        # Update password
        self.admin_data[current_admin] = hashlib.sha256(new_password.encode()).hexdigest()
        self.save_admin()
        
        messagebox.showinfo("Success", "Admin password updated successfully!")
        settings_window.destroy()
        self.show_admin_settings()

    # Add this method to the VotingSystem class
    def show_terms_and_conditions(self):
        """Show terms and conditions in a popup window"""
        terms_window = tk.Toplevel(self.root)
        terms_window.title("Terms and Conditions")
        terms_window.configure(bg=self.style['bg'])
        terms_window.geometry("800x600")

        # Create scrollable frame
        canvas = tk.Canvas(terms_window, bg=self.style['bg'])
        scrollbar = ttk.Scrollbar(terms_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.style['bg'])

        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill="both", expand=True)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Title
        tk.Label(
            scrollable_frame,
            text="Terms and Conditions",
            font=('Arial', 20, 'bold'),
            bg=self.style['bg'],
            fg='#00BFFF'
        ).pack(pady=20)

        # Terms content
        terms_text = """
        1. Voter Registration and Eligibility
        - Users must be at least 18 years old to register as voters
        - Candidates must be at least 25 years old to register
        - All information provided must be accurate and truthful
        - Each user can only register one account

        2. Voting Rights and Responsibilities
        - Each registered voter is entitled to one vote per position
        - Votes cannot be changed once cast
        - Voters must not attempt to manipulate the voting system
        - Sharing account credentials is strictly prohibited

        3. Candidate Registration
        - Candidates must provide accurate personal and campaign information
        - False or misleading information will result in disqualification
        - Candidates must maintain professional conduct
        - Campaign promises must be realistic and ethical

        4. Privacy and Data Protection
        - Personal information will be protected and kept confidential
        - Data will only be used for election-related purposes
        - Users have the right to request their data deletion
        - System administrators will maintain data security

        5. System Usage
        - Users must not attempt to hack or manipulate the system
        - Suspicious activities will be monitored and investigated
        - System maintenance may occur periodically
        - Users must report any system issues or vulnerabilities

        6. Election Integrity
        - All votes will be counted accurately and fairly
        - Results will be transparent and verifiable
        - Independent audits may be conducted
        - Election disputes will be handled through proper channels

        7. Account Security
        - Users are responsible for maintaining password security
        - Suspicious activities should be reported immediately
        - Regular password updates are recommended
        - Multi-factor authentication may be implemented

        8. Modifications to Terms
        - Terms may be updated with notice to users
        - Continued use implies acceptance of new terms
        - Users will be notified of significant changes
        - Updated terms will be clearly dated and accessible

        9. Termination of Service
        - Accounts may be suspended for terms violations
        - Users can request account deletion
        - Election data will be archived securely
        - Appeals process available for account suspension

        10. Disclaimer
        - System availability is not guaranteed
        - Administrators not liable for technical issues
        - Results are final once certified
        - Users accept inherent technology limitations
        """

        tk.Label(
            scrollable_frame,
            text=terms_text,
            font=('Arial', 12),
            bg=self.style['bg'],
            fg=self.style['fg'],
            justify='left',
            wraplength=700
        ).pack(padx=20, pady=10)

        # Accept button
        tk.Button(
            scrollable_frame,
            text="Close",
            command=terms_window.destroy,
            font=self.style['font'],
            bg='#00BFFF',
            fg='white',
            width=20,
            cursor='hand2'
        ).pack(pady=20)

        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

# Try to import PIL, install if not available
try:
    from PIL import Image, ImageTk
except ImportError:
    def install_pillow():
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Pillow'])
            return True
        except subprocess.CalledProcessError:
            return False
    
    if install_pillow():
        from PIL import Image, ImageTk
    else:
        messagebox.showerror("Error", "Failed to install Pillow library. Image upload feature will not work.")

if __name__ == "__main__":
    root = tk.Tk()
    app = VotingSystem(root)
    
    # Add pre-registered candidates
    candidates_data = {
        'candidate1': {
            'username': 'candidate1',
            'password': '1234',
            'full_name': 'Maria Santos',
            'date_of_birth': '1975-06-15',
            'gender': 'Female',
            'national_id': 'PH123456789',
            'phone': '+63 912 345 6789',
            'email': 'maria.santos@email.com',
            'address': {
                'street': '123 Makati Avenue',
                'city': 'Manila',
                'state': 'Metro Manila',
                'postal_code': '1200',
                'country': 'Philippines'
            },
            'party': 'PDP-Laban',
            'current_position': 'Senator',
            'desired_position': 'President',
            'term_length': '6 Years',
            'education': 'PhD in Public Administration, University of the Philippines',
            'experience': '15 years in public service, Former Secretary of Education',
            'platform': 'Focus on education reform, economic development, and poverty alleviation',
            'promises': 'Universal education access, job creation, and infrastructure development',
            'vision': 'A prosperous and educated Philippines with opportunities for all',
            'is_candidate': True,
            'registration_date': '2024-01-15 08:00:00'
        },
        'candidate2': {
            'username': 'candidate2',
            'password': '1234',
            'full_name': 'Ahmad Rahman',
            'date_of_birth': '1980-03-20',
            'gender': 'Male',
            'national_id': 'ID987654321',
            'phone': '+62 811 234 5678',
            'email': 'ahmad.rahman@email.com',
            'address': {
                'street': '45 Sudirman Street',
                'city': 'Jakarta',
                'state': 'Jakarta',
                'postal_code': '10210',
                'country': 'Indonesia'
            },
            'party': 'PDI-P',
            'current_position': 'Governor',
            'desired_position': 'President',
            'term_length': '5 Years',
            'education': 'Masters in Economics, University of Indonesia',
            'experience': '12 years as Regional Governor',
            'platform': 'Economic reform, environmental protection, and social welfare',
            'promises': 'Green energy transition, social security enhancement',
            'vision': 'Sustainable and inclusive development for Indonesia',
            'is_candidate': True,
            'registration_date': '2024-01-16 09:30:00'
        },
        'candidate3': {
            'username': 'candidate3',
            'password': '1234',
            'full_name': 'Somchai Thaksin',
            'date_of_birth': '1978-09-10',
            'gender': 'Male',
            'national_id': 'TH456789012',
            'phone': '+66 89 123 4567',
            'email': 'somchai.thaksin@email.com',
            'address': {
                'street': '78 Sukhumvit Road',
                'city': 'Bangkok',
                'state': 'Bangkok',
                'postal_code': '10110',
                'country': 'Thailand'
            },
            'party': 'Pheu Thai',
            'current_position': 'Member of Parliament',
            'desired_position': 'Prime Minister',
            'term_length': '4 Years',
            'education': 'MBA, Chulalongkorn University',
            'experience': '10 years in Parliament',
            'platform': 'Digital economy transformation and agricultural modernization',
            'promises': 'Rural development, technology investment',
            'vision': 'Thailand 4.0 - A modern, innovative nation',
            'is_candidate': True,
            'registration_date': '2024-01-17 10:15:00'
        },
        'candidate4': {
            'username': 'candidate4',
            'password': '1234',
            'full_name': 'Tan Wei Ming',
            'date_of_birth': '1982-12-05',
            'gender': 'Male',
            'national_id': 'SG789012345',
            'phone': '+65 9123 4567',
            'email': 'tan.weiming@email.com',
            'address': {
                'street': '90 Orchard Road',
                'city': 'Singapore',
                'state': 'Singapore',
                'postal_code': '238875',
                'country': 'Singapore'
            },
            'party': 'PAP',
            'current_position': 'Minister of Trade',
            'desired_position': 'Prime Minister',
            'term_length': '5 Years',
            'education': 'PhD in International Relations, NUS',
            'experience': '8 years in Cabinet',
            'platform': 'Smart nation initiatives and international trade expansion',
            'promises': 'Technology innovation, economic growth',
            'vision': 'Singapore as a global hub for innovation',
            'is_candidate': True,
            'registration_date': '2024-01-18 11:45:00'
        },
        'candidate5': {
            'username': 'candidate5',
            'password': '1234',
            'full_name': 'Nurul Izzah',
            'date_of_birth': '1985-08-25',
            'gender': 'Female',
            'national_id': 'MY234567890',
            'phone': '+60 12 345 6789',
            'email': 'nurul.izzah@email.com',
            'address': {
                'street': '123 Jalan Sultan',
                'city': 'Kuala Lumpur',
                'state': 'Selangor',
                'postal_code': '50000',
                'country': 'Malaysia'
            },
            'party': 'PKR',
            'current_position': 'State Assembly Member',
            'desired_position': 'Prime Minister',
            'term_length': '5 Years',
            'education': 'Masters in Political Science, University of Malaya',
            'experience': '10 years in politics',
            'platform': 'Racial harmony and economic equality',
            'promises': 'Unity government, corruption elimination',
            'vision': 'A united and progressive Malaysia',
            'is_candidate': True,
            'registration_date': '2024-01-19 13:20:00'
        },
        'candidate6': {
            'username': 'candidate6',
            'password': '1234',
            'full_name': 'Nguyen Van Minh',
            'date_of_birth': '1977-04-30',
            'gender': 'Male',
            'national_id': 'VN345678901',
            'phone': '+84 90 123 4567',
            'email': 'nguyen.vanminh@email.com',
            'address': {
                'street': '56 Le Loi Street',
                'city': 'Ho Chi Minh City',
                'state': 'Ho Chi Minh',
                'postal_code': '700000',
                'country': 'Vietnam'
            },
            'party': 'Independent',
            'current_position': 'City Council Member',
            'desired_position': 'Governor',
            'term_length': '5 Years',
            'education': 'Masters in Urban Planning, Vietnam National University',
            'experience': '15 years in local government',
            'platform': 'Urban development and environmental protection',
            'promises': 'Smart city development, pollution reduction',
            'vision': 'Sustainable urban development for Vietnam',
            'is_candidate': True,
            'registration_date': '2024-01-20 14:10:00'
        },
        'candidate7': {
            'username': 'candidate7',
            'password': '1234',
            'full_name': 'Sok Channary',
            'date_of_birth': '1983-11-15',
            'gender': 'Female',
            'national_id': 'KH456789012',
            'phone': '+855 12 345 678',
            'email': 'sok.channary@email.com',
            'address': {
                'street': '34 Norodom Blvd',
                'city': 'Phnom Penh',
                'state': 'Phnom Penh',
                'postal_code': '12000',
                'country': 'Cambodia'
            },
            'party': 'Independent',
            'current_position': 'Provincial Council Member',
            'desired_position': 'Senator',
            'term_length': '6 Years',
            'education': 'BA in Political Science, Royal University of Phnom Penh',
            'experience': '8 years in local politics',
            'platform': 'Rural development and education access',
            'promises': 'School construction, agricultural support',
            'vision': 'Educational and economic opportunities for rural Cambodia',
            'is_candidate': True,
            'registration_date': '2024-01-21 15:30:00'
        },
        'candidate8': {
            'username': 'candidate8',
            'password': '1234',
            'full_name': 'Aung Min Thant',
            'date_of_birth': '1979-07-20',
            'gender': 'Male',
            'national_id': 'MM567890123',
            'phone': '+95 9 876 5432',
            'email': 'aung.minthant@email.com',
            'address': {
                'street': '78 Anawrahta Road',
                'city': 'Yangon',
                'state': 'Yangon',
                'postal_code': '11181',
                'country': 'Myanmar'
            },
            'party': 'Independent',
            'current_position': 'Township Administrator',
            'desired_position': 'Member of Parliament',
            'term_length': '5 Years',
            'education': 'Masters in Public Administration, Yangon University',
            'experience': '12 years in public service',
            'platform': 'Democratic reforms and economic development',
            'promises': 'Transparency in governance, foreign investment',
            'vision': 'A democratic and prosperous Myanmar',
            'is_candidate': True,
            'registration_date': '2024-01-22 16:45:00'
        },
        'candidate9': {
            'username': 'candidate9',
            'password': '1234',
            'full_name': 'Bounmy Thammavong',
            'date_of_birth': '1981-02-28',
            'gender': 'Male',
            'national_id': 'LA678901234',
            'phone': '+856 20 123 4567',
            'email': 'bounmy.thammavong@email.com',
            'address': {
                'street': '45 Setthathirath Road',
                'city': 'Vientiane',
                'state': 'Vientiane',
                'postal_code': '01000',
                'country': 'Laos'
            },
            'party': 'Independent',
            'current_position': 'District Chief',
            'desired_position': 'Governor',
            'term_length': '5 Years',
            'education': 'BA in Economics, National University of Laos',
            'experience': '10 years in district administration',
            'platform': 'Rural modernization and poverty reduction',
            'promises': 'Infrastructure development, tourism promotion',
            'vision': 'Balanced development between urban and rural Laos',
            'is_candidate': True,
            'registration_date': '2024-01-23 17:15:00'
        }
    }
    
    # Add candidates to the system
    for username, data in candidates_data.items():
        # Add to voters database
        app.voters[username] = data
        # Add to candidates list with 0 votes
        app.candidates[data['full_name']] = 0
    
    # Save the updated data
    app.save_voters()
    app.save_votes()
    
    root.mainloop()

# Delete admin.json if it exists
if os.path.exists("admin.json"):
    os.remove("admin.json")
    print("admin.json deleted successfully")
else:
    print("admin.json does not exist") 