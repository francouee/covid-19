---
layout: default
---

   {% include  plot.html %}



# Data Source

The data rely on the data from the European Center for Disease Control and Prevention. The European CDC publishes daily statistics on the COVID-19 pandemic. Not just for Europe, but for the entire world. [link](https://www.ecdc.europa.eu/en)



# Predictions

The model used to make prediction is **Verhulstthe** originally developed for growth modelling. We'll assume the total number of covid 19 cases follows :

$$ f(t)=K \frac{1}{1+e^{-r(t - t_0)}} $$

$$ \cdot \ x_{0}= $$ the value  of the sigmoid's midpoint \\
$$\cdot \ L= $$ the curve's maximum value \\
$$\cdot \ k=$$ the logistic growth rate or steepness of the curve 

