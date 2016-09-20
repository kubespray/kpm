#!/bin/sh

gulp build --dir build --config $KPMUI_ENV
gulp serve --dir build
