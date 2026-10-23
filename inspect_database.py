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
        print("TABLES")
        print("================================")

        for table in tables:
            print(table)

        print()
        print("================================")
        print("COLUMNS")
        print("================================")

        for table in tables:
            print()
            print(f"[{table}]")

            columns = inspector.get_columns(
                table,
                schema="iris_core",
            )

            for column in columns:
                print(
                    f"  {column['name']} "
                    f"| {column['type']} "
                    f"| nullable={column['nullable']}"
                )

    finally:
        session.close()


if __name__ == "__main__":
    main()