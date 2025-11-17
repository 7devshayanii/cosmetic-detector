# 🧴 Cosmetic Ingredient Detector

A modern web application that uses OCR technology to scan cosmetic product ingredient labels and detect harmful substances. Built with Django backend and a beautiful glassmorphic frontend.

## ✨ Features

- **📸 Image Upload & Camera Capture**: Upload images or use your device camera to scan product labels
- **🔬 OCR Text Extraction**: Advanced text recognition using Tesseract OCR
- **⚠️ Harmful Ingredient Detection**: Identifies dangerous cosmetic ingredients with detailed explanations
- **🌱 Veg/Non-Veg Classification**: Detects animal-derived ingredients
- **🎨 Beautiful Glassmorphic UI**: Modern, aesthetic design with smooth animations and gradients
- **📊 Safety Rating System**: Products rated as SAFE, CAUTION, or HARMFUL
- **💾 Admin Panel**: View scan history through Django admin

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Tesseract OCR engine
- Django 5.2+

### Installation

All dependencies are already installed in this Replit environment:

- Django
- Pillow (Image processing)
- pytesseract (OCR wrapper)
- Tesseract OCR engine

### Running the Application

The application is configured to run automatically. Just click the "Run" button or use:

```bash
python manage.py runserver 0.0.0.0:5000
```

### Creating Admin Account

To access the Django admin panel at `/admin/`:

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin credentials.

## 📁 Project Structure

```
.
├── cosmetic_detector/          # Django project settings
│   ├── scanner/                # Main application
│   │   ├── models.py          # Database models
│   │   ├── views.py           # API endpoints
│   │   ├── admin.py           # Admin configuration
│   │   └── ingredient_analyzer.py  # Detection logic
│   ├── settings.py            # Project settings
│   └── urls.py                # URL routing
├── templates/                  # HTML templates
│   ├── index.html             # Home page
│   └── results.html           # Results page
├── static/                     # Static files
│   ├── styles/
│   │   └── main.css          # Glassmorphic styling
│   └── scripts/
│       └── app.js            # Frontend logic
├── uploads/                    # Uploaded images
└── manage.py                  # Django management
```

## 🎯 How It Works

1. **Upload**: User uploads an image or captures one using their camera
2. **OCR**: Tesseract extracts text from the product label
3. **Analysis**: The system checks for:
   - Harmful ingredients (parabens, sulfates, phthalates, etc.)
   - Animal-derived ingredients
   - Safety rating based on harmful ingredient count
4. **Results**: Displays:
   - Extracted ingredient list
   - Harmful ingredients with explanations
   - Safety rating (SAFE/CAUTION/HARMFUL)
   - Veg/Non-veg status

## 🧪 Harmful Ingredients Database

The app detects common harmful cosmetic ingredients including:

- **Parabens**: Hormone disruptors
- **Sulfates (SLS/SLES)**: Skin irritants
- **Phthalates**: Endocrine disruptors
- **Formaldehyde**: Known carcinogen
- **Triclosan**: Thyroid disruptor
- **Mineral Oil**: Pore-clogging
- **Oxybenzone**: Hormone disruptor
- **Hydroquinone**: Linked to cancer
- **Coal Tar**: Carcinogen
- **Aluminum**: Potential neurotoxin

## 🌱 Veg/Non-Veg Detection

Identifies animal-derived ingredients such as:
- Lanolin, Beeswax, Honey
- Carmine, Collagen, Keratin
- Gelatin, Squalene
- Milk derivatives (Lactose, Whey, Casein)
- And many more...

## 🎨 Design Features

- **Glassmorphism**: Frosted glass effect with backdrop blur
- **Gradient Animations**: Smooth, shifting color gradients
- **Responsive Design**: Works on mobile and desktop
- **Smooth Transitions**: Fade and slide animations
- **Modern Color Palette**: Purple, pink, and blue tones

## 📝 API Endpoints

- `GET /` - Home page
- `GET /results/` - Results page
- `POST /api/scan/` - Scan image endpoint
  - Accepts: multipart/form-data with 'image' field
  - Returns: JSON with analysis results
- `GET /admin/` - Admin panel

## 🔧 Admin Panel

Access the admin panel to:
- View all scans
- Filter by safety rating and veg status
- Search extracted text
- See detailed analysis results

## 📱 Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers with camera support

## 🔒 Security

- CSRF protection enabled
- Image upload validation
- Secure file storage
- Admin authentication required

## 📄 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Feel free to fork this project and add more features such as:
- Additional harmful ingredients
- More detailed explanations
- User accounts and scan history
- Ingredient search functionality
- Product comparisons

---

Built with ❤️ using Django and modern web technologies
