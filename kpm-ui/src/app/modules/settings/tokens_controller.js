'use strict';

app.controller('SettingsTokensController', function($scope, KpmApi) {
  $scope.loadTokens = function() {
    KpmApi.get('account/tokens')
    .success(function(data) {
      $scope.tokens = data;
    })
    .error(function() {
    });
  };

  $scope.deleteToken = function(token) {
  };

  $scope.loadTokens();
});
