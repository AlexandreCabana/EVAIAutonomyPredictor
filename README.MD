# Prédiction de l'autonomie des voitures électriques
<!-- TOC -->
* [Prédiction de l'autonomie des voitures électriques](#prédiction-de-lautonomie-des-voitures-électriques)
  * [Description du projet](#description-du-projet)
    * [L'équipe](#léquipe)
    * [Idée](#idée)
    * [Utilité](#utilité)
    * [Inovation](#inovation)
    * [Cas d'utilisation](#cas-dutilisation)
    * [Public cible](#public-cible)
    * [Lien avec autre matière](#lien-avec-autre-matière)
  * [Fonctionemment de l'application](#fonctionemment-de-lapplication)
    * [Source de donnée et transformation](#source-de-donnée-et-transformation)
      * [Kagle](#kagle)
      * [VicomTech](#vicomtech)
      * [VEDElectrique](#vedelectrique)
      * [Calcul de la pente lorsque l'info est manquante](#calcul-de-la-pente-lorsque-linfo-est-manquante)
    * [AI sur des données suivant une somme de fonction polynomiale](#ai-sur-des-données-suivant-une-somme-de-fonction-polynomiale)
      * [Base de l'optimisation par l'IA](#base-de-loptimisation-par-lia)
      * [Graphique de l'erreur en fonction du nombre d'iteration](#graphique-de-lerreur-en-fonction-du-nombre-diteration)
        * [Calcul de l'erreur](#calcul-de-lerreur)
        * [Optimisation et ligne continue](#optimisation-et-ligne-continue)
    * [Test sur jeux de donnée aléatoire](#test-sur-jeux-de-donnée-aléatoire)
        * [Exemple 1](#exemple-1)
      * [Graphique de l'impact de chacun des facteurs par rapport aux données expérimental](#graphique-de-limpact-de-chacun-des-facteurs-par-rapport-aux-données-expérimental)
    * [Exécuter sur la carte graphique](#exécuter-sur-la-carte-graphique)
    * [IA sur les vraies données](#ia-sur-les-vraies-données)
      * [Impact des facteurs pris en compte pour prédire l'autonomie des véhicules électriques](#impact-des-facteurs-pris-en-compte-pour-prédire-lautonomie-des-véhicules-électriques)
      * [Overtrainnimg](#overtrainnimg)
    * [Site web](#site-web)
      * [Diagramme de fonctionnement](#diagramme-de-fonctionnement)
  * [Tutoriel](#tutoriel)
  * [Technologie utilisé](#technologie-utilisé)
  * [Analyse finale](#analyse-finale)
    * [Difficulté rencontrée](#difficulté-rencontrée)
      * [1. Les erreurs de logique](#1-les-erreurs-de-logique)
      * [A.Modèle cubique](#amodèle-cubique)
      * [B. Multiplication de fonction](#b-multiplication-de-fonction)
      * [2. Pas accès aux données au début](#2-pas-accès-aux-données-au-début)
      * [3. Difficulté à travailler sur l'IA à 2:](#3-difficulté-à-travailler-sur-lia-à-2-)
      * [4. Design fait par des LLMs:](#4-design-fait-par-des-llms-)
      * [5. Oubli de clear le cache](#5-oubli-de-clear-le-cache)
      * [6. A FAIRE](#6-a-faire)
    * [Diagramme de Gant](#diagramme-de-gant)
    * [Respect de l'échéancier](#respect-de-léchéancier)
    * [Percepective](#percepective)
    * [Conclusion](#conclusion)
<!-- TOC -->
## Description du projet
### L'équipe
**Alexandre (AlexandreCabana):** Backend/IA

**Luca (LucaFL02):** Modèle et SiteWeb

**Thierry (EatANapkin):** Traitement des données

**Guillaume (gliglo7):** SiteWeb
### Idée
Nous souhaitons créer une application qui permet à ses utilisateurs de prédire avec une IA la distance qu'ils peuvent 
parcourir avec l'énergie restante dans leur véhicule électrique.
### Utilité
Connaitre avec plus de précision l’autonomie d(distance maximale atteignable avec la charge restante) de son véhicule :

- Planifier ses déplacements
- Planifier ses charges
- Réduire sa consommation électrique
- Éviter des imprévus
- Fournir des données plus précises que celles des fabricants

Fonctionnalité :
- Carte pour sélectionner l’itinéraire prévu
- Prise en compte du traffic selon l’heure de départ
- Prise en compte des données météos (automatiquement ou manuellement)
- Entrainement du modèle sur 175Mo de données

Problème à résoudre : Les manufacturiers de véhicules électriques prédisent l’autonomie de leurs véhicules avec des tests sur dynamomètres. Les conditions de tests étant idéales, Les estimations sont souvent mauvaises dû aux impacts qu'à l’environnement sur la décharge lorsqu’on roule sur de vraies routes (vent, température, chauffage, etc.)

Solution : Prédire l’autonomie avec un modèle de machine learning qui est entrainé avec des données de trajets réels.

### Inovation
à FAIRE
### Cas d'utilisation
1. Un utilisateur de VÉ veut connaitre avec une meilleure précision son range pour planifier ses déplacements
2. Un manufacturier de VÉ intègre notre app à ses véhicules pour offrir une meilleure prédiction du range à ses clients

### Public cible
Toutes les personnes qui ont accès à un véhicule électrique ou qui souhaitent acheter des véhicules électriques

### Lien avec autre matière
Maths et informatique : Machine learning, analyse de données

Physique : Paramètres du modèle modifiées par des fonctions physiques pour des prédictions plus précises.
Certains calculs basés sur la physique pour : Distance, altitude, énergie du chauffage/climatisation, énergie et autonomie

## Fonctionemment de l'application
Pour avoir un produit final, il y a trois sections importantes. La première partie est la transformation des données. La deuxième partie est l’entrainement de l’intelligence artificielle pour avoir une fonction mathématique qui prédit l’autonomie. Ensuite, il y a la partie du site-web qui permet à l’utilisateur d’utiliser la fonction mathématique.
### Source de donnée et transformation
Tous les fichiers de cette section sont dans le répertoire transformation de donnée
#### Kagle
Ce premier dataset était le plus riche en données puisqu'il offrait plusieurs trips pour chaque voiture pour arriver à un total de 5000 trips différents. Le dataset était également déjà regroupé par trip ce qui a sauvé beaucoup de temps dans le tri des données pertinentes. 
#### VicomTech
Cette deuxième source de donnée regroupe 29 trips avec deux voitures différentes pour obtenir 58 trips au total. Ce dataset était regroupé par timestamp avec des données correspondates. Pour obtenir une meilleure vue d'ensemble, il a fallu donc regrouper le dataset selon chaque trip_id et faire une analyse statistique pour sortir les données pertinentes. 
#### VEDElectrique
Comme VicomTech, ce dataset était regroupé par timestamps, mais il comportait également beaucoup de données sur des véhicules hybrides ou des véhicules à gaz. Il a donc fallu garder seulement les véhicules exclusivement électriques. Il n'en comportait que 3 et seulement 2 des 3 ont enregistré des données utilisables. Ce qui fait de cette source de donnée la moins riche en donnée.

Les sources des Datasets sont mentionnées dans la section [Technologie utilisé](#technologie-utilisé)

#### Calcul de la pente lorsque l'info est manquante
Pour les données provenant de VED et VicomTech, la pente en % nécessaire pour nos calculs de l'IA n'était pas donné. Ils donnaient cependant la longitude et lattitude en degrés. Il était donc possible d'utiliser l'API de OpenMeteo afin de trouver une altitude pour une lattitude et longitude donnée. Il suffisait ensuite de faire le calcul suivant pour trouver le slope en %.

delta altitude(m) /distance parcourue(m) * 100
### AI sur des données suivant une somme de fonction polynomiale
Tous les fichiers de cette section sont dans le répertoire AIScript

#### Base de l'optimisation par l'IA
Notre IA optimise une fonction qui se définit par une somme de fonction polynomiale telle que 
$f(x,y,z)= f_1(x) + f_2(y) +  f_3(z)$ où $f_n$ est une fonction polynomiale et n fait partie des réelles.
Par exemple,
$$f(x,y,z)= \alpha_{x2} \cdot x ^2 + \alpha_{x1} \cdot x + \alpha_{x0}  + \alpha_{y1} \cdot y + \alpha_{y0} + \alpha_{z1} \cdot z + \alpha_{z0}$$ où $\alpha$ représente des facteurs. 

L'IA trouve les facteurs optimaux pour que la formule globale trouvée  suive le plus possible les données dans notre jeu de donnée transformées. La library Pytorch est utilisée pour facilement faire une descente de gradient avec l'optimiseur ADAM qui détermine le multiple optimal de la pente pour le nouveau facteur. La descente de gradient est un principe d'optimisation. Il faut définir une fonction qui calcul l'erreur en fonction des paramètres que le modèle prend. Ensuite, tu fais la dérivée partielle de chacun des paramètres par rapport à l'erreur. Ensuite, tu multiplies la dérivée par un facteur habituellement constant que tu soustrais à l'erreur. Ainsi, l'erreur va être réduite. Tu fais ça en boucle jusqu'à temp que l'erreur est minimal. Dans notre cas, on utilise l'optimiseur ADAM pour changer le facteur constant par une fonction qui dépend de la variation de l'erreur depuis la dernière fois. Ceci permet à notre programme d'optimiser plus vite. Dans le graphique suivant, vous pouvez constater l'évolution de l'erreur en fonction du nombre d'itérations d'une fonction parfaite.
Dans le graphique suivant, la fonction en mauve est l'erreur que nous optimisons à l'aide des dérivées partielles sur le paramètre x d'une fonction. \

![My image](https://lucidar.me/fr/neural-networks/files/gradient-descent.png)
#### Graphique de l'erreur en fonction du nombre d'iteration
Ce type de graphique permet de suivre l'évolution de l'intelligence artificielle avec le temps.  Il y a une constante dans le fichier de configuration que vous pouvez modifier afin de déterminer à quelle fréquence il sauvegarde et génère les graphiques.
Dans le graphique suivant, vous pouvez constater l'évolution de l'erreur en fonction du nombre d'itérations.
![My image](./images/errorOptmisation.png)
##### Calcul de l'erreur
L'erreur est calculé avec la technique de l'erreur quadratique moyenne, soit
$$MSE = \frac{1}{N} \cdot \sum_{i=1}^{N} {(x_n- \tilde{x_n})^2} $$ où N représente le nombre d'éléments et $x_n$ 
représente la valeur théorique du n-ième élément et $\tilde{x_n}$ représente la valeur n-ième élément prédit.
##### Optimisation et ligne continue
Afin d'accélérer le programme, le programme ne génère pas le graphique de l'erreur en fonction du nombre d'iteration à chaque X iteration. Il y a une constante
au début du script python qui indique à quel intervalle faire le graphique. Lorsque le graphique ce fait, l'erreur est calculé. Par défaut, la constante est à 10 000. Pour avoir une ligne continue sur l'erreur, j'ai utilisé la librairie scipy et la fonction interpolate qui fait une ligne qui passe par les points donnés.
### Test sur jeux de donnée aléatoire
Pour tester notre intelligence artificielle rapidement et éfficacement, le code X génère un jeu de donnée aléatoire qui suit une fonction multivariable aléatoire de degré different.
##### Exemple 1
$$f(a,b,c,d,e,f) = a_3 \cdot a^3 + a_2 \cdot a^2 + a_1 \cdot a + a_0 + b_3 \cdot b^3 + b_2 \cdot b^2 + b_1 \cdot b + b_0 + c_2 \cdot c^2 + c_1 \cdot c + c_0 + d_2 \cdot d^2 + d_1 \cdot d + d_0 + e_1 \cdot e + e_0 + f_1 \cdot f + f_0$$
Lorsque le programme se lance, tous les paramètres sont définis aléatoirement. Après être optimisé, voici les résultats que nous avons obtenus. Dans ce graphique, vous pouvez constater la variation de chacun des paramètres par rapport à l'axe des Y.

![My image](./images/errorOptmisation.png)
#### Graphique de l'impact de chacun des facteurs par rapport aux données expérimental
Pour modéliser la fonction multivariable, nous ne pouvons pas faire de graphique 
traditional, car le corp humain peut voir au maximum une fonction à 2 paramètres. Ainsi, il faut être ingénieux
pour représenter une fonction à plus de variable avec des graphiques. 

En ayant une fonction de type  
$$f(x,y,z)= f_1(x) + f_2(y) +  f_3(z)$$\
Avec la formule suivante, on peut avoir l'effet du paramètre a sur la fonction\
$$f(x,y,z) - f_2(y)- f_3(z) = f_1(x)$$\
Avec la formule suivante, on peut avoir l'effet du paramètre b sur la fonction\
$$f(x,y,z) - f_1(x) - f_3(z) = f_2(y)$$\
Avec la formule suivante, on peut avoir l'effet du paramètre c sur la fonction\
$$f(x,y,z) - f_1(x) - f_2(y) = f_3(z)$$\
On peut ainsi généraliser ceci pour une fonction multivariable.\
$$f(n_1,n_2, ..., n_n) - \sum_{i=1}^{n} f_n(n_n) + f_a(n_a) = f_a(n_a)$$ où a est le paramètre à évaluer\
Ainsi, on peut représenter l'effet d'un paramètre sur la fontion globale.
L'inconvénient de cette technique est que les graphiques générés lorsque l'IA s'entraine sont moins représentatif comme vous pouvez le voir avec le graphique suivant :

![My image](./images/MultidimensionalGraphBeginEnd/beginPrecisionGraph.png)

Ceci se produit, car les prédictions des autres fonctions sont erronées.
Cependant, une fois entrainé, cette technique marche parfaitement et les graphiques sont cohérents.

![My image](./images/MultidimensionalGraphBeginEnd/endPrecisionGraph.png)

### Exécuter sur la carte graphique
Afin d'optimiser l'optimisation de la fonction, la librairie Pytorch doit être réinstallé pour une version compatible avec ta version de CUDA. Dans mon cas, j'ai installé la version 13.0.
Pour installer la version de pytorch, j'ai utilisé la commande : 
```console
pip install torch --index-url https://download.pytorch.org/whl/cu130
```
### IA sur les vraies données
#### Impact des facteurs pris en compte pour prédire l'autonomie des véhicules électriques
Après avoir fait des recherches, nous avons déterminé telle relation pour estimer l'autonomie d'un véhicule électrique.
En premier lieu, voici une liste de définition
- E: énergie consomé sur le trajet
- V: vitesse
- S: pente
- M: masse
- D: distance
- $T_{ext}$: température extérieure
- $T_{int}$: température intérieure
- $f_n$ est une fonction de degré n
- $\alpha$ veut dire proportionnelle

$$E \hspace{0.5em} \alpha \hspace{0.5em} f_1(D) \cdot f_1(M) \cdot f_3(S)$$
$$E \hspace{0.5em} \alpha \hspace{0.5em} f_1(D) \cdot f_2(V) $$
$$E \hspace{0.5em} \alpha \hspace{0.5em} f_1(D) \cdot f_2(T_{ext} - T_{int})$$
#### Overtrainnimg
Normalement, sur un jeu de donnée aléatoire où toutes les données n'ont pas de bruit. Le plus que le programme roule le mieux que c'est. Cependant, lorsque les données ont du bruit, l'IA va trop optimiser sur le jeu de donnée et ne plus être précis. Ainsi, il faut séparer les données en deux, soit une partie pour l'entrainement et une autre pour valider. Lorsque les données sont séparées, on calcule l'erreur sur la partie de validation et d'entrainement. Lorsque que le programme est surentrainé, l'erreur sur les données de validation montre en flèche comme qu'on peut le voir sur le graphique suivant. 
![My image](./images/overtrainExample.png)
On peut aussi calculer une erreur globale qui est une moyenne pondérée entre celle des données de validation et entrainement. Pour accéder au model optimale, on sauvegarde le model dans un fichier qui s'appelle model.json.


### Site web
Le site web a été concu avec le framework FastApi. Un framework est une structure de base pour construire un projet avec de nombreux fonctionalité. La grosse différence avec une librairie et que la manière de lancer le projet est souvent différent qu'un script standard. Dans notre cas, FastAPI permet de crée le backend d'un serveur en python.
#### Diagramme de fonctionnement
Voici un diagramme qui représente les requêtes faites par l'utilisateur et ce qu'il se passe derrière.
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

## Tutoriel

### Qu’est-ce qu’une API?
C’est tout simplement un intermédiaire qui permet à différentes applications de communiquer entre elles. Par exemple, il existe des API pour la météo où, dans l’URL, tu spécifies la position voulue, la date voulue, et l’API de météo va te renvoyer les informations de température et de précipitation pour cette localisation et date spécifique.
### Qu’est-ce que FastAPI?
C’est un framework qui permet de créer des API de manière simple et efficace. Il est notamment utilisé par des géants du web comme Netflix.
### Et un framework, c’est quoi?
Un framework est une structure de base pour construire un projet avec de nombreux fonctionalité. La grosse différence avec une librairie et que la manière de lancer le projet est souvent différent qu'un script standard. Dans notre cas, FastAPI permet de crée le backend d'un serveur en python.

Référence intéressante: https://www.jetbrains.com/help/pycharm/fastapi-project.html#create-project

## Création d’un projet fastAPI
A FAIRE
1)	Installer PyCharm (https://www.jetbrains.com/pycharm/)
2)	Créer un nouveau projet
3)	Sélectionner FastAPI comme type de projet

![My image](./images/1.png)

4)	Spécifier le nom de votre projet, son emplacement et si vous désirez créer un répertoire Git
5)	Cliquer sur Create

À ce moment-là PyCharm va installer le framework de FastAPI et uvicorn (un serveur web). Vous allez aussi voir apparaitre un fichier main.py qui contient du code de base pour la création d’API.

![My image](./images/2.png)


### Pour accéder au site:
Si le site est actif, dirigez-vous sur : https://evaiautonomypredictor.onrender.com/
Sinon,
1) Importez notre projet dans PyCharm
2) Créez un envivronnment venv //A FAIRE
3) Installer les librairies requises: // A FAIRE (installées dans venv)
4) Exécutez main.py 
5) Dirigez-vous sur http://127.0.0.1:8000 dans votre navigateur

## Technologie utilisé
- **Technologies à utiliser** :
    - Language frontend: JavaScript (HTML et CSS)
    - Language backend: Python
    - Framework pour l’application: FastAPI
    - APIs:
        - OpenStreetMap (https://www.openstreetmap.org/)
        - TomTom (https://developer.tomtom.com/)
        - OpenMeteo (https://open-meteo.com/)
    - Bibliothèques FrontEnd:
        - Leaflet (https://leafletjs.com/)
        - PapaParse (https://www.papaparse.com/)
    - Bibliothèques Serveur:
        - uvicorn (https://uvicorn.dev/)
        - Starlette (https://starlette.dev/)
        - Pydantic (https://pydantic.dev/)
        - Pandas (https://pandas.pydata.org/)
        - NumPy (https://numpy.org/)
        - FastAPI(https://fastapi.tiangolo.com/)
        - Pathlib
        - Time
        - JSON
        - Csv
        - Requests
    - Bibliothèque pour entrainer l’IA:
        - Pytorch (https://pytorch.org/)
        - NumPy (https://numpy.org/)
        - SicPy (https://scipy.org/)
        - Matplotlib (https://matplotlib.org/)
        - Pandas (https://pandas.pydata.org/)
        - JSON
        - Math
    - Bases de données pour entrainer IA:
        - Kaggle (https://www.kaggle.com/datasets/ziya07/ev-energy-consumption-dataset)
        - VicomTech (https://github.com/Vicomtech/d-EVD_dual-Electric-Vehicle-Dataset)
        - VEDElectrique (https://github.com/gsoh/VED)
    - Version control: Git et Github



## Analyse finale
### Difficulté rencontrée
#### 1. Les erreurs de logique
#### A.Modèle cubique
La fonction cubique avait mal été définis. Ainsi, lorsque l'optimiseur faisait de l'optimist, elle ne marchait pas. Au début, c'était définit par $f(x)=\alpha_3 \cdot x^3 + \alpha_2 \cdot x^2 + \alpha_3$
Ceci est éroné et devrait être $f(x)=\alpha_3 \cdot x^3 + \alpha_2 \cdot x^2 + \alpha_1$
Ceci est un problème simple, mais il a pris 3h à résoudre.
#### B. Multiplication de fonction
Pendant un moment, je n'arrivais pas à comprendre pourquoi le modèle était très imprécis. Après analyse et réflexion, ceci était dû au fait que si deux paramètres sont multipliées ensemble, toutes les combinaisons de degrés ne sont pas calculées. Par exemple, 
$$f_2(x) = \alpha_{x2} \cdot x^2 + \alpha_{x1} \cdot x + \alpha_{x0}$$
$$f_3(y) = \alpha_{y3} \cdot y^3 +\alpha_{y2} \cdot y^2 + \alpha_{y1} \cdot y + \alpha_{y0}$$
$$f(x,y) = f_2(x)) \cdot f_3(y) $$
$$f(x,y) = (\alpha_{x2} \cdot x^2 + \alpha_{x1} \cdot x + \alpha_{x0}) \cdot (\alpha_{y3} \cdot y^3 +\alpha_{y2} \cdot y^2 + \alpha_{y1} \cdot y + \alpha_{y0})$$
$$f(x, y)=\alpha_{x2} \cdot \alpha_{y3} \cdot x^2 \cdot y^3 + \alpha_{x2} \cdot \alpha_{y2} \cdot x^2 \cdot y^2 +
\alpha_{x2} \cdot \alpha_{y1} \cdot x^2 \cdot y +
\alpha_{x2} \cdot \alpha_{y0} \cdot x^2 +
\alpha_{x1} \cdot \alpha_{y3} \cdot x \cdot y^3 +
\alpha_{x1} \cdot \alpha_{y2} \cdot x \cdot y^2 +
\alpha_{x1} \cdot \alpha_{y1} \cdot x \cdot y +
\alpha_{x1} \cdot \alpha_{y0} \cdot x +
\alpha_{x0} \cdot \alpha_{y3} \cdot y^3 +
\alpha_{x0} \cdot \alpha_{y2} \cdot y^2 +
\alpha_{x0} \cdot \alpha_{y1} \cdot y +
\alpha_{x0} \cdot \alpha_{y0}$$

Au lieu de faire ça, mon code faisait
$$f(x,y) = \alpha_2 \cdot (xy)^2 + \alpha_1 \cdot xy + \alpha 2 $$

Ce n'est donc pas equivalent. J'ai donc fait que l'équivalence soit vraie.
#### 2. Pas accès aux données au début
Un problème que nous avons eu est que pour pratiquer une intelligence artificielle, il faut avoir des données. Cependant, il fallait transformer les données en premier. Pour résoudre ceci, nous avons créé un script qui génère des données aléatoires suivant une fonction multivariable de degré 1 à 3.
#### 3. Difficulté à travailler sur l'IA à 2: 
Après avoir modélisé le modèle, Alexandre et Luca devaient créer l'IA pour intégrer le modèle en Python. Travailler en peer-to-peer se révélait inefficace et une personne faisait plus de travail que l'autre. Nous avons donc décidé de laisser la conception de l'IA à Alexandre alors que Luca aidait Guillaume à concevoir le SiteWeb.

#### 4. Design fait par des LLMs: 
Nous avons décidé de rendre notre site plus beau en modifiant notre CSS avec Gemini et Claude. Cela a eu pour effet de ralentir notre progression sur le siteweb dû aux hallucinations et bugs de cohérences causées par les LLMs. Nous aurions dû nous satisfaire d'un siteweb moins esthétique, mais plus simple afin d'accélérer notre productivité sur des fonctionnalitées concrètes.
#### 5. Oubli de clear le cache
Un des problèmes qui est survenu à quelques reprises est celui de voir aucun changement lors qu'on modifie le code de l'interface graphique. Cela est dû au cache du navigateur. Pour résoudre le problème, il suffit seulement de clear le cache et de le désactiver. Cependant, lorsqu'on y pense pas, cela peut nous faire perdre un temps précieux.

#### 6. A FAIRE
A FAIRE

### Diagramme de Gant
![image](images/Diagramme_de_Gantt.png)

### Respect de l'échéancier
A FAIRE
### Percepective

Si nous avions eu le double du temps pour réaliser notre projet, nous aurions ajouté et amélioré les fonctionnalités suivantes :

- Collecte de plusieurs données sur le véhicule de l’utilisateur en connectant un microcontrôleur au port OBD2 du véhicule
- Prédiction en temps réel en conduisant
- Meilleur UI/UX
- Plus de données et des données plus variées (surtout dans des conditions hivernales)
- Amélioration des opérations possibles
### Conclusion
Bien que les résultats de l’IA ne soient pas très précis, ce projet nous a permis d’acquérir de nombreuses compétences en machine learning, en APIs, en développement frontend et dans plusieurs langages de programmation. Ces compétences nous serons très utiles dans nos études ou notre carrière. Ce projet servait surtout à comprendre le fonctionnement d’ une IA plus qu’à réellement révolutionner l’automobile dû au manque de données. Nous avons beaucoup appris et nous sommes fiers de l’effort que nous avons mis dans l’apprentissage des compétences nécessaires à la réalisation de notre projet.
