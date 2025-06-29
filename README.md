###### FTP Repository/Server Analyzer 
    
    Python 3 script to analyze files on locally mounted FTP server.
    Creates histograms of ages of files 9-10 years of age, as well as those 10+ years old.
    
    
    Uses logging.

###### Software Dependencies/Requirements

    It is expected you will have a recent version of Python3 installed (Python 3.10.x+).
    You will also need a command-line tool to mount a remote FTP server. One such piece
    of software is curlftpfs, which we can insstall like so (e.g. on Ubuntu/Debian):

    $ sudo apt install curlftpfs

###### EXAMPLE USAGE/HOW TO RUN

    Please use with Python 3.10.x or higher. 

    First, we must mount a remove FTP server to a local directory path (may need to be root):
    $ mkdir /mnt/ftp
    $ curlftpfs ftp://ftp.epaaspect6.net /mnt/ftp/ -o 'user=main@epaaspect6.net:N742W!'

![image info](sample_images/wind_dir_google_earth.png)

###### Python/Javascript libraries

    The required 3rd-party (not built-in) Python libraries are required:

    numpy - for array manipulation and matrix computations 
    matplotlib - for creating histogram plots for the contents of the FTP files 

###### PYTHON VERSION:
     
    Supports Python 3.8.x
       
###### @author: 

    Gerasimos 'Geri' Michalitsianos
    Gerasimos.Michalitsianos@kalmancoinc.com
    Last Updated: 29 June 2025
