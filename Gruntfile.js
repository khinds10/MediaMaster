/**
 * Gruntfile.js
 *
 * @author Kevin Hinds @ kevinhinds.com
 * @license http://opensource.org/licenses/gpl-license.php GNU Public License
 */
module.exports = function(grunt) {

	// Project configuration.
	grunt
		.initConfig({
				pkg : grunt.file.readJSON('package.json'),
				uglify : {
					options : {
						banner : '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n',
						mangle : false
					},					
					build : {
						src : [
								'node_modules/angular/angular.min.js',
								'node_modules/angular-ui-bootstrap/ui-bootstrap.min.js',
								'node_modules/angular-ui-bootstrap/ui-bootstrap-tpls.min.js',
								'build/angular/app.js',
								'build/angular/shared/controllers/viewer.js'
							  ],
						dest : 'js/app.min.js'
					}
				},
				sass : {
					dist : {
						options : {
							style : 'compact'
						},
						files : {
							'css/main.css' : 'build/scss/main.scss',
						}
					}
				},
				cssmin : {
					options : {
						shorthandCompacting : false,
						roundingPrecision : -1
					},
					target : {
						files : {
							'css/bootstrap.min.css' : [ 'node_modules/bootstrap/dist/css/bootstrap.min.css' ],
							'css/font-awesome.min.css' : [ 'node_modules/font-awesome/css/font-awesome.min.css' ],
							'css/main.min.css' : [ 'css/main.css' ]
						}
					}
				}
			});

	// Load the plugins including the file watcher
	grunt.loadNpmTasks('grunt-contrib-uglify');
	grunt.loadNpmTasks('grunt-contrib-sass');
	grunt.loadNpmTasks('grunt-contrib-cssmin');

	// Run all tasks
	grunt.registerTask('default', [ 'uglify', 'sass', 'cssmin' ]);
};