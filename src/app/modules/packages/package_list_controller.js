'use strict';

app.controller('PackageListController', function($scope, $stateParams, KpmApi,
      Package) {

  $scope.availableSorts = {
    'Downloads': {sort_descending: true, sort_order: 'downloads', icon: 'download'},
    'Stars': {sort_descending: true, sort_order: 'stars', icon: 'star'},
    'Last update': {sort_descending: true, sort_order: 'updated_at', icon: 'clock-o'},
    'Name': {sort_order: 'default', icon: 'font'}
  };

  $scope.selectedSort = $scope.availableSorts['Downloads'];

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

  // Init (get package list with default sort)
  $scope.applySort($scope.selectedSort);
});
