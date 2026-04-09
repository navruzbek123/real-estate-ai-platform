# 🏠 Real Estate AI Platform with Django

[![Django](https://img.shields.io/badge/Django-4.2-green)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![ML](https://img.shields.io/badge/ML-RandomForest-orange)](https://scikit-learn.org/)
[![Maps](https://img.shields.io/badge/Maps-Yandex-red)](https://yandex.com/maps/)

## ✨ Features

- 🤖 **AI Price Prediction** - Machine Learning model for real estate valuation
- 🗺️ **Interactive Maps** - Yandex Maps integration with property markers
- 🏷️ **Property Management** - Sale & rental listings with premium options
- 👥 **User System** - Multi-role authentication (Free/Premium/Agent/Admin)
- 💳 **Payment Integration** - Sberbank API ready
- 📱 **Responsive Design** - Bootstrap 5 with dark mode

## 🛠️ Tech Stack

- Backend: Django 4.2, DRF
- ML: scikit-learn, RandomForest, Pandas
- Maps: Yandex Maps API
- Frontend: Bootstrap 5, HTMX, Chart.js
- Database: SQLite/PostgreSQL

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/real-estate-ai-platform.git
cd real-estate-ai-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your YANDEX_MAPS_API_KEY

# Run migrations
python manage.py migrate

# Train ML model
python ml_model/train_model.py

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver