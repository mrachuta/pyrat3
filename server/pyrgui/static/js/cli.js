/*
Function provide a state for each client details div
(visible or invisible) - basing on data stored in
localStorage.
*/

function loadClientDetailsState () {
  var visibleDivs = JSON.parse(localStorage.getItem('visible_divs'));
    if (visibleDivs !== null) {
      for (var i=0; i<visibleDivs.length; i++) {
        $(visibleDivs[i].id).show();
      }
    }
}

// Function catching page change request (on paginated client table).

function setClientTableCurrUrl () {
  $('.change-page').click(function (event) {
    // Prevent from use hyperlink
    event.preventDefault();
    /*
    Catch requested link, and set variable clientTableCurrUrl
    as requested link. This will allow to load this page via
    AJAX request and keep it refreshed.
    */
    clientTableCurrUrl = $(this).attr('href');
    loadClientTable();
  })
}


// Run functions when page is loaded

$(document).ready(function () {
  loadClientDetailsState();
  setClientTableCurrUrl();
});