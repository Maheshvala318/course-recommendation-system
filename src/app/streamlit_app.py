"""
🎓 Course Recommendation System — Streamlit Application

Premium UI with course cards. Cosine Similarity only.
Run with: streamlit run src/app/streamlit_app.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from src.config.settings import (
    DEFAULT_TOP_N,
    STREAMLIT_LAYOUT,
    STREAMLIT_PAGE_ICON,
    STREAMLIT_PAGE_TITLE,
)
from src.data.loader import (
    load_original_course_data,
    load_similarity_topk,
    load_tfidf_matrix,
    load_tfidf_vectorizer,
)
from src.models.cosine_recommender import CosineRecommender
from src.models.title_search import TitleSearchEngine


# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title=STREAMLIT_PAGE_TITLE,
    page_icon=STREAMLIT_PAGE_ICON,
    layout=STREAMLIT_LAYOUT,
)


# ──────────────────────────────────────────────
# Custom CSS — Premium Theme
# ──────────────────────────────────────────────
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
.stApp { font-family: 'Inter', sans-serif !important; }

.hero-box {
  text-align: center;
  padding: 2rem 1rem 1rem;
}
.hero-title {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #6c63ff 0%, #00d4aa 50%, #6c63ff 100%);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: shimmer 3s ease infinite;
  margin-bottom: 0.3rem;
}
@keyframes shimmer {
  0% { background-position: 0% center; }
  50% { background-position: 100% center; }
  100% { background-position: 0% center; }
}
.hero-sub {
  color: #9a9ab0;
  font-size: 1.05rem;
  max-width: 600px;
  margin: 0 auto;
  font-weight: 300;
}
.stats-row {
  display: flex;
  justify-content: center;
  gap: 2.5rem;
  margin: 1.2rem 0 1.5rem;
  flex-wrap: wrap;
}
.stat-box { text-align: center; }
.stat-num {
  font-size: 1.5rem;
  font-weight: 700;
  color: #6c63ff;
}
.stat-lbl {
  font-size: 0.75rem;
  color: #6b6b80;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.sec-hdr {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 1.5rem 0 0.8rem;
  padding-bottom: 0.4rem;
  border-bottom: 2px solid rgba(108,99,255,0.2);
}
.sec-hdr h2 {
  font-size: 1.4rem;
  font-weight: 700;
  margin: 0;
}
.c-card {
  border: 1px solid rgba(108,99,255,0.15);
  border-radius: 14px;
  padding: 1.2rem 1.4rem;
  margin-bottom: 0.8rem;
  transition: all 0.25s ease;
  position: relative;
  overflow: hidden;
  background: rgba(108,99,255,0.03);
}
.c-card:hover {
  border-color: #6c63ff;
  box-shadow: 0 6px 24px rgba(108,99,255,0.12);
  transform: translateY(-1px);
}
.c-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.8rem;
  margin-bottom: 0.5rem;
}
.c-title {
  font-size: 1.1rem;
  font-weight: 600;
  line-height: 1.35;
  flex: 1;
}
.c-title a { color: inherit; text-decoration: none; }
.c-title a:hover { color: #6c63ff; }
.bdg {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 16px;
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  white-space: nowrap;
}
.bdg-free { background: rgba(0,212,170,0.12); color: #00d4aa; border: 1px solid rgba(0,212,170,0.25); }
.bdg-paid { background: rgba(108,99,255,0.1); color: #6c63ff; border: 1px solid rgba(108,99,255,0.2); }
.bdg-lvl { background: rgba(255,193,7,0.1); color: #ffc107; border: 1px solid rgba(255,193,7,0.2); }
.bdg-cat { background: rgba(108,99,255,0.06); color: #8a82ff; border: 1px solid rgba(108,99,255,0.15); }
.bdg-match { background: rgba(0,212,170,0.1); color: #00d4aa; border: 1px solid rgba(0,212,170,0.2); }
.c-desc {
  color: #9a9ab0;
  font-size: 0.85rem;
  line-height: 1.5;
  margin-bottom: 0.8rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.c-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  align-items: center;
  margin-bottom: 0.6rem;
}
.c-mi {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #9a9ab0;
}
.c-stars { color: #ffc107; font-size: 0.82rem; letter-spacing: 0.5px; }
.c-rat { font-weight: 600; color: #ffc107; }
.c-tags { display: flex; flex-wrap: wrap; gap: 0.3rem; }
.sel-card {
  background: linear-gradient(135deg, rgba(108,99,255,0.06) 0%, rgba(0,212,170,0.06) 100%);
  border: 1px solid #6c63ff;
  border-radius: 14px;
  padding: 1.2rem 1.4rem;
  margin-bottom: 1.2rem;
}
.sel-lbl {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: #6c63ff;
  margin-bottom: 0.5rem;
}
.divider-line {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(108,99,255,0.2), transparent);
  margin: 1.5rem 0;
}
.foot-box {
  text-align: center;
  padding: 1.5rem 0;
  color: #6b6b80;
  font-size: 0.82rem;
}
.foot-box a { color: #6c63ff; text-decoration: none; }
.foot-box a:hover { text-decoration: underline; }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Load Data (cached)
# ──────────────────────────────────────────────
@st.cache_resource(show_spinner="🔄 Loading course database...")
def initialize():
    original_df = load_original_course_data()
    similarity_topk = load_similarity_topk()
    tfidf_vectorizer = load_tfidf_vectorizer()
    tfidf_matrix = load_tfidf_matrix()
    cosine_engine = CosineRecommender(similarity_topk)
    search_engine = TitleSearchEngine(
        original_df, similarity_topk, tfidf_vectorizer, tfidf_matrix
    )
    return original_df, cosine_engine, search_engine


original_df, cosine_engine, search_engine = initialize()


# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────
def get_stars(rating):
    try:
        r = float(rating)
    except (ValueError, TypeError):
        return "☆☆☆☆☆"
    full = int(r)
    half = 1 if r - full >= 0.5 else 0
    empty = 5 - full - half
    return "★" * full + "⯨" * half + "☆" * empty


def fmt_num(n):
    try:
        n = int(float(n))
    except (ValueError, TypeError):
        return "0"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def fmt_price(price, is_paid):
    try:
        paid = int(float(is_paid))
    except (ValueError, TypeError):
        paid = 1
    if paid == 0:
        return "Free"
    ps = str(price).strip()
    if ps in ("0", "0.0", "0.00", ""):
        return "Free"
    clean = ps.replace("£", "").replace("$", "").replace("€", "").strip()
    try:
        return f"${float(clean):.2f}"
    except ValueError:
        return ps


def make_card_html(row, match_score=None):
    """Build course card HTML (no leading whitespace!)."""
    title = str(row.get("course_title", "Untitled")).replace("<", "&lt;").replace(">", "&gt;")
    url = str(row.get("url", "#"))
    rating = row.get("rating", 0)
    reviews = row.get("reviews", 0)
    subs = row.get("number_of_subscribers", 0)
    duration = str(row.get("duration", "N/A"))
    level = str(row.get("level", ""))
    price = row.get("price", "")
    is_paid = row.get("is_paid", 1)
    desc = str(row.get("description", ""))[:180].replace("<", "&lt;").replace(">", "&gt;")
    cat = str(row.get("category_name", "")).replace("<", "&lt;")
    subcat = str(row.get("sub_category_name", "")).replace("<", "&lt;")

    stars = get_stars(rating)
    price_disp = fmt_price(price, is_paid)
    is_free = price_disp == "Free"
    try:
        rating_str = f"{float(rating):.2f}"
    except (ValueError, TypeError):
        rating_str = "0.00"

    price_bdg = '<span class="bdg bdg-free">Free</span>' if is_free else f'<span class="bdg bdg-paid">{price_disp}</span>'
    lvl_bdg = f'<span class="bdg bdg-lvl">{level}</span>' if level and level != "nan" else ""
    
    # Check if this is a diverse pick (low similarity score relative to top)
    is_diverse = match_score is not None and match_score < 0.4
    
    match_bdg = ""
    if match_score is not None:
        if is_diverse:
            match_bdg = f'<span class="bdg bdg-match" style="background:rgba(255,107,107,0.1);color:#ff6b6b;border-color:rgba(255,107,107,0.2);">✨ Surprise Pick</span>'
        else:
            match_bdg = f'<span class="bdg bdg-match">{match_score:.0%} match</span>'

    if desc == "nan":
        desc = ""

    # CRITICAL: No leading whitespace — prevents markdown code-block interpretation
    return (
        f'<div class="c-card">'
        f'<div class="c-card-top">'
        f'<div class="c-title"><a href="{url}" target="_blank">{title}</a></div>'
        f'<div style="display:flex;gap:0.3rem;flex-shrink:0;">{match_bdg}{price_bdg}</div>'
        f'</div>'
        f'<div class="c-desc">{desc}</div>'
        f'<div class="c-meta">'
        f'<div class="c-mi"><span class="c-stars">{stars}</span> <span class="c-rat">{rating_str}</span> <span>({fmt_num(reviews)} reviews)</span></div>'
        f'<div class="c-mi">👥 {fmt_num(subs)} students</div>'
        f'<div class="c-mi">⏱️ {duration}</div>'
        f'</div>'
        f'<div class="c-tags">{lvl_bdg}<span class="bdg bdg-cat">{cat}</span><span class="bdg bdg-cat">{subcat}</span></div>'
        f'</div>'
    )


# ══════════════════════════════════════════════
# UI Layout
# ══════════════════════════════════════════════

# Hero
total_courses = len(original_df)
try:
    total_cats = original_df["category_name"].nunique()
except Exception:
    total_cats = 0
try:
    avg_rat = float(original_df["rating"].astype(float).mean())
except Exception:
    avg_rat = 0.0

st.markdown(
    f'<div class="hero-box">'
    f'<div class="hero-title">🎓 Course Recommender</div>'
    f'<div class="hero-sub">Discover your next learning adventure. AI-powered recommendations from {total_courses:,}+ Udemy courses.</div>'
    f'</div>'
    f'<div class="stats-row">'
    f'<div class="stat-box"><div class="stat-num">{total_courses:,}</div><div class="stat-lbl">Courses</div></div>'
    f'<div class="stat-box"><div class="stat-num">{total_cats}</div><div class="stat-lbl">Categories</div></div>'
    f'<div class="stat-box"><div class="stat-num">{avg_rat:.1f} ★</div><div class="stat-lbl">Avg Rating</div></div>'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)

# ──────────────────────────────────────────
# Section 1: Select & Discover
# ──────────────────────────────────────────
st.markdown('<div class="sec-hdr"><h2>📚 Select a Course</h2></div>', unsafe_allow_html=True)

course_titles = original_df["course_title"].tolist()
selected_course = st.selectbox(
    "Choose from the database:",
    course_titles,
    label_visibility="collapsed",
    placeholder="Start typing to search courses...",
)

col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    top_n = st.selectbox("Results", [5, 10, 15, 20], index=0)
with col2:
    is_diverse = st.toggle("Discovery Mode", value=True, help="Include some 'surprise' related courses")

if st.button("🔍 Find Similar Courses", type="primary", use_container_width=True):
    course_idx = original_df[original_df["course_title"] == selected_course].index[0]

    # Selected course card
    sel_row = original_df.iloc[course_idx]
    inner = make_card_html(sel_row)
    st.markdown(
        f'<div class="sel-card"><div class="sel-lbl">📌 Selected Course</div>{inner}</div>',
        unsafe_allow_html=True,
    )

    # Recommendations
    rec_indices = cosine_engine.recommend(course_idx, top_n, diverse=is_diverse)

    st.markdown('<div class="sec-hdr"><h2>🎯 Recommended Courses</h2></div>', unsafe_allow_html=True)

    for idx in rec_indices:
        row = original_df.iloc[idx]
        # Get match score
        score = None
        topk_list = cosine_engine.similarity_topk.get(course_idx, [])
        for tidx, tscore in topk_list:
            if tidx == idx:
                score = tscore
                break
        st.markdown(make_card_html(row, match_score=score), unsafe_allow_html=True)


st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)

# ──────────────────────────────────────────
# Section 2: Search by Title
# ──────────────────────────────────────────
st.markdown('<div class="sec-hdr"><h2>🔎 Search by Course Title</h2></div>', unsafe_allow_html=True)

input_title = st.text_input(
    "Type any course title:",
    placeholder="e.g., Python for beginners, Machine Learning, Web Development...",
    label_visibility="collapsed",
)

if st.button("🚀 Search & Recommend", use_container_width=True):
    if input_title.strip() == "":
        st.warning("⚠️ Please type a course title first.")
    else:
        base_course, recommended, found = search_engine.search(
            input_title, top_n=top_n
        )

        if found:
            st.success("✅ Course found — using hybrid similarity")
        else:
            st.info("🔍 Not in database — using TF-IDF text matching")

        if not base_course.empty:
            st.markdown('<div class="sel-lbl">📌 Your Query Match</div>', unsafe_allow_html=True)
            for _, row in base_course.iterrows():
                st.markdown(make_card_html(row), unsafe_allow_html=True)

        if not recommended.empty:
            st.markdown('<div class="sec-hdr"><h2>🎯 Recommended Courses</h2></div>', unsafe_allow_html=True)
            for _, row in recommended.iterrows():
                st.markdown(make_card_html(row), unsafe_allow_html=True)


# Footer
st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
st.markdown(
    '<div class="foot-box">Built with ❤️ by <a href="https://github.com/Maheshvala318">Mahesh Vala</a> · '
    'Powered by <strong>Streamlit</strong> &amp; <strong>scikit-learn</strong> · '
    '<a href="https://github.com/Maheshvala318/course-recommendation-system">GitHub</a></div>',
    unsafe_allow_html=True,
)
