from pathlib import Path

from app.database.session import SessionLocal
from app.loaders.facility_loader import FacilityLoader


def main():
    session = SessionLocal()

    try:
        loader = FacilityLoader(session)

        base_dir = Path(__file__).resolve().parents[2]

        file_path = (
            base_dir
            / "data"
            / "processed"
            / "datacentermap"
            / "facilities_clean.json"
        )

        print(f"Loading: {file_path}")
        print(f"Exists: {file_path.exists()}")

        result = loader.load(file_path)

        print(result)

    finally:
        session.close()


if __name__ == "__main__":
    main()