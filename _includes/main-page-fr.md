# Utilisation du graphique

Le graphique représente la courbe d'évolution pour le COVID-19 du:

1. <span style="color:#1f77b4">**Nombre total de cas**</span> (axes de gauche)
2. <span style="color:#ff7f0e">**Nombre de nouveaux cas**</span> (axes de droite)
3. <span style="color:#d62728">**Nombre total de décés**</span>  (axes de droite)
4. <span style="color:#8c564b">**Nombre de nouveaux décés**</span>  (axes de droite)

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

$$ (t_0^{\star}, K^{\star}, r^{\star}) \in argmin \sum_{i=1}^{n}\big(y_i - f(t_i)\big)^2 $$ 

Quand la capacité K du modèle est connue, le modèle peut être ajusté par régression linéaire en transformant  $$ f(t) $$ en  $$ g(t) = logit (\frac{f(t)}{K}) $$. 

$$ \operatorname{logit}\left(\frac{1}{1+e^{-r(t - t_0)}}\right)=\ln \left(\frac{1}{e^{-r(t - t_0)}}\right)= r t - t_0 $$

Ici, la capacité est inconnue, le modèle doit alors être ajusté avec des algorithmes d'optimisation. Avec des hypothèses résonnables sur les données, il existe des résultats sur l'existance du minimum considéré. [papier](https://www.sciencedirect.com/science/article/abs/pii/S0096300395002510)

L'algorithme d'optimisation utilisé est celui de [Nelder-Mead](https://fr.wikipedia.org/wiki/Méthode_de_Nelder-Mead).

## Distribution des paramètres et calcul d'incertitudes

La distribution des paramêtres optimaux du modèle est calculé par **Bootstrap**. Les échantillons Boostrap sont tirés avec une distribution linéaire, accordant plus d'importance aux données récentes qu'aux autres. La courbe centrale des prédictions correspond à la médiane des paramètres et les courbes supérieures et inférieures respectivement aux 1er et 3ème quantiles.



{% include image.html url="../img/pairplot-parameters.png" description="Distribution des paramètres" width="60%" %}



# Travail à venir

* Remarque sur les prédictions du modèle de Verhulstthe:

Le modèle de Verhulstthe est assez instable dans la phase de croissance exponentielle de la maladie. Le modèle à tendance à sous estimer la phase de croissance esponentielle du virus. 

## Nouveau modèle de croissance

Le nouveau modèle développé conciste à avoir deux modes de croissance du virus. 

1. Croissance exponentielle: $$ f(t) = e^{r_1t} $$
2. Croissance logistique: $$ f(t)=K \frac{1}{1+e^{-r(t - t_0)}} $$

Le modèle final de l'évolution du nombre de cas est:

$$ f(t) = (1-y(t)) \ e^{r_1t} + y(t) \ \big(\ a +  K \frac{1}{1+e^{-r_2(t - t_0)}} \big) $$

$$ \cdot \ y(t)= 0 $$ pour la croissance la phase de croissance exponentielle, 1 sinon.

Cette modélisation permet de prendre en compte la phase avant et après **confinement** grâce à la variable booléenne $$ y $$. La difficulté est d'apprendre l'instant $$t_1$$ pour lequel cette variable passe de $$0$$ à $$1$$.

Afin de garder la continuité de la fonction et de sa dérivé  en $$ t=t_1 $$,  $$ y(t_1)_-=0 $$ et $$ y(t_1)_+=1 $$ il faut que:

1. $$ f(t{_1})_- = f(t{_1})_+ \implies a  = e^{r_1t} - K \frac{1}{1+e^{-r_2(t_1 - t_0)}}  $$
2. $$  f'(t{_1})_- = f'(t{_1})_+ \implies   K= \frac{r_1}{r_2} \  e^{r_1t} \  \frac{ 1+e^{ - r_2 (t_1 - t_0) }}{1 - \frac{1}{1+e^{-r_2(t_1 - t_0)}}} $$ 

{% include image.html url="../img/difs-two-models.png" description="Différence entre les deux modélisations" width="90%" %}



