#!/bin/bash

sudo apt-get install apt-transport-https -y
sudo curl https://repo.varnish-cache.org/GPG-key.txt | sudo apt-key add -
echo "deb https://repo.varnish-cache.org/ubuntu/ precise varnish-4.0" | sudo tee --append /etc/apt/sources.list.d/varnish-cache.list
sudo apt-get update
sudo apt-get install varnish -y
