/* global $ QUnit */

QUnit.test("Errors should be hidden on keypress.", assert => {
  initialize();
  $('input[name="text"]').trigger('keypress');
  assert.equal($('.has-error').is(':visible'), false);
});

QUnit.test("Errors aren't hidden if there is no keypress.", assert => {
  initialize();
  assert.equal($('.has-error').is(':visible'), true);
});

