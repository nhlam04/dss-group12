# Full-Stack Charity Fund Decision Support System

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Web Application
```bash
python app.py
```

### 3. Access the Application
Open your web browser and navigate to:
```
http://localhost:5000
```

## System Overview

This is a complete full-stack web application for charity fund allocation with:
- **SQLite Database** - Stores agents, requests, allocations, and configuration
- **Flask Backend** - RESTful API server
- **Web Frontend** - Bootstrap-based responsive interface

## Features

### Dashboard (/)
- View fund statistics and budget overview
- Configure total budget and allocation settings
- Quick access to all functions

### Charity Agents (/agents)
- Add new charity organizations
- View agent details (success rate, transparency, track record)
- Manage agent database

### Grant Requests (/requests)
- Add new funding requests
- View all requests with filtering (pending/funded/rejected)
- Track request details and efficiency metrics

### Allocate Funds (/allocate)
- Preview allocation with different strategies:
  - Greedy (Full Funding Only)
  - Greedy (Allow Partial Funding)
  - Proportional Allocation
  - Knapsack Optimization
- Run allocation and update database
- View detailed results with rankings

### History (/history)
- View past allocation decisions
- Track budget utilization over time

### Settings (/settings)
- Customize TOPSIS criteria weights
- Adjust importance of each evaluation factor

## Database Schema

### Tables
- `charity_agents` - Organizations requesting funds
- `grant_requests` - Program funding requests
- `fund_config` - Budget and allocation settings
- `allocation_history` - Past allocation runs
- `allocation_decisions` - Individual funding decisions
- `criteria_weights` - TOPSIS weight configuration

## API Endpoints

### Statistics
- `GET /api/stats` - Dashboard statistics

### Agents
- `GET /api/agents` - List all agents
- `POST /api/agents` - Create new agent
- `GET /api/agents/<id>` - Get agent details
- `PUT /api/agents/<id>` - Update agent
- `DELETE /api/agents/<id>` - Delete agent

### Requests
- `GET /api/requests` - List all requests
- `POST /api/requests` - Create new request
- `DELETE /api/requests/<id>` - Delete request

### Fund Configuration
- `GET /api/fund-config` - Get configuration
- `PUT /api/fund-config` - Update configuration

### Allocation
- `POST /api/allocate/preview` - Preview allocation results
- `POST /api/allocate` - Run and save allocation

### History
- `GET /api/history` - Get allocation history

### Criteria Weights
- `GET /api/criteria-weights` - Get weights
- `PUT /api/criteria-weights` - Update weights

## Workflow

1. **Setup Fund**
   - Go to Dashboard
   - Set total budget (e.g., $500,000)
   - Set minimum allocation percentage (e.g., 0.5 for 50%)

2. **Add Charity Agents**
   - Go to Charity Agents page
   - Click "Add New Agent"
   - Enter organization details

3. **Add Grant Requests**
   - Go to Grant Requests page
   - Click "Add New Request"
   - Fill in program details
   - Select charity agent from dropdown

4. **Run Allocation**
   - Go to Allocate Funds page
   - Select allocation strategy
   - Click "Preview Results" to see outcome without saving
   - Click "Run Allocation" to execute and save

5. **Review Results**
   - View allocation summary
   - See which programs are funded/rejected
   - Check budget utilization
   - Go to History to see past allocations

## Technology Stack

**Backend:**
- Python 3.7+
- Flask (Web framework)
- SQLite (Database)
- NumPy (Numerical computations)
- Pandas (Data manipulation)

**Frontend:**
- HTML5
- CSS3 + Bootstrap 5
- JavaScript (Vanilla JS, no framework required)
- Bootstrap Icons

## File Structure

```
charity_fund_system/
├── app.py                      # Flask application
├── database.py                 # Database models and operations
├── charity_decision_system.py  # Core data models
├── topsis_analyzer.py          # TOPSIS algorithm
├── fund_allocator.py           # Allocation strategies
├── templates/                  # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── agents.html
│   ├── requests.html
│   ├── allocate.html
│   ├── history.html
│   └── settings.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── app.js
│       ├── agents.js
│       ├── requests.js
│       ├── allocate.js
│       ├── history.js
│       └── settings.js
├── charity_fund.db             # SQLite database (created on first run)
└── requirements.txt
```

## Security Notes

**For Production Use:**
- Add authentication/authorization
- Use environment variables for configuration
- Enable HTTPS
- Add input validation and sanitization
- Use PostgreSQL or MySQL instead of SQLite
- Add rate limiting
- Enable CSRF protection
- Add logging and monitoring

## Advantages

✅ **No External Dependencies** - Runs entirely on your local machine
✅ **Easy Setup** - Just install requirements and run
✅ **Persistent Data** - All data saved in SQLite database
✅ **User-Friendly** - Intuitive web interface
✅ **Flexible** - Easy to customize and extend
✅ **Complete** - Full CRUD operations for all entities

## Troubleshooting

**Port 5000 already in use:**
```python
# In app.py, change the port:
app.run(debug=True, host='0.0.0.0', port=8080)
```

**Database errors:**
```bash
# Delete the database to reset:
rm charity_fund.db
# Restart the application to create fresh database
```

**Module not found errors:**
```bash
# Reinstall dependencies:
pip install -r requirements.txt
```

## Extending the System

### Add New Criteria
1. Update `criteria_weights` table in `database.py`
2. Modify TOPSIS algorithm in `topsis_analyzer.py`
3. Update Settings page UI

### Add Authentication
```bash
# Install flask-login
pip install flask-login

# Add user model and login views
```

### Deploy to Production
```bash
# Use gunicorn for production
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Support

For issues or questions about this system, refer to:
- `USER_GUIDE.md` - Detailed user guide
- `ARCHITECTURE.md` - System architecture diagrams
- `PROJECT_SUMMARY.md` - Technical overview
