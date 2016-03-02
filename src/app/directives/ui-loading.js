/**
 * Display a loading layer over an element
 * Usage <element ui-loading="is_loading">...</element>
 */
app.directive('uiLoading', function () {
  return {
    restrict: 'A',
    scope: false,
    link: function(scope, element, attrs) {
      var loadingLayer = angular.element('<div class="loading"></div>');
      element.append(loadingLayer);
      element.addClass('loading-container');
      scope.$watch(attrs.uiLoading, function(value) {
        loadingLayer.toggleClass('ng-hide', !value);
      });
    }
  };
});
