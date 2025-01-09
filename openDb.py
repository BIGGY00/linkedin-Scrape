import sqlite3

def count_job_rows():
    conn = sqlite3.connect('job_details.db')
    cursor = conn.cursor()

    # Count the number of rows in the "jobs" table
    cursor.execute("SELECT COUNT(*) FROM jobs")
    row_count = cursor.fetchone()[0]  # Fetch the count result

    print(f"Total number of rows in the 'jobs' table: {row_count}")
    
    conn.close()

if __name__ == "__main__":
    count_job_rows()
