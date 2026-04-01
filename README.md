# Language Detection System (FastAPI + FastText + React)

A production-ready full-stack application that detects the language of input text using FastText, supporting 150+ languages with high accuracy and low latency.

---

## Features

- Language Detection (150+ languages)
- FastText Model (lid.176.bin)
- Script Detection (Tamil, Hindi, Arabic, etc.)
- Top-3 Predictions with Confidence Scores
- Basic Rate Limiting
- Request Logging
- Modern React Frontend (Tailwind UI)
- Docker Support (Full-stack deployment)

---

## Screenshot

![App Screenshot](https://i.postimg.cc/cJ9F8wfT/nlp.png)

---

## Tech Stack

### Backend
- FastAPI
- FastText
- Python
- Uvicorn

### Frontend
- React (Vite)
- Tailwind CSS
- Axios

### DevOps
- Docker
- Docker Compose

---

## Project Structure
```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── middleware.py        # Custom middleware
│   │   ├── config.py            # Configuration settings
│   │   ├── schemas.py           # Pydantic models
│   │   ├── model.py             # ML pipeline and model logic
│   │   └── utils.py             # Utility functions
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile              # Docker configuration
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── hooks/               # Custom React hooks
│   │   └── App.jsx              # Main React component
│   ├── package.json            # Node.js dependencies
│   └── Dockerfile              # Docker configuration
├── README.md                   # This file
└── docker-compose.yml          # Docker Compose configuration
```


---

## Setup Instructions

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Author

Built as a full-stack NLP system focused on performance, scalability, and clean architecture.
