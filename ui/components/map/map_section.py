from streamlit_folium import st_folium
import folium

from ui.components.map.map_builder import create_base_map
from ui.components.map.transmission_layer import add_transmission_lines
from ui.components.map.substation_layer import add_substations
from ui.components.map.transformer_layer import add_transformers
from ui.components.map.facility_layer import add_facilities
from ui.components.map.energy_layer import add_energy_assets
import time

def render_map(
    facilities,
    energy_assets,
    substations,
    high_voltage_lines,
    transformers,
):

    start = time.perf_counter()
    m = create_base_map()
  
    start = time.perf_counter()
    add_transmission_lines(
        m,
        high_voltage_lines,
    )
  
    start = time.perf_counter()
    add_substations(
        m,
        substations,
    )
  
    start = time.perf_counter()
    add_transformers(
        m,
        transformers,
    )
  
    start = time.perf_counter()
    add_facilities(
        m,
        facilities,
    )
  
    add_energy_assets(
        m,
        energy_assets,
    )

    folium.LayerControl(
    collapsed=False,
).add_to(m)

    start = time.perf_counter()

    result = st_folium(
            m,
            width=None,
            height=500,
            use_container_width=True,
            returned_objects=[
                "last_object_clicked",
                "last_clicked",
            ],
            key="nrw-map",
        )

    print(
        f"st_folium: {time.perf_counter() - start:.3f}s"
    )

    return result