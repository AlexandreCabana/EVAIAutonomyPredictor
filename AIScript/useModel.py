import json
from json import JSONDecodeError
import time

def computeDictParam(paramDict):
    result = paramDict.copy()
    result["temperature"] = abs(result["temperature"]  -15)
    result["distanceMultiplyBySpeedSquared"] = result["total_distance"] * result["speed_avg"] ** 2 / 1000
    result["distanceMultiplyBySlopeCube"] = result["total_distance"] * result["slope"] ** 3 / 1000
    result["distanceMultiplyByTemperature"] = result["total_distance"] * (result["temperature"] - 21.5) ** 2 / 1000
    result["distanceMultiplyByTemperature"] = result["total_distance"] * (result["temperature"])/1000
    result["distanceMultiplyByTemperatureSquared"] = result["total_distance"] * (result["temperature"]) ** 2 / 1000
    result["distanceMultiplyByTemperatureSquaredDivideBySpeed"]= result["total_distance"]*result["temperature"] ** 2/result["speed_avg"]
    result["distanceMultiplyByTemperatureDivideBySpeed"]= result["total_distance"]*result["temperature"]/result["speed_avg"]
    return result

def getFunctions(i):
    try:
        with open('../model.json') as f:
            return json.load(f)[str(i)]["functions"]
    except JSONDecodeError:
        time.sleep(.1)
        return getFunctions(i)
def estimate(paramDict, functions):
    estimateValue = 0
    for parameter in functions.keys():
        type = list(functions[parameter].keys())[0]
        curentFunction = functions[parameter][type]
        match type:
            case "lineaire":
                estimateValue += (curentFunction["a"] * paramDict[parameter]
                                  + curentFunction["b"])
            case "quad":
                estimateValue += (curentFunction["a"] * paramDict[parameter] ** 2 +
                                  curentFunction["b"] * paramDict[parameter] +
                                  curentFunction["c"])
            case "cubique":
                estimateValue += (curentFunction["a"] * paramDict[parameter] ** 3
                                  + curentFunction["b"] * paramDict[parameter] ** 2 +
                                  curentFunction["c"] * paramDict[parameter] +
                                  curentFunction["d"])
    return estimateValue

def estimateForIWithText(i, param):
    functions = getFunctions(i)
    print(f"test for i = {i} with {param}")
    estimateValue = estimate(param, functions)
    print(f"estimate kw consumption: {estimateValue}")
    print(f"estimated left battery: {(1 - estimateValue / 72500) * 100}%")
    consomation_per_km = estimateValue / param["total_distance"]

    # trouver la capacité de la batterie
    total_battery_capacity = 72500
    current_charge_percentage=100
    battery_capacity = total_battery_capacity * (current_charge_percentage / 100)
    pourcentage_used = round(estimateValue / total_battery_capacity * 100, 2)

    predicted_range = int(battery_capacity / consomation_per_km) if estimateValue > 0 else 0
    print(f"predicted range: {predicted_range}")

if __name__ == "__main__":
    BESTI = 374633
    TOPI = 450000
    VALUEFORPARAM = {"speed_avg": 95, "slope": 0, "temperature": 15, "total_distance": 130}
    VALUEFORPARAM2 = {"speed_avg": 60, "slope": 0, "temperature": 15, "total_distance": 30}
    VALUEFORPARAM3 = {"speed_avg": 95, "slope": 0, "temperature": -15, "total_distance": 130}
    completeDictParam = computeDictParam(VALUEFORPARAM)
    completeDictParam2 = computeDictParam(VALUEFORPARAM2)
    completeDictParam3 = computeDictParam(VALUEFORPARAM3)
    estimateForIWithText(BESTI, completeDictParam)
    estimateForIWithText(BESTI, completeDictParam2)
    estimateForIWithText(BESTI, completeDictParam3)
    for i in range(5000, TOPI+1, 5000):
        functions = getFunctions(i)
        if estimate(completeDictParam3, functions) - estimate(completeDictParam, functions) > 0.05*72500 :
            estimateForIWithText(i, completeDictParam)
            estimateForIWithText(i, completeDictParam2)
            estimateForIWithText(i, completeDictParam3)