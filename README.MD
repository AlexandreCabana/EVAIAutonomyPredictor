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
    * [AI sur des données aléatoire](#ai-sur-des-données-aléatoire)
      * [Requis](#requis)
      * [Base de l'optimisation par l'IA](#base-de-loptimisation-par-lia)
      * [Graphique de l'impact de chacun des facteurs par rapport aux données expérimental](#graphique-de-limpact-de-chacun-des-facteurs-par-rapport-aux-données-expérimental)
      * [Graphique de l'erreur en fonction du nombre d'iteration](#graphique-de-lerreur-en-fonction-du-nombre-diteration)
        * [Calcul de l'erreur](#calcul-de-lerreur)
        * [Optimisation et ligne continue](#optimisation-et-ligne-continue)
    * [Test sur jeux de donnée aléatoire](#test-sur-jeux-de-donnée-aléatoire)
        * [Example 1](#example-1)
    * [Exécuter sur la carte graphique](#exécuter-sur-la-carte-graphique)
    * [IA sur les vraies données](#ia-sur-les-vraies-données)
      * [Impact des facteurs pris en compte pour prédire l'autonomie des véhicules électriques](#impact-des-facteurs-pris-en-compte-pour-prédire-lautonomie-des-véhicules-électriques)
      * [Quand arrêter l'entrainement](#quand-arrêter-lentrainement)
    * [Site Web](#site-web)
      * [Graphique des communications](#graphique-des-communications)
    * [Technologie utilisé](#technologie-utilisé)
  * [Tutoriel](#tutoriel)
  * [Analyse final](#analyse-final)
    * [Difficulté rencontrer](#difficulté-rencontrer)
    * [Diagramme de Gant](#diagramme-de-gant)
    * [Respect de l'échéancier](#respect-de-léchéancier)
    * [Percepective](#percepective)
    * [Conclusion](#conclusion)
<!-- TOC -->
## Description du projet
### L'équipe
**Alexandre:** Backend/IA

**Luca:** Modèle et SiteWeb

**Thierry:** Traitement des données

**Guillaume:** SiteWeb
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

Problème à résoudre : Les manufacturiers de véhicules électriques prédisent l’autonomie de leurs véhicules avec des tests sur dynamomètres. Les conditions de tests étant idéales, Les estimations sont souvent mauvaises dû aux impacts qu'à l’environnement sur la décharge lorsqu’on roule sur de vrais routes (vent, température, chauffage, etc.)

Solution : Prédire l’autonomie avec un modèle de machine learning qui est entrainé avec des données de trajets réels.

### Inovation
### Cas d'utilisation
1. Un utilisateur de VÉ veut connaitre avec une meilleure précision son range pour planifier ses déplacements
2. Un manufacturier de VÉ intègre notre app à ses véhicules pour offrir une meilleure prédiction du range à ses clients

### Public cible
Toutes les personnes qui ont accès à un véhicule électrique ou qui souhaitent acheter des véhicules électriques

### Lien avec autre matière
Maths et informatique : Machine learning, analyse de données
Physique : Paramètres du modèle modifiées par des fonctions physiques pour des prédictions plus précises.
Certains calculs basés sur la physique pour : Distance, altitude, énergie du chauffage/climatisation

## Fonctionemment de l'application
Pour avoir un produit final, il y a trois sections importantes. La première partie est la transformation des données. La deuxième partie est l’entrainement de l’intelligence artificielle pour avoir une fonction mathématique qui prédit l’autonomie. Ensuite, il y a la partie du site-web qui permet à l’utilisateur d’utiliser la fonction mathématique.
### Source de donnée et transformation
Tous les fichiers de cette section sont dans le répertoire transformation de donnée
#### Kagle
#### VicomTech
#### VEDElectrique
#### Calcul de la pente lorsque l'info est manquante
### AI sur des données suivant une somme de fonction polynomiale
Tous les fichiers de cette section sont dans le répertoire AIScript
#### Requis
Les librairies suivantes sont nécessaires.
- uvicorn
- Pandas
- Pytorch
- Numpy
- Sicpy
- Matplotlib
#### Base de l'optimisation par l'IA
Notre IA optimise une fonction qui se définit par une somme de fonction polynomiale telle que 
$f(x,y,z)= f_1(x) + f_2(y) +  f_3(z)$ où $f_n$ est une fonction polynomiale et n fait partie des réelles.
Par exemple,
$$f(x,y,z)= \alpha_{x2} \cdot x ^2 + \alpha_{x1} \cdot x + \alpha_{x0}  + \alpha_{y1} \cdot y + \alpha_{y0} + \alpha_{z1} \cdot z + \alpha_{z0}$$ où $\alpha$ représente des facteurs. 

L'IA trouve les facteurs optimaux pour que la formule globale trouvée  suive le plus possible les données dans notre jeu de donnée transformées. La library Pytorch est utilisée pour facilement faire une descente de gradient avec l'optimiseur ADAM qui détermine le multiple optimal à la pente. La descente de gradient est un principe d'optimisation. Pour ce faire, il faut définir une fonction qui calcul l'erreur en fonction des paramètres que le modèle prend. Ensuite, tu fais la dérivée partielle de chacun des paramètres par rapport à l'erreur. Ensuite, tu multiplies la dérivée par un facteur habituellement constant que tu soustrais à l'erreur. Ainsi, l'erreur va être réduite. Tu fais ça en boucle jusqu'à temp que l'erreur est minimal. Dans notre cas, on utilise l'optimiseur ADAM pour changer le facteur constant par une fonction qui dépend de la variation de l'erreur depuis la dernière fois. Ceci permet à notre programme d'optimiser plus vite. Dans le graphique suivant, vous pouvez constater l'évolution de l'erreur en fonction du nombre d'itérations d'une fonction parfaite.

![My image](./images/errorOptmisation.png)
#### Graphique de l'impact de chacun des facteurs par rapport aux données expérimental
Pour modéliser la fonction multivariable, nous ne pouvons pas faire de graphique 
traditional, car le corp humain peut voir au maximum une fonction à 2 paramètres. Ainsi, il faut être ingénieux
pour représenter une fonctione à plus de variable avec des graphiques. 

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
L'inconvénient de cette technique est que les graphiques générés lorsque l'IA s'entraine sont moins représentatif comme vous pouvez le voir avec le graphique suivant:

![My image](./images/MultidimensionalGraphBeginEnd/beginPrecisionGraph.png)

Ceci se produit, car les prédictions des autres fonctions sont erronées.
Cependant, une fois entrainé, cette technique marche parfaitement et les graphiques sont cohérents.

![My image](./images/MultidimensionalGraphBeginEnd/endPrecisionGraph.png)
#### Graphique de l'erreur en fonction du nombre d'iteration
##### Calcul de l'erreur
L'erreur est calculé avec la technique de l'erreur quadratique moyenne, soit
$$MSE = \frac{1}{N} \cdot \sum_{i=1}^{N} {(x_n-\overline x)^2} $$ où N représente le nombre d'éléments et $x_n$ 
représente la valeur du n-ième élément
$$\overline x = \frac{\sum_{i=1}^{n} x_n}{n}$$
##### Optimisation et ligne continue
Afin d'accélérer le programme, le programme ne génère pas le graphique de l'erreur en fonction du nombre d'iteration à chaque X iteration. Il y a une constante
au début du script python qui indique à quel intervalle faire le graphique. Lorsque le graphique ce fait, l'erreur est calculé. Par défaut, la constante est à 10 000. Pour avoir une ligne continue sur l'erreur, j'ai utilisé la librairie scipy et la fonction interpolate qui fait une ligne qui passe par les points donnés.
### Test sur jeux de donnée aléatoire
Pour tester notre intelligence artificielle rapidement et éfficacement, le code X génère un jeu de donnée aléatoire qui suit une fonction multivariable aléatoire de degré different.
##### Exemple 1
$$f(a,b,c,d,e,f) = a_3 \cdot a^3 + a_2 \cdot a^2 + a_1 \cdot a + a_0 + b_3 \cdot b^3 + b_2 \cdot b^2 + b_1 \cdot b + b_0 + c_2 \cdot c^2 + c_1 \cdot c + c_0 + d_2 \cdot d^2 + d_1 \cdot d + d_0 + e_1 \cdot e + e_0 + f_1 \cdot f + f_0$$
Lorsque le programme se lance, tous les paramètres sont définis aléatoirement. Après être optimisé, voici les résultats que nous avons obtenus. Dans ce graphique, vous pouvez constater la variation de chacun des paramètres par rapport à l'axe des Y

Dans ce graphique, vous pouvez constater l'évolution de l'erreur en fonction de l'erreur
### Exécuter sur la carte graphique
Afin d'optimiser l'optimisation de la fonction, la librairie Pytorch doit être réinstallé pour une version compatible avec ta version de CUDA. Dans mon cas, j'ai installé la version 13.0.
Pour installer la version de pytorch, j'ai utilisé la commande : 
```console
pip install torch --index-url https://download.pytorch.org/whl/cu130
```
### IA sur les vraies données
#### Impact des facteurs pris en compte pour prédire l'autonomie des véhicules électriques
Après avoir fait des recherches, nous avons déterminé telle relation pour estimer l'autonomie d'un véhicule électrique.
Il existe une corrélation entre X et Y
#### Overtrainnimg
Normalement, sur un jeu de donnée aléatoire où toutes les données n'ont pas de bruit. Le plus que le programme roule le mieux que c'est. Cependant, lorsque les données ont du bruit, l'IA va trop optimiser sur le jeu de donné et ne plus être précis. Ainsi, il faut séparer les données en deux, soit une partie pour l'entrainement et une autre pour valider. Lorsque les données sont séparées, on calcule l'erreur sur la partie de validation et d'entrainement. Lorsque que le programme est surentrainé, l'erreur sur les données de validation montre en flèche comme qu'on peut le voir sur le graphique suivant. On peut aussi calculer une erreur globale qui est une moyenne pondérée entre celle des données de validation et entrainement. On sauvegarde aussi le model dans un fichier qui s'appelle model.json pour être capable d'accéder certaines des itérations du programme.
### Site Web
#### Graphique des communications
Tous les fichiers de cette section sont dans le répertoire fastAPIProject

Configuration pour héberger le site web sur un serveur local avec uvicorn
Dans votre terminal d'IDE entrez la commande:
uvicorn fastApiProject.main:app --reload

Pour accéder au site, dirigez-vous sur http://127.0.0.1:8000 dans votre navigateur
### Technologie utilisé
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
        - Kagle
        - VicomTech
        - VEDElectrique
    - Version control: Git et Github
## Tutoriel

## Analyse final
### Difficulté rencontrer
### Diagramme de Gant
### Respect de l'échéancier
### Percepective

Si nous avions eu le double du temps pour réaliser notre projet, nous aurions ajouté et amélioré les fonctionnalités suivantes:

- Collecte de plusieurs données sur le véhicule de l’utilisateur en connectant un microcontrôleur au port OBD2 du véhicule
- Prédiction en temps réel en conduisant
- Meilleur UI/UX
- Plus de données et des données plus variées
- Amélioration des opérations possibles
### Conclusion
Bien que les résultats de l’IA ne soient pas très précis, ce projet nous a permis d’acquérir de nombreuses compétences en machine learning, en APIs, en développement frontend et dans plusieurs langages de programmation. Ces compétences nous serons très utiles dans nos études ou notre carrière. Ce projet servait surtout à comprendre le fonctionnement d’ une IA plus qu’à réellement révolutionner l’automobile dû au manque de données. Nous avons beaucoup appris et nous sommes fiers de l’effort que nous avons mis dans l’apprentissage des compétences nécessaires à la réalisation de notre projet.
Fait par Alexandre Cabana, Guillaume Lavertus, Luca Ferrandes, Thierry
