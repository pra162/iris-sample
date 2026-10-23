from app.database.session import SessionLocal
from sqlalchemy import text


def main():
    session = SessionLocal()

    try:
        query = text(
            """
            SELECT
                voltage,
                COUNT(id) AS count
            FROM iris_core.power_infrastructure
            WHERE power_type = 'line'
              AND voltage IS NOT NULL
            GROUP BY voltage
            ORDER BY COUNT(id) DESC
            """
        )

        rows = session.execute(query)

        print()
        print("=" * 60)
        print("POWER LINE VOLTAGE LEVELS")
        print("=" * 60)

        for voltage, count in rows:
            print(f"{voltage:30} => {count:,}")

        print("=" * 60)

    finally:
        session.close()


if __name__ == "__main__":
    main()