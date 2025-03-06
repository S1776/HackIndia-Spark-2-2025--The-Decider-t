import folium
from haversine import haversine
import webbrowser
import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
import matplotlib.pyplot as plt
from folium.plugins import AntPath, MarkerCluster

# Dictionary to map country names to airport coordinates
country_airports = {
    "USA": {"airport": "JFK", "lat": 40.6413, "lon": -73.7781},
    "India": {"airport": "DEL", "lat": 28.5562, "lon": 77.1000},
    "UK": {"airport": "LHR", "lat": 51.4700, "lon": -0.4543},
    "France": {"airport": "CDG", "lat": 49.0097, "lon": 2.5479},
    "Germany": {"airport": "FRA", "lat": 50.0379, "lon": 8.5622},
    "Japan": {"airport": "NRT", "lat": 35.7720, "lon": 140.3929},
    # Add more countries and their respective airport coordinates as needed
}

# Function to get user input for flight data
def get_flight_data():
    flights = []
    while True:
        src_country = input("Enter source country (or 'done' to finish): ")
        if src_country.lower() == 'done':
            break
        dst_country = input("Enter destination country: ")
        
        # Get coordinates from the dictionary
        if src_country in country_airports and dst_country in country_airports:
            source = country_airports[src_country]["airport"]
            destination = country_airports[dst_country]["airport"]
            src_lat = country_airports[src_country]["lat"]
            src_lon = country_airports[src_country]["lon"]
            dst_lat = country_airports[dst_country]["lat"]
            dst_lon = country_airports[dst_country]["lon"]
            speed_kmh = 900
            
            # Add intermediate airports (waypoints)
            waypoints = [
                {"airport": "FRA", "lat": 50.0379, "lon": 8.5622},  # Example waypoint
                {"airport": "CDG", "lat": 49.0097, "lon": 2.5479}   # Example waypoint
            ]
            
            flights.append({
                "source": source,
                "destination": destination,
                "src_lat": src_lat,
                "src_lon": src_lon,
                "dst_lat": dst_lat,
                "dst_lon": dst_lon,
                "speed_kmh": speed_kmh,
                "src_country": src_country,
                "dst_country": dst_country,
                "waypoints": waypoints
            })
        else:
            print("Invalid country name. Please try again.")
    return flights

# Get flight data from user
flights = get_flight_data()

# Create a map centered around the midpoint of the flights
m = folium.Map(location=[20, 0], zoom_start=2)

for flight in flights:
    # Calculate distance
    distance_km = haversine((flight["src_lat"], flight["src_lon"]), (flight["dst_lat"], flight["dst_lon"]))
    flight_time = distance_km / flight["speed_kmh"]  # Time in hours

    # Add markers for source and destination
    folium.Marker(
        location=[flight["src_lat"], flight["src_lon"]],
        popup=f"{flight['source']} ({flight['src_country']})",
        icon=folium.Icon(color="red", icon="plane", prefix="fa")
    ).add_to(m)
    folium.Marker(
        location=[flight["dst_lat"], flight["dst_lon"]],
        popup=f"{flight['destination']} ({flight['dst_country']})",
        icon=folium.Icon(color="red", icon="plane", prefix="fa")
    ).add_to(m)

    # Add markers for waypoints
    for waypoint in flight["waypoints"]:
        folium.Marker(
            location=[waypoint["lat"], waypoint["lon"]],
            popup=f"{waypoint['airport']}",
            icon=folium.Icon(color="green", icon="plane", prefix="fa")
        ).add_to(m)

    # Draw animated flight path including waypoints
    path = [(flight["src_lat"], flight["src_lon"])]
    path.extend([(wp["lat"], wp["lon"]) for wp in flight["waypoints"]])
    path.append((flight["dst_lat"], flight["dst_lon"]))
    
    AntPath(
        locations=path,
        color="black",
        weight=2.5,
        opacity=1
    ).add_to(m)

    # Add a moving flight marker
    flight_marker = folium.Marker(
        location=[flight["src_lat"], flight["src_lon"]],
        icon=folium.Icon(color="blue", icon="plane", prefix="fa")
    )
    flight_marker.add_to(m)

    # Display flight info
    print(f"Flight: {flight['source']} ({flight['src_country']}) → {flight['destination']} ({flight['dst_country']}), Distance: {distance_km:.2f} km, Time: {flight_time:.2f} hrs")

# Save the map to an HTML file
map_file = "flight_routes.html"
m.save(map_file)

# Open the map in a web browser
webbrowser.open(f"http://localhost:8000/{map_file}")

# Serve the HTML file using a local server
os.chdir(os.path.dirname(os.path.abspath(map_file)))
httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
print("Serving at port 8000")
httpd.serve_forever()

# Graph Visualization using matplotlib
fig, ax = plt.subplots(figsize=(8, 6))

for flight in flights:
    # Calculate distance
    distance_km = haversine((flight["src_lat"], flight["src_lon"]), (flight["dst_lat"], flight["dst_lon"]))
    flight_time = distance_km / flight["speed_kmh"]  # Time in hours

    # Scatter plot for source & destination
    ax.scatter(flight["src_lon"], flight["src_lat"], color="red", label=f"Source: {flight['source']} ({flight['src_country']})")
    ax.scatter(flight["dst_lon"], flight["dst_lat"], color="red", label=f"Destination: {flight['destination']} ({flight['dst_country']})")

    # Annotate airport names with country names and flight time
    ax.text(flight["src_lon"], flight["src_lat"], f"{flight['source']} ({flight['src_country']})", fontsize=12, verticalalignment="bottom", color="red")
    ax.text(flight["dst_lon"], flight["dst_lat"], f"{flight['destination']} ({flight['dst_country']})", fontsize=12, verticalalignment="bottom", color="red")
    ax.text((flight["src_lon"] + flight["dst_lon"]) / 2, (flight["src_lat"] + flight["dst_lat"]) / 2, f"Time: {flight_time:.2f} hrs", fontsize=10, verticalalignment="bottom", color="green")

    # Draw flight path including waypoints
    path = [(flight["src_lon"], flight["src_lat"])]
    path.extend([(wp["lon"], wp["lat"]) for wp in flight["waypoints"]])
    path.append((flight["dst_lon"], flight["dst_lat"]))
    
    ax.plot([p[0] for p in path], [p[1] for p in path], linestyle="--", color="black")

# Labels & Title
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title("Simulated Flight Routes")
plt.grid()
plt.show()