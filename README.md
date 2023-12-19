# Power Tracker

![img.png](img.png)

## Setup Instructions

Download OpenSSL (https://www.openssl.org/source/) and Python

In Python3.x.x/Modules/Setup, uncomment the four lines relating to SSL

### Installing OpenSSL

```cmdline
sudo apt-get update && sudo apt-get upgrade
sudo apt install build-essential checkinstall zlib1g-dev -y
cd /usr/local/src/
sudo wget https://www.openssl.org/source/openssl-1.1.1c.tar.gz
sudo tar -xf openssl-1.1.1c.tar.gz
cd openssl-1.1.1c
sudo ./config --prefix=/usr/local/ssl --openssldir=/usr/local/ssl shared zlib
sudo make
sudo make test
sudo make install
cd /etc/ld.so.conf.d/
sudo nano openssl-1.1.1c.conf
/usr/local/ssl/lib
sudo ldconfig -v
sudo mv /usr/bin/c_rehash /usr/bin/c_rehash.backup
sudo mv /usr/bin/openssl /usr/bin/openssl.backup
sudo nano /etc/environment
PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/local/ssl/bin"
source /etc/environment
echo $PATH
which openssl
openssl version -a
```

### Installing new Python

```cmdline
sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev
libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev
wget https://www.python.org/ftp/python/3.9.0/Python-3.9.0.tar.xz
tar xf Python-3.9.0.tar.xz
cd Python-3.9.0
./configure --prefix=/usr/local/opt/python-3.9.0
sudo make
sudo make altinstallcd ..
sudo rm -r Python-3.9.0
rm Python-3.9.0.tar.xz
. ~/.bashrc
sudo update-alternatives --config python
python -V
nano ~/.bash_aliases
alias python=/usr/bin/python-3.8
alias python=/usr/local/opt/python-3.9.0/bin/python3.9
. ~/.bashrc
python -V
```

### Installing ePaper dependencies

https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT?spm=a2g0o.detail.1000023.1.74fd1daepMUsXv&file=7.5inch_e-Paper_HAT

### Python module requirements

- requests
- selenium
- beatifulsoup4
- matplotlib

### Installing humor sans font

```cmdline
sudo apt install fonts-humor-sans
rm ~/.cache/matplotlib -r
```

## Previous Debug Notes:

If PuTTY doesn't find the hostname of the pi, find its IP using the router and ping it using command line.
If the OS is flashed using Raspberry Pi Imager, the settings can be changed through it to allow SSH ahead of time.

Otherwise use the set_fresh_pi.py script or the instructions at:

- https://desertbot.io/blog/headless-pi-zero-ssh-access-over-usb-windows
- https://forums.raspberrypi.com/viewtopic.php?t=194843