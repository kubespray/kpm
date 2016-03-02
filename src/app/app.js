var app = angular.module('kpm-ui', ['ui.router']);

app.config(function($stateProvider, $urlRouterProvider) {

  $urlRouterProvider.otherwise('/404');

  // Bind routes to controllers
  $stateProvider
    .state('packages', {
      url: '/packages',
      title: 'Package list',
      controller: 'PackagesController',
      templateUrl: 'app/modules/packages/packages.html'
    })
    .state('package', {
      url: '/package/:id',
      title: 'Package detail',
      controller: 'PackagesController',
      templateUrl: 'app/modules/packages/details.html'
    })
    .state('home', {
      url: '',
      onEnter: function($timeout, $state)  {
        $timeout(function() {
          $state.go('packages');
        });
      }
    })
    .state('error404', {
      templateUrl: 'app/modules/errors/404.html'
    });
});

app.controller('AppController', function($scope) {
  $scope.config = Config;
  console.log("AppController()");
});
