/**
 * サンプルのAngular1アプリケーション
 * ユーザー認証と連携するフロントエンド
 */
(function() {
    'use strict';

    angular
        .module('authApp', [])
        .controller('AuthController', AuthController)
        .service('AuthService', AuthService);

    AuthController.$inject = ['$scope', 'AuthService'];

    function AuthController($scope, AuthService) {
        var vm = this;

        // モデル
        vm.username = '';
        vm.password = '';
        vm.isLoggedIn = false;
        vm.errorMessage = '';

        // メソッド
        vm.login = login;
        vm.logout = logout;
        vm.checkLoginStatus = checkLoginStatus;

        // 初期化
        activate();

        function activate() {
            checkLoginStatus();
        }

        function login() {
            if (!vm.username || !vm.password) {
                vm.errorMessage = 'ユーザー名とパスワードを入力してください';
                return;
            }

            AuthService.login(vm.username, vm.password)
                .then(function(response) {
                    if (response.success) {
                        vm.isLoggedIn = true;
                        vm.errorMessage = '';
                    } else {
                        vm.errorMessage = 'ログインに失敗しました';
                    }
                })
                .catch(function(error) {
                    vm.errorMessage = 'エラーが発生しました: ' + error;
                });
        }

        function logout() {
            AuthService.logout()
                .then(function() {
                    vm.isLoggedIn = false;
                    vm.username = '';
                    vm.password = '';
                });
        }

        function checkLoginStatus() {
            AuthService.isLoggedIn()
                .then(function(status) {
                    vm.isLoggedIn = status;
                });
        }
    }

    AuthService.$inject = ['$http'];

    function AuthService($http) {
        var service = {
            login: login,
            logout: logout,
            isLoggedIn: isLoggedIn
        };

        return service;

        function login(username, password) {
            return $http.post('/users/login', {
                username: username,
                password: password
            }).then(function(response) {
                return response.data;
            });
        }

        function logout() {
            return $http.post('/users/logout')
                .then(function(response) {
                    return response.data;
                });
        }

        function isLoggedIn() {
            return $http.get('/users/status')
                .then(function(response) {
                    return response.data.isLoggedIn;
                });
        }
    }
})();
