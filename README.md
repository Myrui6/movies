
# Cinema Management System

## Overview
A comprehensive cinema management system built with Flask backend and Vue.js frontend, providing movie scheduling, hall management, order processing, and user ticket purchasing functionality.

## Tech Stack
- **Backend**: Flask 2.3.3
- **Frontend**: Vue.js 3, HTML5, CSS3
- **Database**: MySQL
- **Dependencies**: See `requirements.txt`

## Quick Start

### 1. Prerequisites
- Python 3.8+
- MySQL 5.7+
- Git

### 2. Setup Database
```sql
CREATE DATABASE movies;
```
Create your database schema with `schema.sql` .

### 3. Configure Environment
Edit `config.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'movies'
}
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run Application
```bash
python app.py
```
Access at `http://localhost:5000`

## Project Structure
The project follows a clean separation between backend and frontend components. The backend is built with Flask using blueprint modules for different functional areas, while the frontend uses Vue.js components with separate HTML, CSS, and JavaScript files. File uploads are managed in a dedicated directory.

## Core Features
- **Movie Management**: Add, modify, delete movies
- **Schedule Management**: Create and manage screening schedules
- **Hall Management**: Configure screening hall layouts
- **Order System**: Ticket purchase and refund processing
- **User System**: Registration, login, and role-based access

## User Roles
- **Admin/Manager**: Full access to all management functions
- **User**: Browse movies, purchase tickets, view orders

## API Overview
- `/api/movies` - Movie CRUD operations
- `/api/schedules` - Schedule management
- `/api/halls` - Hall configuration
- `/api/orders` - Order processing
- `/api/auth` - User authentication

## Default Port
- Application runs on port 5000
- Access at `http://localhost:5000`
```
