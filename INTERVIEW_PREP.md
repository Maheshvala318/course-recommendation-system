# 🎙️ Interview Preparation Guide: Course Recommender AI

Use this guide to explain your project confidently during technical interviews. It follows the **STAR** (Situation, Task, Action, Result) method and dives into the "Why" behind your technical choices.

---

## 🔝 Project Pitch (The "Elevator Query")
"I built a production-grade Course Recommendation System using Python and Scikit-Learn that suggests relevant Udemy courses from a dataset of 70k+ entries. Unlike basic recommenders, I implemented a **Weighted Hybrid Similarity Engine** that balances text semantic meaning (70%) with standardized numerical features (30%), resulting in highly accurate recommendations. I also optimized the system for production by reducing its memory footprint by 99% using sparse Top-K indexing and deployed it using Docker."

---

## 🧠 Technical Deep Dive (The "How")

### 1. What was the biggest challenge?
**Answer:** "The original system was extremely inefficient and inaccurate. It used a monolithic similarity matrix that was nearly 2GB in size, which made deployment impossible on standard servers. Also, it didn't normalize numerical data, so it would recommend unrelated courses just because they had similar prices."

### 2. How did you fix the accuracy?
**Answer:** "I implemented a weighted hybrid approach. I used **TF-IDF Vectorization** for text features (titles, descriptions, categories) and **StandardScaler** for numerical features (ratings, subscribers, duration). I assigned a 0.7 weight to text and 0.3 to numeric values. This ensures that the system first finds courses with the same *content* and then use popularity/pricing as a tie-breaker."

### 3. How did you optimize for production?
**Answer:** "A full similarity matrix for 15k+ courses is massive ($N \times N$). Instead of storing every single score, I built a **Sparse Top-K Index**. For every course, I only store the top 50 most similar matches. This reduced the storage requirements from **1.9 GB down to 10 MB**—a 99% reduction—allowing the app to load and provide results instantly."

### 4. What is "Discovery Mode"?
**Answer:** "Recommendation systems often suffer from 'echo chambers'—showing only very similar items. I implemented a 'Discovery Mode' that injects variety. It returns 4 top-tier matches and 1 'Surprise Pick' randomly sampled from the 20th to 50th percentile of similar courses. This improves user engagement by introducing serendipity."

---

## 🛠️ Performance & Scalability (System Design)

| Feature | Technical Strategy | Benefit |
|---------|-------------------|---------|
| **Data Scalability** | Sparse Matrices & Top-K Indexing | Handles 70k+ courses with negligible RAM usage. |
| **Search Fallback** | Real-time TF-IDF Search Engine | Provides results even for titles not in the trained dataset. |
| **Deployment** | Docker Multi-stage Build | 150MB image size; isolated environment for 'it works on my machine' consistency. |
| **UI/UX** | Streamlit + Custom CSS | Premium glassmophic design with interactive course cards. |

---

## 💡 Potential Interview Questions

1. **Why use TF-IDF instead of Word2Vec?**
   - *Answer:* "TF-IDF is highly effective for keyword-heavy datasets like course titles/descriptions where specific terms (e.g., 'Python', 'Web Development') carry significant weight. It is Also more computationally efficient for a dataset of this size."

2. **Why normalize numerical features?**
   - *Answer:* "Numerical features have different scales (e.g., ratings are 0-5, but subscribers are 0-100k). Without normalization (StandardScaler), the feature with the largest range (subscribers) would dominate the cosine similarity, making other features irrelevant."

3. **How do you handle 'Cold Start' problems?**
   - *Answer:* "I implemented a Search Fallback engine. If a user enters a query not in the database, the system uses the fitted TF-IDF vectorizer to find the most semantically similar matches from the existing course descriptions."

---
**Tip:** Be prepared to show the `docker-compose.yml` to demonstrate your knowledge of production containerization and memory limits!
