"""Data processing utilities for Rocky Stats analysis.

This module provides functions for downloading, loading, preprocessing,
and filtering EPEL and DockerHub data used in Enterprise Linux distribution
usage analysis.
"""

import os
import pandas as pd
import requests
from datetime import datetime, timedelta
from tqdm import tqdm
from config import (
    DATA_DIR, CACHE_DAYS, EPEL_DATA_URL, DOCKERHUB_DATA_URL,
    EPEL_REPOS, ERROR_DATES, DH_DISTROS, VALID_ROCKY_VERSIONS
)


def download_file(url, local_dir, local_file):
    """Download file with caching and progress bar."""
    local_path = os.path.join(local_dir, local_file)
    
    # Check if the directory exists, create it if it doesn't
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    
    # Check if the file exists and if it's older than CACHE_DAYS
    if os.path.exists(local_path):
        file_timestamp = os.path.getmtime(local_path)
        file_datetime = datetime.fromtimestamp(file_timestamp)
        current_datetime = datetime.now()
        
        if current_datetime - file_datetime > timedelta(days=CACHE_DAYS):
            print(f"File '{local_file}' is older than {CACHE_DAYS} days. Downloading the latest version.")
            _download_with_progress(url, local_path, local_file)
        else:
            print(f"File '{local_file}' is up to date.")
    else:
        print(f"File '{local_file}' does not exist. Downloading the file.")
        _download_with_progress(url, local_path, local_file)


def _download_with_progress(url, local_path, local_file):
    """Internal function to download file with progress bar."""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("Content-Length", 0))
    
    with open(local_path, "wb") as file, tqdm(
        desc=local_file,
        total=total_size,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            progress_bar.update(size)
    
    print(f"File '{local_file}' downloaded successfully.")


def load_epel_data():
    """Load and preprocess EPEL data."""
    # Download data
    download_file(EPEL_DATA_URL, DATA_DIR, "epel.csv")
    
    # Load with proper dtypes
    df = pd.read_csv(
        DATA_DIR + 'epel.csv', 
        parse_dates=['week_end', 'week_start'],
        dtype={
            'os_name': 'string', 
            'os_version': 'string', 
            'os_variant': 'string', 
            'os_arch': 'string'
        }
    )
    
    # Filter to EPEL repositories only
    df = df[df['repo_tag'].isin(EPEL_REPOS)]
    
    # Remove data errors
    for error_date in ERROR_DATES:
        df = df.drop(df[df['week_end'] == error_date].index)
    
    return df


def load_dockerhub_data():
    """Load and preprocess DockerHub data."""
    # Download data
    download_file(DOCKERHUB_DATA_URL, DATA_DIR, "dockerhub.csv")
    
    # Load and process
    df = pd.read_csv(DATA_DIR + 'dockerhub.csv', index_col=0, parse_dates=['Date']).diff().iloc[1:]
    
    # Create aggregated dataframe
    dh_dataframe = pd.DataFrame(index=df.index, columns=DH_DISTROS)
    
    # Aggregate AlmaLinux containers
    dh_dataframe['AlmaLinux'] = (
        df['library/almalinux'] +
        df['almalinux/8-base'] +
        df['almalinux/8-init'] +
        df['almalinux/8-micro'] +
        df['almalinux/8-minimal'] +
        df['almalinux/9-base'] +
        df['almalinux/9-init'] +
        df['almalinux/9-micro'] +
        df['almalinux/9-minimal'] +
        df['almalinux/almalinux'] +
        df['almalinux/amd64'] +
        df['almalinux/arm64v8'] +
        df['almalinux/i386'] +
        df['almalinux/ppc64le'] +
        df['almalinux/s390x']
    )
    
    # Other distributions
    dh_dataframe['CentOS Linux'] = df['library/centos']
    dh_dataframe['Oracle Linux Server'] = df['library/oraclelinux']
    
    # Aggregate RHEL containers
    dh_dataframe['Red Hat Enterprise Linux'] = (
        df['redhat/ubi8'] +
        df['redhat/ubi8-init'] +
        df['redhat/ubi8-micro'] +
        df['redhat/ubi8-minimal'] +
        df['redhat/ubi9'] +
        df['redhat/ubi9-init'] +
        df['redhat/ubi9-micro'] +
        df['redhat/ubi9-minimal']
    )
    
    # Aggregate Rocky Linux containers
    dh_dataframe['Rocky Linux'] = (
        df['library/rockylinux'] +
        df['rockylinux/rockylinux']
    )
    
    return dh_dataframe


def create_pivot_table(df, values='hits', index=None, columns=None, fill_value=0):
    """Create pivot table with consistent parameters."""
    return pd.pivot_table(
        df, 
        values=values, 
        index=index, 
        columns=columns, 
        fill_value=fill_value, 
        aggfunc="sum"
    )


def filter_by_date(df, start_date, date_column='week_end'):
    """Filter dataframe by date."""
    return df[df[date_column] > start_date]


def filter_by_system_age(df, age_condition):
    """Filter dataframe by system age."""
    if age_condition == 'longterm':
        return df[df['sys_age'] > 1]
    elif age_condition == 'ephemeral':
        return df[df['sys_age'] == 1]
    else:
        return df[df['sys_age'] > age_condition] if isinstance(age_condition, int) else df


def filter_by_repo_tag(df, repo_tag):
    """Filter dataframe by repository tag."""
    return df[df['repo_tag'] == repo_tag]


def filter_by_os_name(df, os_name):
    """Filter dataframe by OS name."""
    return df[df['os_name'] == os_name]


def filter_by_arch(df, arch_filter='altarch'):
    """Filter dataframe by architecture."""
    if arch_filter == 'altarch':
        return df[df['repo_arch'] != 'x86_64']
    else:
        return df[df['repo_arch'] == arch_filter]


def add_total_column(df):
    """Add total column to dataframe."""
    df_copy = df.copy()
    df_copy['total'] = df_copy.sum(numeric_only=True, axis=1)
    return df_copy


def filter_valid_rocky_versions(df):
    """Filter dataframe to only include valid Rocky Linux versions."""
    return df[df['os_version'].isin(VALID_ROCKY_VERSIONS)]