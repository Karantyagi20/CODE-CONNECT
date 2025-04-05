import numpy as np
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix
from database import fetch_course_metadata, fetch_user_course_data

def cf_recommendations(student_id, courses):
    # Fetch user-course interaction data
    raw_data = fetch_user_course_data()
    
    # Create a user-item interaction matrix
    unique_students = sorted(set(row['student_id'] for row in raw_data))
    unique_courses = sorted(set(row['course_id'] for row in raw_data))
    student_to_index = {student: idx for idx, student in enumerate(unique_students)}
    course_to_index = {course: idx for idx, course in enumerate(unique_courses)}
    
    matrix = np.zeros((len(unique_students), len(unique_courses)))
    for row in raw_data:
        student_idx = student_to_index[row['student_id']]
        course_idx = course_to_index[row['course_id']]
        matrix[student_idx, course_idx] = row['grade']
    
    # Apply TruncatedSVD for dimensionality reduction
    sparse_matrix = csr_matrix(matrix)
    svd = TruncatedSVD(n_components=50, random_state=42)
    latent_matrix = svd.fit_transform(sparse_matrix)
    
    # Predict ratings for unseen courses
    student_idx = student_to_index[student_id]
    predictions = []
    for course in courses:
        if course in course_to_index:
            course_idx = course_to_index[course]
            predicted_rating = np.dot(latent_matrix[student_idx], svd.components_[:, course_idx])
            predictions.append((course, predicted_rating))
    
    return sorted(predictions, key=lambda x: x[1], reverse=True)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def cbf_recommendations(student_keywords, courses):
    course_data = fetch_course_metadata()
    course_ids = [row['course_id'] for row in course_data]
    keywords = [row['keywords'] for row in course_data]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(keywords)
    student_vector = vectorizer.transform([student_keywords])
    similarity_scores = cosine_similarity(student_vector, tfidf_matrix).flatten()
    recommendations = [(course, score) for course, score in zip(course_ids, similarity_scores)]
    return sorted(recommendations, key=lambda x: x[1], reverse=True)

def generate_recommendations(student_id, student_keywords, courses, cf_weight=7, cbf_weight=10):
    cf_recs = cf_recommendations(student_id, courses)
    cbf_recs = cbf_recommendations(student_keywords, courses)
    cf_dict = {course: score for course, score in cf_recs}
    cbf_dict = {course: score for course, score in cbf_recs}
    hybrid_scores = {}
    for course in courses:
        cf_score = cf_dict.get(course, 0)
        cbf_score = cbf_dict.get(course, 0)
        hybrid_scores[course] = cf_score * cf_weight + cbf_score * cbf_weight
    return sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)[:3]