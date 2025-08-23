from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DateField, HiddenField
from wtforms.validators import DataRequired, Email, Optional, Length, Regexp
import requests
import os
from flask import url_for


class ContactForm(FlaskForm):
    name = StringField(
        'Full Name', 
        validators=[DataRequired(), Length(max=100)]
    )
    email = StringField(
        'Email', 
        validators=[DataRequired(), Email(), Length(max=120)]
    )
    phone = StringField(
        'Phone', 
        validators=[Optional(), Length(max=20)]
    )
    service_type = SelectField(
        'Service Type', 
        choices=[
            ('', 'Select an option…'),
            ('Panel / Service Upgrade', 'Panel / Service Upgrade'),
            ('Lighting & Fixtures', 'Lighting & Fixtures'),
            ('EV Charger Installation', 'EV Charger Installation'),
            ('Rewiring / Safety', 'Rewiring / Safety'),
            ('Troubleshooting / Repairs', 'Troubleshooting / Repairs'),
            ('Other', 'Other'),
        ],
        validators=[Optional()]
    )
    zip = StringField(
        'ZIP Code',
        validators=[
            Optional(),
            Regexp(r'^\d{5}$', message="ZIP code must be 5 digits.")
        ]
    )
    preferred_date = DateField(
        'Preferred Date',
        format='%Y-%m-%d',
        validators=[Optional()]
    )
    message = TextAreaField(
        'Message',
        validators=[DataRequired(), Length(max=1000)]
    )
    
    turnstile_token = HiddenField()

    SPAM_KEYWORDS = [
        "watch this", "unsubscribe", "goldsolutions.pro", "click here"
    ]

    def validate(self, extra_validators=None):
        if not super().validate():
            return False

        # Keyword spam
        msg = (self.message.data or "").lower()
        if any(word in msg for word in self.SPAM_KEYWORDS):
            self.message.errors.append("Message appears to be spam.")
            return False

        # Cloudflare Turnstile
        secret = os.getenv("TURNSTILE_SECRET_KEY")

        if secret:
            verify_resp = requests.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                data={"secret": secret, "response": self.turnstile_token.data}
            ).json()

            print(verify_resp)
            
            if not verify_resp.get("success"):
                self.turnstile_token.errors.append("Captcha validation failed.")
                return False

            # optional hostname check:
            expected = 'www.planelectricllc.com'
            print(f"Expected {expected}")
            if expected and verify_resp.get("hostname") not in (expected, "localhost", "127.0.0.1"):
                self.turnstile_token.errors.append("Invalid captcha hostname.")
                return False

            score = verify_resp.get("score")
            if score is not None and score < 0.2:
                self.turnstile_token.errors.append("Failed spam score.")
                return False

        return True
