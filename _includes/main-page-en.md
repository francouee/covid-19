

# Chart usage

The chart show the evolution of COVID-19 for:

1. <span style="color:#1f77b4">**Total number of cases**</span> (left axis)
2. <span style="color:#ff7f0e">**New cases**</span> (right axis)
3. <span style="color:#d62728">**Total number of deaths**</span>  (right axis)
4. <span style="color:#8c564b">**New deaths**</span>  (right axis)

The top part of the graph allows to:

* Select the displayed **country** for the curves

* Show the  total number of cases  **predictions** made by the model explained next section.

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

{% include image.html url="../img/pairplot-parameters.png" description="Parameters distribution" width="60%" %}

# Future work

* Note about Verhulstthe model:

Verhulstthe model is unstable during the exponential growth of the virus . The model tend to underestimate the virus  growth phase. 

## New growth modeling

The model concist to have two growth mode of the virus: 

1. Exponential growth: $$ f(t) = e^{r_1t} $$
2. Logistic growth: $$ f(t)=K \frac{1}{1+e^{-r(t - t_0)}} $$

The total number of cases in the final model is:

$$ f(t) = (1-y(t)) \ e^{r_1t} + y(t) \ \big(\ a +  K \frac{1}{1+e^{-r_2(t - t_0)}} \big) $$

$$ \cdot \ y(t)= 0 $$ during the exponential growth, 1 otherwise.

This modelisation allows to tale into acount the phase before and after **containment** measures with the $$y(t)$$ variable.  The difficulty relies on the estimaiton of time $$t_1$$ when this variable change from $$0$$ to $$1$$.

In order to preserve both the function and it's derivative continuity for $$ t=t_1 $$  ($$  y(t_1)_-=0 $$ and $$ y(t_1)_+=1 $$) it is needed that:

1. $$ f(t{_1})_- = f(t{_1})_+ \implies a  = e^{r_1t} - K \frac{1}{1+e^{-r_2(t_1 - t_0)}}  $$
2. $$  f'(t{_1})_- = f'(t{_1})_+ \implies   K= \frac{r_1}{r_2} \  e^{r_1t} \  \frac{ 1+e^{ - r_2 (t_1 - t_0) }}{1 - \frac{1}{1+e^{-r_2(t_1 - t_0)}}} $$ 

{% include image.html url="../img/difs-two-models.png" description="Différence between models" width="90%" %}