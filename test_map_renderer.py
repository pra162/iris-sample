#!/usr/bin/env python
"""Test script for MapRenderer"""

from app.database.session import SessionLocal
from app.exporters.map_renderer import MapRenderer

# Get a facility ID from the database
session = SessionLocal()

try:
    # Get first facility
    from app.database.repositories.facility_repository import FacilityRepository
    repo = FacilityRepository(session)
    facilities = repo.get_all()
    
    if not facilities:
        print("No facilities found in database")
        exit(1)
    
    facility = facilities[0]
    print(f"Testing with facility: {facility.name} (ID: {facility.id})")
    print(f"Location: {facility.latitude}, {facility.longitude}")
    print(f"City: {facility.city}")
    
    # Create renderer and generate map
    renderer = MapRenderer(session)
    output_path = renderer.render_facility(facility.id, radius_km=10)
    
    print(f"\nMap generated successfully: {output_path}")
    
finally:
    session.close()
