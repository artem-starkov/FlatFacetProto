let app = angular.module("app", []);
app.controller("ctrl", function ($scope, $http) {

    $scope.in_progress = true;
    $scope.result = 'Ожидание результатов'

    $scope.get_results = function(){
        if($scope.task_id == -1)
            return;
        $http({
                method: 'GET',
                url: '/task_info/' + $scope.task_id,
                async:false,
            }).then(function success (response) {
                $scope.loops += 1;
                $scope.produced = response.data.produced;
                $scope.task_id = response.data.task_id;
                $scope.target = response.data.target;
                $scope.dataset_size = response.data.dataset_size;
                document.getElementById('bar').style.width = (($scope.produced / $scope.target) * 100) + '%';
                if($scope.produced == $scope.target){
                    window.location.href='/dataset/' + $scope.task_id;
                    clearInterval($scope.timer);
                    $scope.in_progress = false;
                    if ($scope.loops > 1)
                        window.location.reload(false);
                }
            });
    }

    $scope.start = function(){
      $scope.get_results();
      $scope.timer = setInterval($scope.get_results, 1000);
  }

});