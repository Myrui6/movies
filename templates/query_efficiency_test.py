import time
import mysql.connector
from mysql.connector import Error


class QueryEfficiencyTest:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root',
                database='movies'
            )
            print("Database connected successfully")
        except Error as e:
            print(f"Connection error: {e}")

    def test_query_1(self):
        cursor = self.connection.cursor()

        start_time = time.time()

        cursor.execute("""
                       SELECT row_num, col_num, state
                       FROM seat
                       WHERE schedule_id = 1
                       ORDER BY row_num, col_num
                       """)

        results = cursor.fetchall()
        end_time = time.time()

        cursor.close()

        print(f"Test 1 - Seat query: {len(results)} rows, Time: {(end_time - start_time) * 1000:.2f}ms")
        return end_time - start_time

    def test_query_2(self):
        cursor = self.connection.cursor()

        start_time = time.time()

        cursor.execute("""
                       SELECT o.id, m.name, s.start_time, h.name, o.seat_details, o.total_price
                       FROM `order` o
                                JOIN schedule s ON o.schedule_id = s.id
                                JOIN movie m ON s.movie_id = m.id
                                JOIN hall h ON s.hall_id = h.id
                       WHERE o.user_id = 1
                       ORDER BY s.start_time DESC
                       """)

        results = cursor.fetchall()
        end_time = time.time()

        cursor.close()

        print(f"Test 2 - User orders: {len(results)} rows, Time: {(end_time - start_time) * 1000:.2f}ms")
        return end_time - start_time

    def test_query_3(self):
        cursor = self.connection.cursor()

        start_time = time.time()

        cursor.execute("""
                       SELECT s.id, m.name, s.start_time, h.name, s.price
                       FROM schedule s
                                JOIN movie m ON s.movie_id = m.id
                                JOIN hall h ON s.hall_id = h.id
                       WHERE m.name LIKE '%Avengers%'
                         AND s.start_time > NOW()
                       ORDER BY s.start_time LIMIT 10
                       """)

        results = cursor.fetchall()
        end_time = time.time()

        cursor.close()

        print(f"Test 3 - Schedule search: {len(results)} rows, Time: {(end_time - start_time) * 1000:.2f}ms")
        return end_time - start_time

    def test_query_4(self):
        cursor = self.connection.cursor()

        start_time = time.time()

        try:
            cursor.execute("START TRANSACTION")

            cursor.execute("""
                           SELECT row_num, col_num, state
                           FROM seat
                           WHERE schedule_id = 1
                             AND row_num IN (1, 2)
                             AND col_num IN (1, 2)
                               FOR UPDATE
                           """)

            seats = cursor.fetchall()

            for seat in seats:
                if seat[2] == 0:
                    cursor.execute("""
                                   UPDATE seat
                                   SET state = 1
                                   WHERE schedule_id = 1
                                     AND row_num = %s
                                     AND col_num = %s
                                   """, (seat[0], seat[1]))

            cursor.execute("""
                           INSERT INTO `order` (user_id, schedule_id, seat_details, total_price, state)
                           VALUES (1, 1, 'Row 1 Seat 1, Row 1 Seat 2', 100.00, 0)
                           """)

            cursor.execute("COMMIT")

        except Exception as e:
            cursor.execute("ROLLBACK")
            print(f"Transaction failed: {e}")

        end_time = time.time()
        cursor.close()

        print(f"Test 4 - Purchase transaction: Time: {(end_time - start_time) * 1000:.2f}ms")
        return end_time - start_time

    def test_query_5(self):
        cursor = self.connection.cursor()

        start_time = time.time()

        cursor.execute("""
                       SELECT o.id, u.name, m.name, s.start_time, o.total_price
                       FROM `order` o
                                JOIN user u ON o.user_id = u.id
                                JOIN schedule s ON o.schedule_id = s.id
                                JOIN movie m ON s.movie_id = m.id
                       ORDER BY s.start_time DESC LIMIT 20
                       OFFSET 0
                       """)

        results = cursor.fetchall()
        end_time = time.time()

        cursor.close()

        print(f"Test 5 - Pagination query: {len(results)} rows, Time: {(end_time - start_time) * 1000:.2f}ms")
        return end_time - start_time

    def test_explain_plan(self):
        print("\n=== EXPLAIN Query Plans ===")
        queries = [
            ("Seat query", "EXPLAIN SELECT * FROM seat WHERE schedule_id = 1 AND state = 0"),
            ("Order query", "EXPLAIN SELECT * FROM `order` WHERE user_id = 1"),
            ("Schedule query", "EXPLAIN SELECT * FROM schedule WHERE movie_id = 1 AND start_time > NOW()"),
            ("Join query",
             "EXPLAIN SELECT o.id, m.name FROM `order` o JOIN schedule s ON o.schedule_id = s.id JOIN movie m ON s.movie_id = m.id WHERE o.user_id = 1")
        ]

        cursor = self.connection.cursor()

        for query_name, explain_query in queries:
            print(f"\n{query_name}:")
            cursor.execute(explain_query)
            plan = cursor.fetchall()
            for row in plan:
                print(f"  {row}")

        cursor.close()

    def run_all_tests(self):
        print("=== Starting Query Efficiency Tests ===\n")

        times = []

        times.append(self.test_query_1())
        times.append(self.test_query_2())
        times.append(self.test_query_3())
        times.append(self.test_query_4())
        times.append(self.test_query_5())

        self.test_explain_plan()

        avg_time = sum(times) / len(times) * 1000
        print(f"\n=== Tests Completed ===")
        print(f"Average query time: {avg_time:.2f}ms")
        print(f"Total test time: {sum(times):.3f} seconds")

    def close(self):
        if self.connection:
            self.connection.close()


if __name__ == "__main__":
    tester = QueryEfficiencyTest()
    tester.run_all_tests()
    tester.close()