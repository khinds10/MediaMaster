/**
 * MediaMaster Angular JS App
 * @author Kevin Hinds @ kevinhinds.com
 * @license http://opensource.org/licenses/gpl-license.php GNU Public License
 */
var MainApp = angular.module('MediaMasterApp', ['ui.bootstrap', 'viewerCtrl']);

// Intercept POST requests, convert to standard form encoding
MainApp.config([ '$httpProvider', function($httpProvider) {
    $httpProvider.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded";
    $httpProvider.defaults.transformRequest.unshift(function(data, headersGetter) {
	var key, result = [];
	for (key in data) {
	    if (data.hasOwnProperty(key)) {
			if (typeof (data[key]) == "undefined") {
				data[key] = '';
				result.push(encodeURIComponent(key) + "=" + encodeURIComponent(data[key]));
			}
	    }
	}
	return result.join("&");
    });
} ]);