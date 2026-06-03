# 🔌 API Documentation & Backend Guide

## API Endpoints Complete

### 🔐 Authentication

```
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
POST /api/auth/refresh-token
```

**Login Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Login Response:**
```json
{
  "token": "eyJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

---

### 💼 Jobs Endpoints

#### Get All Jobs (with filters)
```
GET /api/jobs?category=IT&location=București&limit=20&offset=0
```

**Query Parameters:**
- `category`: IT, Management, Vânzări, Design, HR, Contabilitate
- `location`: București, Cluj, Timișoara, Brașov, Iași, Remote
- `jobType`: Full-time, Part-time, Contract, Remote
- `experienceLevel`: Entry, Junior, Mid, Senior
- `minSalary`: number
- `maxSalary`: number
- `technologies`: React,Node.js (comma-separated)
- `search`: search term
- `limit`: number (default 20)
- `offset`: number (default 0)

**Response:**
```json
{
  "jobs": [
    {
      "id": 1,
      "title": "Senior React Developer",
      "company": "TechCorp",
      "location": "București",
      "salary": 7500,
      "jobType": "Full-time",
      "experienceLevel": "Senior",
      "postedDate": "2024-01-15T10:30:00Z",
      "description": "...",
      "requirements": ["3+ ani React", "TypeScript"],
      "benefits": ["WFH", "Bonus"],
      "technologies": ["React", "Node.js"],
      "category": "IT",
      "applyUrl": "https://techcorp.ro/apply/1",
      "recruiterEmail": "careers@techcorp.ro",
      "companyDescription": "...",
      "applicants": 45
    }
  ],
  "total": 150,
  "limit": 20,
  "offset": 0
}
```

---

#### Get Similar Jobs
```
GET /api/jobs/:jobId/similar?limit=3
```

**Response:**
```json
{
  "jobs": [
    { ...job object... }
  ]
}
```

---

#### Get Job Details
```
GET /api/jobs/:jobId
```

---

### ❤️ Saved Jobs Endpoints

#### Save Job
```
POST /api/user/saved-jobs
Content-Type: application/json
Authorization: Bearer {token}

{
  "jobId": 1
}
```

**Response:**
```json
{
  "success": true,
  "message": "Job saved successfully"
}
```

---

#### Get Saved Jobs
```
GET /api/user/saved-jobs
Authorization: Bearer {token}
```

**Response:**
```json
{
  "jobs": [
    { ...job object with savedDate... }
  ],
  "count": 5
}
```

---

#### Get Saved Jobs Count
```
GET /api/user/saved-jobs/count
Authorization: Bearer {token}
```

**Response:**
```json
{
  "count": 5
}
```

---

#### Unsave Job
```
DELETE /api/user/saved-jobs/:jobId
Authorization: Bearer {token}
```

---

### 📲 Applications Endpoints

#### Track Application
```
POST /api/user/applications
Authorization: Bearer {token}

{
  "jobId": 1
}
```

**Response:**
```json
{
  "success": true,
  "applicationId": 123,
  "appliedAt": "2024-01-20T15:30:00Z"
}
```

---

#### Get Applications History
```
GET /api/user/applications?limit=20&offset=0
Authorization: Bearer {token}
```

**Response:**
```json
{
  "applications": [
    {
      "id": 123,
      "jobId": 1,
      "jobTitle": "Senior React Developer",
      "company": "TechCorp",
      "appliedAt": "2024-01-20T15:30:00Z",
      "status": "pending" // pending, viewed, rejected, accepted
    }
  ],
  "total": 5
}
```

---

### 🔔 Notifications Endpoints

#### Get Notifications
```
GET /api/user/notifications?limit=20
Authorization: Bearer {token}
```

**Response:**
```json
{
  "notifications": [
    {
      "id": 1,
      "title": "New Job Posted",
      "message": "Senior React Developer at TechCorp",
      "type": "job_match", // job_match, application_update, profile_view
      "read": false,
      "timestamp": "2024-01-20T15:30:00Z",
      "jobId": 1
    }
  ]
}
```

---

#### Mark as Read
```
PATCH /api/user/notifications/:notificationId
Authorization: Bearer {token}

{
  "read": true
}
```

---

#### Delete Notification
```
DELETE /api/user/notifications/:notificationId
Authorization: Bearer {token}
```

---

### 👤 User Profile Endpoints

#### Get Profile
```
GET /api/user/profile
Authorization: Bearer {token}
```

**Response:**
```json
{
  "profile": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+40701234567",
    "appliedCount": 5,
    "savedCount": 12,
    "viewCount": 0,
    "createdAt": "2023-12-01T10:00:00Z"
  }
}
```

---

#### Update Profile
```
PUT /api/user/profile
Authorization: Bearer {token}

{
  "name": "John Doe",
  "phone": "+40701234567",
  "location": "București"
}
```

---

### 🏢 Company Endpoints

#### Get Company Info
```
GET /api/companies/:companyId
```

**Response:**
```json
{
  "company": {
    "id": 1,
    "name": "TechCorp Romania",
    "industry": "Software Development",
    "description": "...",
    "employees": "200+",
    "website": "https://techcorp.ro",
    "phone": "+40212345678",
    "email": "info@techcorp.ro",
    "rating": 4.5,
    "jobsOpen": 5,
    "address": "Bucharest, Romania",
    "foundedYear": 2010
  }
}
```

---

#### Get Company Reviews
```
GET /api/companies/:companyId/reviews?limit=10
```

---

### 🔔 Job Alerts Endpoints

#### Create Job Alert
```
POST /api/user/job-alerts
Authorization: Bearer {token}

{
  "keyword": "React Developer",
  "location": "București",
  "minSalary": 5000
}
```

---

#### Get Job Alerts
```
GET /api/user/job-alerts
Authorization: Bearer {token}
```

---

#### Delete Job Alert
```
DELETE /api/user/job-alerts/:alertId
Authorization: Bearer {token}
```

---

## 🚀 Backend Implementation Examples

### Node.js + Express + MongoDB

```javascript
const express = require('express');
const mongoose = require('mongoose');
const jwt = require('jsonwebtoken');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// Database models
const jobSchema = new mongoose.Schema({
  title: String,
  company: String,
  location: String,
  salary: Number,
  jobType: String,
  experienceLevel: String,
  description: String,
  requirements: [String],
  benefits: [String],
  technologies: [String],
  applyUrl: String,
  recruiterEmail: String,
  postedDate: { type: Date, default: Date.now },
  applicants: { type: Number, default: 0 }
});

const Job = mongoose.model('Job', jobSchema);

// Middleware
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  
  if (!token) return res.sendStatus(401);
  
  jwt.verify(token, process.env.ACCESS_TOKEN_SECRET, (err, user) => {
    if (err) return res.sendStatus(403);
    req.user = user;
    next();
  });
};

// Routes
app.get('/api/jobs', async (req, res) => {
  try {
    const { category, location, search, limit = 20, offset = 0 } = req.query;
    
    let query = {};
    if (category) query.category = category;
    if (location) query.location = location;
    if (search) {
      query.$or = [
        { title: { $regex: search, $options: 'i' } },
        { company: { $regex: search, $options: 'i' } },
        { description: { $regex: search, $options: 'i' } }
      ];
    }
    
    const jobs = await Job.find(query)
      .limit(parseInt(limit))
      .skip(parseInt(offset))
      .sort({ postedDate: -1 });
    
    const total = await Job.countDocuments(query);
    
    res.json({
      jobs,
      total,
      limit: parseInt(limit),
      offset: parseInt(offset)
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/user/saved-jobs', authenticateToken, async (req, res) => {
  try {
    const { jobId } = req.body;
    
    // Save to database (user_id, job_id)
    // Implementation depends on your schema
    
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

### Python + Flask + PostgreSQL

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import jwt

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://...'
db = SQLAlchemy(app)

# Models
class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), required=True)
    company = db.Column(db.String(255), required=True)
    location = db.Column(db.String(100))
    salary = db.Column(db.Integer)
    job_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    query = Job.query
    
    if 'location' in request.args:
        query = query.filter_by(location=request.args['location'])
    
    if 'search' in request.args:
        search = f"%{request.args['search']}%"
        query = query.filter(
            (Job.title.ilike(search)) | 
            (Job.company.ilike(search))
        )
    
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    jobs = query.limit(limit).offset(offset).all()
    total = query.count()
    
    return jsonify({
        'jobs': [job.to_dict() for job in jobs],
        'total': total,
        'limit': limit,
        'offset': offset
    })

@app.route('/api/user/saved-jobs', methods=['POST'])
def save_job():
    token = request.headers.get('Authorization')
    user_id = decode_token(token)
    
    data = request.get_json()
    job_id = data['jobId']
    
    # Save to saved_jobs table
    # saved_job = SavedJob(user_id=user_id, job_id=job_id)
    # db.session.add(saved_job)
    # db.session.commit()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=3000)
```

---

## 📊 Database Schema Suggestions

### Jobs Table
```sql
CREATE TABLE jobs (
  id INT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(255) NOT NULL,
  company VARCHAR(255) NOT NULL,
  location VARCHAR(100),
  salary INT,
  job_type VARCHAR(50),
  experience_level VARCHAR(50),
  description TEXT,
  requirements JSON,
  benefits JSON,
  technologies JSON,
  category VARCHAR(50),
  apply_url VARCHAR(255),
  recruiter_email VARCHAR(255),
  company_description TEXT,
  applicants_count INT DEFAULT 0,
  posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Saved Jobs Table
```sql
CREATE TABLE saved_jobs (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  job_id INT NOT NULL,
  saved_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (job_id) REFERENCES jobs(id),
  UNIQUE(user_id, job_id)
);
```

### Applications Table
```sql
CREATE TABLE applications (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  job_id INT NOT NULL,
  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  status ENUM('pending', 'viewed', 'rejected', 'accepted'),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (job_id) REFERENCES jobs(id)
);
```

---

## 🔒 Security Best Practices

1. **Use HTTPS** - Always in production
2. **JWT Tokens** - Short-lived access tokens (15 min) + refresh tokens
3. **Rate Limiting** - Max 100 requests/minute per IP
4. **Input Validation** - Validate all inputs on server
5. **CORS** - Whitelist only your app domain
6. **SQL Injection** - Use parameterized queries
7. **Password Hashing** - bcrypt with 10+ rounds

---

## 📈 Performance Optimization

- Add database indexes on frequently queried fields
- Cache job listings (Redis)
- Implement pagination (limit 20-50 items)
- Use CDN for images
- Enable gzip compression
- Monitor API response times

---

**Happy coding! 🚀**
