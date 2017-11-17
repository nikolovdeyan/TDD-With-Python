/* global $ */

window.Superlists = {};

window.Superlists.initialize = function() {

  $('input[name="text"]').on('keypress', () => {
    $('.has-error').hide();
  });

};
