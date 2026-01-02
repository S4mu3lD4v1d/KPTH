from flask import Flask, request, jsonify
import folium
import geopandas as gpd
import os

app = Flask(__name__)

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json  # Assume geo data
    gdf = gpd.GeoDataFrame.from_features(data['features'])
    # Simple analysis
    area = gdf.area.sum()
    # Create map
    m = folium.Map()
    folium.GeoJson(gdf).add_to(m)
    m.save('map.html')
    # Export to institutions (placeholder)
    # requests.post('https://research.facility/api', json=data)
    return jsonify({'area': area, 'map': 'map.html'})

if __name__ == '__main__':
    app.run(debug=True, port=5002)