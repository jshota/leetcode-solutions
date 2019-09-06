#!/bin/bash
echo '1. optimized layout'
echo '2. initial commit'
echo '3. delete files'
echo 'or customize comment'
read input

case $input in
    1) 
        input='optimized layout'
    ;;
    2) 
        input='initial commit'
    ;; 
    3) 
        input='deleted files'
    ;;
esac

git add . 
git commit -m "feat: $input"
git push origin master
