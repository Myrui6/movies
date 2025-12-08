import mysql.connector
import random
from datetime import datetime, timedelta


def generate_test_data():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='movies'
    )
    cursor = conn.cursor()

    print("Generating users...")
    for i in range(1, 101):
        cursor.execute("INSERT INTO user (name, password) VALUES (%s, %s)",
                       (f"user_{i}", f"pass_{i}"))

    print("Generating administrators...")
    for i in range(1, 11):
        cursor.execute("INSERT INTO administrator (name, password) VALUES (%s, %s)",
                       (f"admin_{i}", f"admin_pass_{i}"))

    print("Generating movies...")
    movies_data = [
        ("Avengers: Endgame", "Action", "USA", 181, "Superhero movie"),
        ("The Lion King", "Animation", "USA", 118, "Disney classic"),
        ("Inception", "Sci-Fi", "USA", 148, "Dream within a dream"),
        ("Titanic", "Romance", "USA", 195, "Love story on ship"),
        ("Spirited Away", "Animation", "Japan", 125, "Studio Ghibli"),
        ("The Dark Knight", "Action", "USA", 152, "Batman movie"),
        ("Parasite", "Drama", "Korea", 132, "Oscar winner"),
        ("La La Land", "Musical", "USA", 128, "Musical romance"),
        ("Interstellar", "Sci-Fi", "USA", 169, "Space adventure"),
        ("Coco", "Animation", "USA", 105, "Pixar animation")
    ]

    for movie in movies_data:
        cursor.execute("INSERT INTO movie (name, type, region, time, brief) VALUES (%s, %s, %s, %s, %s)", movie)

    print("Generating halls...")
    halls_data = [
        ("Hall A", 10, 15),
        ("Hall B", 8, 12),
        ("Hall C", 12, 20),
        ("Hall D", 6, 10),
        ("Hall E", 15, 25),
        ("Hall F", 10, 18)
    ]

    for hall in halls_data:
        cursor.execute("INSERT INTO hall (name, total_rows, total_columns) VALUES (%s, %s, %s)", hall)

    conn.commit()

    print("Generating schedules...")
    cursor.execute("SELECT id FROM movie")
    movie_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT id FROM hall")
    hall_ids = [row[0] for row in cursor.fetchall()]

    start_date = datetime.now()
    for i in range(100):
        movie_id = random.choice(movie_ids)
        hall_id = random.choice(hall_ids)
        start_time = start_date + timedelta(hours=i * 2)
        price = random.choice([35.00, 45.00, 55.00, 65.00, 75.00])

        cursor.execute("""
                       INSERT INTO schedule (movie_id, hall_id, start_time, price)
                       VALUES (%s, %s, %s, %s)
                       """, (movie_id, hall_id, start_time, price))

    conn.commit()

    print("Generating seats...")
    cursor.execute("SELECT s.id, h.total_rows, h.total_columns FROM schedule s JOIN hall h ON s.hall_id = h.id")
    schedules = cursor.fetchall()

    for schedule_id, total_rows, total_columns in schedules:
        for row in range(1, total_rows + 1):
            for col in range(1, total_columns + 1):
                state = random.choice([0, 0, 0, 1])
                cursor.execute("""
                               INSERT INTO seat (schedule_id, row_num, col_num, state)
                               VALUES (%s, %s, %s, %s)
                               """, (schedule_id, row, col, state))

    conn.commit()

    print("Generating orders...")
    cursor.execute("SELECT id FROM user")
    user_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT s.id, h.total_rows, h.total_columns FROM schedule s JOIN hall h ON s.hall_id = h.id")
    schedule_seats = cursor.fetchall()

    for i in range(300):
        user_id = random.choice(user_ids)
        schedule_id, total_rows, total_columns = random.choice(schedule_seats)

        seat_count = random.randint(1, 4)
        seats = []

        for _ in range(seat_count):
            row = random.randint(1, total_rows)
            col = random.randint(1, total_columns)
            seats.append(f"Row {row} Seat {col}")

        seat_details = ", ".join(seats)
        total_price = seat_count * 45.00
        state = random.choice([0, 1, 2])
        reason = "Test reason" if state == 1 else None

        cursor.execute("""
                       INSERT INTO `order` (user_id, schedule_id, seat_details, total_price, state, reason)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       """, (user_id, schedule_id, seat_details, total_price, state, reason))

    conn.commit()

    print("Test data generation completed!")
    cursor.close()
    conn.close()


if __name__ == "__main__":
    generate_test_data()