import networkx as nx
import osmnx as ox
import random
from matplotlib import pyplot as plt
import json
import re

def update_readme(location, current_time, image_path="map.png"):
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r"(<!-- START_SECTION:map -->)(.*?)(<!-- END_SECTION:map -->)"
    replacement = (
        r"### " + location + r"\n" +  
        r"Update time: " + current_time + r"  \n" +
        r"![location](" + image_path + r")\n\3"
)
    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(updated_content)

with open("locations.json", "r", encoding="utf-8") as f:
    locations = json.load(f)

category = random.choice(["universities", "museums", "art_galleries"])
place = random.choice(locations[category])
place_name = place["name"]
center_lat, center_lon = place["lat"], place["lon"]

location_text = f"{place_name}({center_lat}, {center_lon})"
current_time = ox.utils.ts()

distance = 1500

G = ox.graph_from_point((center_lat, center_lon), dist=distance, network_type='drive', truncate_by_edge=True)

if category == "universities":
    tags_related = {"amenity": "library", "building": "university"}
    related_label = "Libraries & Academic Buildings"
elif category == "museums":
    tags_related = {"tourism": "museum", "building": "civic"}
    related_label = "Museums & Civic Buildings"
else:
    tags_related = {"tourism": "gallery", "building": "arts_centre"}
    related_label = "Galleries & Arts Centers"

tags_buildings = {"building": True}
gdf_buildings = ox.features.features_from_point((center_lat, center_lon), tags_buildings, dist=distance)
gdf_related = ox.features.features_from_point((center_lat, center_lon), tags_related, dist=distance)

fig, ax = ox.plot.plot_graph(G, show=False, figsize=(10, 10), node_size=0, edge_color="#CCCCCC", edge_linewidth=0.5)
if not gdf_buildings.empty:
    ox.plot.plot_footprints(gdf_buildings, show=False,ax=ax, color='#999999', alpha=0.7)
if not gdf_related.empty:
    ox.plot.plot_footprints(gdf_related,show=False,ax=ax, color='#333333', alpha=0.9)
ax.set_facecolor('#E5E5E5')

plt.savefig("map.png", dpi=300, bbox_inches='tight')
plt.close()

update_readme(location_text, current_time)
