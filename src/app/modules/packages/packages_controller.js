'use strict';

app.controller('PackagesController', function($scope, $stateParams, KpmApi) {

  $scope.availableSorts = {
    'Downloads': {sort_descending: true, sort_order: 'downloads'},
    'Last update': {sort_descending: true, sort_order: 'updated_at'},
    'Name': {sort_order: 'default'}
  };

  // Filtering and sorting parameters
  $scope.queryParams = {};

  $scope.getPackages = function() {
    console.log($scope.queryParams);
    KpmApi.get('packages', $scope.queryParams)
    .success(function(data) {
      $scope.ui.loading = false;
      $scope.packages = data;
    })
    .error(function(data) {
      $scope.error = $scope.build_error(data);
      $scope.ui.loading = false;
    });
  };

  $scope.applySort = function(querySort) {
    $scope.queryParams.sort_order = querySort.sort_order;
    $scope.queryParams.sort_descending = querySort.sort_descending;
    $scope.getPackages();
  };

  // Apply search parameter if any
  if ($stateParams.search) {
    $scope.queryParams.named_like = $stateParams.search;
  };

  // Init
  $scope.getPackages();
});
