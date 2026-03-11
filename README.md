# Flask Web Application

A simple Flask web application project.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python app.py
```

The application will start on `http://0.0.0.0:5000`

## Configuration

Set environment variables to customize the application:

- `DEBUG` - Enable debug mode (default: False)
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 5000)
- `SECRET_KEY` - Secret key for sessions
- `DATABASE_URI` - Database connection URI

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check endpoint
