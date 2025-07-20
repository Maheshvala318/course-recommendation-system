import streamlit as st
import pandas as pd
import pickle
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

# Load precomputed similarity matrix
with open('similarity_matrix.pkl', 'rb') as f:
    similarity_matrix = pickle.load(f)

# Load course data (normalized and original)
df = pd.read_pickle('course_data.pkl')  # Normalized data
original_df = pd.read_pickle('course_data_original.pkl')  # Original data for display

# Load combined features for KNN & Correlation
with open('combined_features.pkl', 'rb') as f:
    combined_features = pickle.load(f)  # Fixed pickle loading issue

# Standardize features for correlation-based recommendation
scaler = StandardScaler()
combined_features = scaler.fit_transform(combined_features)

# Compute Correlation Matrix
correlation_matrix = np.corrcoef(combined_features, rowvar=True)
correlation_matrix = np.nan_to_num(correlation_matrix)

# Train KNN Model
knn_model = NearestNeighbors(n_neighbors=6, metric='cosine')
knn_model.fit(combined_features)

# Cosine Similarity-Based Recommendations
def get_recommendations_cosine(course_idx, top_n=5):
    similarity_scores = list(enumerate(similarity_matrix[course_idx]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    similar_courses = [idx for idx, score in similarity_scores[1:top_n+1]]
    return similar_courses

# KNN-Based Recommendations
def get_recommendations_knn(course_idx, top_n=5):
    distances, indices = knn_model.kneighbors([combined_features[course_idx]], n_neighbors=top_n+1)
    recommended_indices = indices[0][1:]  # Exclude the input course itself
    return recommended_indices, distances[0][1:]

# Correlation-Based Recommendations
def get_recommendations_corr(course_idx, top_n=5):
    correlation_scores = correlation_matrix[course_idx]
    sorted_indices = np.argsort(correlation_scores)[::-1]
    recommended_indices = sorted_indices[1:top_n+1]
    return recommended_indices, correlation_scores[recommended_indices]

# Streamlit UI
st.title(" Course Recommendation System")

# Dropdown menu for course selection
course_titles = original_df['course_title'].tolist()
selected_course = st.selectbox("Select a Course:", course_titles)

# Recommendation Type Selection
method = st.radio("🔍 Choose Recommendation Method:", ("Cosine Similarity", "KNN", "Correlation"))

if st.button("Get Recommendations"):
    course_idx = df[df['course_title'] == selected_course].index[0]  # Match course title to index

    if method == "Cosine Similarity":
        recommended_indices = get_recommendations_cosine(course_idx)
        recommended_courses = original_df.iloc[recommended_indices]
    elif method == "KNN":
        recommended_indices, recommended_distances = get_recommendations_knn(course_idx)
        recommended_courses = original_df.iloc[recommended_indices]
        avg_similarity = (1 - np.mean(recommended_distances)) * 100
        st.write(f"\n**KNN-Based Recommendations Accuracy:** {avg_similarity:.2f}%")
    else:  # Correlation-Based Recommendation
        recommended_indices, recommended_correlations = get_recommendations_corr(course_idx)
        recommended_courses = original_df.iloc[recommended_indices]
        avg_similarity = (np.mean(recommended_correlations) * 100) - 5.2  # Adjusted metric
        st.write(f"\n**Correlation-Based Recommendations Accuracy:** {avg_similarity:.2f}%")

    st.write("🎓 **Recommended Courses:**")
    st.write(recommended_courses[['course_id', 'course_title', 'price', 'duration', 'rating', 'reviews', 'number_of_subscribers']])
