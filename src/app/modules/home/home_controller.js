app.controller('HomeController', function($scope, $state, KpmApi, Session) {
  if (Session.isAuthenticated()) {
    // Fetch user's packages
    $scope.ui.loading = true;
    KpmApi.get('packages', {
      username: Session.user.username
    })
    .success(function(data) {
      $scope.ui.loading = false;
      $scope.packages = data;
    })
    .error(function(data) {
      $scope.ui.loading = false;
    });
  }
  else {
    // Redirect unauthenticated users to login page
    $state.go('login');
  }
});
