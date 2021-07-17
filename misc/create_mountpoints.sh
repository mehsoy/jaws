#!/usr/bin/env bash
mkdir /mnt/jaws

mkdir /mnt/jaws/home
dd if=/dev/zero of=/mnt/jaws/dmd_home.img bs=1M count=30
mkfs.xfs /mnt/jaws/dmd_home.img  # you may use a different fs
mount -o loop /mnt/jaws/dmd_home.img /mnt/jaws/home

mkdir /mnt/jaws/dmd5
dd if=/dev/zero of=/mnt/jaws/dmd5.img bs=1M count=50
mkfs.xfs /mnt/jaws/dmd5.img  # you may use a different fs
mount -o loop /mnt/jaws/dmd5.img /mnt/jaws/dmd5/

mkdir /mnt/jaws/centos127
dd if=/dev/zero of=/mnt/jaws/centos127.img bs=1M count=100
mkfs.xfs /mnt/jaws/centos127.img  # you may use a different fs
mount -o loop /mnt/jaws/centos127.img /mnt/jaws/centos127/

mkdir /mnt/jaws/archive1
dd if=/dev/zero of=/mnt/jaws/archive1.img bs=1M count=120
mkfs.xfs /mnt/jaws/archive1.img  # you may use a different fs
mount -o loop /mnt/jaws/archive1.img /mnt/jaws/archive1/

