## 🌍 Make it Live: Deployment for your Resume

To share this project on your resume, you need a public URL where recruiters can click and see the app working. Here are the two best ways to do it for free.

> [!IMPORTANT]
> **Do I need to keep Docker open?**
> **No.** Once you deploy to Hugging Face or Streamlit Cloud, the app runs on **their servers** in the cloud. You can turn off your computer, close Docker, and the link will still work 24/7 for anyone with the URL. This is exactly what you want for a resume!

---

## 🏁 Phase 0: The Very First Step (GitHub)
Before you can deploy to Hugging Face or Streamlit, your code **must** be stored on GitHub. This is the "Source of Truth" for your app.

### How to do it:
1.  **Create a Repository**: Go to [github.com/new](https://github.com/new) and name it `course-recommendation-system`. Leave it "Public".
2.  **Initialize Git** (run these in your project terminal):
    ```bash
    git init
    git add .
    git commit -m "feat: Professional Course Recommender with Hybrid AI"
    ```
3.  **Push to GitHub**:
    ```bash
    git remote add origin https://github.com/your-username/course-recommendation-system.git
    git branch -M main
    git push -u origin main
    ```

---

## Option 1: Streamlit Community Cloud (Easiest & Cleanest)
This is the "official" way to host Streamlit apps. It's free and looks very professional.

### Steps:
1.  **Push to GitHub**: Make sure your project is in a public GitHub repository.
2.  **Sign up**: Go to [share.streamlit.io](https://share.streamlit.io) and connect your GitHub account.
3.  **Deploy**:
    - Click "New app".
    - Select your repository and branch.
    - **Main file path**: `src/app/streamlit_app.py`.
4.  **Important**: You need to ensure your `requirements.txt` is updated (it is!). Streamlit Cloud will install everything automatically.

---

## Option 2: Hugging Face Spaces (Best for Docker) 🐳
Since your project is already professionally Dockerized, Hugging Face is the perfect home for it.

### Phase 1: Create the Space
1.  **Go to Hugging Face**: [huggingface.co/new-space](https://huggingface.co/new-space)
2.  **Name your Space**: `course-recommender`
3.  **SDK**: Select **Docker**. 
4.  **Template**: Select **Blank** (since you already have your own `Dockerfile`).
5.  **Visibility**: Public.

### Phase 2: Connect to GitHub
1.  Scroll down to **"Repository type"** and select **"GitHub"**.
2.  Search for and select: `Maheshvala318/course-recommendation-system`.
3.  Click **"Connect"**.

### Phase 3: Watch it Build
Hugging Face will automatically pull your code and start building the container.
-   Open the **"Logs"** tab to see the progress.
-   Once it's finished, your app will be live!

---

## 📝 Tips for your Resume
When you add this to your resume, don't just put the link. Add a "Technical Highlights" section:

> **Course Recommender AI** | [Live Link] | [GitHub]
> * Built a production-grade recommendation engine handling 70k+ courses using **Weighted Hybrid Similarity**.
> * Optimized system performance by **99%** (1.9GB to 10MB) using Sparse Top-K Indexing.
> * Implemented a premium glassmorphic UI with a custom **Discovery Mode** to improve user engagement.
> * Fully containerized with **Docker** for consistent production deployment.

---

## ⚠️ Data File Note
For both options, you must make sure the files in `data/processed/` are pushed to GitHub. 
*   `course_data_original.pkl`
*   `similarity_topk.pkl`
*   `tfidf_matrix.pkl`
*   `tfidf_vectorizer.pkl`

Since these are small (~70MB total), GitHub will accept them. **Do NOT** upload the 600MB `combined_features.pkl`.
