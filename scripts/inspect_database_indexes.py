from app.database.session import SessionLocal
from sqlalchemy import inspect


def main():
    session = SessionLocal()

    try:
        inspector = inspect(session.bind)

        tables = inspector.get_table_names(
            schema="iris_core"
        )

        print("================================")
        print("INDEXES")
        print("================================")

        for table in tables:
            print()
            print(f"[{table}]")

            indexes = inspector.get_indexes(
                table,
                schema="iris_core",
            )

            if not indexes:
                print("  No indexes")
                continue

            for index in indexes:
                print(
                    f"  {index['name']} "
                    f"| columns={index['column_names']} "
                    f"| unique={index['unique']}"
                )

    finally:
        session.close()


if __name__ == "__main__":
    main()