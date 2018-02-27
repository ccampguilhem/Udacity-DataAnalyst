/*
 * Global variables
 */
//GeoJSON data
var geoData = null;
//Routes data
var routesData = null;
// Projection for map
var projection = null;
//Number of cuts in route length
var nbCuts = 3;
//Size for airports circle
var minSizeAirport = 1;
var maxSizeAirport = 20;
//Stroke width for routes
var minSizeRoute = 0.1;
var maxSizeRoute = 2.0;
//Transitions
var shortTransition = 200;
var mediumTransition = 500;
var longTransition = 4000;
var animationTransition = 2000;
//User-defined selections
var currentAirportSelection = null;
var currentMinLength = null;
var currentMaxLength = null;

/*
 * Main drawing function
 *
 * - data: GeoJSON data loaded from html page
 */
function draw(data) {
    
    "use strict";

    geoData = data;

    //Load routes dataset
    d3.csv("routes.csv", function(d) {
        //converts string to numeric value
        d["Distance"] = +d["Distance"]; 
        d["Flights"] = +d["Flights"];
        d["OriginLat"] = +d["OriginLat"];
        d["OriginLong"] = +d["OriginLong"];
        d["DestLat"] = +d["DestLat"];
        d["DestLong"] = +d["DestLong"];
        return d;
        }, callbackRoutes);
}

/*
 * Callback method for routes data
 *
 * - data: routes dataset
 */
function callbackRoutes(data) {

    //Save routes data
    routesData = data;

    //Play introduction
    playIntroduction();
}

/*
 * Introduction of animation
 */
function playIntroduction() {

    //Create containers for introduction
    var main = d3.select("div#main");
    var intro = main.append("div")
        .attr("class", "row")
        .attr("id", "intro")
        .style("text-align", "justify")
        .append("div")
        .attr("class", "col-md-12");
    var panel = intro.append("div")
        .attr("id", "panel")
        .style("margin-top", "250px");
    var notes = intro.append("div")
        .attr("id", "notes")
        .style("text-align", "center")
        .style("margin-top", "50px");

    //Display messages
    d3.select("#panel")
        .append("h5")
        .html(`The following visualization shows the organisation of US domestic flights in 2008
            and use of different types of aircrafts.`);
    d3.select("#panel")
        .append("br")
    d3.select("#panel")
        .append("h5")
        .html(`Each route is represented by a line. The thickness indicates the number of flights 
            on that route. Airports are shown as dots which size depends on number of flights 
            from or to that airport.`);
    d3.select("#panel")
        .append("br");
    d3.select("#panel")
        .append("h5")
        .html(`The animation displays routes per group of route length starting with shorter ones.
            Then, it shows the traffic from/to the five biggest airports in US.`);
    d3.select("#panel")
        .append("br");
    d3.select("#panel")
        .append("h5")
        .html(`Once animation is completed, use the <span class="text-primary">slider</span> to 
            filter route by lengths. <span class="text-primary">Hover</span> an airport to display 
            additional information. <span class="text-primary">Click</span> on the dot to filter 
            traffic for that airport. <span class="text-primary">Click</span> again to restore 
            previous display.`);
    d3.select("#panel")
        .append("br");
    d3.select("#panel")
        .append("div")
        .style("text-align", "center")
        .append("button")
        .attr("type", "button")
        .attr("class", "btn btn-primary btn-lg")
        .style("text-align", "center")
        .html("Got it !")
        .attr("onclick", "stopIntroduction()");
    d3.select("#notes")
        .append("p")
        .html(`<small>The GeoJSON data used is taken from 
            <a href="https://github.com/PublicaMundi/MappingAPI">PublicaMundi</a>.<br>
            Uses the Darkly theme from <a href="https://bootswatch.com/">bootswatch.com</a>.<br>
            Uses D3.js v4 <a href="https://d3js.org/">library</a>.<br>
            The Jupyter notebook used to prepare the dataset for visualization may be found 
            <a href="https://github.com/ccampguilhem/Udacity-DataAnalyst/blob/master/07-DataVisualization/P06-MakeEffectiveDataVisualization/effective_visualization.ipynb">here</a>.
            </small>`);                        
}

function stopIntroduction() {
    
    //Fade out and destroy containers
    d3.select("#intro")
        .transition()
        .duration(mediumTransition)
        .on("end", function() {
            d3.select("div#intro").remove();
            drawMap();
        })
        .style("opacity", 0);
}

/*
 * Draw map
 */
function drawMap() {

    //Create container for status bar
    d3.select("div#main")
        .append("div")
        .attr("class", "row status")
        .append("div")
        .attr("class", "col-md-12")
        .append("h6")
        .style("text-align", "center")
        .style("margin-top", "20px")
        .html("No route displayed.");

    //Create container for svg
    d3.select("div#main")
        .append("div")
        .attr("class", "row")
        .attr("id", "center")
        .append("div")
        .attr("class", "col-md-10")
        .append("div")
        .attr("class", "map");

    //Draw GeoJSON map
    var margin = 10,
        width = 1140 - margin,
        height = 575 - margin;

    var svg = d3.select("div.map")
        .append("svg")
        .attr("width", width + margin)
        .attr("height", height + margin)
        .append("g")
        .attr("class", "states")

    projection = d3.geoAlbers()
        .scale(1250)
        .translate([460., 280.]);
    var path = d3.geoPath().projection(projection);

    var map = svg.selectAll("path")
        .data(geoData.features)
        .enter()
        .append("path")
        .style("opacity", 0)
        .attr("d", path)
        .transition()
        .duration(shortTransition)
        .style("opacity", 1);

    setTimeout(playAnimation, shortTransition);
}

/*
 * Play animation
 */
 function playAnimation() {

    //Calculate cuts
    var cuts = calculateCuts(routesData, nbCuts);
    //console.log("callbackRoutes.cuts:", cuts);

    //Tool tip for airports
    var tooltip = d3.select("div.map")
        .append("div")   
        .attr("class", "tooltip")
        .style("opacity", 0);

    //Routes
    var routes = d3.select("div.map")
        .select("svg")
        .append("g")
        .attr("class", "routes");

    //Circles for airports
    var svg = d3.select("div.map")
        .select("svg")
        .append("g")
        .attr("class", "circles");

    //Container for controls
    var controls = d3.select("div#center")
        .append("div")
        .attr("class", "col-md-2")
        .style("visibility", "hidden");

    //Controls
    minLengthControl = controls.append("div")
        .attr("class", "form-group")
        .append("fieldset");
    minLengthControl.append("label")
        .attr("class", "control-label")
        .attr("for", "minLengthInput")
        .html("Min route length:");
    minLengthControl.append("input")
        .attr("type", "number")
        .attr("id", "minLengthInput")
        .attr("min", cuts[0])
        .attr("max", cuts[nbCuts])
        //.attr("step", "100")
        .attr("value", cuts[0])
        .on("input", function() { currentMinLength = +this.value; });
    currentMinLength = cuts[0];
    maxLengthControl = controls.append("div")
        .attr("class", "form-group")
        .append("fieldset");
    maxLengthControl.append("label")
        .attr("class", "control-label")
        .attr("for", "maxLengthInput")
        .html("Max route length:");
    maxLengthControl.append("input")
        .attr("type", "number")
        .attr("id", "maxLengthInput")
        .attr("min", cuts[0])
        .attr("max", cuts[nbCuts])
        //.attr("step", "100")
        .attr("value", cuts[nbCuts])
        .on("input", function() { currentMaxLength = +this.value; });
    currentMaxLength = cuts[nbCuts];
    applyButton = controls.append("button")
        .attr("type", "submit")
        .attr("class", "btn btn-primary")
        .attr("id", "apply")
        .html("Apply")
        .on("click", function() {
            if (currentMinLength > currentMaxLength) {
                currentMinLength = currentMaxLength - 1;
                document.getElementById("minLengthInput").value = currentMinLength.toString();
            }
            update(routesData, currentMinLength, currentMaxLength, currentAirportSelection);
        });

    //Bind enter key to apply button
    //from https://stackoverflow.com/a/39318404/8500344
    document.onkeydown = function (e) {
        e = e || window.event;
        switch (e.which || e.keyCode) {
            case 13 : //Your Code Here (13 is ascii code for 'ENTER')
                document.getElementById("apply").click();
            break;
  }
}

    //Prepare data for animation
    var animationData = [];
    for (i = 1; i <= nbCuts; i++) {
        animationData.push({
            "minLength": cuts[i-1],
            "maxLength": cuts[i],
            "airport": null}
            );
    }
    big5 = ["William B Hartsfield-Atlanta Intl", "Chicago O'Hare International", "Denver Intl", 
            "Phoenix Sky Harbor International", "Los Angeles International"];
    for (i = 0; i < big5.length; i++)
    animationData.push({
        "minLength": cuts[0],
        "maxLength": cuts[nbCuts],
        "airport": big5[i]}
        );
    animationData.push({
        "minLength": cuts[0],
        "maxLength": cuts[nbCuts],
        "airport": null});

    //Routes animation
    setTimeout(function(){ 
        var i = 0;
        update(routesData, animationData[i].minLength, animationData[i].maxLength, 
            animationData[i].airport);
        var interval = setInterval(function(){
            //this function is called at specified time intervals    
            i++;
            if (i >= animationData.length) {
                //Make controls visible
                controls.style("visibility", "visible");
                //stops the iteration
                clearInterval(interval);
            } else {
                update(routesData, animationData[i].minLength, animationData[i].maxLength,
                    animationData[i].airport);
            }
        }, animationTransition);
        }
    , animationTransition);
 }

 /*
 * Create a cut array for route length
 *
 * The cut is made using quantiles of route length. If nbcuts is 4, the routes are cut in quartiles.
 * If nbcuts is 10, the routes are cut in deciles,...
 *
 * - data: routes dataset
 * - nbCuts: number of cut to make
 * - return: an array with cut values
 */
function calculateCuts(data, nbCuts) {
    
    //Calculate quantiles for routes animation
    var routes = d3.nest()
        // group by Route
        .key(function(d) { return d["Route"]; })
        // aggregate (get first distance)
        .rollup(function(v) { return v[0]["Distance"]; })
        .entries(data) // bind data
    
    //Create an array with distances
    var lengths = [];
    for (i = 0; i < routes.length; i++) {
        lengths.push(routes[i].value);
    }

    //Cuts
    var value = 0.;
    var cuts = [];
    for (i = 0; i <= nbCuts; i++) {
        value = i * (1. / nbCuts);
        cuts.push(d3.quantile(lengths, value));
    }
    return cuts;
}

/* 
 * Aggregation function for airports
 *
 * - data: airport group data
 * - return: object with aggregated value for airport
 */
function aggregateAirports(data) {
    return {
        "OriginLat": data[0]["OriginLat"],
        "OriginLong": data[0]["OriginLong"],
        "OriginCity": data[0]["OriginCity"],
        "OriginState": data[0]["OriginState"],
        "DestLat": data[0]["DestLat"],
        "DestLong": data[0]["DestLong"],
        "DestCity": data[0]["DestCity"],
        "DestState": data[0]["DestState"],
        "Flights": d3.sum(data, function(d) { return d["Flights"]; })
    };
}

/* 
 * Create airports dataset
 *
 * - data: route dataset
 * - minLength: minimal route length to consider
 * - maxLength: maximal route length to consider
 * - selectedAirport: filter only routes including this airport
 * - return: airports dataset
 */
function createAirportsDataset(data, minLength=0, maxLength=999999, selectedAirport=null) {

    //Filter routes by length
    //console.log("createAirportsDataset.data", data);
    //console.log("createAirportsDataset.minLength: ", minLength);
    //console.log("createAirportsDataset.maxLength: ", maxLength);
    var filtered = data.filter(function(d) {
        if (selectedAirport === null) {
            return (d["Distance"] >= minLength) && (d["Distance"] <= maxLength);
        } else {
            var bool1 = (d["Distance"] >= minLength) && (d["Distance"] <= maxLength);
            var bool2 = (d["OriginAirport"] === selectedAirport) ||
                    (d["DestAirport"] === selectedAirport)
            return bool1 && bool2;
        }
        
    })
    //console.log("createAirportsDataset.filtered", filtered);

    //Group by airports
    var airportsAgg = d3.nest()
        //group by origin airport
        .key(function(d) { return d["OriginAirport"]; })
        //group by destination airport
        .key(function(d) { return d["DestAirport"]; })
        //aggregate
        .rollup(aggregateAirports)
        //bind filtered data
        .entries(filtered)
    //console.log("createAirportsDataset.airportsAgg", airportsAgg);

    //Calculate number of flights per airport (need to sum origin and dest airports)
    var airportsDict = {};
    for (i = 0; i < airportsAgg.length; i++) {
        var from = airportsAgg[i].key;
        if (!(from in airportsDict)) {
            airportsDict[from] = {
                "Flights": 0,
                "Latitude": airportsAgg[i].values[0].value.OriginLat,
                "Longitude": airportsAgg[i].values[0].value.OriginLong,
                "City": airportsAgg[i].values[0].value.OriginCity,
                "State": airportsAgg[i].values[0].value.OriginState}
        }
        var values = airportsAgg[i].values;
        for (j = 0; j < values.length; j++) {
            var to = values[j].key;
            var flights = values[j].value.Flights;
            if (!(to in airportsDict)) {
                airportsDict[to] = {
                    "Flights": 0,
                    "Latitude": values[j].value.DestLat,
                    "Longitude": values[j].value.DestLong,
                    "City": values[j].value.DestCity,
                    "State": values[j].value.DestState}
            }
            airportsDict[from].Flights += flights;
            airportsDict[to].Flights += flights;
        }
    }
    //console.log("createAirportsDataset.airportsDict", airportsDict);

    //Generate airports dataset
    var airports = [];
    for (name in airportsDict) {
        var item = {
            "Airport": name,
            "Flights": airportsDict[name].Flights,
            "Latitude": airportsDict[name].Latitude,
            "Longitude": airportsDict[name].Longitude,
            "City": airportsDict[name].City,
            "State": airportsDict[name].State,
            "Coords": projection([airportsDict[name].Longitude, airportsDict[name].Latitude]),
            };
        airports.push(item);
    }

    //Sort array (decreasing flights)
    function compareAirports(a, b) {
        if (a.Flights < b.Flights) {
            return -1;
        } else if (a.Flights > b.Flights) {
            return 1;
        } else {
            return 0;
        }
    }
    airports.sort(compareAirports);
    airports.reverse();
    return airports;
}

/*
 * Update the map with route dataset
 *
 * - data: route dataset
 * - minLength: minimal route length to consider
 * - maxLength: maximal route length to consider
 * - selectedAirport: filter only routes including this airport
 */
function update(data, minLength, maxLength, selectedAirport=null) {

    //Update status
    var statusText;
    if (selectedAirport === null) {
        statusText = "Routes between " + minLength.toFixed() + " and " + 
                    maxLength.toFixed() + " nautic miles.";
    } else {
        statusText = "Routes between " + minLength.toFixed() + " and " + 
                    maxLength.toFixed() + " nautic miles from or to " + 
                    selectedAirport + ".";
    }
    var status = d3.select("div.status")
            .select("h6")
            .html(statusText);

    //Update routes
    updateRoutes(data, minLength, maxLength, selectedAirport);

    //Update airports
    updateAirports(data, minLength, maxLength, selectedAirport);
}

/*
 * Update the airports on the map
 *
 * - data: route dataset
 * - minLength: minimal route length to consider
 * - maxLength: maximal route length to consider
 * - selectedAirport: filter only routes including this airport
 */
function updateAirports(data, minLength, maxLength, selectedAirport=null) {
    
    //Calculate min and max number of flights (used for scaling)
    var airports = createAirportsDataset(data);
    maxFlights = d3.max(airports, function(d) { return d.Flights; });
    minFlights = d3.min(airports, function(d) { return d.Flights; });

    //Create scales
    console.log("updateAirports.{minFlights,maxFlights}", minFlights, maxFlights);
    var flightsScale = d3.scaleSqrt()
        .domain([minFlights, maxFlights])
        .range([minSizeAirport, maxSizeAirport]);

    //Create airports dataset
    airports = createAirportsDataset(data, minLength, maxLength, selectedAirport);
    console.log("updateAirports.airports: ", airports);

    //Select svg groups
    var svg = d3.select("div.map")
        .select("svg")
        .select("g.circles");

    var tooltip = d3.select("div.map")
        .select("div.tooltip")

    //Draw circles
    var circles = svg.selectAll("circle")
        //Bind data and uses airport name as identifier
        .data(airports, function(d) { return d.Airport; });
        
    //Remove all circles already on the page and not filtered anymore
    circles.exit() //select all elements leaving the page
        .transition()
        .duration(mediumTransition)
        .attr("r", 0)
        .remove();
    
    //Append new circles (the one which has been filtered in)
    circles.enter() //only select the new elements
        .append("circle")
        .on("mouseover", function (d) {
            tooltip.transition()
                .duration(shortTransition)
                .style("opacity", 0.7);
            tooltip.html("Airport: " + "<i>" + d.Airport + "</i>" + "<br>" + 
                "City: " + "<i>" + d.City + "</i>" + "<br>" + 
                "State: " + "<i>" + d.State + "</i>" + "<br>" + 
                "Number of flights: " + "<i>" + d.Flights + "</i>" + "<br>")
                .style("left", d.Coords[0] + 30 + "px")
                .style("top", d.Coords[1] - 20 + "px");
            d3.select(this)
                .style("cursor", "pointer")
                .transition()
                .duration(shortTransition)
                .style("fill", "#00BC8C");
        })
        .on("mouseout", function (d) {
            tooltip.transition()
                .duration(shortTransition)
                .style("opacity", 0.0);
            d3.select(this)
                .style("cursor", "default")
                .transition()
                .duration(shortTransition)
                .style("fill", "white");
        })
        .merge(circles) //select new elements and the elements already there
        .on("click", function (d) {
            if (currentAirportSelection === d.Airport) {
                currentAirportSelection = null;
                update(data, minLength, maxLength);
            } else {
                currentAirportSelection = d.Airport;
                update(data, minLength, maxLength, d.Airport);
            }
        })        
        .attr("cx", function(d) { return d.Coords[0]; })
        .attr("cy", function(d) { return d.Coords[1]; })
        .transition()
        .duration(mediumTransition)
        .attr("r", function(d) { return flightsScale(d.Flights); })
}

/* 
 * Aggregation function for routes
 *
 * - data: airport group data
 * - return: object with aggregated value for routes
 */
function aggregateRoutes(data) {
    return {
        "OriginLat": data[0]["OriginLat"],
        "OriginLong": data[0]["OriginLong"],
        "DestLat": data[0]["DestLat"],
        "DestLong": data[0]["DestLong"],
        "Flights": d3.sum(data, function(d) {
            return d["Flights"];
        })
    };
}

/*
 * Create routes dataset
 *
 * - data: route dataset
 * - minLength: minimal route length to consider
 * - maxLength: maximal route length to consider
 * - selectedAirport: filter only routes including this airport
 * - return: routes dataset
 */
function createRoutesDataset(data, minLength=0, maxLength=999999, selectedAirport=null) {
    
    //Filter routes by length
    //console.log("createRoutesDataset.data", data);
    //console.log("createRoutesDataset.minLength: ", minLength);
    //console.log("createRoutesDataset.maxLength: ", maxLength);
    var filtered = data.filter(function(d) {
        if (selectedAirport === null) {
            return (d["Distance"] >= minLength) && (d["Distance"] <= maxLength);
        } else {
            var bool1 = (d["Distance"] >= minLength) && (d["Distance"] <= maxLength);
            var bool2 = (d["OriginAirport"] === selectedAirport) ||
                    (d["DestAirport"] === selectedAirport)
            return bool1 && bool2;
        }
    })
    console.log("createRoutesDataset.filtered", filtered);

    //Group by routes
    var routesAgg = d3.nest()
        //group by routes
        .key(function(d) { return d["Route"]; })
        //aggregate
        .rollup(aggregateRoutes)
        //bind filtered data
        .entries(filtered)

    console.log("createRoutesDataset.routesAgg", routesAgg);

    //Generate routes dataset
    var routes = [];
    for (i = 0; i < routesAgg.length; i++) {
        var item = {
            "Route": routesAgg[i].key,
            "Flights": routesAgg[i].value.Flights,
            "FromLatitude": routesAgg[i].value.OriginLat,
            "FromLongitude": routesAgg[i].value.OriginLong,
            "ToLatitude": routesAgg[i].value.DestLat,
            "ToLongitude": routesAgg[i].value.DestLong,
            };
        routes.push(item);
    }
    return routes;
}

/*
 * Update the routes on the map
 *
 * - data: route dataset
 * - minLength: minimal route length to consider
 * - maxLength: maximal route length to consider
 * - selectedAirport: filter only routes including this airport
 */
function updateRoutes(data, minLength, maxLength, selectedAirport=null) {

    //Calculate min and max number of flights (used for scaling)
    var routes = createRoutesDataset(data);
    maxFlights = d3.max(routes, function(d) { return d.Flights; });
    minFlights = d3.min(routes, function(d) { return d.Flights; });
    console.log("updateRoutes.{minFlights,maxFlights}", minFlights, maxFlights);

    // Create routes dataset
    routes = createRoutesDataset(data, minLength, maxLength, selectedAirport);
    console.log("updateRoutes.routes: ", routes);

    //Select svg group
    var svg = d3.select("div.map")
        .select("svg")
        .select("g.routes");

    //Create a path generator
    var pathGenerator = d3.geoPath()
        .projection(projection)

    //Create scale for route width
    var routesScale = d3.scaleLinear()
        .domain([minFlights, maxFlights])
        .range([minSizeRoute, maxSizeRoute]);

    //Create routes
    var paths = svg.selectAll("path")
        //bind data and select route as identifier
        .data(routes, function(d) { return d.Route; });

    //Remove all paths already on the page
    paths.exit() // select all elements already in the page not in the filter :)
        .transition()
        .duration(mediumTransition)
        .style("stroke-width", 0)
        .remove() // remove all elements selected by exit
    
    //Append new paths (the ones which have been filtered in)
    paths.enter()
        .append("path")
        .attr("class", "route")
        .attr("d", function(d) {
            //Generate a GeoJSON LineString object
            var line = {
                "type": "LineString",
                "coordinates": [
                    [d.FromLongitude, d.FromLatitude], 
                    [d.ToLongitude, d.ToLatitude]
                    ]
                };
            return pathGenerator(line);
            })
        .attr("route", function(d) { return d.Route; })
        .style("stroke-width", 0)
        .transition()
        .duration(mediumTransition)
        .style("stroke-width", function(d) { return routesScale(d.Flights); })
}