from sqlalchemy.orm import Session

from app.loaders.facility_loader import FacilityLoader


class LoadFacilitiesCommand:

    def __init__(self, session: Session):

        self.loader = FacilityLoader(
            session
        )

    def execute(self):

        return self.loader.load(
            "data/processed/datacentermap/facilities_clean.json"
        )