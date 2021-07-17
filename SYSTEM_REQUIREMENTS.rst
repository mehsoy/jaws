The following linux utils must be installed to run this Daemon:
---------------------------------------------------------------
rsync
tar 1.30 or newer
getent
cut
grep
munge 0.5x or later

Required for the default configurations to run properly:
-----------------------------------------------------

Following mount points need to exist:
    ``/mount/dmd5``, ``/mount/centos127``, ``/mount/archive1``

Exemplary set up of one mount point (make sure ``/mount`` exists):

.. code-block::

    mkdir /mount/dmd5
    dd if=/dev/zero of=/root/dmd5.img bs=1M count=600
    mkfs.xfs dmd5.img  # you may use a different fs
    mount -o loop /root/dmd5.img /mount/dmd5/



Required only on Worker node for the shiftc command:
-----------------------------------------------------
Method for deployment right now is cloning this project from git into dmdenv/bin/shift,
since installation via pip is not possible w/o setup.py. Directories in dmdenv for the 
man pages has to be setup manually, i.e dmdenv/man/man1.

The configuration file for shift-mrg, i.e. .shiftrc, currently has to be in the home 
directory of centos. Furthermore the metadata in .shift is stored on the home directory
aswell. (Goal is that the config file would reside in dmdenv/ as the default install prefix,
optimal location for metadata unclear.)

required: perl>=5.8.5

Following may also have to be installed via yum, since they are not contained in the original
version(?)

 - perl-Data-Dumper.x86_64 
 - Digest/MD5.pm 
 - perl-IO-Compress.noarch
 - perl-Text-ParseWords-3.29-4.el7.noarch 
 - perl-5.16.3-292.el7.x86_64
 - perl-DB_File-1.830-6.el7.x86_64


Required only on Search node for installing pylibacl via pip:
-------------------------------------------------------------
 - pylibacl34-devel
 - libacl-devel
 - gcc


