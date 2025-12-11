# PostgreSQL Setup Instructions

## Quick Setup

1. **Set your PostgreSQL password as an environment variable:**
   ```bash
   export DB_PASSWORD='your_actual_postgres_password'
   ```

2. **Create the database:**
   ```bash
   PGPASSWORD=$DB_PASSWORD psql -U postgres -h localhost -c "CREATE DATABASE resumify_db;"
   ```

3. **Run migrations:**
   ```bash
   source venv/bin/activate
   export DB_PASSWORD='your_actual_postgres_password'
   python manage.py migrate
   ```

## Alternative: Use SQLite (for quick testing)

If you want to use SQLite instead, edit `resumify_backend/settings.py` and uncomment the SQLite configuration.

## Or use the setup script:

```bash
./setup_db.sh
```

