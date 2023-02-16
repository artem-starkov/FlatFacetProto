let app = angular.module("app", []);
app.controller("ctrl", function ($scope, $http) {

    $scope.run_id = -1;

    $scope.stop_run = function(){
    console.log($scope.run_id);
        if($scope.run_id == -1)
            return;
        $http({
                method: 'POST',
                url: '/stop_run/' + $scope.run_id,
                async:false,
            }).then(function success (response) {
                //window.location.href='/dataset/' + $scope.task_id;
                console.log(1);
            });
    }

    $scope.init = function(run_id){
	    $scope.run_id = run_id;
	}

});

