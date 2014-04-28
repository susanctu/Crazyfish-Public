/****************************     Constants      *****************************/

// Default height of the hit area
HIT_AREA_DEFAULT_HEIGHT = 40;

/**************************** Global variables   *****************************/

// Warning: order of these categories matter, and should match the order
// in which they are displayed on the website.
var categories = getCategoriesObject();

// Same as previous one, but verbose and used for display purposes.
// Again, order matters.
var categoriesVerbose = getVerboseCategoriesObject();

// Likewise, order of these sorting flags matter, and should match the order
// in which the sorting logos are displayed.
var sortType = ['magic',
                'price',
                'start-time',
                'duration'];

/**************************** Misc function      *****************************/

/**
 * Converts a numerical value between 0 and 100 to a percentage string.
 * @param {float} numValue: a float between 0 and 100;
 * @return {string}: string of the value followed by percent sign.
 *
 */
function numToPercentString( numValue ) {
    return numValue.toString() + '%';
};

/**
 * Counts the number of properties inside an Object.
 * @param {object} a JS object
 * @return {int} number of properties of the object
 *
 */
function countProperties(obj) {
    var count = 0;

    for(var prop in obj) {
        if(obj.hasOwnProperty(prop))
            ++count;
    }

    return count;
}


/**************************** Read HTML data     *****************************/

/**
 * Returns the HTML ID tag of the results tab which is selected.
 * @return {string} A string representing the HTML id of the current results
 *   tab.
 *
 */
function getSelectedTabHtmlId () {
    return $( '#results-area .results.selected' ).attr('id');
}

/**
 * Returns the jQuery object containing the left time anchor
 * @return: jQuery object corresponding to left time anchor.
 *
 */
function getTimeAnchorLeft () {
    return $( '#' + getSelectedTabHtmlId() + ' .timeline-header .timeheader .anchor.left' );
}

/**
 * Returns the jQuery object containing the right time anchor
 * @return: jQuery object corresponding to right time anchor.
 *
 */
function getTimeAnchorRight () {
    return $( '#' + getSelectedTabHtmlId() + ' .timeline-header .timeheader .anchor.right' );
}

/**
 * Returns the jQuery object containing the time box child of an anchor object.
 * @param: jQuery handle to an anchor
 * @return: jQuery object corresponding to a time box
 *
 */
function getTimeBoxChildOfAnchor ( anchor ) {
    return anchor.children().children('.time-flag.timebox');
}

/**
 * Returns the jQuery object containing the left graydiv.
 * @return: jQuery object corresponding to left graydiv.
 *
 */
function getGraydivLeft () {
    return $( '#' + getSelectedTabHtmlId() + ' .events-table .graydiv-left' );
}

/**
 * Returns the jQuery object containing the right graydiv.
 * @return: jQuery object corresponding to right graydiv.
 *
 */
function getGraydivRight () {
    return $( '#' + getSelectedTabHtmlId() + ' .events-table .graydiv-right' );
}

/**
 * Returns the width in pixels of the time slider area
 * @return {int}: width of time slider area.
 *
 */
function getWidthTimeSliderArea () {
    return $( ' .head-block .timeheader ' ).width();
}

/**
 * Returns the jQuery object which holds the event description string
 * @return {jQuery Object} Object which holds the event description string.
 */
 function getEventDescriptionHolder () {
     return $( '#' + getSelectedTabHtmlId() + ' .timeline-header .head-block .left-column-header .col-header-cat' );
 }

/**
 * Returns an array of category IDs for all the categories that have been
 * selected in the current tab.
 * @return {array} An array of category IDs (integers)
 *
 */
function getSelectedCategoriesNumId () {
    var selectedNumIds = [];
    var selectedLogos = $( '#' + getSelectedTabHtmlId() + ' .filter-logos-wrapper .filter-logos .selected' );
    for ( var i = 0; i < selectedLogos.length; i++ ) {
        selectedNumIds.push(parseInt(selectedLogos.eq(i).parents('li').find('.category-id').html()))
    }
    return selectedNumIds;
};

/**
 * Returns a string describing the categories selected.
 * @return {string} A string describing the categories selected
 *
 */
function getSelectedCategoriesString () {
    var selectedCategoriesId = getSelectedCategoriesNumId();
    var sumStr = '';

    if ( selectedCategoriesId.length == 0 ) {
        return 'All events';
    }
    if ( selectedCategoriesId.length == countProperties(categoriesVerbose) ) {
        sumStr = 'All events';
    }
    else {
        for ( var i=0; i < selectedCategoriesId.length-1; i++ ) {
            sumStr += categoriesVerbose[selectedCategoriesId[i]] + ', ';
        }
        sumStr += categoriesVerbose[selectedCategoriesId[selectedCategoriesId.length-1]] + ' events';
    }

    return sumStr.charAt(0).toUpperCase() + sumStr.slice(1);
};

/**
 * Returns the numerical ID of the sorting logo selected, so that the sorting
 * type is equal to sortType[result].
 * @return {int} numerical ID of the sorting logo selected.
 *
 */
function getSelectedSortLogoNumId () {
    var selectedLogos = $( '#' + getSelectedTabHtmlId() + ' .sort-logos-wrapper .sort-logos .selected' );
    for ( var i = 0; i < selectedLogos.length; i++ ) {
        var cLogoClass = selectedLogos.eq(i).attr('class');
        for ( var k = 0; k < sortType.length; k++ ) {
            if ( cLogoClass.indexOf( sortType[k] ) != -1 ) {
                return k;
            }
        }
    }
};

/**
 * Returns the height in pixels of the event-info child of an event jQuery
 * object. If called with more than one object, returns an array of heights
 * with as many elements as there were jQuery objects.
 * @return {int} a height (or an array of heights) in pixels.
 */
function getEventInfoChildHeight ( eventObj ) {
    allHeights = [];
    for ( var i = 0; i < eventObj.length; i++ ) {
        allHeights.push( eventObj.eq(i).children( '.event-info' ).height() )
    }
    if ( allHeights.length == 1 ) {
        allHeights = allHeights[0];
    }
    return allHeights;
};


/**
 * Returns the height in pixels of the event-details child of an event jQuery
 * object. If more than one element are passed in, then returns an array of
 * heights with as many elements as there were jQuery objects.
 * @return {int} a height (or an array of heights) in pixels.
 *
 */
function getEventDetailsChildHeight ( eventObj ) {
    allHeights = [];
    for ( var i = 0; i < eventObj.length; i++ ) {
        allHeights.push( eventObj.eq(i).children( '.event-details' ).height() )
    }
    if ( allHeights.length == 1 ) {
        allHeights = allHeights[0];
    }
    return allHeights;
};

/**
 * Returns the min and max time corresponding to 0% and 100% position
 * of the sliders. Returned in 24h string format: 'hh:mm:ss'.
 * The seconds field is optional and will appear only if it was specified in
 % the html in the first place.
 % Note: this function only fetches data from the html.
 * @return {[str, str]} Start and end time of slider bar.
 */
function getMinAndMaxTimes () {
    return [$( '#' + getSelectedTabHtmlId() + ' .timeline-header .head-block .time-helper-min-value' ).html(),
            $( '#' + getSelectedTabHtmlId() + ' .timeline-header .head-block .time-helper-max-value' ).html()]
};

/**
 * Builds the event array for the current event tab. 
 * @return {array} An event array with n elements, where n is the total number
 *         of events for the current tab, and each element of the array is an
 *         array composed of the following fields:
 *             [0]: position of the events with the current sorting
 *             [1]: list of categories the event belongs to (array of ints)
 *             [2]: magic rating of the event (float)
 *             [3]: price of the events, 0 if the event is free
 *             [4]: start time of the event as a percentage of the time slider
 *             [5]: duration of the event as a percentage of the time slider (ex: 15.5 for 15.5%)
 *
 */
function getEventArray () {
    var eventArr = [];
    var allEvents = getActiveTabEvents();

    for ( var i = 0; i < allEvents.length; i++ ) {
        // Each event should have a event-helper field in which this information is stored
        // and only needs to be retrieved from there.
        var cEventHelper = allEvents.eq(i).children( '.event-helper' );

        var cCategory = cEventHelper.children( '.event-helper-category' ).html().trim();
        if ( cCategory.length > 0  &&  cCategory[0] === "[" ) {
            cCategory = cCategory.substring(1)
        }
        cCategory = cCategory.split(',');
        cCategory = cCategory.map( function (x) {
            return parseInt(x);
        });

        var cMagic = parseFloat( cEventHelper.children( '.event-helper-magic' ).html() );

        var cPrice = parseFloat( cEventHelper.children( '.event-helper-price' ).html() );

        var cStartTime = cEventHelper.children( '.event-helper-start-time ' ).html();
        cStartTime = timeStringToPercentage(cStartTime);

        var cDuration = cEventHelper.children( '.event-helper-duration-minutes ' ).html();
        cDuration = durationInMinutesToPercentage(cDuration);

        eventArr.push([i, cCategory, cMagic, cPrice, cStartTime, cDuration]);
    }
    return eventArr;
};

/**
 * Returns a javascript object which links category id and category name.
 * @return {object} a javascript object such that the name of category with
 *         ID i is var[i]
 *
 */
function getCategoriesObject () {
    var allCategories = getActiveTabCategoryControls();
    var catObject = {};

    for ( var i=0; i < allCategories.length; i++ ) {
        var cCategory = allCategories[i];
        var cId = parseInt(allCategories.eq(i).find('.category-id').html());
        var cNameArr = allCategories.eq(i).find('.filter-logo').attr('class').split(' ');
        for ( var j=0; j < cNameArr.length; j++ ) {
            if ( cNameArr[j].indexOf('filter-logo-') > -1 ) {
                var cName = cNameArr[j].substring('filter-logo-'.length);
                break;
            }
        }
        catObject[cId] = cName;
    }

    return catObject
};

/**
 * Returns a javascript object which links category id and category verbose
 * description.
 * @return {object} a javascript object such that the verbose description of
 *         category with ID i is var[i]
 *
 */
function getVerboseCategoriesObject () {
    var allCategories = getActiveTabCategoryControls();
    var catVerboseObject = {};

    for ( var i=0; i < allCategories.length; i++ ) {
        var cCategory = allCategories[i];
        var cId = parseInt(allCategories.eq(i).find('.category-id').html());
        var cName = allCategories.eq(i).find('.tooltip-comment').html();
        catVerboseObject[cId] = cName;
    }

    return catVerboseObject
};

/**************************** Get/Set properties *****************************/

/**
 * Get the list of all category controls in the active tab event graph.
 * @return {[jQuery]} An array of event objects.
 *
 */
function getActiveTabCategoryControls () {
    return $( '#' + getSelectedTabHtmlId() + ' .controls-header .filter-logos-wrapper li ' );
}

/**
 * Returns the height of the event table in pixels
 * @ return {int} height of the event table
 */
function getEventTableHeight () {
    return $( '.event-holder .events-table' ).height()
}

/**
 * Returns the start and end positions of the time sliders.
 * @return {[int, int]} Start and End time in percentage.
 *
 */
function getTimeSlidersPosition () {
    var posLeft = getTimeAnchorLeft().position().left;
    var posRight = getTimeAnchorRight().position().left;
    var maxWidth = getWidthTimeSliderArea();

    posLeft = Math.round(1000*posLeft/maxWidth)/10;
    posRight = Math.round(1000*posRight/maxWidth)/10;

    return [posLeft, posRight];
};

/**
 * Get the list of all events in the active tab event graph.
 * @return {[jQuery]} An array of event objects. 
 * 
 */
function getActiveTabEvents () {
    return $( '#' + getSelectedTabHtmlId() + ' .results-content .events-table .event ' );
}

/**
 * Get a single separator jQuery object for the active tab.
 * @return {]jQuery]} An separator
 *
 */
function getActiveTabSeparators () {
    return separator = $( '#' + getSelectedTabHtmlId() + ' .results-content .events-table .separator ' );
}

/**
 * Get the list of separators in the table of events from the active tab.  
 * @return {[jQuery]} An array of separator jQuery objects.
 *
 */
function getActiveTabSeparators () {
    return $( '#' + getSelectedTabHtmlId() + ' .results-content .events-table .separator ' );
}

/**
 * Returns a jQuery object containing the active tab event graph.
 * @return {[jQuery]} A jQuery object containing the active tab event graph.
 *
 */
function getActiveTabEventsGraph () {
    return $( '#' + getSelectedTabHtmlId() + ' .results-content .events-table .events-graph ' );
}

/**
 * Returns a jQuery object containing the active tab no event found warning 
 * element.
 *
 */
function getActiveTabNoEventWarningDiv () {
    return $( '#' + getSelectedTabHtmlId() + ' .results-content .no-event-found-warning ' );
}

/**
 * Sets the height of the hit-area to a user-defined value.
 * @param {int} Height of the hit-area in pixels
 *
 */
function setHitAreaHeight ( newHeight ) {
    $( '.event-holder .timeline-header .timeline-table .timeheader .hit-area' ).height(newHeight);
}

/**
 * Sets the events table graph data from a DOM array.
 * @param {[DOM]} An array of DOM elements which will go on the event graph.
 *
 */
function setActiveTabEventsGraphFromDOM ( domArray ) {
    // Get raw html from the DOM array
    var newHtml = '';
    for ( var i = 0; i < domArray.length; i++ ) {
        newHtml += domArray[i].outerHTML;
    }

    // Set the html inside the events graph
    getActiveTabEventsGraph().html( newHtml );
}

/**
 * Sets the events table graph data from an array of jQuery objects.
 * @param {[jQuery]} An array of jQuery elements which will go on the event graph.
 *
 */
function setActiveTabEventsGraphFromJQObj ( jqObjArray ) {
    // Get raw html from the DOM array
    var newHtml = '';
    for ( var i = 0; i < jqObjArray.length; i++ ) {
        newHtml += jqObjArray[i][0].outerHTML;
    }

    // Set the html inside the events graph
    getActiveTabEventsGraph().html( newHtml );
}

/**
 * Sets the height of the hit area to a user-defined value specified in pixels.
 * @param {int} Hit area height in pixels.
 *
 */
function SetHitAreaHeight ( newHeight ) {
    $( '.event-holder .timeline-header .timeline-table .timeheader .hit-area' ).height( newHeight );
};

/****************************     Utilities      *****************************/

/**
 * Converts a percentage position into an hour:min AM/PM string.
 * @param {str} A string describing a percentage (ex: '15.5%').
 * @return {str} A time string (ex: '8:55 am').
 */
function percentageToTimeString ( percentStr ) {
    var timeBounds = getMinAndMaxTimes();
    var tMin = timeBounds[0];
    var tMax = timeBounds[1];
    var dNew = new Date();

    // Converting min and max strings to milliseconds
    tMin = timeStringToMilliseconds(tMin);
    tMax = timeStringToMilliseconds(tMax);

    // Calculating milliseconds corresponding to percentage
    var newTime = percentStr.slice(0, percentStr.lastIndexOf("%"));
    newTime = parseFloat(newTime)/100;
    newTime = Math.round(tMin + (tMax - tMin)*newTime);

    // Formatting the new time string and returning
    var newTimeStr = [];
    newTimeStr[0] = Math.floor(newTime/60/60/1000);
    newTimeStr[1] = (Math.round((newTime - newTimeStr[0]*60*60*1000)/60/1000)).toString();
    if ( newTimeStr[1].length == 1) {
        newTimeStr[1] = "0" + newTimeStr[1];
    }

    var hour = newTimeStr[0];
    newTimeStr[0] = newTimeStr[0].toString();
    if ( hour == 0 ) {
        return "12:" + newTimeStr[1] + " AM";
    }
    if ( hour == 12 ) {
        return "12:" + newTimeStr[1] + " PM";
    }
    if ( hour > 12 ) {
        return (hour-12).toString() + ":" + newTimeStr[1] + " PM";
    }
    return newTimeStr[0] + ":" + newTimeStr[1] + " AM";
}

/**
 * Converts a time string (ex: '8:55 AM') into a number of millisecconds, which
 * can then be used to set a Date object.
 * @param {str} A time string
 * @return {float} number of milliseconds representing the time.
 *
 */
function timeStringToMilliseconds ( timeStr ) {
    timeStr = timeStr.toLowerCase();

    // Remove potential leading white spaces
    timeStr = timeStr.trim();

    // If time string is 'T...' need to drop the leading T.
    if ( timeStr[0] == 't' ) {
        timeStr = timeStr.slice(1);
    }

    // Then, need to determine if the time string is in AM/PM format. 
    // If so we'll need to convert it to 24 hours format.
    var amPmPos = timeStr.indexOf('m');
    if ( amPmPos != -1 ) {
        // If it is, split hours and minutes, find if am or pm and format.
        var amPm = timeStr.substr(amPmPos-1, amPmPos+1);
        timeStr = timeStr.substr(0, amPmPos-1);
        timeStr = timeStr.split(':');

        // Remove any potential leading or trailing white spaces here
        timeStr[0] = timeStr[0].trim();
        timeStr[1] = timeStr[1].trim();

        // Various formatting rules here...
        if ( timeStr[0].length == 1 ) {
            timeStr[0] = '0' + timeStr[0];
        }
        if ( timeStr[0] == '12') { 
            if ( amPm == 'am' ) {
                timeStr[0] = '00';
            }
        }
        else {
            if ( amPm == 'pm' ) {
                timeStr[0] = (parseInt(timeStr[0]) + 12).toString();
            }
        }
    }
    else {
        timeStr = timeStr.split(':');
    }
    timeStr[0] = parseFloat(timeStr[0]);
    timeStr[1] = parseFloat(timeStr[1]);

    // Parse the date string 
    return (timeStr[0]*60*60*1000 + timeStr[1]*60*1000);
}

/**
 * Converts a time string (ex: '8:55 AM') into a percentage of the time slider.
 * @param {str} A time string
 * @return {float} A percentage (ex: 15.5 is 15.5%, NOT 15500%).
 *
 */
function timeStringToPercentage ( timeStr ) {
    var timeBounds = getMinAndMaxTimes();
    var tMin = timeBounds[0];
    var tMax = timeBounds[1];

    tMin = timeStringToMilliseconds(tMin);
    tMax = timeStringToMilliseconds(tMax);
    var tNew = timeStringToMilliseconds(timeStr);

    return Math.round(1000*(tNew-tMin)/(tMax-tMin))/10;
}

/**
 * Converts a duration into a percentage of the time slider. 
 * The duration should be in minutes, and should be an int, float, or a string 
 * representing an int or float. 
 * @param {int or float or str} A duration in minutes
 * @return {float} A percentage string (ex: 15.5 for 15.5%)
 *
 */
function durationInMinutesToPercentage ( duration ) {
    // Check if string
    if ( typeof(duration) == 'string' ) {
        duration = parseFloat(duration.trim());
    }

    // Convert
    var timeBounds = getMinAndMaxTimes();
    var tMin = timeStringToMilliseconds(timeBounds[0]);
    var tMax = timeStringToMilliseconds(timeBounds[1]);
    duration = duration*60*1000;

    return Math.round(1000*duration/(tMax-tMin))/10;
}

/**
 * Puts all the events specified in the index list on top of the event list,
 * and puts all the others on the bottom of the list. 
 * This method does not affect event visibility.
 * @param {[int]} An array of event indices.
 *
 */
function updateEventGraphOrder ( eventIndexList ) {
    // Getting jQuery representation of events. 
    var allEvents = getActiveTabEvents();
    var nEvents = allEvents.length;
    if ( nEvents == 0 ) {
        return;
    }
    var separators = getActiveTabSeparators();

    // Get index of events missing from event list
    var missingFromEventIndexList = [];
    for ( var i = 0; i < allEvents.length; i++ ) {
        if ( eventIndexList.indexOf(i) == -1 ) {
            missingFromEventIndexList.push(i);
        }
    }

    // Building the updated array of jQuery
    var newEventsJQ = [];
    var nSeparatorsUsed = 0;
    var maxIndVis = -1;

    // Start with events that were specified
    for ( var i = 0; i < eventIndexList.length; i++ ) {
        newEventsJQ.push( allEvents.eq(eventIndexList[i]) );

        // There are only nEvents-1 separators, and their visibility 
        // should be set to that of the parent event.
        if ( nSeparatorsUsed < nEvents-1 ) {
            var cSeparator = separators.eq(nSeparatorsUsed);
            if ( allEvents.eq(eventIndexList[i]).is(":visible") ) {
                cSeparator.toggle( true );
            }
            else {
                cSeparator.toggle( false );
            }
            newEventsJQ.push( cSeparator );
            nSeparatorsUsed += 1;
        }

        // Also looking for last visible element
        if ( allEvents.eq(eventIndexList[i]).is(":visible") ) {
            if ( i > maxIndVis ) {
                maxIndVis = i;
            }
        }
    }

    // Put all other events at the end
    for ( var i = 0; i < missingFromEventIndexList.length; i++ ) {

        newEventsJQ.push( allEvents.eq(missingFromEventIndexList[i]) );

        // There are only nEvents-1 separators. Adjust visibility 
        // before pushing on JQ array.
        if ( nSeparatorsUsed < nEvents-1 ) {
            var cSeparator = separators.eq(nSeparatorsUsed);
            if ( allEvents.eq(missingFromEventIndexList[i]).is(":visible") ) {
                cSeparator.toggle( true );
            }
            else {
                cSeparator.toggle( false );
            }
            newEventsJQ.push( cSeparator );
            nSeparatorsUsed += 1;
        }

        // Also looking for last visible element
        if ( allEvents.eq(missingFromEventIndexList[i]).is(":visible") ) {
            if ( i + eventIndexList.length > maxIndVis ) {
                maxIndVis = i + eventIndexList.length;
            }
        }
    }

    // Making sure the separator after the last element visible is off
    // if the last visible element is not the last in the list.
    if ( maxIndVis != nEvents - 1 ) {
        newEventsJQ[maxIndVis*2+1].toggle( false );
    }

    // Setting the event table to the new data.
    setActiveTabEventsGraphFromJQObj( newEventsJQ );
}

/**
 * Shows all the events specified in the index list. Hides all other events.
 * @param {[int]} An array of event indices.
 *
 */
function updateEventGraphVisibility ( eventIndexList ) {
    // Getting jQuery representation of events. 
    // Note: will have to be converted to DOM representation as they are used!
    var allEvents = getActiveTabEvents(); 
    var separator = getActiveTabSeparators();
    var maxIndDisplayed

    if ( eventIndexList.length == 0 ) {
        getActiveTabNoEventWarningDiv().toggle( true );
    }
    else {
        getActiveTabNoEventWarningDiv().toggle( false );
        maxIndDisplayed = Math.max.apply(null, eventIndexList);
    }

    var indexLastSeparator;
    for ( var i = 0; i < allEvents.length; i++ ) {
        // Toggle on elements in the eventIndex list
        if ( eventIndexList.indexOf(i) != -1 ) {
            allEvents.eq(i).toggle( true );
            // There is 1 fewer active separator than events shown
            if ( i < allEvents.length - 1 ) {
                separator.eq(i).toggle( true );
            }
            indexLastSeparator = i;
        }
        // Toggle off the others
        else {
            allEvents.eq(i).toggle( false );
            // There is 1 fewer separator than events
            if ( i < allEvents.length - 1 ) {
                separator.eq(i).toggle( false );
            }
        }
    }

    // Making sure last separator is off
    if ( indexLastSeparator < allEvents.length - 1) {
        separator.eq(indexLastSeparator).toggle( false );
    }
    
    // Updating the height of the hit area
    SetHitAreaHeight( HIT_AREA_DEFAULT_HEIGHT + getEventTableHeight() );
}

/**
 * Compares two events represented by their array, using the comparison method
 * specified by the user.
 * @param {array} An array representing a single event (see getEventArray()
 *        for format)
 * @param {array} An array representing a single event.
 * @param {int} Optional, the type of comparison run on your event. 0 will
 *        compare by magic, 1 by price, 2 by start time and 3 by duration.
 *        Defaults to magic, if no comparison mode is specified.
 * @return {float} negative is event1 is smaller than event2, positive
 *        otherwise.
 *
 */
function compareEventsAscending ( event1, event2, mode ) {
    if ( typeof(mode) === "undefined" || mode === null ) {
        mode = 0;
    }

    return event1[2+mode] - event2[2+mode];
}

/**
 * Compares two events represented by their array, using the comparison method
 * specified by the user. 
 * @param {array} An array representing a single event (see getEventArray()
 *        for format)
 * @param {array} An array representing a single event.
 * @param {int} Optional, the type of comparison run on your event. 0 will
 *        compare by magic, 1 by price, 2 by start time and 3 by duration.
 *        Defaults to magic, if no comparison mode is specified.
 * @return {float} negative is event1 is smaller than event2, positive 
 *        otherwise.
 *
 */
function compareEventsDescending ( event1, event2, mode ) {
    if ( typeof(mode) === "undefined" || mode === null ) {
        mode = 0;
    }

    return event2[2+mode] - event1[2+mode];
}

/**
 * Sorts the event array according to the sorting mode specified by the user
 * and returns an array of indices representing in which order the events
 * should be displayed.
 * @param {array} An array of events (as returned by getEventArray())
 * @return {array} An array of indices.
 *
 */
function sortEventArrayAscending ( eventArray, mode ) {
    if ( typeof(mode) === "undefined" || mode === null ) {
        mode = 0;
    }

    eventArray = eventArray.sort( function(a,b) {
        return compareEventsAscending(a,b,mode)
    });

    var result = [];
    for ( var i = 0; i < eventArray.length; i++ ) {
        result.push(eventArray[i][0]);
    }

    return result;
}

/**
 * Sorts the event array according to the sorting mode specified by the user
 * and returns an array of indices representing in which order the events 
 * should be displayed.
 * @param {array} An array of events (as returned by getEventArray())
 * @return {array} An array of indices.
 *
 */
function sortEventArrayDescending ( eventArray, mode ) {
    if ( typeof(mode) === "undefined" || mode === null ) {
        mode = 0;
    }

    eventArray = eventArray.sort( function(a,b) { 
        return compareEventsDescending(a,b,mode)
    });

    var result = [];
    for ( var i = 0; i < eventArray.length; i++ ) {
        result.push(eventArray[i][0]);
    }

    return result;
}

/**
 * Get the IDs of elements matching the current filters (categories, start
 * and end time)
 * @return {[int]} An array of element IDs, possibly empty, matching the filters
 *         chosen by the user.
 *
 */ 
function getIdEventsMatchingFilters () {
    // Get the set of filters entered by the user
    var catSelected = getSelectedCategoriesNumId();
    var tsPosition = getTimeSlidersPosition();
    var tMinAllowed = tsPosition[0];
    var tMaxAllowed = tsPosition[1];

    // Get the events
    // Category is supposed to be in [1], start time in [4] and
    // duration in [5], with start time and duration in percentages.
    var allEvents = getEventArray();

    // Filter
    var eventsToDisplay = [];
    for ( var i = 0; i < allEvents.length; i++ ) {
        var shouldBeDisplayed = true;
        
        // Check if categories match
        var hasCorrectCategory = false;
        if ( catSelected.length == 0 ) {
            hasCorrectCategory = true;
        }
        else {
            var cCategory = allEvents[i][1];
            for ( var k = 0; k < cCategory.length; k++ ) {
                if ( catSelected.indexOf(cCategory[k]) != -1 ) {
                    hasCorrectCategory = true;
                    break;
                }
            }
        }
        shouldBeDisplayed = shouldBeDisplayed && hasCorrectCategory;

        // Check if start time matches
        var cStartTime = allEvents[i][4];
        shouldBeDisplayed = shouldBeDisplayed && ( cStartTime >= tMinAllowed );

        // Check if end time matches
        var cEndTime = allEvents[i][5] + cStartTime;
        shouldBeDisplayed = shouldBeDisplayed && ( cEndTime <= tMaxAllowed );

        if ( shouldBeDisplayed ) {
            eventsToDisplay.push(allEvents[i][0]);
        }
    }

    return eventsToDisplay;
}


/**************************** Filter / sort list *****************************/

// Toggle selection of filter controls
$( '.filter-logos-wrapper .filter-logos' ).click( function() {
    $( this ).children( '.filter-logo' ).toggleClass( 'selected' );
    getEventDescriptionHolder().html( getSelectedCategoriesString() )
    
    // Filter the events as things get toggled
    updateEventGraphVisibility( getIdEventsMatchingFilters() );
});

// Toggle selection of sort controls
$( '.sort-logos-wrapper .sort-logos' ).click( function() {
    // Check if we just clicked on the logo that was already selected
    var toggledSelected = ( $( this ).children( '.sort-logo' ).attr('class').indexOf('selected') != -1 );

    $( '.sort-logos-wrapper .sort-logos .sort-logo' ).toggleClass( 'selected', false );
    $( this ).children( '.sort-logo' ).toggleClass( 'selected' );
    // If we clicked on the logo previously selected, change sorting order
    if ( toggledSelected ) {
        $( this ).children( '.sort-logo' ).toggleClass( 'descending' );
    }

    // TODO: sort as things get toggled
    var cSortMode = getSelectedSortLogoNumId();
    if ( $( this ).children( '.sort-logo' ).attr('class').indexOf('descending') != -1 ) {
        updateEventGraphOrder( sortEventArrayDescending( getEventArray(), cSortMode) );
    }
    else {
        updateEventGraphOrder( sortEventArrayAscending( getEventArray(), cSortMode) );
    }
});

/****************************    Times table     *****************************/

// Set the height of the hit area
$( '.event-holder .timeline-header .timeline-table .timeheader .hit-area' ).height( function() {
    return HIT_AREA_DEFAULT_HEIGHT + getEventTableHeight();
});

// Drag the sliders. Bind event to document, not sliders!
// Note: this function also deals with all of the event filtering by date.
$( document ).on('mousedown', '.head-block .hit-area', function(e) {
    // Prevent selection of other elements
    $(this).addClass("unselectable");

    var cAnchor = $( this ).parents( '.anchor' );
    var startWidth = cAnchor.position().left;
    var startX = e.pageX;

    var borderWidth = 2;
    var minXAnchorLeft = 0;
    var minXAnchorRight = getTimeAnchorLeft().position().left + borderWidth;
    var maxXAnchorLeft = getTimeAnchorRight().position().left - borderWidth;
    var maxXAnchorRight = getWidthTimeSliderArea();
    var maxWidth = getWidthTimeSliderArea();

    // Reset mouse events on mouse up so that things stop moving
    $( document ).on( 'mouseup', function(e) {
        $( document ).off( 'mouseup' ).off( 'mousemove' );
    });

    // Resize here, as the mouse moves
    $( document ).on( 'mousemove', function(me) {
        if ( cAnchor.attr('class').indexOf('left') != -1 ) {
            // New width in percent...
            var newWidth = Math.min(Math.max(startWidth + me.pageX - startX, minXAnchorLeft), maxXAnchorLeft);
            var newWidthPercentAnchor = Math.round(1000*newWidth/maxWidth)/10;

            // graydiv should be 1 px wider to avoid aliasing effects in some browsers
            var newWidthPercentGrayDiv = Math.round((1000*newWidth+1)/maxWidth)/10;

            newWidthPercentAnchor = newWidthPercentAnchor.toString() + '%';
            newWidthPercentGrayDiv = newWidthPercentGrayDiv.toString() + '%';

            // Move anchor and resize stripe here.
            cAnchor.css('left', newWidthPercentAnchor);
            getGraydivLeft().css('width', newWidthPercentGrayDiv);

            // Set time flag in time box
            if ( newWidthPercentAnchor == '0%' ) {
                getTimeBoxChildOfAnchor(cAnchor).css('display', 'none');
            }
            else {
                getTimeBoxChildOfAnchor(cAnchor).css('display', 'block');
                getTimeBoxChildOfAnchor(cAnchor).html( percentageToTimeString(newWidthPercentAnchor) );
            }
        }
        else {
            // New width in percent...
            var newWidth = Math.min(Math.max(startWidth + me.pageX - startX, minXAnchorRight), maxXAnchorRight);
            var newWidthPercentAnchor = Math.round(1000*newWidth/maxWidth)/10;

            // graydiv should be 1 px wider to avoid aliasing effects in some browsers
            var newWidthPercentGrayDiv = 100 - Math.round((1000*newWidth+1)/maxWidth)/10;

            newWidthPercentAnchor = newWidthPercentAnchor.toString() + '%';
            newWidthPercentGrayDiv = newWidthPercentGrayDiv.toString() + '%';

            // Move anchor and resize stripe here.
            cAnchor.css('left', newWidthPercentAnchor);
            getGraydivRight().css('width', newWidthPercentGrayDiv);

            // Set time flag in time box
            if ( newWidthPercentAnchor == '100%' ) {
                getTimeBoxChildOfAnchor(cAnchor).css('display', 'none');
            }
            else {
                getTimeBoxChildOfAnchor(cAnchor).css('display', 'block');
                getTimeBoxChildOfAnchor(cAnchor).html( percentageToTimeString(newWidthPercentAnchor) );
            }
        }

        // Filter the events as things get toggled
        updateEventGraphVisibility( getIdEventsMatchingFilters() );
    });
});

/****************************     Event table    *****************************/

// Show event details when event is clicked
$(document).on('click', '.results .events-table .event', function() {
    $( this ).toggleClass( 'selected' );

    // Rescale the size of the event
    if ( $( this ).attr( 'class' ).indexOf( 'selected' ) != -1 ) {
        $( this ).height( getEventInfoChildHeight($( this )) + getEventDetailsChildHeight($( this )) );
    }
    else {
        $( this ).height( getEventInfoChildHeight($( this )) );
    }

    // Rescale the time sliders hit area
    // +1 is to account for 1px bottom border
    setHitAreaHeight( HIT_AREA_DEFAULT_HEIGHT + getEventTableHeight() );
});

// Close event details when click on collapse
$(document).on('click', '.results .events-table .event .event-details .deselect', function() {
    // Click will propagate to parent event and call toggle function there...
    // so toggleClass is actually called twice, and to make the window disappear
    // we have to set toggleClass to true manually here.

    $( this ).parents( '.event' ).toggleClass( 'selected' , true );

    // Other solution would be to stop upwards propagation of click event, but not
    // sure how to do this...
});
