# Fake Profile Identification Using ANN

A Django web application for fake profile identification with user registration, admin activation, dataset view, prediction form, and report pages.

## Live Demo

🔗 [View Live Website](https://karthikeyakatreddy-fake-profile.onrender.com)

## GitHub Repository

🔗 [View Source Code](https://github.com/Karthikeyakatreddy/Karthikeyakatreddy-fake-profile-detection-ml-django)

## Main Fixes Added

- Fixed Django startup crash caused by TensorFlow being imported at server startup.
- Added production-ready Django settings using environment variables.
- Added WhiteNoise static file support for deployment.
- Added `requirements.txt`, `Procfile`, `.gitignore`, and deployment guidance.
- Fixed dataset table rendering.
- Fixed prediction/report pages so missing log files do not crash the app.
- Removed generated cache files and private uploaded media from the GitHub-ready package.

## Features

- User registration and login
- Admin login and user activation
- Dataset view page
- Machine learning prediction form
- Fake profile classification result
- Prediction report pages
- Responsive professional UI
- Deployed live using Render

## Technologies Used

- Python
- Django
- Machine Learning
- ANN / ML Model
- Pandas
- NumPy
- Scikit-learn
- HTML
- CSS
- Bootstrap
- JavaScript
- Render
- GitHub

## Run Locally

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
