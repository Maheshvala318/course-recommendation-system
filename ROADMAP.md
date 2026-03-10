# ROADMAP.md — Course Recommendation System

## Milestone 1: Deployment-Ready v1 (Current)

### Phase 1: Project Restructuring ✅
- Analyze existing messy codebase
- Create modular `src/` package structure
- Clean and deduplicate all source files
- Create CLAUDE.md and PROJECT_SUMMARY.md

### Phase 2: Data Pipeline ⬜
- Run `scripts/organize_files.py` to move data to proper directories
- Run `scripts/convert_similarity_matrix.py` to create sparse top-K index
- Move old large similarity matrices to `_legacy_large_files/` (gitignored)
- Verify all pickle artifacts load correctly

### Phase 3: Application Testing ⬜
- Test Streamlit app with all 3 recommendation methods
- Test title search (both dataset match and TF-IDF fallback)
- Verify Streamlit caching works (data loads once)
- Browser-based UI validation

### Phase 4: Deployment ⬜
- Build and test Docker image
- Set up cloud deployment (Streamlit Cloud / Railway)
- Configure production environment variables
- Write final deployment README

---

## Milestone 2: Enhanced Features (Future)
- Multi-platform data (Coursera integration)
- Advanced filtering and sorting
- FastAPI backend
- CI/CD pipeline
