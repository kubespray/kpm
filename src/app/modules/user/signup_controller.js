app.controller('SignupController', function($scope, $state, KpmApi, Session) {

  // Create user
  $scope.submit = function() {
    KpmApi.post('users', {
      user: {
        'username': $scope.username,
        'email': $scope.email,
        'password': $scope.password,
        'password_confirmation': $scope.password_confirmation
      }
    })
    .success(function(data) {
      // Login user after sign-up
      Session.username = data.username;
      Session.email = data.email;
      KpmApi.authorization_token = data.token;

      // Redirect to homepage
      $state.go('packages');
    })
    .error(function(data) {
      if (data.errors) {
        $scope.errors = [];
        for (key in data.errors) {
          // Build error message from API error reporting
          $scope.errors.push(key + ' ' + data.errors[key].join(' '));
        }
      }
      else {
        $scope.errors = ['Oh no, something wrong happened!'];
      }
    });
  };
});
