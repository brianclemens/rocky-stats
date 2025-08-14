"""Configuration settings for Rocky Stats analysis.

This module contains all configuration parameters, constants, and settings
used across the Rocky Stats project for analyzing Enterprise Linux 
distribution usage patterns.
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta

# Plot settings
EMPHASIZE = 'Rocky Linux'
FIGX = 16.18
FIGY = 10
PLOTSTYLE = 'ggplot'

# Date ranges
STARTDATE = datetime.today() - relativedelta(years=1)
STARTDATE_LONG = '2020-12-08'

# Directory paths
DATA_DIR = 'data/'
WORK_DIR = 'out/'

# Distribution definitions
DISTROS = [
    'AlmaLinux', 
    'CentOS Linux', 
    'CentOS Stream', 
    'Oracle Linux Server', 
    'Red Hat Enterprise Linux', 
    'Rocky Linux'
]

CURRENT_DISTROS = [
    'AlmaLinux', 
    'CentOS Stream', 
    'Oracle Linux Server', 
    'Red Hat Enterprise Linux', 
    'Rocky Linux'
]

DH_DISTROS = [
    'AlmaLinux', 
    'CentOS Linux', 
    'Oracle Linux Server', 
    'Red Hat Enterprise Linux', 
    'Rocky Linux'
]

# Color scheme
COLORS = {
    'AlmaLinux': '#4AC1FA',
    'CentOS Linux': '#E9A942',
    'CentOS Stream': '#9A5689',
    'Oracle Linux Server': '#BE503B',
    'Red Hat Enterprise Linux': '#E2321D',
    'Rocky Linux': '#48B585'
}

# Display labels
LABELS = {
    'AlmaLinux': 'AlmaLinux',
    'CentOS Linux': 'CentOS Legacy',
    'CentOS Stream': 'CentOS Stream',
    'Oracle Linux Server': 'Oracle',
    'Red Hat Enterprise Linux': 'RHEL',
    'Rocky Linux': 'Rocky Linux'
}

# Data URLs
EPEL_DATA_URL = "https://data-analysis.fedoraproject.org/csv-reports/countme/totals.csv"
DOCKERHUB_DATA_URL = "https://docs.google.com/spreadsheets/d/16SfYqf2cZIe-t4ADNNXTeX3RBz5vi4kXSkwCrKFD0M8/export?gid=0&format=csv"

# Data filtering
EPEL_REPOS = ['epel-8', 'epel-9', 'epel-10']

# Dates with data errors to exclude
ERROR_DATES = [
    '2023-05-07',
    '2023-05-14', 
    '2023-10-29',
    '2023-11-05'
]

# Cache settings
CACHE_DAYS = 7

# Valid Rocky Linux versions for filtering
VALID_ROCKY_VERSIONS = [
    # Rocky Linux 8.x series
    '8.3', '8.4', '8.5', '8.6', '8.7', '8.8', '8.9', '8.10',
    # Rocky Linux 9.x series  
    '9.0', '9.1', '9.2', '9.3', '9.4', '9.5', '9.6',
    # Rocky Linux 10.x series
    '10.0'
]