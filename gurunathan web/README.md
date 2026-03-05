# Gurunathan Traders - Full Stack Retail Hardware Website

A complete Flask + SQLite website for **Gurunathan Traders** (near Hosur, Tamil Nadu) with:

- Public business website
- Product catalog with search and category filter
- Contact form (saved to database)
- Admin login panel
- Product CRUD (add/edit/delete)
- Product image upload
- Customer inquiry viewer

## 1. Project Folder Structure

```text
Gurunathan Traders/
|-- app.py
|-- requirements.txt
|-- README.md
|-- shop.db                  (auto-created on first run)
|-- static/
|   |-- css/
|   |   |-- style.css
|   |-- js/
|   |   |-- main.js
|   |-- images/
|       |-- products/        (uploaded product images)
|       |-- site/            (category/sample placeholder images)
|-- templates/
|   |-- base.html
|   |-- home.html
|   |-- products.html
|   |-- services.html
|   |-- about.html
|   |-- contact.html
|   |-- admin/
|       |-- base.html
|       |-- login.html
|       |-- dashboard.html
|       |-- product_form.html
|       |-- messages.html
```

## 2. Features Implemented

### Public Website
- Home page with hero section, category highlights, CTA buttons
- Products page with search and category filter
- Services page
- About page
- Contact page with map + form
- Floating WhatsApp button on all pages

### Admin Panel
- Secure login (password hash stored in DB)
- Add product
- Edit product
- Delete product
- Upload product image
- View contact inquiries

### Database Tables
- `categories`
- `products`
- `admin_users`
- `contact_messages`

## 3. Beginner Setup (Windows)

### Step A: Install Python
1. Download Python 3.11+ from [python.org](https://www.python.org/downloads/).
2. During install, tick **Add Python to PATH**.

### Step B: Open this project folder in terminal

```powershell
cd "C:\Users\Sathasivam Stalin\Downloads\gurunathan web"
```

### Step C: Create virtual environment

```powershell
python -m venv venv
```

### Step D: Activate virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

### Step E: Install dependencies

```powershell
pip install -r requirements.txt
```

### Step F: Run website

```powershell
python app.py
```

### Step G: Open in browser

- Main site: [http://127.0.0.1:5000](http://127.0.0.1:5000)
- Admin login: [http://127.0.0.1:5000/admin/login](http://127.0.0.1:5000/admin/login)

## 4. Default Admin Login

- Username: `admin`
- Password: `Admin@123`

Important: change this after first deployment by updating the DB value or building a password-change route.

## 5. How Product Images Work

- Admin uploads image while adding/editing product.
- Images are saved in: `static/images/products/`
- Image path is saved in SQLite `products.image_url`.
- Allowed formats: `png, jpg, jpeg, webp, gif`.

## 6. Google Maps + WhatsApp Configuration

Open `app.py` and update `SHOP_INFO`:

- `phone`
- `whatsapp` (country code + number, no `+`)
- `email`
- `address`

For map location, update the iframe URL in:
- `templates/contact.html`

## 7. SEO Basics Included

- Meta description + keywords in base template
- Semantic headings and clean route URLs
- Fast-loading local assets
- Mobile-friendly responsive layout

## 8. Deployment Guide (Free/Low Cost)

## Option 1: Render (Recommended for Flask)
1. Push this project to GitHub.
2. Create account on [Render](https://render.com/).
3. New Web Service -> connect GitHub repo.
4. Build command:

```bash
pip install -r requirements.txt
```

5. Start command:

```bash
python app.py
```

6. Add environment variable in Render:
- `SECRET_KEY` = strong random value

Note: For production, use Gunicorn + persistent disk for uploaded images and SQLite file.

## Option 2: PythonAnywhere
1. Upload project or clone from GitHub.
2. Create virtualenv and install requirements.
3. Configure WSGI file to point to Flask app.
4. Ensure static folder mapping is configured.
5. Reload app.

## Option 3: Railway
1. Push code to GitHub.
2. Deploy project in Railway.
3. Set start command and env vars.
4. Attach persistent storage for uploads/database.

GitHub Pages cannot host Flask backend apps (only static frontend), so use Render/PythonAnywhere/Railway for full-stack hosting.

## 9. Production Notes

- Set `debug=False` in production.
- Use strong `SECRET_KEY`.
- Use HTTPS hosting.
- Back up `shop.db` regularly.
- Add CSRF protection and rate limit for hardened production.

## 10. Quick Business Customization Checklist

- Replace sample product names/prices in admin panel
- Upload real product photos
- Update contact number and WhatsApp number
- Set exact Google Map pin location
- Add local-language content (Tamil + English) if needed

---

If you want, the next step can be Tamil bilingual support and invoice-style PDF quotation download from the admin panel.
