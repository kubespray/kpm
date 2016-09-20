#!/bin/sh

gulp build $KPMUI_ENV

gulp build --config $KPMUI_ENV
gulp serve --dir build
