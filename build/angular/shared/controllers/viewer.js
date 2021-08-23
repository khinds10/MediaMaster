/**
 * viewer.js
 *   controller for media file viewer
 *
 * @author Kevin Hinds @ kevinhinds.com
 * @license http://opensource.org/licenses/gpl-license.php GNU Public License
 */
var viewerCtrl = angular.module("viewerCtrl", []);
viewerCtrl.controller("viewerCtrl", [ '$scope', '$http', function($scope, $http) {

		// current page
		$scope.page = 0;
	
	    // current page
		$scope.years = 1;
	
	    // sort default
	    $scope.sortType = 'random';
	
		// first page
		$scope.firstPage = function() {
			$scope.page = 0;
			$scope.getResults();
		}
		
		// next page
		$scope.nextPage = function() {
			$scope.page = $scope.page + 1;
			$scope.getResults();
		}

		// prev page
		$scope.prevPage = function() {
			if ($scope.page > 0) {
				$scope.page = $scope.page - 1;
			}
			$scope.getResults();
		}
		
        // set the sort based on the selected
	    $scope.setSort = function(sortType) {
        	$scope.sortType = sortType;
        	$scope.getResults();
	    };

        // set the sort based on the selected
	    $scope.setYears = function(years) {
        	$scope.years = years;
        	$scope.getResults();
	    };


        // load results with query parameters from python script
		$scope.getResults = function() {
		    var date = new Date();
            var currentYear = date.getFullYear();
		    var yearsAge = currentYear - $scope.years;
		    urlQuery = '/indexer/query.py?mediaType=' + $scope.mediaType + '&sortType=' + $scope.sortType + '&keyword=' + $scope.keyword + '&page=' + $scope.page + '&year=' + yearsAge;
    		$scope.thumbnails = [];
            $http({
                url : urlQuery,
                method : "GET",
            }).then(function(response) {
                $scope.thumbnails = response.data.results;
            });
		};
		
        // open file
	    $scope.viewFile = function(fullPath) {
	    	if (!fullPath) {
	    		$scope.nextPage();
	    	} else {
	    		window.open(fullPath, fullPath, 'width=500,height=600');
	    	}
	    }
	    
        // setup the initial thumbnail results
        $scope.thumbnails = [];
        $scope.keyword = '';
        $scope.mediaType = 'all';
        $scope.sortType = 'random';
		$scope.getResults();
}]);
