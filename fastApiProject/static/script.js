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
