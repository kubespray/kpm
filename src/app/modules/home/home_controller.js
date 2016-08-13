app.controller('HomeController', function($scope, $state, KpmApi, Session) {
  // Redirect unauthenticated users to login page
  if (!Session.isAuthenticated()) {
    $state.go('login');
  }

  // Fetch user's packages
  $scope.ui.loading = true;
  KpmApi.get('packages', {
    username: Session.username
  })
  .success(function(data) {
    $scope.ui.loading = false;
    $scope.packages = data;
  })
  .error(function(data) {
    $scope.ui.loading = false;
  });
});
