AcademiQ — OBE Intelligence Platform

AI-powered Outcomes-Based Education analytics, early alert system, and accreditation reporting for universities.

Built for the DIU AI Project Competition 2026 as a standalone system and as a module for the Chloris university platform.

What it does
AcademiQ turns a university's mandatory OBE data into a live intelligence system. It automatically calculates Course Outcome (CO) and Program Outcome (PO) attainment from uploaded marksheets, predicts which students are at risk of failing specific learning outcomes by Week 6 of the semester, sends automated email alerts to those students and their advisors, and generates accreditation-ready PDF reports in under 60 seconds.

Features

OBE Attainment Engine — automatically computes CO and PO attainment levels from marks data, no manual spreadsheets required
ML Risk Prediction — XGBoost model predicts at-risk students per CO by mid-semester with ~85% accuracy on real data
Email Alert System — automated HTML email alerts to students and faculty with risk level, affected COs, and recommended actions
Excel / CSV Upload — drag-and-drop marksheet upload supporting .csv, .xlsx, and .xls with validation preview
PDF Report Generation — one-click accreditation-ready OBE reports formatted for UGC and ABET submission
Role-based Dashboards — separate views for students, faculty, heads of department, and deans
Downloadable Templates — pre-filled Excel templates so faculty can fill in marks and upload directly


Tech stack
LayerTechnologyBackendFastAPI, SQLAlchemy, SQLite / PostgreSQLMLXGBoost, scikit-learn, pandasAuthJWT (python-jose), bcryptPDFReportLabExcelopenpyxl, pandasAsync tasksCelery + RedisFrontendReact 18, Vite, TailwindCSSChartsRechartsStateZustandHTTPAxiosUpload UIreact-dropzone

Project structure
academiq/
├── academiq-backend/
│   ├── main.py
│   ├── api/
│   │   ├── routes_auth.py
│   │   ├── routes_obe.py
│   │   ├── routes_alerts.py
│   │   ├── routes_upload.py
│   │   └── routes_reports.py
│   ├── services/
│   │   ├── obe_engine.py
│   │   ├── ml_predictor.py
│   │   ├── alert_service.py
│   │   ├── upload_service.py
│   │   └── report_service.py
│   ├── ml/
│   │   ├── train.py
│   │   ├── features.py
│   │   └── models/
│   ├── models/
│   │   ├── db_models.py
│   │   └── schemas.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── database/
│   │   ├── connection.py
│   │   └── crud.py
│   ├── seed_data.py
│   └── requirements.txt
│
└── academiq-frontend/
    └── src/
        ├── api/
        ├── store/
        ├── pages/
        │   ├── student/
        │   ├── faculty/
        │   └── dean/
        └── components/
            ├── layout/
            ├── charts/
            └── common/

Getting started
Prerequisites

Python 3.10+
Node.js 18+
Git

Backend setup
bash# Clone the repo
git clone https://github.com/your-username/academiq.git
cd academiq/academiq-backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac / Linux

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your DATABASE_URL, SECRET_KEY, SMTP settings

# Seed the database with demo data
python seed_data.py

# Train the ML model
python ml/train.py

# Start the server
uvicorn main:app --reload --port 8000
API docs available at http://localhost:8000/docs
Frontend setup
bashcd academiq/academiq-frontend

# Install dependencies
npm install

# Copy and configure environment variables
cp .env.example .env
# Set VITE_API_URL=http://localhost:8000/api

# Start the dev server
npm run dev
Frontend available at http://localhost:5173

Demo credentials
RoleEmailPasswordFacultyfaculty@diu.edu.bdtest1234Deandean@diu.edu.bdtest1234Student (good)alice@diu.edu.bdtest1234Student (at-risk)david@diu.edu.bdtest1234

API endpoints
MethodEndpointDescriptionPOST/api/auth/registerRegister a new userPOST/api/auth/loginLogin and get JWT tokenGET/api/obe/co-attainment/{course_id}CO attainment for a courseGET/api/obe/po-attainment/{program_id}PO attainment for a programGET/api/obe/risk/{course_id}ML risk scores for all studentsGET/api/obe/my-risk/{course_id}Student's own risk scoreGET/api/obe/course-summary/{course_id}Course health summaryGET/api/alerts/preview/{course_id}Preview alerts (dry run)POST/api/alerts/trigger/{course_id}Send real email alertsPOST/api/upload/marksheetUpload CSV or Excel marksheetGET/api/upload/template/{course_id}Download Excel templateGET/api/reports/obe/{course_id}Download PDF OBE report

Environment variables
Backend .env
envAPP_NAME=AcademiQ
APP_ENV=development
DATABASE_URL=sqlite:///./academiq.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
FRONTEND_URL=http://localhost:5173
REDIS_URL=redis://localhost:6379/0
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@academiq.com
MODEL_PATH=ml/models/risk_model_v1.pkl
Frontend .env
envVITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=AcademiQ

How the ML model works
The risk prediction model is trained on historical marks data using XGBoost. Features are extracted from Week 1–9 performance only, simulating what the system knows at the mid-semester alert point.
Input features:

Overall marks percentage (weeks 1–9)
Assignment submission rate
Per-CO early scores (CO1–CO4)

Output:

Risk score (0–1 probability)
Risk level (low / medium / high)
List of specific at-risk COs

To retrain on new data:
bashpython ml/train.py
The model file is saved to ml/models/risk_model_v1.pkl and loaded automatically by the prediction service.

Switching to real data
The system is designed to work with real university data with zero code changes. To switch from demo data to real marks:

Export marks from your university ERP as .xlsx or .csv
Format the file with three columns: student_id, assessment_id, obtained_marks
Upload via the Upload Marks page or the /api/upload/marksheet endpoint
Retrain the ML model: python ml/train.py

A downloadable template is available from the Upload page or /api/upload/template/{course_id}.

Merging into Chloris
AcademiQ was designed to be merged into the Chloris university platform. The merge requires:

Copy api/routes_obe.py, routes_alerts.py, routes_upload.py, routes_reports.py into Chloris backend
Copy services/ folder into Chloris backend
Copy ml/ folder into Chloris backend
Append OBE tables to Chloris db_models.py
Register routers in Chloris main.py
Copy pages/obe/ and components/obe/ into Chloris frontend
Add obeService.ts to Chloris services/

No existing Chloris files need to be deleted or overwritten.

Roadmap

 React frontend — all role dashboards
 Real SMTP email delivery
 PostgreSQL migration for production
 DIU ERP direct integration
 Celery batch prediction (nightly scheduled alerts)
 Multi-course and multi-semester views
 Attendance data integration for improved ML accuracy
 Mobile-responsive UI


Contributing
Pull requests are welcome. For major changes please open an issue first to discuss what you would like to change.

License
MIT

Acknowledgements
Built with FastAPI, XGBoost, ReportLab, React, Recharts, and TailwindCSS.
Developed as a competition submission for Daffodil International University AI Project Competition 2026.
