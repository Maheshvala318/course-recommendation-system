# REQUIREMENTS.md — Course Recommendation System

## v1 — Core (Current Milestone)

### Functional Requirements
- [x] **FR-01**: Select a course from dropdown → get 5 similar courses
- [x] **FR-02**: Three recommendation methods: Cosine Similarity, KNN, Correlation
- [x] **FR-03**: Free-text title search with TF-IDF fallback for unknown titles
- [x] **FR-04**: Display course details: title, price, duration, rating, reviews, subscribers
- [x] **FR-05**: Similarity/accuracy scores displayed for KNN and Correlation methods

### Non-Functional Requirements
- [x] **NFR-01**: Modular code structure (separate packages for data, models, config, app)
- [x] **NFR-02**: Streamlit caching for all data loads (no reload on every rerun)
- [x] **NFR-03**: Sparse top-K similarity index (~20MB instead of 1.9GB)
- [x] **NFR-04**: Docker-ready deployment (Dockerfile + docker-compose.yml)
- [x] **NFR-05**: Environment variable config (no hardcoded secrets)
- [x] **NFR-06**: .gitignore for large data files and artifacts

## v2 — Future Enhancements
- [ ] **FR-06**: User authentication and personalized history
- [ ] **FR-07**: Multi-platform support (Coursera + Udemy combined)
- [ ] **FR-08**: Advanced filtering (by price, duration, level, category)
- [ ] **FR-09**: REST API endpoint (FastAPI) for programmatic access
- [ ] **FR-10**: Automated retraining pipeline (Airflow/cron for data refresh)
- [ ] **NFR-07**: CI/CD pipeline (GitHub Actions)
- [ ] **NFR-08**: Cloud deployment (Streamlit Cloud / Railway / AWS)
- [ ] **NFR-09**: Monitoring and logging (error tracking, usage analytics)

## Out of Scope
- Real-time data scraping in production (scrapers are reference-only)
- Payment processing or course enrollment
- User review submission system
- Mobile native app
