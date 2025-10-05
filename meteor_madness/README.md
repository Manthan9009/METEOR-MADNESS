# Meteor Madness 🌠

A Django web application that fetches and displays Near-Earth Object (NEO) data from NASA's API.

## Features

- **Fetch Asteroids**: Retrieve real-time asteroid data from NASA's NeoWs API
- **View Asteroid List**: Browse all tracked asteroids with filtering options
- **Detailed View**: See comprehensive information about each asteroid
- **APOD**: View NASA's Astronomy Picture of the Day
- **Modern UI**: Beautiful, responsive design with Tailwind CSS

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

4. Run the development server:
```bash
python manage.py runserver
```

5. Visit `http://127.0.0.1:8000/` in your browser

## NASA API

The application uses your NASA API key: `vP8d4ncyijGNHGrddoIaX9MmdSx79VvkjZP5jg9u`

This is configured in `meteor_madness/settings.py`.

## Usage

1. Click "Fetch Data" to retrieve the latest asteroid data from NASA
2. Browse the asteroid list to see all tracked objects
3. Click on any asteroid for detailed information
4. Visit the APOD page to see NASA's daily astronomy picture

## Technologies

- Django 5.2.7
- Tailwind CSS
- Font Awesome
- NASA NeoWs API
- NASA APOD API
