#!/usr/bin/python3
import os
import time
import logging
import sys
import subprocess

global ROOT_FTP_MOUNT_PATH 
ROOT_FTP_MOUNT_PATH = '/mnt/ftp'
SECONDS_YEARS = 31557600
MAX_AGE_YEARS = 1E10
DEBUG = os.environ.get('DEBUG', '0') != '0'

THIS_SCRIPT = sys.argv[0]
USAGE = f'$ python3 {THIS_SCRIPT} <optional|mount_ftp_directory_path'

logging.basicConfig(stream = sys.stderr,
  level = logging.DEBUG if DEBUG else logging.INFO,
  format  =
    '[%(asctime)s.%(msecs)03d %(levelname)s] %(filename)s:%(lineno)d:\n%(message)s'
      if DEBUG else '[%(asctime)s.%(msecs)03d %(levelname)s] %(message)s',
  datefmt = '%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

global matplotlib 
matplotlib = False
try:
  import matplotlib.pyplot as plt
  from matplotlib.pylab import *
  matplotlib = False 
  logger.info(f'matplotlib found to be installed. Histograms will be created.')
except ImportError:
  logger.warn(f'WARNING: matplotlib not installed. Histograms will not be created.')

def get_all_filenames() -> list:
  '''Return list[] of all filenames (full paths) in the mounted
  ftp directory.

  Returns:
    list: list of filenames and their ages & sizes. List of tuples.
  '''
  # initialize empty list[] to hold filenames and
  # ages of those files in years and seconds
  # ---------------------------------------------
  filenames_ages_sizes = []

  # walk the mounted input ftp directory recursively
  # ------------------------------------------------
  for root, dirs, files in os.walk(ROOT_FTP_MOUNT_PATH):
    path = root.split(os.sep)
    for f in files:

      # get full path of file and current time
      # --------------------------------------
      full_path = os.path.join(root, f)

      if os.path.isfile(full_path):

        # compute file age in seconds & years
        # -----------------------------------
        current_time = time.time()
        file_age_seconds = current_time - os.path.getmtime(full_path)
        file_age_years = float(file_age_seconds) / SECONDS_YEARS
        file_age_years = round(file_age_years, 3)

        # get size in bytes
        # -----------------
        size_mb = os.path.getsize(full_path) / float(1E6)    

        # add to the list
        # ---------------
        filenames_ages_sizes.append(
                (full_path, file_age_years, file_age_seconds, size_mb))

  # return the results
  # ------------------
  return filenames_ages_sizes

def write_ftp_file_records_to_txt(outName_txt: str, 
        ftp_file_records: list, age_range_years: tuple) -> list:
  '''Write names of files to text-file, as well as age
  in years and the size in MB ... get the extension to a list
  as well while we loop

  Args:
    outName_txt (str): out name of text file with file names and ages
    ftp_file_records (list): List of tuples of filenames, ages, sizes
    age_range_years (tuple): min. and max. age in years of file

  Returns:
    list: list of tuples, relevant list of ftp file records found in age range.
  '''
  if os.path.isfile(outName_txt):
    os.remove(outName_txt)
  
  f_filenames = open(outName_txt, 'w')
  f_filenames.write('%s\n' % 'name,age in years,size in MB')
  age_file_records = []
  ftp_file_records = sorted(ftp_file_records, key = lambda f: f[1])

  for ftp_file_record in ftp_file_records:

    # write out the file-path, age in years, and size (in MB)
    # as a comma-delimited string to the output file
    # -------------------------------------------------------
    file_path = ftp_file_record[0]
    file_age_years = ftp_file_record[1]
    file_size_mb = ftp_file_record[3]
    ftp_record_str = ','.join(
            [file_path, str(file_age_years), str(file_size_mb)])
    
    if file_age_years > age_range_years[0] and file_age_years < age_range_years[1]:
      f_filenames.write('%s\n' % ftp_record_str)
      age_file_records.append(ftp_file_record)

  f_filenames.close()
  return age_file_records

def get_extensions_ftp_files(ftp_file_records: list) -> list:
  '''Get extensions for a list[] of filenames (where each "filename" in the
  input list actually contains the filename itself, the size in MB, and the
  age in years of the file.

  Args:
    ftp_file_records (list): List of FTP files. List of tuples with names, ages, sizes.
  Returns:
    list: extensions. Unique.
  '''
  ftp_server_extensions = []
  for ftp_record in ftp_file_records:
    ftp_server_extensions.append(os.path.splitext(ftp_record[0])[1])
  return list(set(ftp_server_extensions))

def create_histograms_for_ftp_records(ftp_file_records: list, 
        extensions: list, aspect_server: str, title_flag: str, outNameFlag: str) -> None:
  '''For a list of tuples of FTP file records (filename, age, size), and for
  each extension, create a histogram of the age and counts.
  '''
  for extension in extensions:

    filenames_with_extension = []
    file_ages = []

    for ftp_record in ftp_file_records:
      if ftp_record[0].lower().endswith(extension.lower()):

        filenames_with_extension.append(ftp_record)
        file_ages.append(ftp_record[1])

    # create histogram for the files with this extension
    # --------------------------------------------------
    title = aspect_server + ': ' + title_flag + ' (' + extension + ' extension)'
    outName = '.'.join([aspect_server, outNameFlag, extension.replace('.', ''), 'png'])

    if os.path.isfile(outName):
      os.remove(outName)
  
    # write out a histogram file
    # --------------------------
    if matplotlib:
      ioff()
      plt.title(title)
      plt.hist(file_ages)
      plt.grid(linewidth = 0.2)
      plt.xticks(rotation = 45, ha = 'center', fontsize = 5)
      plt.savefig(outName, dpi = 150)
      plt.close()
    else:
      logger.warn(f'following file: {outName} will not be created as matplotlib not installed.')

def compute_total_disk_usage(ftp_records: list) -> float:
  '''Compute total space from a srt of FTP file records. Return value in GB.
  '''
  total_size_mb = 0.0
  for ftp_record in ftp_records: total_size_mb += float(ftp_record[3])
  return round(total_size_mb / float(1000), 4)

def main() -> int:

  # get single input arg
  # --------------------
  global matplotlib
  global ROOT_FTP_MOUNT_PATH
  
  try:
    ROOT_FTP_MOUNT_PATH = sys.argv[1]
    logger.info(f'following ftp mount path passed-in: {ROOT_FTP_MOUNT_PATH}')
  except:
    logger.info(f'defaulting to mount path: {ROOT_FTP_MOUNT_PATH}')

  # check if mount path exists
  # --------------------------
  if not os.path.isdir(ROOT_FTP_MOUNT_PATH):
    logger.error(f'ERROR (fatal): not a directory: {ROOT_FTP_MOUNT_PATH}. Exiting ...')
    sys.exit(1)
  logger.info(f'mount path is: {ROOT_FTP_MOUNT_PATH}')

  # begin script ...
  # ----------------
  this_script = sys.argv[0]
  logger.info(f'began running script: {this_script}')
  logger.info(f'  scanning following mounted ftp path: {ROOT_FTP_MOUNT_PATH}')

  # get the name of the ASPECT server for the mount location
  # --------------------------------------------------------
  result = subprocess.run(['df', '-h'], 
          capture_output = True, text = True, check = True).stdout.split('\n')
  aspect_ftp_server = None
  for line in result:
    if line.strip().endswith(ROOT_FTP_MOUNT_PATH): aspect_ftp_server = line.split(' ')[0].split('#')[1]
  if aspect_ftp_server:
    aspect_ftp_server = aspect_ftp_server.replace('ftp://', '').replace('/', '')
  logger.info(f'aspect server being analyzed: {aspect_ftp_server}')

  if not aspect_ftp_server:
    logger.warning(f'warning: no mount located at: {ROOT_FTP_MOUNT_PATH}')
    aspect_ftp_server = 'none'

  # first get the names of all files in the
  # ftp mount path
  # ---------------------------------------
  filenames_sizes_ages = sorted(get_all_filenames(), key = lambda tup: tup[1])
  logger.info(f"number of files found: {len(filenames_sizes_ages)}") 

  # write text-files ... based on different age ranges of files
  # -----------------------------------------------------------
  ftp_file_records_10plus_years = write_ftp_file_records_to_txt(
          aspect_ftp_server + '.filenames_10+years.txt', filenames_sizes_ages, (10, MAX_AGE_YEARS)) 
  extensions_10plus_years = get_extensions_ftp_files(ftp_file_records_10plus_years)

  ftp_file_records_9_10_years = write_ftp_file_records_to_txt(
          aspect_ftp_server + '.filenames_9_10_years.txt', filenames_sizes_ages, (9, 10)) 
  extensions_9_10_years = get_extensions_ftp_files(ftp_file_records_9_10_years)

  logger.info(f'no. files on ftp server > 10 years old: {len(ftp_file_records_10plus_years)}')
  logger.info(f'no. files on ftp server 9-10 year old: {len(ftp_file_records_9_10_years)}')

  if len(ftp_file_records_10plus_years) > 0:
    # create histogram for 10+ year old files ; one histogram for each extension
    # --------------------------------------------------------------------------
    create_histograms_for_ftp_records(
      ftp_file_records_10plus_years, extensions_10plus_years, aspect_ftp_server, '10+ years old', '10+years')
    
  elif len(ftp_file_records_9_10_years) > 0:
    # create histogram for 9-19 years old files ; one histogram for each extension
    # ----------------------------------------------------------------------------
    create_histograms_for_ftp_records(
      ftp_file_records_9_10_years, extensions_9_10_years, aspect_ftp_server, '9-10 years old', '9_10_years')
  
  # write out ALL files, ages (in years), and size in MB
  # ----------------------------------------------------
  write_ftp_file_records_to_txt(
          aspect_ftp_server + '.ALL_FILENAMES.txt', filenames_sizes_ages, (0.0, MAX_AGE_YEARS)) 
  
  # log some basic info.
  # --------------------
  total_disk_usage_mb = compute_total_disk_usage(
          filenames_sizes_ages)
  disk_usage_9to10_years = compute_total_disk_usage(
          ftp_file_records_9_10_years)
  disk_usage_10plus_years = compute_total_disk_usage(
          ftp_file_records_10plus_years)
  logger.info(f'total file disk usage / volume (GB): {total_disk_usage_mb}')
  logger.info(f'total file disk usage (9-10 y/o) (GB): {disk_usage_9to10_years}')
  logger.info(f'total file disk usage (10+ years) (GB): {disk_usage_10plus_years}')
  return 0

if __name__ == '__main__':
  main()
