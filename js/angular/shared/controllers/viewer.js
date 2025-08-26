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
		$scope.years = 5;
	
	    // sort default
	    $scope.sortType = 'newest';
	
        // sort default modelPreview is shown
	    $scope.modelPreview = false;
	    
        // favorites mode flag
	    $scope.favoritesMode = false;
	
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
	    
        // set the sort based on the selected
	    $scope.setModelPreview = function(modelPreview) {
        	$scope.modelPreview = modelPreview;
        	$scope.getResults();
	    };	    

        // Initialize exclusiveOption
        $scope.exclusiveOption = null;

        // Define setExclusiveOption function
        $scope.setExclusiveOption = function(option) {
            $scope.exclusiveOption = option;
            $scope.getResults();
        };
        
        // Toggle favorites mode
        $scope.toggleFavoritesMode = function() {
            $scope.page = 0; // Reset to first page
            $scope.getResults();
        };
        
        // Toggle favorite status for a file
        $scope.toggleFavorite = function(thumbnail, event) {
            // Stop event propagation to prevent opening the file
            if (event) {
                event.stopPropagation();
            }
            
            const action = thumbnail.isFavorite ? 'remove' : 'add';
            
            $http({
                url: '/indexer/api.py',
                method: 'GET',
                params: {
                    action: action,
                    file_id: thumbnail.fileId
                }
            }).then(function(response) {
                if (response.data.success) {
                    thumbnail.isFavorite = !thumbnail.isFavorite;
                }
            });
        };

        // load results with query parameters from python script
		$scope.getResults = function() {
		    var date = new Date();
            var currentYear = date.getFullYear();
		    var yearsAge = currentYear - $scope.years;
		    
		    var urlQuery = '/indexer/api.py?' + 
		        'action=query' +
		        '&mediaType=' + ($scope.mediaType || 'all') + 
		        '&sortType=' + ($scope.sortType || 'newest') + 
		        '&keyword=' + ($scope.keyword || '') + 
		        '&page=' + ($scope.page || 0) + 
		        '&year=' + yearsAge +
		        '&modelPreview=' + $scope.modelPreview + 
		        '&favorites=' + $scope.favoritesMode;

		    // Add the exclusive option if set
		    if ($scope.exclusiveOption) {
		        urlQuery += '&' + $scope.exclusiveOption + '=true';
		    }

		    console.log(urlQuery);

		    $scope.thumbnails = [];
		    $http({
		        url: urlQuery,
		        method: "GET",
		    }).then(function(response) {
		        $scope.thumbnails = response.data.results;
		    });
		};
		
        // open file
	    $scope.viewFile = function(fullPath, width, height) {
	    	if (!fullPath) {
	    		$scope.nextPage();
	    	} else {
	    		// Calculate window size based on image dimensions
	    		var windowWidth, windowHeight;
	    		var maxDimension = 800;
	    		var padding = 50; // Add some padding for window borders
	    		
	    		console.log('Opening file:', fullPath, 'with dimensions:', width, 'x', height);
	    		
	    		if (width && height && width > 0 && height > 0) {
	    			// Calculate proportional size with max dimension of 800
	    			if (width > height) {
	    				// Landscape image
	    				windowWidth = Math.min(width, maxDimension) + padding;
	    				windowHeight = Math.min(height * (maxDimension / width), maxDimension) + padding;
	    			} else {
	    				// Portrait image
	    				windowHeight = Math.min(height, maxDimension) + padding;
	    				windowWidth = Math.min(width * (maxDimension / height), maxDimension) + padding;
	    			}
	    			console.log('Calculated window size:', windowWidth, 'x', windowHeight);
	    		} else {
	    			// Fallback to default size if dimensions not available
	    			windowWidth = 1000;
	    			windowHeight = 1200;
	    			console.log('Using default window size (dimensions not available):', windowWidth, 'x', windowHeight);
	    		}
	    		
	    		window.open(fullPath, fullPath, 'width=' + windowWidth + ',height=' + windowHeight);
	    	}
	    }
	    
        // setup the initial thumbnail results
        $scope.thumbnails = [];
        $scope.keyword = '';
        $scope.mediaType = 'all';
        $scope.sortType = 'newest';
        $scope.isGrown = false;
        $scope.isExpanded = false;
        $scope.isFeatured = false;
        $scope.favoritesMode = false;
		$scope.getResults();
}]);
