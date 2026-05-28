# Fake Profile Identification Using ANN

A Django web application for fake profile identification with user registration, admin activation, dataset view, prediction form, and report pages.

## Main fixes added

- Fixed Django startup crash caused by TensorFlow being imported at server startup.
- Added production-ready Django settings using environment variables.
- Added WhiteNoise static file support for deployment.
- Added `requirements.txt`, `Procfile`, `.gitignore`, and deployment guidance.
- Fixed dataset table rendering.
- Fixed prediction/report pages so missing log files do not crash the app.
- Removed generated cache files and private uploaded media from the GitHub-ready package.

## Run locally

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

Admin demo login inside the project:

```text
Username: admin
Password: admin
```

## Deploy with GitHub + Render

1. Create a GitHub repository.
2. Push this project folder to GitHub.
3. On Render, create a new Web Service from the GitHub repository.
4. Use these settings:
   - Build command: `./build.sh`
   - Start command: `gunicorn Fake_Profile_Identification_using_ANN.wsgi:application`
5. Add environment variables:
   - `DEBUG=False`
   - `DJANGO_SECRET_KEY=<your-long-random-secret>`
   - `ALLOWED_HOSTS=<your-render-service>.onrender.com,localhost,127.0.0.1`
   - `CSRF_TRUSTED_ORIGINS=https://<your-render-service>.onrender.com`

## Note about GitHub Pages

GitHub Pages cannot run this project because it is a Django backend application. Use GitHub for the source code and a Python hosting service such as Render, Railway, or PythonAnywhere for the live website.
