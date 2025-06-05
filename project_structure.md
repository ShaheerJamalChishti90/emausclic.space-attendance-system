/attendance_app
│
├── /static
│   └── Logo.png               # Static assets like images, CSS, JS
│
├── /templates
│   ├── admin_logs.html        # Admin logs page template
│   ├── admin_settings.html    # Admin settings page template
│   ├── already_logged_in.html # Already logged-in user page
│   ├── form.html              # Main form page template
│   └── success.html           # Success submission page template
│
├── /logs
│   ├── attendance_2025-06-04.xlsx  # Attendance log file
│   └── TestingFile_attendance.xls  # Test attendance file
│
├── .htaccess                  # Apache config (optional)
├── app.py                     # Main Flask application
├── wsgi.py                    # WSGI entry point for deployment
├── settings.json              # Configuration settings
├── requirements.txt           # Python dependencies
└── Procfile                   # Deployment configuration  