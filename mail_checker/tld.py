import os

# source: https://data.iana.org/TLD/tlds-alpha-by-domain.txt

def load_tlds(file_path):
  with open(file_path, 'r') as file:
    tlds = [line.strip().lower() for line in file if line.strip() and not line.startswith('#')]
  return tlds

def load_tlds_from_relative_path():
  current_dir = os.path.dirname(__file__)
  file_path = os.path.join(current_dir, 'static', 'tlds-alpha-by-domain.txt')
  return load_tlds(file_path)

tlds = load_tlds_from_relative_path()