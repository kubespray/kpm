#!/bin/sh

/opt/kpm-ui/node_modules/.bin/gulp build --dir build --config $KPMUI_ENV
/opt/kpm-ui/node_modules/.bin/gulp serve --dir build
