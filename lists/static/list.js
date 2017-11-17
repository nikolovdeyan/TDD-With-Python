/* global $ */

let initialize = function() {

  $('input[name="text"]').on('keypress', () => {
    $('.has-error').hide();
  });

};
