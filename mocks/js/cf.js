/* Filter / sort list */

// Toggle selection of filter controls
$( '.filter-logos-wrapper .filter-logos' ).click(function() {
    $( this ).children( '.filter-logo' ).toggleClass( 'selected' );
});

$( '.sort-logos-wrapper .sort-logos' ).click(function() {
    $( this ).children( '.sort-logo' ).toggleClass( 'selected' );
});