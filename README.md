# Resumify

A full-stack Resume Generator platform with modern UI, backend APIs, and future AI features.

## Tech Stack

- **Frontend**: React 19 + Vite + TypeScript + Tailwind CSS v4
- **Backend**: Django REST Framework + PostgreSQL
- **Architecture**: Monorepo (frontend/ + backend/)
- **State Management**: Zustand
- **API Calls**: Axios

## Project Structure

```
resumify/
├── frontend/          # React + Vite + TypeScript + Tailwind v4
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── utils/        # Utility functions
│   │   ├── types/        # TypeScript type definitions
│   │   └── styles/       # Global styles
│   └── package.json
├── backend/           # Django REST Framework
│   ├── resumify_backend/  # Django project settings
│   ├── users/            # User management app
│   ├── resumes/          # Resume CRUD app
│   └── requirements.txt
└── README.md
```

## Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- PostgreSQL 12+ (optional, SQLite fallback available)

## Installation

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Set up PostgreSQL database:
   - Create a database named `resumify_db`
   - Update database credentials in `resumify_backend/settings.py` if needed
   - Or use SQLite by uncommenting the SQLite config in `settings.py`

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

## Running the Application

### Frontend

From the `frontend/` directory:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Backend

From the `backend/` directory (with virtual environment activated):
```bash
python manage.py runserver
```

The backend API will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/token/` - Obtain JWT token (login)
- `POST /api/token/refresh/` - Refresh JWT token

### Resumes
- `GET /api/resumes/` - List all resumes (authenticated)
- `POST /api/resumes/` - Create a new resume
- `GET /api/resumes/:id/` - Get a specific resume
- `PUT /api/resumes/:id/` - Update a resume
- `DELETE /api/resumes/:id/` - Delete a resume
- `GET /api/my-resumes/` - Get all resumes for current user

## Frontend Pages

- `/` - Home page
- `/login` - Login page
- `/register` - Registration page
- `/builder` - Resume builder page
- `/preview/:id` - Resume preview page

## Development Notes

- The frontend uses Tailwind CSS v4 with the Vite plugin (`@tailwindcss/vite`)
- The backend uses Django REST Framework with JWT authentication
- Resume data is stored as JSON in the database
- CORS is configured to allow requests from `localhost:3000`

## Next Steps

- Implement full resume form functionality
- Add PDF generation
- Implement user authentication on frontend
- Add AI features for resume enhancement
- Add resume templates

## License

MIT

