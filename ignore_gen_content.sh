#!/bin/bash

git checkout -- site_docs/biochemistry/topic??/*.html
git checkout -- site_docs/biochemistry/topic??/index.md
git clean -f -- ":(glob)site_docs/**/bbq-*-questions.txt"
