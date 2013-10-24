$(document).ready(function() {
  var headerHeight = $('header').outerHeight(true);
  var navHeight = $('nav').outerHeight(true);
  function stickNavbar () {
    if ($(window).scrollTop() > headerHeight) {
      $('header').css('margin-bottom', navHeight + 'px');
      $('nav').addClass('navbar-fixed-top');
    } 
    else {
      $('header').css('margin-bottom', '0');
      $('nav').removeClass('navbar-fixed-top');
    }
  }

  $(window).scroll(stickNavbar);
  stickNavbar();
});
