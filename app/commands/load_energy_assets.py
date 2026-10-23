from pathlib import Path

from app.database.session import SessionLocal
from app.loaders.energy_asset_loader import EnergyAssetLoader


def main():

    session = SessionLocal()

    try:

        loader = EnergyAssetLoader(session)

        file_path = (
            Path(__file__)
            .resolve()
            .parent.parent.parent
            / "data"
            / "processed"
            / "mastr"
            / "power_generation.json"
        )

        print(f"Loading: {file_path}")
        print(f"Exists: {file_path.exists()}")

        result = loader.load(file_path)

        print(result)

    finally:
        session.close()


if __name__ == "__main__":
    main()