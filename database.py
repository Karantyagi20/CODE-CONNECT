import mysql.connector

def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Am5500207@",
            database="coursemetadata"
        )
        return connection
    except mysql.connector.Error as err:
        raise Exception(f"Database connection failed: {err}")

# Fetch student's past courses and grades
def fetch_student_courses(student_id):
    connection = connect_to_db()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT course_id, grade FROM student_courses WHERE student_id = %s"
        cursor.execute(query, (student_id,))
        data = cursor.fetchall()
        return data
    finally:
        cursor.close()
        connection.close()

# Fetch user-course interaction data for Collaborative Filtering
def fetch_user_course_data():
    connection = connect_to_db()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT student_id, course_id, grade FROM student_courses"
        cursor.execute(query)
        data = cursor.fetchall()
        return data
    finally:
        cursor.close()
        connection.close()

# Save student preferences
def store_student_preferences(student_id, keywords):
    connection = connect_to_db()
    try:
        cursor = connection.cursor()
        query = "INSERT INTO student_preferences (student_id, keywords) VALUES (%s, %s)"
        cursor.execute(query, (student_id, keywords))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

# Fetch course metadata for Content-Based Filtering
def fetch_course_metadata():
    connection = connect_to_db()
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT course_id, keywords FROM courses"
        cursor.execute(query)
        data = cursor.fetchall()
        return data
    finally:
        cursor.close()
        connection.close()
