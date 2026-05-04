let map;
let markers = [];
let start = null;
let end = null;
let currentPolyline = null;

function openMap() {
    const container = document.getElementById("map-container");
    container.style.display = "block";

    if (!map) {
        map = L.map('map').setView([45.5, -73.56], 10); // Montreal

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap'
        }).addTo(map);

        map.on('click', (e) => onMapClick(e));
    }
}
function onMapClick(e) {
    // Reset si déjà 2 points
    if (markers.length >= 2) {
            markers.forEach(m => map.removeLayer(m));
            markers = [];
            start = null;
            end = null;
    }
            const marker = L.marker(e.latlng).addTo(map);
    markers.push(marker);

    if (!start) {
        start = e.latlng;
        document.getElementById("coords").innerText =
            `Départ: ${start.lat.toFixed(5)}, ${start.lng.toFixed(5)}`;
    } else {
        end = e.latlng;
        document.getElementById("coords").innerText =
            `Départ: ${start.lat.toFixed(5)}, ${start.lng.toFixed(5)}
            Arrivée: ${end.lat.toFixed(5)}, ${end.lng.toFixed(5)}`;
    }
        }

function confirmMap() {
    if (!start || !end) {
        alert("Choisis un point de depart ET d'arrivee !");
        return;
    }

    document.getElementById("start_lat").value = start.lat;
    document.getElementById("start_lng").value = start.lng;
    document.getElementById("end_lat").value = end.lat;
    document.getElementById("end_lng").value = end.lng;

    // Affiche la route automatiquement après confirmation
    displayRoute();
}

async function displayRoute() {
    if (!start || !end) {
        alert("Choisis un point de depart ET d'arrivee !");
        return;
    }
    
    console.log("Affichage de la route...");
    console.log(`Start: ${start.lat}, ${start.lng}`);
    console.log(`End: ${end.lat}, ${end.lng}`);

    try {
        
        const response = await fetch('http://127.0.0.1:8000/route', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                start_lat: start.lat,
                start_lng: start.lng,
                end_lat: end.lat,
                end_lng: end.lng
            })
        });

        if (!response.ok) {
            console.error(`Erreur HTTP: ${response.status} ${response.statusText}`);
            return;
        }

        const data = await response.json();
        console.log("Données reçues:", data);
        
        // Extract route coordinates
        const routeCoords = data.route.map(coord => [coord[0], coord[1]]);
        console.log("Coordonnées de la route:", routeCoords);
        
        // Remove previous route if it exists
        if (currentPolyline) {
            map.removeLayer(currentPolyline);
            console.log("Ancienne route supprimée");
        }
        
        // Draw the route on the map as a polyline
        currentPolyline = L.polyline(routeCoords, {
            color: 'blue',
            weight: 4,
            opacity: 0.7
        }).addTo(map);
        
        console.log("Polyline ajoutée à la carte");

        // Show distance and duration
        const distance = data.distance.toFixed(2);
        const duration = data.duration.toFixed(2);
        console.log(`Distance: ${distance} km`);
        console.log(`Duration: ${duration} minutes`);
        
        // Display route info on the page
        document.getElementById('route-distance').textContent = distance;
        document.getElementById('route-duration').textContent = duration;
        document.getElementById('route-info').style.display = 'block';
        
        // Optional: fit map to route bounds
        const group = new L.featureGroup([currentPolyline]);
        map.fitBounds(group.getBounds());
        
    } catch (error) {
        console.error("Erreur lors de la récupération du trajet:", error);
    }
}


async function fetchCarInfo() {
    try {
        const response = await fetch('static/car_info.csv');
        const csvString = await response.text();
        const result = Papa.parse(csvString);
        return result.data;
    } catch (error) {
        console.error("Erreur de fetch:", error);
    }
}

function getBrands(data){
    console.log("brands: ")
    const brandsSet = new Set();
    data.forEach((model) => {
        const brandName = model[0];
        brandsSet.add(brandName);
    })
    console.log(brandsSet);
    return brandsSet;
}

async function init() {
    const data = await fetchCarInfo();
    console.log(data);
    brandSet = getBrands(data)
    const brandList = document.getElementById('marque-list');
    brandList.innerHTML = "";
    let selectedModel = null;

    // Populate the brand list with options
    brandSet.forEach((brandName) => {
        const newOption = new Option(brandName,brandName);
        brandList.add(newOption);
    })

    // Add an event listener to the brand list to update the model list when a brand is selected
    const modelList = document.getElementById('modele-list');
    brandList.addEventListener('change', (event) => {
        const selectedBrand = event.target.value;
        console.log(`Selected brand: ${selectedBrand}`);
        // Update the model list based on the selected brand
        modelList.innerHTML = ''; 
        modelList.add(new Option("Select a model", ""));       
        data.forEach((model) => {
            if(selectedBrand === model[0]){
                const newOption = new Option(model[1],model[1]);
                modelList.add(newOption);
            }
        })
    });

    modelList.addEventListener('change', (event) => {
        let selectedModelName = event.target.value;
        console.log(`Selected model: ${selectedModelName}`);
        data.forEach((model) => {
            if(selectedModelName === model[1]){
                selectedModel = model;
                console.log(`Selected model info: ${selectedModel}`);
            }
        });
    });

    console.log("working");
}
init();

// METEO PART
// - get localisation
const x = document.getElementById("demo");

function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(success, error);
  } else {
    x.innerHTML = "Geolocation is not supported by this browser.";
  }
}

function success(position) {
  x.innerHTML = "Latitude: " + position.coords.latitude +
  "<br>Longitude: " + position.coords.longitude;
  fetchMeteo(position);
}

function error() {
  alert("Sorry, no position available.");
}

//- api call with open-meteo
// ex:https://api.open-meteo.com/v1/forecast?latitude=45.53670606232232&longitude=-73.67448869055289&hourly=temperature_2m&current=temperature_2m&start_date=2026-03-23&end_date=2026-03-23

function fetchMeteo(position){
    const apiUrl = `https://api.open-meteo.com/v1/forecast?latitude=${position.coords.latitude}&longitude=${position.coords.longitude}&hourly=temperature_2m`;

    fetch(apiUrl)
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        console.log('Weather data:', data);
        const hourly_data = data.hourly;
        const data_time = hourly_data.time;
        const data_temperature = hourly_data.temperature_2m;
        console.log(data_time);
        console.log(data_temperature);
      })
      .catch(error => {
        console.error('There has been a problem with your fetch operation:', error);
      });
}

// --host 0.0.0.0 --port 8080