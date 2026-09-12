import networkx as nx
import osmnx as ox
import random
from matplotlib import pyplot as plt
import json
import re
import logging


ox.settings.use_cache = False
logging.basicConfig(level=logging.INFO)  
logger = logging.getLogger("osmnx")  

def update_readme(location, current_time, image_path="map.png"):
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()
    

    content = content.rstrip('\x03')
    
    pattern = r"(<!-- START_SECTION:map -->).*?(<!-- END_SECTION:map -->)"
    replacement = (
        f"<!-- START_SECTION:map -->\n"
        f"### {location}\n"
        f"<!--START_SETCTION:temp-->\n"
        f"![temp](images/demo.gif)\n"
        f"<!--END:SETCTION:temp-->\n"
        f"![location]({image_path})\n"
        f"Update time: {current_time}(UTC) [^1] \n"
        f"<!-- END_SECTION:map -->"
    )
    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    if content == updated_content:
        logger.warning("README content was not changed")
    else:
        logger.info("README content was successfully updated")
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(updated_content)


with open("locations.json", "r", encoding="utf-8") as f:
    locations = json.load(f)

distance = 1000

def try_generate_map(locations, distance):
    while True:  
        
        category = random.choice(["universities", "museums", "art_galleries"])
        place = random.choice(locations[category])
        place_name = place["name"]
        center_lat, center_lon = place["lat"], place["lon"]
        location_text = f"{place_name}({center_lat}, {center_lon})"
        current_time = ox.utils.ts()

        logger.info(f"Trying: {location_text}, Category: {category}")

        
        try:
            G = ox.graph_from_point((center_lat, center_lon), dist=distance, network_type='drive', truncate_by_edge=True)
            logger.info(f"Graph loaded: {len(G.nodes)} nodes, {len(G.edges)} edges")
        except Exception as e:
            logger.error(f"Failed to load graph: {e}")
            continue  

        
        if category == "universities":
            tags_related = {"amenity": ["library", "university"], "building": True}
        elif category == "museums":
            tags_related = {"tourism": "museum", "building": True}
        else:
            tags_related = {"tourism": "gallery", "building": True}
        tags_buildings = {"building": True}

        logger.info(f"Related tags: {tags_related}")

        
        try:
            gdf_buildings = ox.features.features_from_point((center_lat, center_lon), tags_buildings, dist=distance)
            logger.info(f"Buildings found: {len(gdf_buildings)}")
        except Exception as e:
            logger.error(f"Failed to load buildings: {e}")
            continue  

        try:
            gdf_related = ox.features.features_from_point((center_lat, center_lon), tags_related, dist=distance)
            logger.info(f"Related features found: {len(gdf_related)}")
        except Exception as e:
            logger.error(f"Failed to load related features: {e}")
            continue  

        
        try:
            fig, ax = ox.plot.plot_graph(G, show=False, figsize=(10, 10), node_size=0, edge_color="#CCCCCC", edge_linewidth=0.5)
            if gdf_buildings is not None and not gdf_buildings.empty:
                ox.plot.plot_footprints(gdf_buildings, show=False, ax=ax, color='#999999', alpha=0.7)
            if gdf_related is not None and not gdf_related.empty:
                ox.plot.plot_footprints(gdf_related, show=False, ax=ax, color='#333333', alpha=0.9)
            #ax.set_facecolor('#E5E5E5')
            plt.savefig("map.png", dpi=300, bbox_inches='tight')
            plt.close()
            logger.info("Map generated successfully!")
            return location_text, current_time  
        except Exception as e:
            logger.error(f"Failed to generate map: {e}")
            continue  


location_text, current_time = try_generate_map(locations, distance)
update_readme(location_text, current_time)
logger.info(f"README updated with {location_text}")