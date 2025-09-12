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

        // Array to track opened windows
        $scope.openedWindows = [];
        
        // Fallback function to open video with original dimensions
        $scope.openVideoWithDimensions = function(fullPath, width, height, padding) {
            var videoWindowWidth = width + padding;
            var videoWindowHeight = height + padding;
            
            var videoHTML = `
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Video Player</title>
                    <style>
                        body { margin: 0; padding: 0; background: #000; display: flex; justify-content: center; align-items: center; height: 100vh; }
                        video { max-width: 100%; max-height: 100%; }
                    </style>
                </head>
                <body>
                    <video controls autoplay muted loop>
                        <source src="${fullPath}" type="video/mp4">
                        <source src="${fullPath}" type="video/webm">
                        <source src="${fullPath}" type="video/ogg">
                        Your browser does not support the video tag.
                    </video>
                </body>
                </html>
            `;
            
            // Calculate position for side-by-side placement
            var position = $scope.getNextWindowPosition(videoWindowWidth, videoWindowHeight);
            console.log('Fallback video window position:', position, 'size:', videoWindowWidth + 'x' + videoWindowHeight);
            
            // Open in new window with video player
            var videoWindow = window.open('', '_blank', 'width=' + videoWindowWidth + ',height=' + videoWindowHeight + ',resizable=yes,scrollbars=yes');
            videoWindow.document.write(videoHTML);
            videoWindow.document.close();
            
            // Move window to calculated position
            try {
                videoWindow.moveTo(position.x, position.y);
                console.log('Moved fallback video window to:', position.x, position.y);
            } catch (e) {
                console.log('Could not move fallback video window:', e);
            }
            
            // Track the opened window
            $scope.openedWindows.push(videoWindow);
        };
        
        // Track window positions for side-by-side placement
        $scope.windowPositions = {
            currentX: 50,  // Starting X position
            currentY: 50,  // Starting Y position
            windowSpacing: 400,  // Fixed 400px spacing between windows
            maxWindowsPerRow: 5,  // Maximum 5 windows per row
            windowCount: 0  // Track total number of windows opened
        };
        
        // Calculate next window position for side-by-side placement
        $scope.getNextWindowPosition = function(windowWidth, windowHeight) {
            var pos = $scope.windowPositions;
            
            // Calculate position based on window count
            var row = Math.floor(pos.windowCount / pos.maxWindowsPerRow);
            var col = pos.windowCount % pos.maxWindowsPerRow;
            
            var position = {
                x: pos.currentX + (col * pos.windowSpacing),
                y: pos.currentY + (row * pos.windowSpacing)
            };
            
            // Increment window count for next window
            pos.windowCount++;
            
            return position;
        };
        
        // Close all open popup windows
        $scope.closeAllWindows = function() {
            var closedCount = 0;
            
            // Close all tracked windows
            for (var i = $scope.openedWindows.length - 1; i >= 0; i--) {
                try {
                    if ($scope.openedWindows[i] && !$scope.openedWindows[i].closed) {
                        $scope.openedWindows[i].close();
                        closedCount++;
                    }
                    // Remove from tracking array
                    $scope.openedWindows.splice(i, 1);
                } catch (e) {
                    console.log('Could not close window:', e);
                    // Remove from tracking array even if close failed
                    $scope.openedWindows.splice(i, 1);
                }
            }
            
            // Reset window positions when all windows are closed
            if (closedCount > 0) {
                $scope.windowPositions.currentX = 50;
                $scope.windowPositions.currentY = 50;
                $scope.windowPositions.windowCount = 0;
                console.log('Closed ' + closedCount + ' popup windows and reset positions');
            } else {
                console.log('No popup windows were open');
            }
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
	    $scope.viewFile = function(fullPath, width, height, fileType, thumbnailIndex) {
	    	if (!fullPath) {
	    		$scope.nextPage();
	    	} else {
	    		// Calculate window size based on image dimensions
	    		var windowWidth, windowHeight;
	    		var maxDimension = 1067; // Increased from 800 to 1067 (33% larger)
	    		var padding = 67; // Increased from 50 to 67 (33% larger)
	    		
	    		console.log('Opening file:', fullPath, 'with dimensions:', width, 'x', height, 'fileType:', fileType);
	    		
	    		if (width && height && width > 0 && height > 0) {
	    			if (fileType === 'video') {
	    				// For videos, use actual video dimensions
	    				windowWidth = width + padding;
	    				windowHeight = height + padding;
	    				console.log('Video window size (actual dimensions):', windowWidth, 'x', windowHeight);
	    			} else {
	    				// For images, calculate proportional size with max dimension of 1067
	    				if (width > height) {
	    					// Landscape image
	    					windowWidth = Math.min(width, maxDimension) + padding;
	    					windowHeight = Math.min(height * (maxDimension / width), maxDimension) + padding;
	    				} else {
	    					// Portrait image
	    					windowHeight = Math.min(height, maxDimension) + padding;
	    					windowWidth = Math.min(width * (maxDimension / height), maxDimension) + padding;
	    				}
	    				console.log('Image window size (proportional):', windowWidth, 'x', windowHeight);
	    			}
	    		} else {
	    			// Fallback to default size if dimensions not available
	    			windowWidth = 1333; // Increased from 1000 to 1333 (33% larger)
	    			windowHeight = 1600; // Increased from 1200 to 1600 (33% larger)
	    			console.log('Using default window size (dimensions not available):', windowWidth, 'x', windowHeight);
	    		}
	    		
	    		// Check if it's a video file and create a muted video player
	    		if (fileType === 'video') {
	    			// Check if there's a -LG version available
	    			var videoPath = fullPath;
	    			var baseName = fullPath.substring(0, fullPath.lastIndexOf('.'));
	    			var extension = fullPath.substring(fullPath.lastIndexOf('.'));
	    			var lgPath = baseName + '-LG' + extension;
	    			
	    			console.log('Original video path:', fullPath);
	    			console.log('Looking for -LG version:', lgPath);
	    			
	    			// Check if -LG version exists and get its dimensions
	    			$http({
	    				url: '/indexer/api.py',
	    				method: 'GET',
	    				params: {
	    					action: 'get_file_dimensions',
	    					file_path: lgPath
	    				}
	    			}).then(function(response) {
	    				console.log('API response for -LG video:', response.data);
	    				
	    				var lgWidth = width;
	    				var lgHeight = height;
	    				
	    				if (response.data && response.data.width && response.data.height) {
	    					lgWidth = response.data.width;
	    					lgHeight = response.data.height;
	    					console.log('Found -LG video dimensions:', lgWidth, 'x', lgHeight);
	    				} else {
	    					console.log('No -LG video found, using original dimensions');
	    					console.log('Response data:', response.data);
	    				}
	    				
	    				// Calculate window size for -LG video
	    				var videoWindowWidth = lgWidth + padding;
	    				var videoWindowHeight = lgHeight + padding;
	    				console.log('Video window size (LG dimensions):', videoWindowWidth, 'x', videoWindowHeight);
	    				
	    				// Create video HTML with -LG path
	    				var videoHTML = `
	    					<!DOCTYPE html>
	    					<html>
	    					<head>
	    						<title>Video Player</title>
	    						<style>
	    							body { margin: 0; padding: 0; background: #000; display: flex; justify-content: center; align-items: center; height: 100vh; }
	    							video { max-width: 100%; max-height: 100%; }
	    						</style>
	    					</head>
	    					<body>
	    						<video controls autoplay muted loop>
	    							<source src="${lgPath}" type="video/mp4">
	    							<source src="${lgPath}" type="video/webm">
	    							<source src="${lgPath}" type="video/ogg">
	    							<source src="${fullPath}" type="video/mp4">
	    							<source src="${fullPath}" type="video/webm">
	    							<source src="${fullPath}" type="video/ogg">
	    							Your browser does not support the video tag.
	    						</video>
	    					</body>
	    					</html>
	    				`;
	    				
	    				// Calculate position for side-by-side placement
	    				var position = $scope.getNextWindowPosition(videoWindowWidth, videoWindowHeight);
	    				console.log('Video window position:', position, 'size:', videoWindowWidth + 'x' + videoWindowHeight);
	    				
	    				// Open in new window with video player
	    				var videoWindow = window.open('', '_blank', 'width=' + videoWindowWidth + ',height=' + videoWindowHeight + ',resizable=yes,scrollbars=yes');
	    				videoWindow.document.write(videoHTML);
	    				videoWindow.document.close();
	    				
	    				// Move window to calculated position
	    				try {
	    					videoWindow.moveTo(position.x, position.y);
	    					console.log('Moved video window to:', position.x, position.y);
	    				} catch (e) {
	    					console.log('Could not move video window:', e);
	    				}
	    				
	    				// Track the opened window
	    				$scope.openedWindows.push(videoWindow);
	    			}).catch(function(error) {
	    				console.log('Error getting -LG dimensions, using original video:', error);
	    				// Fallback to original video with original dimensions
	    				$scope.openVideoWithDimensions(fullPath, width, height, padding);
	    			});
	    			
	    			return; // Exit early since we're handling video asynchronously
	    		} else {
	    			// For images, create a custom image viewer with folder navigation
	    			var imageHTML = `
	    				<!DOCTYPE html>
	    				<html>
	    				<head>
	    					<title>Image Viewer</title>
	    					<style>
	    						body { 
	    							margin: 0; 
	    							padding: 0; 
	    							background: #000; 
	    							display: flex; 
	    							justify-content: center; 
	    							align-items: center; 
	    							height: 100vh; 
	    							cursor: pointer;
	    							overflow: hidden;
	    						}
	    						img { 
	    							max-width: 100%; 
	    							max-height: 100%; 
	    							object-fit: contain;
	    						}
	    						.nav-info {
	    							position: fixed;
	    							top: 10px;
	    							right: 10px;
	    							background: rgba(0,0,0,0.7);
	    							color: white;
	    							padding: 5px 10px;
	    							border-radius: 3px;
	    							font-family: Arial, sans-serif;
	    							font-size: 12px;
	    						}
	    						.loading {
	    							position: fixed;
	    							top: 50%;
	    							left: 50%;
	    							transform: translate(-50%, -50%);
	    							color: white;
	    							font-family: Arial, sans-serif;
	    						}
	    					</style>
	    				</head>
	    				<body>
	    					<div class="nav-info" id="navInfo">Use ← → arrow keys to navigate folder</div>
	    					<div class="loading" id="loading">Loading folder images...</div>
	    					<img src="${fullPath}" alt="Image" id="currentImage" style="display: none;">
	    					<script>
	    						var currentIndex = 0;
	    						var folderImages = [];
	    						var currentPath = '${fullPath}';
	    						
	    						// Load folder images from API
	    						function loadFolderImages() {
	    							var xhr = new XMLHttpRequest();
	    							var apiUrl = '/indexer/api.py?action=folder_images&current_path=' + encodeURIComponent(currentPath);
	    							console.log('Loading folder images from:', apiUrl);
	    							
	    							xhr.open('GET', apiUrl, true);
	    							xhr.onreadystatechange = function() {
	    								if (xhr.readyState === 4) {
	    									if (xhr.status === 200) {
	    										try {
	    											console.log('API Response length:', xhr.responseText.length);
	    											console.log('API Response preview:', xhr.responseText.substring(0, 200));
	    											
	    											if (xhr.responseText.trim() === '') {
	    												console.error('Empty response from API');
	    												document.getElementById('loading').textContent = 'Empty response from server';
	    												return;
	    											}
	    											
	    											var response = JSON.parse(xhr.responseText);
	    											if (response.results && response.results.length > 0) {
	    												folderImages = response.results;
	    												console.log('Found', folderImages.length, 'images in folder');
	    												
	    												// Find current image index in folder
	    												for (var i = 0; i < folderImages.length; i++) {
	    													if (folderImages[i].fullPath === currentPath) {
	    														currentIndex = i;
	    														break;
	    													}
	    												}
	    												// Hide loading, show image
	    												document.getElementById('loading').style.display = 'none';
	    												document.getElementById('currentImage').style.display = 'block';
	    												updateImageInfo();
	    											} else {
	    												console.log('No images found in folder or empty results');
	    												document.getElementById('loading').textContent = 'No other images found in this folder';
	    											}
	    										} catch (e) {
	    											console.error('Error parsing folder images:', e);
	    											console.error('Response text:', xhr.responseText);
	    											console.error('Response length:', xhr.responseText.length);
	    											document.getElementById('loading').textContent = 'Error parsing folder images: ' + e.message + ' (Response length: ' + xhr.responseText.length + ')';
	    										}
	    									} else {
	    										console.error('HTTP Error:', xhr.status, xhr.statusText);
	    										document.getElementById('loading').textContent = 'HTTP Error: ' + xhr.status;
	    									}
	    								}
	    							};
	    							xhr.send();
	    						}
	    						
	    						function updateImage(index) {
	    							if (index >= 0 && index < folderImages.length) {
	    								document.getElementById('currentImage').src = folderImages[index].fullPath;
	    								currentPath = folderImages[index].fullPath;
	    								currentIndex = index;
	    								updateImageInfo();
	    							}
	    						}
	    						
	    						function updateImageInfo() {
	    							document.title = 'Image Viewer - ' + (currentIndex + 1) + ' of ' + folderImages.length;
	    						}
	    						
	    						document.addEventListener('keydown', function(e) {
	    							if (e.key === 'ArrowLeft') {
	    								e.preventDefault();
	    								var newIndex = currentIndex > 0 ? currentIndex - 1 : folderImages.length - 1;
	    								updateImage(newIndex);
	    							} else if (e.key === 'ArrowRight') {
	    								e.preventDefault();
	    								var newIndex = currentIndex < folderImages.length - 1 ? currentIndex + 1 : 0;
	    								updateImage(newIndex);
	    							} else if (e.key === 'Escape') {
	    								window.close();
	    							}
	    						});
	    						
	    						// Load folder images when page loads
	    						loadFolderImages();
	    						
	    						// Hide nav info after 3 seconds
	    						setTimeout(function() {
	    							document.getElementById('navInfo').style.display = 'none';
	    						}, 3000);
	    					</script>
	    				</body>
	    				</html>
	    			`;
	    			
	    			// Calculate position for side-by-side placement
	    			var position = $scope.getNextWindowPosition(windowWidth, windowHeight);
	    			console.log('Image window position:', position, 'size:', windowWidth + 'x' + windowHeight);
	    			
	    			// Open in new window with image viewer
	    			var imageWindow = window.open('', '_blank', 'width=' + windowWidth + ',height=' + windowHeight + ',resizable=yes,scrollbars=yes');
	    			imageWindow.document.write(imageHTML);
	    			imageWindow.document.close();
	    			
	    			// Move window to calculated position
	    			try {
	    				imageWindow.moveTo(position.x, position.y);
	    				console.log('Moved image window to:', position.x, position.y);
	    			} catch (e) {
	    				console.log('Could not move image window:', e);
	    			}
	    			
	    			// Track the opened window
	    			$scope.openedWindows.push(imageWindow);
	    		}
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
