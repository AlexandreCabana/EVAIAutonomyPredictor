let map;
let markers = [];
let start = null;
let end = null;
let currentPolyline = null;
let geocoderControl = null;
        document.getElementById("map-container").style.display = "inline";

    if (!map) {
        //centered to mtl
        map = L.map("map").setView([45.5, -73.56], 10); //L is the Leaflet global object
        //creates map
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { //zoom z et position x,y
            attribution: "© OpenStreetMap"
        }).addTo(map);

        //Search bar
        if (L.Control.Geocoder) //checks if Geocoder is included {
            geocoderControl = L.Control.geocoder({
                collapsed: false,
                defaultMarkGeocode: false, //ne pas mettre markeur autommatiquement, géré plus bas
                placeholder: "Search an address"
            })
                //creates and displays the searched marker
                .on("markgeocode", (e) => {
                    const center = e.geocode.center;
                    map.fitBounds(e.geocode.bbox);
                    addPoint(center);
                })
                .addTo(map);
        }

        map.on("click", (e) => addPoint(e.latlng)); //adds marker on click



//logique d'ajout d'un markeur au coordonnées latlng
function addPoint(latlng) {
    //supprime le dernier trajet
    if (currentPolyline) {
        map.removeLayer(currentPolyline);
        currentPolyline = null;
    }
    //Si plus de 2 markeurs, on les supprime pour en mettre un seul
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

//Confirme et affiche le trajet
async function confirmMap() {
    if (!start || !end) {
        alert("Choisis un point de depart ET d'arrivee !");
        return;
    }

    document.getElementById("start_lat").value = start.lat;
    document.getElementById("start_lng").value = start.lng;
    document.getElementById("end_lat").value = end.lat;
    document.getElementById("end_lng").value = end.lng;

    //On récupère la météo au point de départ
    await fetchMeteoForPoint(start.lat, start.lng);
    updateMeteoInfo();

    displayRoute();
}

//Dessine le trajet
async function displayRoute() {
    if (!start || !end) {
        alert("Choisis un point de depart ET d'arrivee !");
        return;
    }

    console.log("Affichage de la route...");
    console.log(`Start: ${start.lat}, ${start.lng}`);
    console.log(`End: ${end.lat}, ${end.lng}`);

    try {

        const response = await fetch("/route", {
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

        //distance total parcourue
        const distance = route_data.distance.toFixed(2);

        //durée totale réelle
        const duration = route_data.duration !== null && route_data.duration !== undefined ? route_data.duration.toFixed(2) : "0";

        //durée théorique sans traffic
        const baseDuration = route_data.base_duration !== null && route_data.base_duration !== undefined
            ? route_data.base_duration.toFixed(2)
            : duration;

        //retard par le traffic
        const computedTrafficDelay =
            route_data.traffic_delay !== null && route_data.traffic_delay !== undefined
                ? route_data.traffic_delay
                : ((route_data.duration ?? 0) - (route_data.base_duration ?? 0));

        const trafficDelay = computedTrafficDelay.toFixed(2);

        //OSRM si tomtom marche pas
        const provider = route_data.provider || "osrm";

        document.getElementById("route-distance").textContent = distance;
        document.getElementById("route-duration").textContent = duration;
        document.getElementById("route-base-duration").textContent = baseDuration;
        document.getElementById("route-traffic-delay").textContent = trafficDelay;
        document.getElementById("route-provider").textContent = provider;
        document.getElementById("duration").value = duration;
        document.getElementById("route-info").style.display = "block";//affiche après calculs

        const group = new L.featureGroup([currentPolyline]);
        map.fitBounds(group.getBounds()); //centre la map sur le trajet
    } catch (error) {
        console.error("Erreur lors de la recuperation du trajet:", error);
    }
}
