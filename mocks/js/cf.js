/* Filter / sort list */

// Toggle selection of filter controls
$( '.filter-logos-wrapper .filter-logos' ).click( function() {
    $( this ).children( '.filter-logo' ).toggleClass( 'selected' );
    // TODO: the text in .timeheader .left-column-header .col-header-cat should also be updated
});

// Toggle selection of sort controls
$( '.sort-logos-wrapper .sort-logos' ).click( function() {
    $( this ).children( '.sort-logo' ).toggleClass( 'selected' );
});

/* Times table */

$( '.event-holder .timeline-header .timeline-table .timeheader .hit-area' ).height( function() {
    // Height of the event table should usually be 40px...
    var c_height = 40;
    return 40 + $( '.event-holder .events-table' ).height();
});

/* Event table */

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
});