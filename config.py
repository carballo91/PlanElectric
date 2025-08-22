import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    TURNSTILE_SITE_KEY = os.getenv("TURNSTILE_SITE_KEY")
    TURNSTILE_SECRET_KEY = os.getenv("TURNSTILE_SECRET_KEY")
    
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = os.getenv("EMAIL_PORT")
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", os.getenv("MAIL_USERNAME"))