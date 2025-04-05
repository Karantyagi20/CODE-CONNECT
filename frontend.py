import streamlit as st
import mysql.connector

# Function to connect to MariaDB
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",       # Replace with your MariaDB host
            user="root",            # Replace with your MariaDB username
            password="password",    # Replace with your MariaDB password
            database="course_db"    # Replace with your database name
        )
        return connection
    except mysql.connector.Error as err:
        st.error(f"Error connecting to MariaDB: {err}")
        return None

# Function to create tables if they don't exist
def create_tables(connection):
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            course_code VARCHAR(50) NOT NULL,
            course_name VARCHAR(255) NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_courses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_name VARCHAR(255) NOT NULL,
            previous_courses TEXT NOT NULL
        )
    """)
    connection.commit()

# Function to insert course details into the database
def insert_course(connection, course_code, course_name):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO courses (course_code, course_name) VALUES (%s, %s)", (course_code, course_name))
    connection.commit()

# Function to insert user's previous courses into the database
def insert_user_courses(connection, user_name, previous_courses):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users_courses (user_name, previous_courses) VALUES (%s, %s)", (user_name, previous_courses))
    connection.commit()

# Recommendation logic (simple example)
def generate_recommendations(courses):
    # Example recommendation logic: Recommend advanced versions of the added courses
    recommendations = []
    for course in courses:
        if "101" in course["course_code"]:
            recommendations.append(course["course_code"].replace("101", "201"))
        else:
            recommendations.append(course["course_code"] + "-Advanced")
    return recommendations

# Main Streamlit app
def main():
    st.title("Course Management System")

    # Connect to MariaDB
    connection = connect_to_db()
    if connection:
        create_tables(connection)

    # Create tabs
    tab1, tab2 = st.tabs(["Add Course", "User Previous Courses"])

    with tab1:
        st.header("Add Multiple Courses")
        n = st.number_input("How many courses do you want to add?", min_value=1, max_value=10, value=1, step=1)
        courses = []

        for i in range(n):
            st.subheader(f"Course {i+1}")
            course_code = st.text_input(f"Enter Course Code for Course {i+1}:")
            course_name = st.text_input(f"Enter Course Name for Course {i+1}:")
            courses.append({"course_code": course_code, "course_name": course_name})

        if st.button("Submit Courses"):
            valid = True
            for course in courses:
                if not course["course_code"] or not course["course_name"]:
                    valid = False
                    break

            if valid:
                for course in courses:
                    insert_course(connection, course["course_code"], course["course_name"])
                
                # Generate recommendations
                recommendations = generate_recommendations(courses)
                st.session_state.recommendations = recommendations  # Store recommendations in session state
                
                # Display recommendations in a popup
                st.success("Courses added successfully!")
                st.info(f"Based on your input, we recommend the following courses: {', '.join(recommendations)}")
            else:
                st.error("Please fill in all fields for each course.")

    with tab2:
        st.header("Enter User's Previous Courses")
        user_name = st.text_input("Enter Your Name:")
        previous_courses = st.text_area("Enter Previous Courses (comma-separated):")

        if st.button("Submit User Data"):
            if user_name and previous_courses:
                # Add recommendations to previous courses if available
                if "recommendations" in st.session_state:
                    recommendations = st.session_state.recommendations
                    previous_courses += ", " + ", ".join(recommendations)
                    del st.session_state.recommendations  # Clear recommendations after use

                insert_user_courses(connection, user_name, previous_courses)
                st.success("User data added successfully!")
            else:
                st.error("Please fill in all fields.")

    # Close the database connection when done
    if connection:
        connection.close()

if __name__ == "_main_":
    main()