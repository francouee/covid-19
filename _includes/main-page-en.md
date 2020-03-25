

# Chart usage

The chart show the evolution of COVID-19 for:

1. **Total number of cases** (left axis)
2. **New cases** (right axis)
3. **Total number of death**  (right axis)
4. **New deaths**  (right axis)

The top part of the graph allows to:

* Select the displayed **country** for the curves

* Show the total number of cases **prédictions** made with model explained the next section.

* Visualise the prediction made the day $$ j-slider \ value $$. For instance, if the slider value is 3, the displayed curve corresponds to the total number of cases prediction made 3 days sooner.

# Data Source

The data rely on the data from the European Center for Disease Control and Prevention. The European CDC publishes daily statistics on the COVID-19 pandemic. Not just for Europe, but for the entire world. [ECDC website](https://www.ecdc.europa.eu/en),  [data](https://covid.ourworldindata.org/data/ecdc/full_data.csv).



# Predictions

The total number of Covid 19 cases is predicted using the [Verhulstthe model](https://en.wikipedia.org/wiki/Logistic_function), originally developed for growth modelling. We'll assume the total number of Covid 19 cases follows :

$$ f(t)=K \frac{1}{1+e^{-r(t - t_0)}} $$

$$ \cdot \ t_{0}= $$ the value  of the sigmoid's midpoint \\
$$\cdot \ K= $$ the capacity, here the maximum number of people infected \\
$$\cdot \ r=$$ the logistic growth rate or steepness of the curve 

## Model fitting

The model is fitted to minimise the mean squared error (MSE):

$$ (t_0^{\star}, K^{\star}, r^{\star}) \in argmin \sum_{i=1}^{n}\big(y_i - f(t_i)^2\big) $$ 

When the capacity $$ K $$ is known, this model can be fitted using a linear regression transforming $$ f(t) $$ in  $$ g(t) = logit (\frac{f(t)}{K}) $$. 

$$ \operatorname{logit}\left(\frac{1}{1+e^{-r(t - t_0)}}\right)=\ln \left(\frac{1}{e^{-r(t - t_0)}}\right)= r t - t_0 $$

Here, $$ K $$ is unknown, and the model need to be fitted with numerical optimisation. Still, under reasonable conditions existence of optimal parameters exists. [paper](https://www.sciencedirect.com/science/article/abs/pii/S0096300395002510)

The [Nelder-Mead](https://en.wikipedia.org/wiki/Nelder–Mead_method) optimisation algorithm is used to find the optimum parameters.

## Parameters distribution

The estimation of optimum parameters distribution is computed with a **Bootstrap** method. The distribution used to sample the parameters is linear, granting more importance to recent values than old ones. The central curve of the prediction is obtained with the median parameters and the upper and lower are obtained respectively with the 1st and 3rd quantiles.

