/* 
 * Object to store filter information in the routes dataset
 */
function RouteFilter() {
    //Create a new object
    this.minRouteLength = null;
    this.maxRouteLength = null;
    this.airportsSelection = null;
    this.description = null;
    this.routeVisibility = true;
    this.flightsFilter = null;
}

/* 
 * Reset route filter
 *
 * - return: route filter object
 */
RouteFilter.prototype.reset = function() {
    //Restore object in its default state
    this.minRouteLength = null;
    this.maxRouteLength = null;
    this.airportsSelection = null;
    this.description = null;
    this.routeVisibility = true;
    this.flightsFilter = null;
    console.log("RouteFilter.reset.flightsFilter", this.flightsFilter);
    return this;
}

/*
 * Set min route length.
 *
 * - value: min route length
 * - return: route filter object
 */
RouteFilter.prototype.setMinRouteLength = function(value) {
    //Configure min route length
    this.minRouteLength = value;
    if (!(this.maxRouteLength === null)) {
        if (this.minRouteLength > this.maxRouteLength) {
            this.maxRouteLength = this.minRouteLength;
        }
    }
    return this;
}

/*
 * Get min route length.
 *
 * - return: min route length
 */
RouteFilter.prototype.getMinRouteLength = function() {
    return this.minRouteLength;
}

/*
 * Set max route length.
 *
 * - value: max route length
 * - return: route filter object
 */
RouteFilter.prototype.setMaxRouteLength = function(value) {
    //Configure max route length
    this.maxRouteLength = value;
    if (!(this.minRouteLength === null)) {
        if (this.minRouteLength > this.maxRouteLength) {
            this.minRouteLength = this.maxRouteLength;
        }
    }
    return this;
}

/*
 * Get max route length.
 *
 * - return: max route length
 */
RouteFilter.prototype.getMaxRouteLength = function() {
    return this.maxRouteLength;
}

/*
 * Add an airport to selection.
 *
 * - value: airport name
 * - return: route filter object
 */
RouteFilter.prototype.addAirport = function(value) {
    //Add an airport to selection
    if (this.airportsSelection === null) {
        this.airportsSelection = d3.set();
    }
    this.airportsSelection.add(value);
    return this;
}

/*
 * Stat whether airport is in selection.
 *
 * If selection is empty, we consider that all airports are in there.
 *
 * - value: airport name
 * - return: true or false
 */
RouteFilter.prototype.hasAirport = function(value) {
    if (this.airportsSelection === null) {
        return true;
    } else {
        return this.airportsSelection.has(value);
    }
    return this;
}

/*
 * Remove airport from selection.
 *
 * If airport is not in the selection, nothing happens.
 *
 * - value: airport name
 * - return: route filter object
 */
RouteFilter.prototype.removeAirport = function(value) {
    if (this.airportsSelection === null) {
        return this;
    } else {
        this.airportsSelection.remove(value);
        if (this.airportsSelection.empty()) {
            this.airportsSelection = null;
        }
        return this;
    }
}

/*
 * Stat whether airport selection is empty.
 *
 * - return: true or false
 */
RouteFilter.prototype.isAirportEmpty = function() {
    if (this.airportsSelection === null) {
        return true;
    } else {
        return this.airportsSelection.empty();
    }
}

/*
 * Clear all selected airports
 *
 * - return: route filter object
 */
RouteFilter.prototype.clearAirports = function() {
    if (!(this.airportsSelection === null)) {
        this.airportsSelection = null;
    }
    return this;
}

/*
 * Create a filter function for dataset.
 *
 * - return: filter function
 */
RouteFilter.prototype.filter = function() {
    var self = this;
    console.log("RouteFilter.filter.flightsFilter", this.flightsFilter);
    return function(d) {
        //Apply filter rules to provided dataset
        var result = true;
        //Airport filter
        if (!(self.airportsSelection === null)) {
            result = (self.airportsSelection.has(d.OriginAirport) || 
                      self.airportsSelection.has(d.DestAirport)) && result;
        }
        //Route length
        if (!(self.minRouteLength === null)) {
            result = (d.Distance >= self.minRouteLength) && result;
        }
        if (!(self.maxRouteLength === null)) {
            result = (d.Distance <= self.maxRouteLength) && result;
        }
        //Flights number
        if (!(self.flightsFilter === null)) {
            result = self.flightsFilter.has(d.Route) && result;
        }
        return result;
    }
}

/*
 * Set description associated to filter conditions.
 *
 * - value: description
 */
RouteFilter.prototype.setDescription = function(value) {
    this.description = value;
    return this;
}

/*
 * Get description associated to filter conditions.
 *
 * - return: description message
 */
RouteFilter.prototype.getDescription = function() {
    if (this.description === null) {
        if ((this.minRouteLength === null) && (this.maxRouteLength === null)) {
            if (this.airportsSelection === null) {
                return "All routes";
            } else {
                return "All routes from/to " + this.airportsSelection.values().join(", ");
            }
        } else if (this.maxRouteLength === null) {
            if (this.airportsSelection === null) {
                return "Routes above " + this.minRouteLength.toFixed() + " nautic miles";
            } else {
                return "Routes above " + this.minRouteLength.toFixed() + " nautic miles from/to " + 
                    this.airportsSelection.values().join(", ");
            }
        } else if (this.minRouteLength === null) {
            if (this.airportsSelection === null) {
                return "Routes below " + this.maxRouteLength.toFixed() + " nautic miles";
            } else {
                return "Routes below " + this.maxRouteLength.toFixed() + " nautic miles from/to " + 
                    this.airportsSelection.values().join(", ");
            }
        } else {
            if (this.airportsSelection === null) {
                return "Routes between " + this.minRouteLength.toFixed() + " and " + 
                    this.maxRouteLength.toFixed() + " nautic miles";
            } else {
                return "Routes between " + this.minRouteLength.toFixed() + " and " + 
                    this.maxRouteLength.toFixed() + " nautic miles from/to " + 
                    this.airportsSelection.values().join(", ");
            }
        }
    } else {
        return this.description;
    }
}

/*
 * Toggle route visibility
 *
 * - value: route visibility toggle
 * - return: route filter object
 */
RouteFilter.prototype.toggleRouteVisibility = function(value) {
    if (value) {
        this.routeVisibility = true;
    } else {
        this.routeVisibility = false;
    }
    return this;
}

/*
 * Stat wheter routes are visible
 *
 * - return: true or false
 */
RouteFilter.prototype.isRouteVisible = function(value) {
    return this.routeVisibility;
}

/*
 * Set threshold for number of flights per route
 *
 * - data: route dataset
 * - value: threshold value
 * - return: route filter object
 */
RouteFilter.prototype.setRouteFlightsThreshold = function(data, value) {
    //Aggregate routes dataset on routes
    var routesAgg = d3.nest()
        .key(function(d) { return d["Route"]; })
        .rollup(function(g) {
            return d3.sum(g, item => item.Flights);
        })
        .entries(data)
    //Filter with threshold
    routesAgg = routesAgg.filter(item => item.value >= value);
    //Collect all routes in a set
    this.flightsFilter = d3.set();
    var self = this;
    routesAgg.forEach(function(item){
        self.flightsFilter.add(item.key);
    });
    console.log("RouteFilter.setRouteFlightsThreshold.flightsFilter", this.flightsFilter);
    return this;
}



