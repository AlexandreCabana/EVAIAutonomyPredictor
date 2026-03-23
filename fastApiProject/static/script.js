let map;
let markers = [];
let start = null;
let end = null;

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

    getRoute(start, end);
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

async function test() {
    const data = await fetchCarInfo();
    console.log(data);
    brandSet = getBrands(data)
    const brandList = document.getElementById('marque-list');

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

test();
