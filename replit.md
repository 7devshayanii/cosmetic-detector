# Cosmetic Ingredient Detector - Project Documentation

## Overview
A modern web application that uses OCR technology to scan cosmetic product ingredient labels and detect harmful substances. The app features a beautiful glassmorphic UI design and provides detailed analysis of cosmetic ingredients.

## Purpose
- Scan cosmetic product labels using image upload or camera
- Extract ingredient text using OCR (Tesseract)
- Detect harmful cosmetic ingredients
- Classify products as vegetarian or non-vegetarian
- Provide safety ratings (SAFE, CAUTION, HARMFUL)

## Tech Stack
- **Backend**: Django 5.2.8
- **Frontend**: HTML, CSS (Glassmorphism), Vanilla JavaScript
- **OCR**: Tesseract + pytesseract
- **Image Processing**: Pillow
- **Database**: SQLite

## Recent Changes (Nov 17, 2025)
- Initial project setup with Django
- Created scanner app with Scan model
- Built ingredient analyzer with harmful ingredients database
- Implemented veg/non-veg classification
- Created glassmorphic frontend with animations
- Added image upload and camera capture functionality
- Built results page with detailed analysis display
- Configured Django admin panel for scan history
- Set up workflow to run on port 5000

## Project Architecture

### Backend Structure
- `cosmetic_detector/scanner/` - Main application
  - `models.py` - Scan model for storing analysis history
  - `views.py` - API endpoints for scanning and serving pages
  - `ingredient_analyzer.py` - Core logic for detecting harmful ingredients
  - `admin.py` - Admin panel configuration

### Frontend Structure
- `templates/` - HTML templates
  - `index.html` - Home page with upload interface
  - `results.html` - Analysis results display
- `static/` - Static assets
  - `styles/main.css` - Glassmorphic design with animations
  - `scripts/app.js` - Frontend logic for uploads and API calls

### Key Features
1. **Image Upload**: Drag-and-drop or click to upload
2. **Camera Capture**: Use device camera for instant scanning
3. **OCR Processing**: Tesseract extracts text from images
4. **Ingredient Analysis**: Checks against database of 10+ harmful ingredient categories
5. **Veg/Non-Veg Detection**: Identifies 30+ animal-derived ingredients
6. **Safety Rating**: Automatic rating based on harmful ingredient count
7. **Beautiful UI**: Gradient animations, glassmorphism, responsive design

## Harmful Ingredients Database
- Parabens (hormone disruptors)
- Sulfates (skin irritants)
- Phthalates (endocrine disruptors)
- Formaldehyde (carcinogen)
- Triclosan (thyroid disruptor)
- Mineral Oil (pore-clogging)
- Oxybenzone (hormone disruptor)
- Hydroquinone (cancer risk)
- Coal Tar (carcinogen)
- Aluminum (neurotoxin risk)

## Animal-Derived Ingredients
Detects 30+ ingredients including lanolin, beeswax, honey, carmine, collagen, keratin, gelatin, milk derivatives, and more.

## API Endpoints
- `GET /` - Home page
- `GET /results/` - Results page
- `POST /api/scan/` - Image analysis endpoint
- `GET /admin/` - Admin panel

## Running the Application
The app runs automatically on port 5000. Access via the webview.

## Admin Access
Create superuser: `python manage.py createsuperuser`
Access admin at `/admin/`

## User Preferences
None specified yet.

## Next Steps / Future Enhancements
- Add user authentication
- Expand harmful ingredients database
- Create ingredient encyclopedia
- Add product comparison feature
- Implement user scan history
- Add allergen detection
- Multi-language support
