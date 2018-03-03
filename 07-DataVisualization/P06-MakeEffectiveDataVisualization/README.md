# Make Effective Data Visualization

[Cédric Campguilhem](https://github.com/ccampguilhem), February 2018

# Summary

I mainly want to share some intersting findings in the way aeronautic US traffic is organized as a decentralized system
 dominated by Boeing aircrafts:
- location of big airports in a east to west line,
- not so much big airports on east and west coasts,
- popular routes do not necessarily start or end in the biggest airports,
- mostly Boeing aircafts are used but some routes and airports show different proportions.

# Design

During my exploratory analysis I clearly missed a "geographical" display of information to better understand the way 
traffic is organized. Displaying information on a map was a no-brainer. This also enables to encode "location" of 
routes and airports in a natural way using spatial positionning.

The initial datasets contains more than 7 millions of flights. I anticipated it would cause some refresh performance 
issues (I might be wrong though).
Besides, as I do not have the exact route but only the start and end points this would lead to either draw the same line 
multiple times without added value or to use kind of jittering with potential issues of overplotting. That's why I 
have aggregated data by routes and orient the information displayed to *number of flights*.

I chosed to use size of circles to encode *number of flights* for airports, thickness of line for routes, and size 
of bars for aircraft manufacturers.

I wanted to limit use of colors to a minimum. I kept different color for airports hovering to highlight the fact 
it may be clicked. I also used color for the bar chart for contrast reason (labels are white on both sides of the 
bar).

I wanted to use a dark theme and to have a map "illuminated" by flights like night pictures from Earth taking from space. 
That's why I have selected a white color for airports and routes while using a low contrast map of united states.

I wanted to use D3 js and do everything using html as it would be an opportunity for me to learn something that I am 
not at all familiar with! Event if I struggled a with d3 design at first, I find it elegant and gallery really 
shines and show that library has a lot of potential ! Using v4 was a deliberate choice, at the cost of sometimes only 
finding examples for v3 version.

# Feedback

## Feedback 1

Text on introduction is too bright. On map, it's not obvious you can click on airports to filter map. and once an aircraft 
has been selected it's not obvious to know that you have to click again to unselect. It could be great to unselect by clicking 
anywhere on the map. The controls to filter route length do not show clearly which are the default settings. The bar chart is 
not clear: is it the number of aircrafts by manufacturer used on that routes or is it the number of flights ? It's nearly 
impossible to focus on the map and on the bart chart at the same time during the animation.

## Feedback 2

The bar chart shall make more visible what is the proportion of flights for a given aircraft manufacter for the selected 
routes. Introduction text is unclear about what the main message is. It could be a good idea to filter aircrafts as well, for 
example by displaying in a different color the flights where aircraft is used. It could be a good idea to add a filter on 
number of flights as well so that it's easier to see what are the main routes: the animation by route length spreads the 
information on multiple frames. Why not allowing multiple selections for airports and aircrafts ?

## Feedback 3

It's not intuitive to know how to unselect an airport. Besides, if you don't know well the geography of United States it 
could be helpfull to have a list in controls to select airports by name (using a text filter if list is too long to search).
The map lacks visibility when all routes and airports are displayed. What is the use of having states with a different color
 while hovering? The controls to filter route length is not intuitive. You could also have a menu to select the aircrafts 
to filter. A filter for flights number could be added. The map area is too "white", why not using scale colors for airport 
traffic instead of only size? Same remark for the route length with a color scale as well. As the instructions are on the 
previous page, it's not easy to remember all: it shall be possible to display the help from main page. When selecting an 
item (airport, aircraft) it could be good to have a switch option either to remove the filtered-out elements from display 
or to change the color of filtered-in elements.

## What I decided to include

There are some "cheap" improvements:

- remove brightness of introduction text,
- introduce a new shape of mouse pointer to make more visible airports may be clicked, and make sure that a click anywhere
  unselects,
- introduce a reset button to restore full display,
- remove hover effect on states,
- add a title to the bar chart.

To improve visualization I consider some feedback as essential:

- make message more visible and adapt animation to message,
- slow the animation down so that map and bar chart may be seen (or disable bar chart if not essential to the message being 
  displayed,
- add help text on the main page,
- allow filtering by aircrats to better see the use of aircrafts by airports/routes,
- implement a filter on number of flights to better see the most popular routes,
- multiple selections for airports and aircrafts.

There are some feedback I will not take into account:

- modification of bar chart to see the proportion: I am a bit sceptical about the visibility as bars would be very small,
- menu list for airport selection: I am afraid to spend too much time with it due to my knowledge in html,
- changing the control to filter route length: I've tried to add a range slider instead without success due to JQuery 
  compatibility issues,
- color scales: I specifically wanted to avoid using colors too much, I would prefer stick to my initial idea,
- using an optional color overlay instead of removing items when filtering: that would be a bigger change in my code and 
  I prefer to keep project to reasonable time investment.

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

