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
        sumStr += categoriesVerbose[i] + ', ';
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


/**************************** Filter / sort list *****************************/

// Toggle selection of filter controls
$( '.filter-logos-wrapper .filter-logos' ).click( function() {
    $( this ).children( '.filter-logo' ).toggleClass( 'selected' );
    // TODO: the text in .timeheader .left-column-header .col-header-cat should also be updated
    $( '#' + getSelectedTabHtmlId() + ' .timeline-header .head-block .left-column-header .col-header-cat' ).html(
        getSelectedCategoriesString()
    )
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