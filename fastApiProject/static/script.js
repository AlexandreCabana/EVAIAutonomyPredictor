let map;
let markers = [];
let start = null;
let end = null;
let currentPolyline = null;
let geocoderControl = null;
let currentMeteoMode = "manuel";
let meteoData = null;

function openMap() {
    const container = document.getElementById("map-container");
    container.style.display = "inline";

    if (!map) {
        //centered to mtl
        map = L.map("map").setView([45.5, -73.56], 10);
        //creates map
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "© OpenStreetMap"
        }).addTo(map);

        //Search bar
        if (L.Control.Geocoder) {
            geocoderControl = L.Control.geocoder({
                collapsed: false,
                defaultMarkGeocode: false,
                placeholder: "Search an address"
            })
                //creates and displays searched marker
                .on("markgeocode", (e) => {
                    const center = e.geocode.center;
                    map.fitBounds(e.geocode.bbox);
                    addPoint(center);
                })
                .addTo(map);
        }

        map.on("click", (e) => addPoint(e.latlng)); //adds marker on click
    }
}

function addPoint(latlng) {
    if (markers.length >= 2) {
        markers.forEach((m) => map.removeLayer(m));
        markers = [];
        start = null;
        end = null;
    }

    const marker = L.marker(latlng).addTo(map);
    markers.push(marker);

    if (!start) {
        start = latlng;
        document.getElementById("coords").innerText =
            `Depart: ${start.lat.toFixed(5)}, ${start.lng.toFixed(5)}`;
    } else {
        end = latlng;
        document.getElementById("coords").innerText =
            `Depart: ${start.lat.toFixed(5)}, ${start.lng.toFixed(5)}\nArrivee: ${end.lat.toFixed(5)}, ${end.lng.toFixed(5)}`;
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

    fetchMeteoForPoint(start.lat, start.lng);
    updateMeteoInfo();

    displayRoute();
}

async function fetchMeteoForPoint(lat, lon, date = null, heure = null) {
    try {
        const response = await fetch("http://127.0.0.1:8000/meteo", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                lat: lat,
                lon: lon,
                date: date,
                heure: heure
            })
        });

        if (!response.ok) {
            console.error(`Erreur HTTP meteo: ${response.status} ${response.statusText}`);
            return;
        }

        meteoData = await response.json();
        console.log("Donnees meteo recues:", meteoData);
    } catch (error) {
        console.error("Erreur lors de la recuperation de la meteo:", error);
    }
}
function updateMeteoInfo(){
    try{
        const temperatureInput = document.getElementById("temperature");
        if(currentMeteoMode === "auto"){
            if (temperatureInput && meteoData.temperature !== undefined && meteoData.temperature !== null) {
                temperatureInput.value = meteoData.temperature;
            }
        }

        if (meteoData.meteo) {
            //va chercher le type de meteo
            const meteoRadio = document.querySelector(`input[name="meteo"][value="${meteoData.meteo}"]`);
            if (meteoRadio) {
                meteoRadio.checked = true;
            }
        }
    } catch (error) {
        console.error("Erreur lors de la recuperation de la meteo:", error);
    }
    console.log("update meteo info");
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
        const response = await fetch("http://127.0.0.1:8000/route", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                start_lat: start.lat,
                start_lon: start.lng,
                end_lat: end.lat,
                end_lon: end.lng
            })
        });

        if (!response.ok) {
            console.error(`Erreur HTTP: ${response.status} ${response.statusText}`);
            return;
        }

        const route_data = await response.json();
        console.log("Donnees recues:", route_data);

        const routeCoords = route_data.route;

        if (currentPolyline) {
            map.removeLayer(currentPolyline);
        }

        //trace une ligne à travers tous les points
        currentPolyline = L.polyline(routeCoords, {
            color: "blue",
            weight: 4,
            opacity: 0.7
        }).addTo(map);

        const distance = route_data.distance.toFixed(2);
        const duration = route_data.duration !== null && route_data.duration !== undefined ? route_data.duration.toFixed(2) : "0";
        const baseDuration = route_data.base_duration !== null && route_data.base_duration !== undefined
            ? route_data.base_duration.toFixed(2)
            : duration;
        const computedTrafficDelay =
            route_data.traffic_delay !== null && route_data.traffic_delay !== undefined
                ? route_data.traffic_delay
                : ((route_data.duration ?? 0) - (route_data.base_duration ?? 0));
        const trafficDelay = computedTrafficDelay.toFixed(2);
        const provider = route_data.provider || "osrm";

        document.getElementById("route-distance").textContent = distance;
        document.getElementById("route-duration").textContent = duration;
        document.getElementById("route-base-duration").textContent = baseDuration;
        document.getElementById("route-traffic-delay").textContent = trafficDelay;
        document.getElementById("route-provider").textContent = provider;
        document.getElementById("duration").value = duration;
        document.getElementById("route-info").style.display = "block";

        const group = new L.featureGroup([currentPolyline]);
        map.fitBounds(group.getBounds());
    } catch (error) {
        console.error("Erreur lors de la recuperation du trajet:", error);
    }
}

async function fetchCarInfo() {
    try {
        const response = await fetch("static/car_info.csv");
        const csvString = await response.text();
        const result = Papa.parse(csvString);
        return result.data;
    } catch (error) {
        console.error("Erreur de fetch:", error);
    }
}

function getBrands(data) {
    const brandsSet = new Set();
    data.forEach((model) => {
        const brandName = model[0];
        brandsSet.add(brandName);
    });
    return brandsSet;
}

async function init() {
    const data = await fetchCarInfo();
    const brandList = document.getElementById("marque-list");
    const modelList = document.getElementById("modele-list");
    if (!brandList || !modelList || !data) {
        return;
    }

    const brandSet = getBrands(data);

    let selectedModel = null;

    brandSet.forEach((brandName) => {
        const newOption = new Option(brandName, brandName);
        brandList.add(newOption);
    });

    brandList.addEventListener("change", (event) => {
        const selectedBrand = event.target.value;
        modelList.innerHTML = "";
        modelList.add(new Option("Select a model", ""));
        data.forEach((model) => {
            if (selectedBrand === model[0]) {
                const newOption = new Option(model[1], model[1]);
                modelList.add(newOption);
            }
        });
    });

    modelList.addEventListener("change", (event) => {
        const selectedModelName = event.target.value;
        data.forEach((model) => {
            if (selectedModelName === model[1]) {
                selectedModel = model;
                console.log(`Selected model info: ${selectedModel}`);
            }
        });
    });
}

const x = document.getElementById("demo");

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(success, error);
    } else if (x) {
        x.innerHTML = "Geolocation is not supported by this browser.";
    }
}

//pour utiliser la localisation de l'utilisateur
function success(position) {
    if (x) {
        x.innerHTML = "Latitude: " + position.coords.latitude +
            "<br>Longitude: " + position.coords.longitude;
    }
    fetchMeteoForPoint(position.coords.latitude, position.coords.longitude);
}

function error() {
    alert("Sorry, no position available.");
}

// Slider - runs first before anything can crash it
const slider = document.getElementById('ac_target_temperature');
const display = document.getElementById('ac-target-temperature-value');
if (slider && display) {
    display.textContent = slider.value;
    slider.addEventListener('input', () => display.textContent = slider.value);
}

// Meteo toggles
const check_starttime = document.getElementById('start-time-check');
const startTimeSection = document.getElementById('start-time-div');
const radioButtonName = document.getElementsByName('meteo-mode');
const meteoManuelSection = document.getElementById('meteo-manuelle-section');

let lastValidMode = "manuel";

if (check_starttime && startTimeSection) {
    check_starttime.addEventListener('change', (event) => {
        startTimeSection.classList.toggle('hidden', !event.target.checked);
        if(!event.target.checked){
            toggleMeteoSection('manuel');
            const manuelRadio = document.querySelector(`input[name="meteo-mode"][value="manuel"]`);
            if (manuelRadio) {
                manuelRadio.checked = true;
            }
            lastValidMode = "manuel"
        }
    });
}

radioButtonName.forEach(radio => {
    radio.addEventListener("change", (event) => {
        const selectedValue = event.target.value;
        toggleMeteoSection(selectedValue);
    });
});

// Load car info after everything else
if (typeof Papa !== 'undefined') {
    init();
} else {
    window.addEventListener('load', init);
}
function toggleMeteoSection(mode) {
    if (!meteoManuelSection) {
        return;
    }
    if (mode === 'auto') {
        meteoManuelSection.classList.add('disabled');
        currentMeteoMode = "auto";
    } else {
        meteoManuelSection.classList.remove('disabled');
        currentMeteoMode = "manuel";
    }
}

// change TIME AND DATE for departure time + fetch and update the meteo information

const start_date_field = document.getElementById('start_date');
const start_time_field = document.getElementById('start_time');


async function updateMeteo(){
    if (!start_date_field || !start_time_field) {
        return;
    }
    console.log(start_date_field.value);
    console.log(start_time_field.value);
    //parse time
    const [start_time_hrsStr,start_time_minStr] = start_time_field.value.split(":");
    const start_hrs = parseInt(start_time_hrsStr,10);
    const start_min = parseInt(start_time_minStr,10);
    const start_hours_rounded = Math.round(start_hrs + start_min/60);

    start_lat = document.getElementById("start_lat").value;
    start_lng = document.getElementById("start_lng").value;
    if(start_lat != "" && start_lng != ""){
        await fetchMeteoForPoint(start_lat, start_lng, start_date_field.value,start_hours_rounded);
    }else{
        alert("Vous devez spécifier un trajet avantt")
    }
    updateMeteoInfo();
}