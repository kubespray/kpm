var app = angular.module('kpm-ui', ['ngMaterial', 'ui.router']);

app.config(function($stateProvider) {

  // Bind routes to controllers
  $stateProvider
  .state('home', {
    url: '',
    title: 'Welcome to KPM',
    controller: 'HomeController',
    templateUrl: 'app/modules/home/home.html'
  })
  .state('packages', {
    url: '/packages',
    title: 'Package list',
    controller: 'PackagesController',
    templateUrl: 'app/modules/packages/packages.html'
  })
  .state('package', {
    // Type 'any' prevents from encoding the '/' in package name
    url: '/package/{name:any}',
    title: 'Package detail',
    controller: 'PackagesController',
    templateUrl: 'app/modules/packages/details.html'
  })
  .state('login', {
    url: '/login',
    title: 'Login',
    controller: 'LoginController',
    templateUrl: 'app/modules/user/login.html'
  })
  .state('signup', {
    url: '/signup',
    title: 'Create an account',
    controller: 'SignupController',
    templateUrl: 'app/modules/user/signup.html'
  })
  .state('error404', {
    templateUrl: 'app/modules/errors/404.html'
  });
});

app.controller('AppController', function($rootScope, $sce, Session) {
  // Expose modules in root scope for templates convenience
  $rootScope.config = Config;
  $rootScope.session = Session;

  // Update page title on state change
  $rootScope.$on('$stateChangeSuccess', function(event, toState) {
    $rootScope.pageTitle = $sce.trustAsHtml('KPM | ' + toState.title);
  });

  // Application-wide ui variables
  $rootScope.ui = {
    loading: false
  };
});

