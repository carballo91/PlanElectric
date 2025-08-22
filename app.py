from flask import Flask, render_template, request, redirect, url_for, flash
from forms import ContactForm
from dotenv import load_dotenv
from flask_mail import Mail, Message
import os
from config import Config

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config.from_object(Config)
mail = Mail(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    
    print(os.getenv("MAIL_USERNAME"))

    if form.validate_on_submit():

        # Pull data
        name = form.name.data
        email = form.email.data
        phone = form.phone.data
        service_type = form.service_type.data
        zipcode = form.zip.data
        preferred_date = form.preferred_date.data
        message = form.message.data
        token = form.turnstile_token.data

        # Build the message
        subject = "New Contact Request – Plan Electric"
        recipients = [os.getenv("MAIL_USERNAME")]  # your inbox
        print(f"Recipeints: {recipients}")
        msg = Message(subject=subject, recipients=recipients, reply_to=form.email.data)

        # Plain text (always include)
        msg.body = (
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Phone: {phone}\n"
            f"Service Type: {service_type}\n"
            f"ZIP: {zipcode}\n"
            f"Preferred Date: {preferred_date}\n\n"
            f"Message:\n{message}\n"
        )

        # Optional HTML version
        msg.html = render_template("emails/contact.html", form=form)

        try:
            mail.send(msg)
            print("It got to this pooint")
            flash(f"Thank you {form.name.data}, we’ll be in touch shortly.", "success")
            return redirect(url_for('contact'))
        except Exception as e:
            # Log e in production
            flash(f"Sorry, we couldn’t send your message right now. Please try again. {e}", "error")


    return render_template("contact.html", form=form)

if __name__ == '__main__':
    app.run(debug=True)
