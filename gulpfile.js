'se strict';

var gulp = require('gulp');
var concat = require('gulp-concat');
var sass = require('gulp-sass');
var uglify = require('gulp-uglify');
var processhtml = require('gulp-processhtml');
var templateCache = require('gulp-angular-templatecache');
var rename = require('gulp-rename');
var express = require('express');

const default_setup = {
  config: 'local',
  port: 8081,
  dir: 'src'
};

var setup = require('yargs').default(default_setup).argv;

// Start express server
gulp.task('serve', function() {
  var server = express();
  var path = __dirname + '/' + setup.dir;
  console.log('* Serving ' + path + ' on port ' + setup.port);
  server.use(express.static(path));
  server.listen(setup.port);
});

// Select configuration file from --config option
gulp.task('config', function() {
  var fs = require('fs');
  var config_path = 'src/config/' + setup.config + '.js';
  if (fs.existsSync(config_path)) {
    console.log('* Using configuration: ' + setup.config);
    gulp.src(config_path)
      .pipe(rename('config.js'))
      .pipe(gulp.dest(setup.dir + '/config'));
  }
  else {
    console.log("Error: configuration file '" + config_path + "' doesn't exist");
    process.exit(1);
  }
});

// Compile all .scss files to app/build/style.min.css
gulp.task('sass', function () {
  gulp.src('src/style/**/*.scss')
    .pipe(sass({outputStyle: 'compressed'}).on('error', sass.logError))
    .pipe(concat('style.min.css'))
    .pipe(gulp.dest(setup.dir + '/style'));
});

// Build the application to --dir directory
gulp.task('build', ['config', 'sass'], function() {
  // Concat and minify application javascripts
  gulp.src('src/app/**/*.js')
    .pipe(concat('app.min.js'))
    .pipe(uglify({mangle: false, compress: true}))
    .pipe(gulp.dest(setup.dir + '/js'))

  // Process index.html to replace links with minified files
  gulp.src('src/index.html')
    .pipe(processhtml())
    .pipe(gulp.dest(setup.dir));

  // Concat angular templates
  gulp.src('src/app/**/*.html')
    .pipe(templateCache({
      root: 'app',
      module: 'kpm-ui'
    }))
    .pipe(gulp.dest(setup.dir + '/js'));

  // Copy images
  gulp.src('src/images/**')
    .pipe(gulp.dest(setup.dir + '/images'));

  // Copy CSS images
  gulp.src('src/style/images/**')
    .pipe(gulp.dest(setup.dir + '/style/images'));
});

// Sass with watcher + server. For development only!
gulp.task('default', ['config', 'sass', 'serve'], function() {
  gulp.watch('src/style/**/*.scss', ['sass']);
});

