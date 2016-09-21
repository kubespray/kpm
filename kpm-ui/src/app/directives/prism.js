'use strict';

/**
 * Usage: <code prism="yaml"></code>
 */
app.directive('prism', function() {
  return {
    restrict: 'A',
    scope: {
      prism: '@'
    },
    link: function(scope, element) {
      element.addClass('language-' + scope.prism);
      element.ready(function() {
        Prism.highlightElement(element[0]);
      });
    }
  };
});
