from flask import Flask, request, jsonify
from database import connect_to_db, fetch_student_courses, store_student_preferences, fetch_course_metadata
from recommendation import generate_recommendations

app = Flask(_name_)

# Endpoint 1: Fetch Academic History
@app.route('/api/student/<int:student_id>/history', methods=['GET'])
def get_academic_history(student_id):
    try:
        courses = fetch_student_courses(student_id)
        return jsonify({"student_id": student_id, "courses": courses})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint 2: Save Student Preferences
@app.route('/api/student/<int:student_id>/preferences', methods=['POST'])
def save_preferences(student_id):
    data = request.get_json()
    keywords = data.get("keywords", "").strip()

    if not keywords:
        return jsonify({"error": "Keywords are required"}), 400

    try:
        store_student_preferences(student_id, keywords)
        return jsonify({"message": "Preferences saved successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint 3: Get Course Recommendations
@app.route('/api/student/<int:student_id>/recommendations', methods=['GET'])
def get_recommendations(student_id):
    try:
        # Fetch stored preferences
        connection = connect_to_db()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT keywords FROM student_preferences WHERE student_id = %s"
        cursor.execute(query, (student_id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        if not result:
            return jsonify({"error": "No preferences found. Please save preferences first."}), 404

        student_keywords = result['keywords']
        course_data = fetch_course_metadata()
        courses = [row['course_id'] for row in course_data]

        # Generate recommendations
        recommendations = generate_recommendations(student_id, student_keywords, courses)
        return jsonify({"student_id": student_id, "recommendations": recommendations})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if _name_ == '_main_':
    app.run(debug=True)