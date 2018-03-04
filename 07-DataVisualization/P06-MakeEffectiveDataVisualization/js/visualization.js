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
//Bar charts
var minSizeBar = 0;
var maxSizeBar = 600;
//Transitions
var shortTransition = 200;
var mediumTransition = 500;
var longTransition = 4000;
var animationTransition = 4000;
//User-defined selections
var userSelection = new RouteFilter();

/*
 * Entry point (called from HTML code)
 *
 * - data: GeoJSON data loaded from html page
 */
function entryPoint(data) {
    
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
            and use of different aircraft manufacturers. The data is taken from 
            <a href="http://stat-computing.org/dataexpo/2009/">http://stat-computing.org</>.`);
    d3.select("#panel")
        .append("br")
    d3.select("#panel")
        .append("h5")
        .attr("class", "text-warning")
        .html("It shows a decentralized traffic dominated by Boeing aircrafts.")
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
        .append("div")
        .style("text-align", "center")
        .append("button")
        .attr("type", "button")
        .attr("class", "btn btn-primary btn-lg")
        .attr("id", "gotit")
        .style("text-align", "center")
        .html("Got it !")
        .on("click", stopIntroduction);
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

/*
 * Stop introduction and transition to animation
 */
function stopIntroduction() {
    
    //Fade out and destroy containers
    d3.select("#intro")
        .transition()
        .duration(mediumTransition)
        .on("end", function() {
            d3.select("div#intro").remove();
            createPageLayout();
            draw();
            prepareAnimation();
        })
        .style("opacity", 0);
}

/*
 * Create page layout
 */
function createPageLayout() {
    //Overall page
    var overall = d3.select("div#main")
        .append("div")
        .attr("class", "row");

    //Content part (status + map + bottom)
    var content = overall.append("div")
        .attr("class", "col-md-10")
        .attr("id", "content");
    content.append("div")
        .attr("class", "row")
        .attr("id", "status")
        .style("height", "50px")
        .append("div")
        .attr("class", "col-md-12")
        .style("text-align", "center")
        .append("h5")
        .style("margin-top", "20px");
    content.append("div")
        .attr("class", "row")
        .attr("id", "map");
    content.append("div")
        .attr("class", "row")
        .attr("id", "bottom")
        .style("visibility", "hidden");

    //Controls part
    var controls = overall.append("div")
        .attr("class", "col-md-2")
        .attr("id", "controls")
        .style("visibility", "hidden");
}

/*
 * Draw visualization elements
 */
function draw() {
    drawMap();
    drawBarChart();
    setTimeout(playAnimation, shortTransition); 
}

/*
 * Draw map
 */
function drawMap() {

    //Draw GeoJSON map
    var margin = 10,
        width = 950 - margin,
        height = 575 - margin;

    var svg = d3.select("div#map")
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
        .data(geoData.features, function(d){
            return d.properties.name;
        })
        .enter()
        .append("path")
        .style("opacity", 0)
        .attr("d", path)
        .attr("class", "state")
        .transition()
        .duration(shortTransition)
        .style("opacity", 1);
}

/*
 * Draw bar chart
 */
function drawBarChart() {

    //Create container for svg
    var container = d3.select("div#bottom");
    container.append("h6")
        .html("Number of flights by aircraft manufacturer:")
        .style("margin-left", "210px");
    container.append("div")
        .attr("class", "bar");

    //Draw bar chart
    var margin = 10,
        width = 950 - margin,
        height = 250 - margin;

    var svg = d3.select("div.bar")
        .append("svg")
        .attr("width", width + margin)
        .attr("height", height + margin);
}

/*
 * Prepare animation elements
 */
function prepareAnimation() {
    //Prepare animation elements
    var cuts = calculateCuts(routesData, nbCuts);
    //console.log("callbackRoutes.cuts:", cuts);

    //Tool tip for airports
    var tooltip = d3.select("div#map")
        .append("div")   
        .attr("class", "tooltip")
        .style("opacity", 0);

    //Routes
    var routes = d3.select("div#map")
        .select("svg")
        .append("g")
        .attr("class", "routes");

    //Circles for airports
    var svg = d3.select("div#map")
        .select("svg")
        .append("g")
        .attr("class", "circles");

    //Bar chart
    var bars = d3.select("div.bar")
        .select("svg")
        .append("g")
        .attr("class", "bars");
    var ticks = d3.select("div.bar")
        .select("svg")
        .append("g")
        .attr("class", "ticks");
    var labels = d3.select("div.bar")
        .select("svg")
        .append("g")
        .attr("class", "labels");

    //Container for controls
    var controls = d3.select("div#controls");

    //Route length controls
    var routeControl = controls.append("div")
        .attr("class", "form");

    routeControl.append("legend")
        .html("Controls");

    var minLengthInput = routeControl.append("div")
        .attr("class", "form-group");
    minLengthInput.append("label")
        .attr("class", "control-label")
        .attr("for", "minLengthInput")
        .html("Min route length:");
    minLengthInput.append("input")
        .attr("type", "number")
        .attr("id", "minLengthInput")
        .attr("min", cuts[0])
        .attr("max", cuts[nbCuts])
        .attr("value", cuts[0]);

    var maxLengthInput = routeControl.append("div")
        .attr("class", "form-group");
    maxLengthInput.append("label")
        .attr("class", "control-label")
        .attr("for", "maxLengthInput")
        .html("Max route length:");
    maxLengthInput.append("input")
        .attr("type", "number")
        .attr("id", "maxLengthInput")
        .attr("min", cuts[0])
        .attr("max", cuts[nbCuts])
        .attr("value", cuts[nbCuts]);

    var flightInput = routeControl.append("div")
        .attr("class", "form-group");
    flightInput.append("label")
        .attr("class", "control-label")    
        .attr("for", "flightInput")
        .html("Min flights per route:");
    flightInput.append("input")
        .attr("type", "number")
        .attr("id", "flightInput")
        .attr("min", 0)
        .attr("max", 20000)
        .attr("value", 0);

    var visibilityInput = routeControl.append("div")
        .attr("class", "form-group")
        .append("div")
        .attr("class", "form-check");

    var label = visibilityInput.append("label")
        .attr("class", "form-check-label")
        .html(`<input id="visibilityInput" class="form-check-input" type="checkbox"
                value="" checked="">
               Route visibility`);

    var buttonGroup = routeControl.append("div")
        .attr("class", "form-group");

    var applyButton = buttonGroup.append("button")
        .attr("type", "submit")
        .attr("class", "btn btn-primary btn-block")
        .attr("id", "apply")
        .html("Apply")
        .on("click", function() {
            //Get values from controls
            var minLength = +d3.select("#minLengthInput").property("value");
            var maxLength = +d3.select("#maxLengthInput").property("value");
            var routeFlights = +d3.select("#flightInput").property("value");
            var routeVisibility = d3.select("#visibilityInput").property("checked");
            //Configure values
            userSelection.setMinRouteLength(minLength);
            userSelection.setMaxRouteLength(maxLength);
            userSelection.setRouteFlightsThreshold(routesData, routeFlights);
            userSelection.toggleRouteVisibility(routeVisibility);
            //Update controls
            minLength = userSelection.getMinRouteLength();
            maxLength = userSelection.getMaxRouteLength();
            d3.select("#minLengthInput").property("value", minLength);
            d3.select("#maxLengthInput").property("value", maxLength);
            //Update visualization
            update(routesData, userSelection);
        });    
    
    //General controls
    var resetButton = buttonGroup.append("button")
        .attr("type", "submit")
        .attr("class", "btn btn-primary btn-block")
        .attr("id", "reset")
        .html("Reset")
        .on("click", function() {
            userSelection.reset();
            d3.select("#minLengthInput").property("value", cuts[0].toString());
            d3.select("#maxLengthInput").property("value", cuts[nbCuts].toString());
            d3.select("#flightInput").property("value", 0);
            d3.select("#visibilityInput").property("checked", true);
            update(routesData, userSelection);
        });

    var replayButton = buttonGroup.append("button")
        .attr("type", "submit")
        .attr("class", "btn btn-primary btn-block")
        .attr("id", "replay")
        .html("Replay")
        .on("click", function() {
            d3.select("div#controls").style("visibility", "hidden");
            d3.select("div#bottom").style("visibility", "hidden");
            userSelection.reset();
            d3.select("#minLengthInput").property("value", cuts[0].toString());
            d3.select("#maxLengthInput").property("value", cuts[nbCuts].toString());
            d3.select("#flightInput").property("value", 0);
            d3.select("#visibilityInput").property("checked", true);            
            playAnimation();
        });

    //Instructions
    var instructions = controls.append("div")
        .attr("class", "form");
    instructions.append("legend")
        .html("About");
    var about = instructions.append("div")
        .attr("class", "form-group");
    about.append("p")
        .html("Click on the button below to display help:")
    var helpButton = about.append("button")
        .attr("type", "button")
        .attr("data-toggle", "modal")
        .attr("data-target", "#help")
        .attr("class", "btn btn-primary btn-block")
        .attr("id", "help")
        .html("Help");
    about = instructions.append("div")
        .attr("class", "form-group");
    about.append("p")
        .html("Cédric Campguilhem</span>, March 2018");
    about.append("a")
        .attr("href", "https://github.com/ccampguilhem/Udacity-DataAnalyst")
        .html("https://github.com/ccampguilhem/Udacity-DataAnalyst");

    //Click binding on map to unselect airport
    d3.select("div#map")
        .select("svg")
        .select("g.states")
        .on("click", function() {
            userSelection.clearAirports();
            update(routesData, userSelection); 
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
}  

/*
 * Play animation
 */
function playAnimation() {

    //Prepare data for animation
    var animationData = [];

    // //Routes by length
    // for (i = 1; i <= nbCuts; i++) {
    //     var item = new RouteFilter();
    //     item.setMinRouteLength(cuts[i-1])
    //         .setMaxRouteLength(cuts[i]);
    //     animationData.push(item);
    // }
    
    //5 biggest airports
    var big5 = ["William B Hartsfield-Atlanta Intl", "Chicago O'Hare International", "Denver Intl", 
            "Phoenix Sky Harbor International", "McCarran International"];
    var big5Animation = new RouteFilter();
    big5Animation.toggleRouteVisibility(false)
        .setDescription("5 major airports in spread in central area");
    big5.forEach(item => big5Animation.addAirport(item));
    animationData.push(big5Animation);
    
    //Coasts airports
    var coasts = ["San Francisco International", "Metropolitan Oakland International", 
        "San Jose International", "Los Angeles International", "Burbank-Glendale-Pasadena", 
        "Long Beach (Daugherty )", "Ontario International", "John Wayne /Orange Co", 
        "San Diego International-Lindbergh", "Miami International", 
        "Fort Lauderdale-Hollywood Int'l", "Palm Beach International", "Gen Edw L Logan Intl", 
        "Theodore F Green State", "Long Island - MacArthur", "Westchester Cty", "LaGuardia", 
        "Newark Intl", "John F Kennedy Intl", "Baltimore-Washington International", 
        "Washington Dulles International", "Ronald Reagan Washington National", "Philadelphia Intl"
    ];
    var coastsAnimation = new RouteFilter();
    coastsAnimation.toggleRouteVisibility(false)
        .setDescription("High concentration of smaller airports along coasts");
    coasts.forEach(item => coastsAnimation.addAirport(item));
    animationData.push(coastsAnimation);

    //Popular routes
    var popularAnimation = new RouteFilter();
    popularAnimation.setDescription("Most popular routes are limited to East and West (more than " + 
        "19000 flights)...")
        .setRouteFlightsThreshold(routesData, 19000);
    animationData.push(popularAnimation);
    var popularAnimation = new RouteFilter();
    popularAnimation.setDescription("then extend to central area (more than 15750 flights)...")
        .setRouteFlightsThreshold(routesData, 15750);
    animationData.push(popularAnimation);
    var popularAnimation = new RouteFilter();
    popularAnimation.setDescription("and finally link East and West (more than 11000 flights).")
        .setRouteFlightsThreshold(routesData, 11000);
    animationData.push(popularAnimation);

    //Full map
    animationData.push(new RouteFilter());

    //Routes animation (nested timeout and interval to have a shorter delay for first frame)
    var i = 0;
    setTimeout(function() {
        update(routesData, animationData[i]);
        var interval = setInterval(function(){
            //this function is called at specified time intervals
            i++;
            if (i >= animationData.length) {
                //Make bar chart and controls visible
                d3.select("div#controls").style("visibility", "visible");
                d3.select("div#bottom").style("visibility", "visible");
                //stops the iteration
                clearInterval(interval);
            } else {
                update(routesData, animationData[i]);
            }
        }, animationTransition);
    }, mediumTransition);
}

/*
 * Update the map with route dataset
 *
 * - data: route dataset
 * - userSelection: user selection
 */
function update(data, userSelection) {

    console.log("udpate", userSelection.getDescription());
    console.log("update.userSelection.flightsFilter", userSelection.flightsFilter);

    //Update status
    var status = d3.select("div#status")
            .select("h5")
            .html(userSelection.getDescription());

    //Update routes
    updateRoutes(data, userSelection);

    //Update airports
    updateAirports(data, userSelection);

    //Update aircrafts
    updateAircrafts(data, userSelection);
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
 * - userSelection: user selection
 * - return: airports dataset
 */
function createAirportsDataset(data, userSelection=null) {

    //Filter routes by length
    var filtered;
    if (userSelection === null) {
        filtered = data;
    } else {
        filtered = data.filter(userSelection.filter());
    }
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

    //If route are not displayed, also filter this dataset
    //short-circuit prevent right operator from being evaluated
    if (!(userSelection === null) && !(userSelection.isRouteVisible())) {
        airports = airports.filter(item => userSelection.hasAirport(item.Airport));
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
 * Update the airports on the map
 *
 * - data: route dataset
 * - userSelection: user selection
 */
function updateAirports(data, userSelection) {
    
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
    airports = createAirportsDataset(data, userSelection);
    console.log("updateAirports.airports: ", airports);

    //Select svg groups
    var svg = d3.select("div#map")
        .select("svg")
        .select("g.circles");

    var tooltip = d3.select("div#map")
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
            if (userSelection.isAirportEmpty()) {
                userSelection.addAirport(d.Airport);
            } else if (userSelection.hasAirport(d.Airport)) {
                userSelection.clearAirports();
            } else {
                userSelection.clearAirports();
                userSelection.addAirport(d.Airport);
            }
            update(data, userSelection);
        })        
        .attr("cx", function(d) { return d.Coords[0]; })
        .attr("cy", function(d) { return d.Coords[1]; })
        .transition()
        .ease(d3.easeLinear)
        .duration(mediumTransition)
        .attr("r", function(d) { return flightsScale(d.Flights); })
}

/* 
 * Aggregation function for routes
 *
 * - data: routes group data
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
 * - userSelection: user selection
 * - return: routes dataset
 */
function createRoutesDataset(data, userSelection=null) {
    
    //Filter routes by length
    var filtered;
    if (userSelection === null) {
        filtered = data;
    } else {
        if (userSelection.isRouteVisible()) {
            filtered = data.filter(userSelection.filter());
        } else {
            filtered = [];
        }
    }
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
 * - userSelection: user selection 
 */
function updateRoutes(data, userSelection=null) {

    //Calculate min and max number of flights (used for scaling)
    var routes = createRoutesDataset(data);
    maxFlights = d3.max(routes, function(d) { return d.Flights; });
    minFlights = d3.min(routes, function(d) { return d.Flights; });
    console.log("updateRoutes.{minFlights,maxFlights}", minFlights, maxFlights);

    // Create routes dataset
    routes = createRoutesDataset(data, userSelection);
    console.log("updateRoutes.routes: ", routes);

    //Select svg group
    var svg = d3.select("div#map")
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

/* 
 * Aggregation function for aircrafts
 *
 * - data: aircrafts group data
 * - return: object with aggregated value for aircrafts
 */
function aggregateAircrafts(data) {
    return {
        "Flights": d3.sum(data, function(d) {
            return d["Flights"];
        })
    };
}

/*
 * Create the aircrafts dataset
 *
 * - data: route dataset
 * - userSelection: user selection
 */
function createAircraftsDataset(data, userSelection=null) {
    //Filter routes by length
    var filtered;
    if (userSelection === null) {
        filtered = data;
    } else {
        filtered = data.filter(userSelection.filter());
    }
    console.log("createAircraftsDataset.filtered", filtered);

    //Group by aircraft
    var aircraftsAgg = d3.nest()
        //group by aircraft
        .key(function(d) { return d["Manufacturer"]; })
        //aggregate
        .rollup(aggregateAircrafts)
        //bind filtered data
        .entries(filtered)
    console.log("createAircraftsDataset.aircraftsAgg", aircraftsAgg);

    //Get full list of aircrafts
    //This is to ensure that all aircrafts are in the dataset even if number of flights is 0
    //This way bar chart will always have the same components
    allAircrafts = d3.set(data, function(d) { return d["Manufacturer"]; });
    var aircraftsDict = {};
    allAircrafts.each(function(d) {
        aircraftsDict[d] = 0;
    });
    console.log("createAircraftsDataset.aircraftsDict", aircraftsDict);

    //Generate aircrafts dataset
    var aircrafts = [];
    for (i = 0; i < aircraftsAgg.length; i++) {
        var name = aircraftsAgg[i].key;
        var flights = aircraftsAgg[i].value.Flights;
        aircraftsDict[name] = flights;
    }
    for (var name in aircraftsDict) {
        var item = {
            "Aircraft": name,
            "Flights": aircraftsDict[name]
        };
        aircrafts.push(item);
    }
    
    //Sort aircrafts so that they always appear in alphabetical order
    aircrafts.sort(function (a, b) {
        return a.Aircraft.localeCompare(b.Aircraft);
    });

    return aircrafts;
}

/*
 * Update the bar chart with aircrafts data
 *
 * - data: route dataset
 * - userSelection: user selection
 */
function updateAircrafts(data, userSelection=null) {

    // Create aircrafts dataset
    var aircrafts = createAircraftsDataset(data, userSelection);
    var maxFlights = d3.max(aircrafts, function(d) { return d.Flights; });
    var minFlights = d3.min(aircrafts, function(d) { return d.Flights; });    
    console.log("updateAircrafts.aircrafts: ", aircrafts);

    //Select svg groups
    var bars = d3.select("div.bar")
        .select("svg")
        .select("g.bars");
    var ticks = d3.select("div.bar")
        .select("svg")
        .select("g.ticks");
    var labels = d3.select("div.bar")
        .select("svg")
        .select("g.labels");

    //Create scale
    var aircraftsScale = d3.scaleLinear()
        .domain([minFlights, maxFlights])
        .range([minSizeBar, maxSizeBar]);

    //Draw bars
    var rects = bars.selectAll("rect")
        .data(aircrafts, function(d) { return d.Aircraft; });

    rects.enter() //select missing elements
        .append("rect")
        .merge(rects)
        .attr("height", 12)
        .attr("x", 210)
        .attr("y", function(d, i) { return i * (12 + 5) + 2; })
        .transition()
        .duration(mediumTransition)
        .attr("width", function(d) { return aircraftsScale(d.Flights); });

    //Draw ticks
    var texts = ticks.selectAll("text")
        .data(aircrafts, function(d) { return d.Aircraft; });

    texts.enter()
        .append("text")
        .merge(texts)
        .text(function(d) { return d.Aircraft; })
        .attr("x", 200)
        .attr("y", function(d, i) { return i * (12 + 5) + 12; })
        .style("text-anchor", "end")
        .attr("font-size", 12)
        .style("fill", "white");

    //Draw labels
    texts = labels.selectAll("text")
        .data(aircrafts, function(d) { return d.Aircraft; });

    texts.enter()
        .append("text")
        .style("text-anchor", "begin")
        .attr("font-size", 12)
        .style("fill", "white")
        .style("font-style", "italic")
        .attr("x", function(d) { return 200 + 20; })
        .attr("y", function(d, i) { return i * (12 + 5) + 12; })
        .merge(texts)
        //.transition()
        //.duration(shortTransition)
        //.style("opacity", 0)
        .transition()
        .duration(mediumTransition)
        //.style("opacity", 1);
        .text(function(d) { 
            if (d.Flights > 0) {
                return d.Flights;
            } else {
                return "";
            }})
        .attr("x", function(d) { return 200 + 20 + aircraftsScale(d.Flights); })
        .attr("y", function(d, i) { return i * (12 + 5) + 12; })
}
