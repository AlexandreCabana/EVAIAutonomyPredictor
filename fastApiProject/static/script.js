let currentMeteoMode = "auto";
let meteoData = null;

//récupère les données météos selon coordonnées
async function fetchMeteoForPoint(lat, lon, date = null, heure = null) {
    try {
        const response = await fetch("/meteo", {
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

//mets à jour le siteweb si
function updateMeteoInfo(){
    try{
        const temperatureInput = document.getElementById("temperature");
        if (!meteoData) {
            return;
        }
        //affiche la température automatique sur le site
        if(currentMeteoMode === "auto"){
            if (temperatureInput && meteoData.temperature !== undefined && meteoData.temperature !== null) {
                temperatureInput.value = meteoData.temperature;
            }
        }

        //Coche le bon mode de météo (pluie, soleil, nuageux,...)
        if (meteoData.meteo) {
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


//récupère la liste de véhicules
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
//récupère les marques
function getBrands(data) {
    const brandsSet = new Set();
    data.forEach((model) => {
        const brandName = model[0];
        brandsSet.add(brandName);
    });
    return brandsSet;
}

//liste de marques et de modèles
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

    //met à jour marque
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

    //met a jour modèle
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

//pour utiliser la localisation de l'utilisateur
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(success, error);

}}
//condition succès
function success(position) {
     const userLatLng = L.latLng(position.coords.latitude, position.coords.longitude);
    if (map) {
        map.setView(userLatLng, 13);
        addPoint(userLatLng);
    }

    fetchMeteoForPoint(position.coords.latitude, position.coords.longitude);
}

//condition erreur
function error() {
    alert("Sorry, no position available.");
}

// Slider logic
function bindSliderValue(sliderId, displayId) {
    const slider = document.getElementById(sliderId);
    const display = document.getElementById(displayId);
    if (!slider || !display) {
        return;
    }

    display.textContent = slider.value;

    //changer text quand on change la valeur du slider
    slider.addEventListener('input', () => {
        display.textContent = slider.value;
    });
}


bindSliderValue('ac_target_temperature', 'ac-target-temperature-value');
bindSliderValue('current_charge_percentage', 'current-charge-value');

// Meteo toggles
const check_starttime = document.getElementById('start-time-check');
const startTimeSection = document.getElementById('start-time-div');
const radioButtonName = document.getElementsByName('meteo-mode');
const meteoManuelSection = document.getElementById('meteo-manuelle-section');

let lastValidMode = "auto";

if (check_starttime && startTimeSection) {
    check_starttime.addEventListener('change', (event) => {
        startTimeSection.classList.toggle('hidden', !event.target.checked);
    });
}

//logique de changement de type de météo
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

//sélectionner mode météo auto ou manuelle
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

const checkedMeteoMode = document.querySelector('input[name="meteo-mode"]:checked');
if (checkedMeteoMode) {
    toggleMeteoSection(checkedMeteoMode.value);
}

// change TIME AND DATE for departure time + fetch and update the meteo information

const start_date_field = document.getElementById('start_date');
const start_time_field = document.getElementById('start_time');

//calculs météos
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
        alert("Vous devez spécifier un trajet avant")
    }
    updateMeteoInfo();
}
