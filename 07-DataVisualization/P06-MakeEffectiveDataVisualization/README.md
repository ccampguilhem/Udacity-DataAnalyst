# Make Effective Data Visualization

[Cédric Campguilhem](https://github.com/ccampguilhem), February 2018

# Summary

# Design

# Feedback

# Resources

I obviously used a lot of resources to build the visualization, in addition to the ones provided during the course.

The most obvious ones:

- D3 js [documentation](https://github.com/d3/d3/blob/master/API.md#d3-api-reference). Especially required as I switched to 
  v4 which has minor and major differences with v3 (new `merge` function).
- I used a bootstrap template for the page as I didn't want to struggle too much about positioning, styling texts and 
  controls... I used Darkly theme from [bootswatch.com](https://bootswatch.com/">bootswatch.com).
- As I had no experience in html/css, I followed the Html/Css introduction course from Udacity which introduced bootstrap to 
  me, before starting the data analyst course.
- I got the map from [PublicaMundi](https://github.com/PublicaMundi/MappingAPI">PublicaMundi).

All the data wrangling, and exploratory data analysis has been made in a Jupyter notebook with `pandas` and `seaborn` mainly. 
The Jupyter notebook itself provides references used for the analysis in the appendix section. You can check the notebook from 
[here](https://github.com/ccampguilhem/Udacity-DataAnalyst/blob/master/07-DataVisualization/P06-MakeEffectiveDataVisualization/effective_visualization.ipynb).

Then I used JavaScript, css and svg documentation from [Mozilla.org](https://developer.mozilla.org) and 
[w3schools.com](https://www.w3schools.com). For svg properties, elements, CSS styling, and JavaScript reference. More often than 
not, the links to this documentation was provided in Stack Overflow questions and answers. There are too many to give a list 
but I have basically duplicated the solution in this [thread](https://stackoverflow.com/a/39318404/8500344) to code the ENTER 
key binding to a button in my page.

The [d3noob](https://bl.ocks.org/d3noob) helped me quite a lot understaning the way `merge` works in v4 as `update` has been 
removed. I also found very usefull this step by step [tutorial](https://www.digitalocean.com/community/tutorials/getting-started-with-data-visualization-using-javascript-and-the-d3-library) 
for making a bar chart.

I really wanted to give a try to a slider to filter route length but really struggled to implement it. I haven't tried yet 
with this [one](https://refreshless.com/nouislider/) which seems promising.

I also use GeoJSON [documentation](http://wiki.geojson.org) to undertand what to provide to `d3.geoPath` function to display 
routes on the map.

Finally, I relied a lot on [Wikipedia](https://en.wikipedia.org) and [Airfleets.net](http://www.airfleets.net) for data cleaning.

