#!/usr/bin/bash

if [ -z $1 ] ; then
  echo "Plase, pass the increment level for the new project version:"
  echo "1 -> {0}. 1 . 0"
  echo "2 ->  0 .{1}. 0"
  echo "3 ->  0 . 1 .{0}"
  echo
  echo "e.g.:"
  echo "./gen_tag 2"
  echo "-> old: 1.1.3"
  echo "-> new: 1.2.0"

  exit 0

elif [ $1 -lt 1 ] || [ $1 -gt 3 ] ; then
  echo "Invalid increment version"

  exit 0
fi

git_stash=$(git status)

echo $git_stash

project=pyproject.toml

echo "getting version line in $project"
line_number=$(nl pyproject.toml | sed -n '/name\ =\ \"Tchangos\"/{n;p}' | awk '{print $1}')
echo "-> $line_number"

echo "extracting line content ->"
line_content=$(sed -n $line_number'p' $project)
echo "-> $line_content"

echo "extracting project version"
version=$(echo $line_content | sed 's/version\ =\ //' | sed 's/\"//gI' | sed 's/\ //gI')
echo "-> $version"

echo "updating project version"
n1=$(echo $version | awk -F. '{print $1}')
n2=$(echo $version | awk -F. '{print $2}')
n3=$(echo $version | awk -F. '{print $3}')

case $1 in
  '1')
    n1=$((n1 + 1))
    n2=0
    n3=0
    ;;
  '2')
    n2=$((n2 + 1))
    n3=0
    ;;
  '3')
    n3=$((n3 + 1))
    ;;
esac

echo "-> ${n1}.${n2}.${n3}"

echo "updating project file $project from $version to $n1.$n2.$n3"
sed -i "${line}s/$version/$n1.$n2.$n3/" $project
echo

read -p "Inform the message for the tag commit [or live it empty to open editor]:" tag_commit_message

echo "commiting project version update from $version to $n1.$n2.$n3"
git add $project
git commit -m "updating $project version from $version to $n1.$n2.$n3"

echo "creating tag for new version -> v$n1.$n2.$n3"
[ -z $tag_commit_message ] && git tag -a "v$n1.$n2.$n3" || git tag -a "v$n1.$n2.$n3" -m $tag_commit_message

echo "pushing version update change to current branch"
git push

echo "pushing tag"
git push origin tag "v$n1.$n2.$n3"
