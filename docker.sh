#!/usr/bin/bash

project=tchangos
default_image_name=${project}-image
default_container_name=${project}-container


function get_opt() {
  while true; do
    read -p "$1" -n 1 option
    if [ -z $option ]; then
      [ -n $2 ] && option=$2 || option=y
    fi

    case "$option" in
      [Yy])
        return 0
        ;;
      [Nn])
        return 1
        ;;
    esac
  done
}


[ "$1" = "-d" ] &&\
  image_name=$default_image_name ||\
  read -p "which name you want to give for the image? [Default: ${default_image_name}]: " image_name

[ -z $image_name ] && image_name=$default_image_name

if [ "$1" != "-d" ] ; then
  get_opt "do you want to put this image as {latest}? y/N " n
  option=$?
  echo ""
  [ $option -eq 0 ] &&\
    echo "using latest for image version" &&\
    version=latest
fi
[ -z $version ] &&\
    echo "getting current version of the project" &&\
    version=$(sed -n "/name\ \=\ \"Tchangos\"/{n;p}" pyproject.toml | sed "s/version\ \=\ //gI" | sed "s/\"//gI")

echo "creating image {$image_name} version {$version}"
docker buildx build -t $image_name:$version .

if [ "$1" != "-d" ] ; then
  get_opt "do you want to create the container for the application? [Y/n]: " y
  option=$?
  echo ""
  [ $option -eq 0 ] &&\
    read -p "which name you want to give for the container? [Default: ${default_container_name}]: " container_name
fi

if [ $option -eq 0 ]; then
  [ -z $container_name ] && container_name=$default_container_name

  echo "creating new container {$container_name} using image {${image_name}:${version}}"
  docker container run -d --name $container_name -p 80:80 $image_name:$version
fi
