from flask import Flask, render_template, request, redirect, url_for, flash, Response
from forms import ContactForm
from dotenv import load_dotenv
from flask_mail import Mail, Message
import os
from config import Config
from datetime import datetime

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

@app.route("/sitemap.xml", methods=["GET"])
def sitemap():
    """
    Generates sitemap.xml for search engines.
    """

    # List of static routes: endpoint, changefreq, priority
    static_pages = [
        ("home",    "weekly",  "1.0"),
        ("about",   "yearly",  "0.8"),
        ("services","monthly", "0.9"),
        ("projects","monthly", "0.8"),
        ("contact", "yearly",  "0.7"),
    ]

    lastmod = datetime.utcnow().date().isoformat()
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 '
        'http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">',
    ]

    for endpoint, changefreq, priority in static_pages:
        loc = url_for(endpoint, _external=True)
        xml_parts.append("  <url>")
        xml_parts.append(f"    <loc>{loc}</loc>")
        xml_parts.append(f"    <lastmod>{lastmod}</lastmod>")
        xml_parts.append(f"    <changefreq>{changefreq}</changefreq>")
        xml_parts.append(f"    <priority>{priority}</priority>")
        xml_parts.append("  </url>")

    xml_parts.append("</urlset>")
    sitemap_xml = "\n".join(xml_parts)

    return Response(sitemap_xml, mimetype="application/xml")

@app.route("/robots.txt")
def robots():
    robots_txt = f"""User-agent: *
Disallow:

Sitemap: {url_for('sitemap', _external=True)}
"""
    return Response(robots_txt, mimetype="text/plain")

if __name__ == '__main__':
    app.run(debug=True)
