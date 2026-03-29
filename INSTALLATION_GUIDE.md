# ALVO Platform - Installation Guide

## Prerequisites

- Python 3.9+
- Node.js 16+
- npm or yarn
- PostgreSQL (optional, SQLite for development)

## Backend Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd alvo-platform
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
cd dashboard_project
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the `dashboard_project` directory:
```env
DATABASE_URL=sqlite:///./app.db  # For development
# DATABASE_URL=postgresql://user:password@localhost/alvo  # For production

OPENROUTER_API_KEY=your_openrouter_api_key
SECRET_KEY=your_secret_key_for_jwt
```

### 5. Database Setup
```bash
# The application will automatically create tables on first run
# For PostgreSQL, create the database first:
createdb alvo
```

### 6. Run Backend Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000

## Frontend Installation

### 1. Navigate to Frontend Directory
```bash
cd dashboard_project/frontend
```

### 2. Install Dependencies
```bash
npm install
# or
yarn install
```

### 3. Environment Configuration
Create a `.env` file in the `frontend` directory:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws
```

### 4. Run Development Server
```bash
npm start
# or
yarn start
```

The frontend will be available at: http://localhost:3000

## Docker Installation (Optional)

### 1. Build and Run with Docker Compose
```bash
docker-compose up -d
```

### 2. Docker Compose Configuration
Create a `docker-compose.yml` file:
```yaml
version: '3.8'

services:
  backend:
    build: ./dashboard_project
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/alvo
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    depends_on:
      - db

  frontend:
    build: ./dashboard_project/frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=alvo
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Production Deployment

### Backend Production Setup

1. **Install Production Dependencies**
```bash
pip install gunicorn uvicorn[standard]
```

2. **Run with Gunicorn**
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

3. **Nginx Configuration**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### Frontend Production Build

1. **Build for Production**
```bash
cd dashboard_project/frontend
npm run build
```

2. **Serve Static Files**
```bash
npm install -g serve
serve -s build -l 3000
```

## Database Migration

### SQLite to PostgreSQL Migration

1. **Export SQLite Data**
```bash
sqlite3 app.db .dump > backup.sql
```

2. **Create PostgreSQL Database**
```bash
createdb alvo
psql -d alvo -f backup.sql
```

3. **Update Environment Variables**
```env
DATABASE_URL=postgresql://user:password@localhost/alvo
```

## Testing

### Backend Tests
```bash
cd dashboard_project
pytest tests/
```

### Frontend Tests
```bash
cd dashboard_project/frontend
npm test
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
```

2. **Database Connection Error**
- Check DATABASE_URL in .env file
- Ensure database server is running
- Verify credentials

3. **Missing Dependencies**
```bash
pip install -r requirements.txt --force-reinstall
npm install --legacy-peer-deps
```

4. **WebSocket Connection Issues**
- Check firewall settings
- Verify proxy configuration
- Ensure CORS is properly configured

### Logs

Backend logs are available in:
- Console output (development)
- `/var/log/alvo/` (production)

Frontend logs are available in:
- Browser console
- Build output

## Security Considerations

1. **Environment Variables**
   - Never commit .env files to version control
   - Use strong SECRET_KEY values
   - Rotate API keys regularly

2. **Database Security**
   - Use strong passwords
   - Enable SSL for PostgreSQL connections
   - Restrict database access by IP

3. **API Security**
   - Implement rate limiting
   - Use HTTPS in production
   - Validate all input data

## Performance Optimization

1. **Backend**
   - Use connection pooling for database
   - Implement caching (Redis)
   - Use background tasks for heavy operations

2. **Frontend**
   - Enable gzip compression
   - Use CDN for static assets
   - Implement code splitting

## Support

For issues and questions:
- Create an issue in the repository
- Check existing documentation
- Contact the development team

## License

[License information]