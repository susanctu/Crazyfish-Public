/**************************** Global variables   *****************************/

// Warning: order of these categories matter, and should match the order
// in which they are displayed on the website.
var categories = ['arts-culture',
                  'classes-workshops',
                  'conference',
                  'family',
                  'food-wine',
                  'meetup',
                  'music',
                  'sport'];

// Same as previous one, but verbose and used for display purposes.
// Again, order matters.
var categoriesVerbose = ['arts &amp; culture',
                         'classes &amp; workshops',
                         'conference',
                         'family',
                         'food &amp; wine',
                         'meetup',
                         'music',
                         'sport'];

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
        var cLogoClass = selectedLogos.eq(i).attr('class');
        for ( var k = 0; k < categories.length; k++ ) {
            if ( cLogoClass.indexOf( categories[k] ) != -1 ) {
                selectedNumIds.push(k);
                break;
            }
        }
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
    for ( var i=0; i < selectedCategoriesId.length-1; i++ ) {
        sumStr += categoriesVerbose[selectedCategoriesId[i]] + ', ';
    }
    sumStr += categoriesVerbose[selectedCategoriesId[selectedCategoriesId.length-1]] + ' events';
    return sumStr.charAt(0).toUpperCase() + sumStr.slice(1);
};

/**
 * Returns the numerical ID of the sorting logo selected, so that the sorting
 * type is equal to sortType[result].
 * @return {int} numerical ID of the sorting logo selected.
 *
 */
function getSelectedLogoNumId () {
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
 * Returns the min and max time corresponding to 0% and 100% position
 * of the sliders. Returned in 24h string format: 'Thh:mm:ss'.
 * The seconds field is optional and will appear only if it was specified in
 % the html in the first place.
 % Note: this function only fetches data from the html.
 * @return {[str, str]} Start and end time of slider bar.
 */
function getMinAndMaxTimes () {
    return ['T' + $( '#' + getSelectedTabHtmlId() + ' .timeline-header .head-block .time-helper-min-value' ).html(),
            'T' + $( '#' + getSelectedTabHtmlId() + ' .timeline-header .head-block .time-helper-max-value' ).html()]
}

/**
 * Converts a percentage position into an hour:min AM/PM string.
 * @param {str} A string describing a percentage (ex: '15.5%').
 * @return {str} A time string (ex: '8:55 am').
 */
function percentageToTimeString ( percentStr ) {
    var [tMin, tMax] = getMinAndMaxTimes();
    var dNew = new Date();

    // Converting min and max strings to milliseconds
    tMin = Date.parse(tMin);
    tMax = Date.parse(tMax);

    // Calculating milliseconds corresponding to percentage
    var newTime = percentStr.slice(0, percentStr.lastIndexOf("%"));
    newTime = parseFloat(newTime)/100;
    newTime = Math.round(tMin + (tMax - tMin)*newTime);
    dNew.setTime(newTime);

    // Formatting the new time string and returning
    var newTimeStr = dNew.toTimeString().split(":");
    var hour = parseFloat(newTimeStr[0]);
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


/**************************** Filter / sort list *****************************/

// Toggle selection of filter controls
$( '.filter-logos-wrapper .filter-logos' ).click( function() {
    $( this ).children( '.filter-logo' ).toggleClass( 'selected' );
    getEventDescriptionHolder().html( getSelectedCategoriesString() )
});

// Toggle selection of sort controls
$( '.sort-logos-wrapper .sort-logos' ).click( function() {
    $( '.sort-logos-wrapper .sort-logos .sort-logo' ).toggleClass( 'selected', false );
    $( this ).children( '.sort-logo' ).toggleClass( 'selected' );
});

/**************************** Times table        *****************************/

// Set the height of the hit area
$( '.event-holder .timeline-header .timeline-table .timeheader .hit-area' ).height( function() {
    // Height of the event table should usually be 40px...
    var c_height = 40;
    return 40 + $( '.event-holder .events-table' ).height();
});

// Drag the sliders
$( '.head-block .hit-area' ).on( 'mousedown', function(e) {
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

    // TODO: Filter events by time.

    });
});

/**************************** Event table        *****************************/

// Show event details when event is clicked
$( '.results .events-table .event' ).click( function() {
    $( this ).toggleClass( 'selected' );
});

// Close event details when click on arrow
$( '.results .events-table .event .event-details .deselect' ).click( function() {
    // Click will propagate to parent event and call toggle function there...
    // so toggleClass is actually called twice, and to make the window disappear
    // we have to set toggleClass to true manually here.

    $( this ).parents( '.event' ).toggleClass( 'selected' , true );

    // Other solution would be to stop upwards propagation of click event, but not
    // sure how to do this...
});