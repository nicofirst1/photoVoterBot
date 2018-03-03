#!/usr/bin/env bash
#usage ./commitAndPush.sh "comment", comment is optional
if [ $# -eq 0 ]
  then
    comment="bug fixed"
  else
    comment="$@"
fi

git add commitAndPush.sh  main.py Pipfile Procfile requirements.txt runtime.txt;
git commit -m "$comment";
git push origin master;
