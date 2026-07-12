#!/bin/sh

wc -l $(find . -name "bbq-*.txt") | sort -nr
