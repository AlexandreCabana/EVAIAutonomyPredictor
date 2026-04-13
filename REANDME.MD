# H1 Prédiction de l'autonomie des voitures électriques

## Source de donné et transformation
Tous les fichiers de cette section sont dans le répertoire transformation de donnée
###Kagle
###VicomTech
###VEDElectrique
###Calcul de la pente lorsque l'info est manquante
## AI
Tous les fichiers de cette section sont dans le répertoire AI
### Requis
Les librairies suivantes sont nécessaires
- Pandas
- Pytorch
- Numpy
- Sicpy
- Matplotlib
### Impact des facteurs pris en compte pour prédire l'autonomie des véhicules électriques
#### Pente
#### Distance
#### Vitesse moyenne
#### Température extérieure
#### Formule globale
### Base de l'optimisation par l'IA
L'IA trouve les facteurs optimaux pour que la 
formule globale trouvée avant 
suive le plus possible les données dans notre jeu de 
donnée transformées. La library Pytorch est utilisé 
pour facilement faire une descente de gradient avec l'optimiseur ADAM qui détermine le multiple optimal à la pente.

### Graphique de l'impact de chacun des facteurs par rapport aux données expérimental
Pour modéliser la fonction multivariable, nous ne pouvons pas faire de graphique 
traditional, car le corp humain peut voir au maximum une fonction à 2 paramètres. Ainsi, il faut être ingénieux
pour représenter une fonctione à plus de variable avec des graphiques. 

En ayant une fonction de type
$$
f(x,y,z)= f_1(x) + f_2(x) +  f_3(x)
$$
Avec la formule suivante, on peut avoir l'effet du paramètre a sur la fonction
$$
f(x,y,z) - f_2(x)- f_3(x) = f_1(x)
$$
Avec la formule suivante, on peut avoir l'effet du paramètre b sur la fonction
$$
f(x,y,z) - f_1(x) - f_3(x) = f_2(x)
$$
Avec la formule suivante, on peut avoir l'effet du paramètre c sur la fonction
$$
f(x,y,z) - f_1(x) - f_2(x) = f_3(x)
$$
On peut ainsi généraliser ceci pour une fonction multivariable.
$$
f(n_1,n_2, ..., n_n) - \sum_{i=1}^{n} f_n(n_n) + f_a(n_a) = f_a(n_a)
$$ où a est le paramètre à évaluer

Ainsi, on peut représenter l'effet d'un paramètre sur la fontion globale.
L'inconvénient de cette technique est que les graphiques générés lorsque l'IA
s'entraine sont moins représentatif, car les prédictions sont plus ou moins bonne.
Cependant, une fois entrainé, cette technique marche parfaitement et les graphiques sont cohérents.
### Graphique de l'erreur en fonction du nombre d'iteration
#### Calcul de l'erreur
L'erreur est calculé avec la technique de l'erreur quadratique moyenne, soit
$$
MSE = \sum_{i=1}^{n} \frac{x_n-\overline x}{\sigma}
$$
$$
\overline x = \frac{\sum_{i=1}^{n} x_n}{n}
$$
$$
\sigma = \sqrt\frac{\sum_{i=1}^{n}(x_n - \overline x)^2}{n}
$$
#### Optimisation et ligne continue
Afin d'accélérer le programme, le programme ne calcul pas l'erreur à chaque itération. Il y a une constante
au début du script python qui indique à quel intervalle faire le graphique. Lorsque le graphique ce fait,
l'erreur est calculé. Par défaut, la constante est à 10 000. Pour avoir une ligne continue sur l'erreur, j'ai utilisé la
librairie scipy et la fonction interpolate
qui fait une ligne qui passe par les points donnés.
### Test sur jeux de donnée aléatoire
Pour tester notre intelligence artificielle, les données n'étaient pas prête. Ainsi, le script Y,
génère un jeu de donnée aléatoire qui suit une fonction multivariable aléatoire de degré different.
#### Example 1
$$ 
f(a,b,c,d,e,f) = a_3*a^3+a_2*a^2 +a_1*a + a_0 + b_3*b^3+b_2*b^2 +b_1*b + b_0 + c_2*c^2 +c_1*c + c_0 + d_2*d^2 +d_1*d + d_0 
+ e_1*e + e_0 + f_1*f + f_0
$$
Lorsque le programme se lance, tous les paramètres sont définis aléatoirement. Après être optimisé, voici les résultats 
que nous avons obtenus. 
Dans ce graphique, vous pouvez constater la variation de chacun des paramètres par rapport à l'axe des Y

Dans ce graphique, vous pouvez constater l'évolution de l'erreur en fonction de l'erreur
### Exécuter sur la carte graphique
Afin d'optimiser l'optimisation de la fonction, la librairie Pytorch doit être réinstallé pour une 
version compatible avec ta version de CUDA. Dans mon cas, j'ai installé la version 13.0.
Pour installer la version de pytorch, j'ai utilisé la commande : 
```console
pip install torch --index-url https://download.pytorch.org/whl/cu130
```
## User Interface
Tous les fichiers de cette section sont dans le répertoire website

Fait par Alexandre Cabana, Guillaume Lavertus, Luca Ferrandes, Thierry