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
}

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
}

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
}

/**
 * Returns the start and end positions of the time sliders.
 * @return {[int, int]} Start and End time in percentage.
 *
 */
// TODO

/**
 * Returns the min and max time corresponding to 0% and 100% position
 * of the sliders. Returned in string format: 'hh:mm am/pm'.
 * @return {[str, str]} Start and end time of slider bar.
 */

/**
 * Converts a percentage position into an hour:min AM/PM string.
 * @param {str} A string describing a percentage (ex: '15.5%').
 * @return {str} A time string (ex: '8:55 am').
 */
// TODO


/**************************** Filter / sort list *****************************/

/**
 * Returns the jQuery object which holds the event description string
 * @return {jQuery Object} Object which holds the event description string.
 */
 function getEventDescriptionHolder () {
     return $( '#' + getSelectedTabHtmlId() + ' .timeline-header .head-block .left-column-header .col-header-cat' );
 }

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
    var maxXAnchorRight = $( this ).parents( '.timeheader' ).width();
    var maxWidth = maxXAnchorRight;

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
        }

    // TODO: update the strings of the numeric time displays. Filter events by time.

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