# Diagramme de fonctionnement

Ce document decrit le flux reel de l'application, cote frontend et backend, a partir des fichiers actuellement presents dans le depot.

## Vue d'ensemble

```mermaid
flowchart LR
    U[Utilisateur]

    subgraph FE[Frontend]
        IDX[index.html\nFormulaire principal]
        JS1[script.js\nvehicule, meteo, sliders]
        JS2[trajet.js\ncarte, route, marqueurs]
        RES[resultat.html\npage resultat]
        CSV[static/car_info.csv\ncatalogue vehicules]
    end

    subgraph BE[Backend FastAPI - main.py]
        HOME[GET /.]
        METEO[POST /meteo]
        ROUTE[POST /route]
        SUBMIT[POST /submit]
        RESULT[GET /result]
        MODEL[Chargement model.json]
        CARLOOKUP[Lecture car_info.csv]
        ELEV[Calcul altitude + pente]
        ACP[Calcul AC/chauffage]
        PRED[Calcul consommation + autonomie]
    end

    subgraph EXT[Services externes]
        OM[Open-Meteo\nforecast + elevation]
        TT[TomTom Routing\ntrafic]
        OSRM[OSRM Routing\nfallback + distance]
    end

    subgraph TRAIN[Pipeline modele hors ligne]
        DATA[Dataset d'entrainement]
        SCRIPT[script.py\nentrainement PyTorch]
        MJSON[model.json\ncoefficients appris]
    end

    U --> HOME
    HOME --> IDX
    IDX --> JS1
    IDX --> JS2
    JS1 --> CSV

    U -->|choix depart/arrivee| JS2
    JS2 -->|fetch /meteo| METEO
    JS2 -->|fetch /route| ROUTE
    METEO --> OM
    ROUTE --> TT
    TT -. echec .-> OSRM
    ROUTE --> OSRM
    METEO --> JS1
    ROUTE --> JS2

    U -->|soumission formulaire| SUBMIT
    JS1 -->|marque, modele, meteo,\ncharge, temperature| SUBMIT
    JS2 -->|coords + duree| SUBMIT

    SUBMIT --> CARLOOKUP
    SUBMIT --> MODEL
    SUBMIT --> ELEV
    SUBMIT --> ACP
    ELEV --> OM
    SUBMIT --> OSRM
    CARLOOKUP --> CSV
    MODEL --> MJSON
    ACP --> CARLOOKUP
    SUBMIT --> PRED
    MODEL --> PRED
    CARLOOKUP --> PRED
    ELEV --> PRED
    ACP -. calcule mais non reintegre dans le score final actuel .-> PRED

    PRED -->|redirect| RESULT
    RESULT --> RES
    RES --> U

    DATA --> SCRIPT
    SCRIPT --> MJSON
```

## Sequence principale

```mermaid
sequenceDiagram
    participant User as Utilisateur
    participant UI as Frontend
    participant API as FastAPI
    participant Meteo as Open-Meteo
    participant Route as TomTom/OSRM
    participant Model as model.json
    participant Cars as car_info.csv

    User->>UI: Ouvre la page
    UI->>API: GET /
    API-->>UI: index.html
    UI->>Cars: Charger la liste des vehicules
    Cars-->>UI: Marques + modeles

    User->>UI: Selectionne le trajet sur la carte
    UI->>API: POST /meteo (lat, lon, date, heure)
    API->>Meteo: Forecast courant ou horaire
    Meteo-->>API: Temperature + meteo
    API-->>UI: JSON meteo

    UI->>API: POST /route (start_lat/lon, end_lat/lo)
    API->>Route: Position de départ et d'arrivée
    Route-->>API: Distance + duree + geometrie
    API-->>UI: JSON route

    User->>UI: Soumet le formulaire
    UI->>API: POST /submit (modele, ac_target_temp, ..., meteo, start, end, distance, duration)
    Cars->>API: Recuperer dimensions + batterie
    API->>Meteo: Position de départ et d'arrivée
    Meteo-->>API: Récuperer données d'altitude
    Model->>API: Charger les coefficients appris
    API->>API: Calcul pente, vitesse moyenne, consommation, autonomie
    UI->>API: GET /result 
    API-->>UI: resultats.html   (range, distance, duration, ... , consomation_per_km)
    UI-->>User: Affiche autonomie predite
```

