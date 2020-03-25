# Utilisation du graphique

Le graphique représente la courbe d'évolution pour le COVID-19 du:

1. **Nombre total de cas** (axes de gauche)
2. **Nombre de nouveaux cas** (axes de droite)
3. **Nombre total de décés**  (axes de droite)
4. **Nombre de nouveaux décés**  (axes de droite)

La partie haute du graphique permet de:

* Selectionner le **pays** d'affichage des courbes 

* Afficher les **prédictions** du nombre total de cas suivant le modèle décrit dans la section suivante.

* Visualiser la prédiction faite au jour $$ j-valeur \ slider $$. Par exemple lorsque le valeur du slider est 3, la courbe affichée correspond à la prédiction du nombre total de cas calculée 3 jours plus tôt.



# Source de données

Les données proviennent du Centre européen de prévention et contrôle des maladies. Ce centre publie chaque jour des statistiques sur l'évolution de l'épidémie du COVID-19 dans le monde. [Site de l'ECDC](https://www.ecdc.europa.eu/en),  [lien vers les données](https://covid.ourworldindata.org/data/ecdc/full_data.csv).

# Prédictions

La prédiction du nombre total de personne atteinte par le COVID-19 est estimée avec le modèle de [Verhulstthe](https://fr.wikipedia.org/wiki/Fonction_logistique_(Verhulst)). Ce modèle fut originalement proposé pour modèliser des phénomènes de croissance comme l'évolution de la population mondiale. Le modèle suppose que le nombre total de cas du COVID-19  suit la loi:

$$ f(t)=K \frac{1}{1+e^{-r(t - t_0)}} $$

$$ \cdot \ t_{0}= $$ Le point d'inflexion de la croissance \\
$$\cdot \ K= $$ La capacité, ici le nombre maximum de personnes pouvant être infectées \\
$$\cdot \ r=$$ Le taux de croissance de la fonction

## Ajustement du modèle

Le modèle est ajusté pour minimiser l'erreur quadratique moyenne (MSE):

$$ (t_0^{\star}, K^{\star}, r^{\star}) \in argmin \sum_{i=1}^{n}\big(y_i - f(t_i)^2\big) $$ 

Quand la capacité K du modèle est connue, le modèle peut être ajusté par régression linéaire en transformant  $$ f(t) $$ en  $$ g(t) = logit (\frac{f(t)}{K}) $$. 

$$ \operatorname{logit}\left(\frac{1}{1+e^{-r(t - t_0)}}\right)=\ln \left(\frac{1}{e^{-r(t - t_0)}}\right)= r t - t_0 $$

Ici, la capacité est inconnue, le modèle doit alors être ajusté avec des algorithmes d'optimisation. Avec des hypothèses résonnables sur les données, il existe des résultats sur l'existance du minimum considéré. [papier](https://www.sciencedirect.com/science/article/abs/pii/S0096300395002510)

L'algorithme d'optimisation utilisé est celui de [Nelder-Mead](https://fr.wikipedia.org/wiki/Méthode_de_Nelder-Mead).

## Distribution des paramètres et calcul d'incertitudes

La distribution des paramêtres optimaux du modèle est calculé par **Bootstrap**. Les échantillons Boostrap sont tirés avec une distribution linéaire, accordant plus d'importance aux données récentes qu'aux autres. La courbe centrale des prédictions correspond à la médiane des paramètres et les courbes supérieures et inférieures respectivement aux 1er et 3ème quantiles.