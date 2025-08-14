"""Plotting utilities for Rocky Stats analysis.

This module provides functions for creating consistent, branded visualizations
for Enterprise Linux distribution usage analysis. Includes support for
area charts, line plots, bar charts, and specialized Rocky Linux version
color schemes.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import numpy as np
from datetime import datetime
import matplotlib.colors as mcolors
from config import (
    FIGX, FIGY, PLOTSTYLE, EMPHASIZE, COLORS, LABELS, 
    DISTROS, CURRENT_DISTROS, WORK_DIR
)


def thousands(x, pos):
    """Format numbers as thousands with 'k' suffix."""
    return '{:,.0f}k'.format(x*1e-3)


def millions(x, pos):
    """Format numbers as millions with 'M' suffix."""
    return '{:,.1f}M'.format(x*1e-6)


def generate_rocky_version_colors(versions):
    """Generate colors for Rocky Linux versions based on major version themes."""
    # Base colors for major versions
    base_colors = {
        8: '#48B585',  # Green (original Rocky color)
        9: '#4A90E2',  # Blue  
        10: '#E94B3C'  # Red
    }
    
    version_colors = {}
    
    for version in versions:
        try:
            major = int(version.split('.')[0])
            if major in base_colors:
                # Get all versions for this major version to create a gradient
                major_versions = [v for v in versions if v.startswith(f'{major}.')]
                major_versions.sort(key=lambda x: float(x.split('.')[1]) if '.' in x else 0)
                
                # Create shades from darker to lighter
                base_color = base_colors[major]
                num_versions = len(major_versions)
                
                if num_versions == 1:
                    version_colors[version] = base_color
                else:
                    # Create a range of shades from darker to lighter
                    for i, v in enumerate(major_versions):
                        # Create shade: 0.6 (darker) to 1.0 (original) to 1.2 (lighter)
                        shade_factor = 0.7 + (0.5 * i / (num_versions - 1))
                        
                        # Convert hex to RGB, apply shade, convert back
                        rgb = mcolors.hex2color(base_color)
                        if shade_factor < 1.0:
                            # Darken
                            shaded_rgb = tuple(c * shade_factor for c in rgb)
                        else:
                            # Lighten
                            shaded_rgb = tuple(min(1.0, c + (1.0 - c) * (shade_factor - 1.0)) for c in rgb)
                        
                        version_colors[v] = mcolors.rgb2hex(shaded_rgb)
        except (ValueError, IndexError):
            # Fallback for invalid versions
            version_colors[version] = '#666666'  # Gray
    
    return version_colors


def setup_plot(figsize=(FIGX, FIGY)):
    """Setup matplotlib plot with consistent style."""
    plt.style.use(PLOTSTYLE)
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot()
    return fig, ax


def setup_dates(ax, interval='monthly'):
    """Setup date formatting for x-axis."""
    if interval == 'quarterly':
        # For long-term charts - show every 3 months
        xmajorrule = mdates.RRuleLocator(mdates.rrulewrapper(mdates.MONTHLY, interval=3))
    elif interval == 'monthly':
        # For regular charts - show every month
        xmajorrule = mdates.RRuleLocator(mdates.rrulewrapper(mdates.MONTHLY))
    else:
        # Custom interval
        xmajorrule = mdates.RRuleLocator(mdates.rrulewrapper(mdates.MONTHLY, interval=interval))
    
    ax.xaxis.set_major_locator(xmajorrule)
    plt.xticks(rotation=45)


def setup_axis_formatting(ax, y_format='thousands', date_interval='monthly'):
    """Setup axis formatting."""
    setup_dates(ax, interval=date_interval)
    
    if y_format == 'thousands':
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(thousands))
    elif y_format == 'millions':
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(millions))
    
    ax.set_ylim(bottom=0)


def add_title_and_timestamp(title, ax=None):
    """Add title with timestamp."""
    plt.title(title, loc='left')
    plt.title(datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z"), loc='right')


def save_plot(filename, bbox_inches='tight'):
    """Save plot in both PNG and SVG formats."""
    plt.margins(0, tight=True)
    plt.savefig(WORK_DIR + filename + '.png', bbox_inches=bbox_inches)
    plt.savefig(WORK_DIR + filename + '.svg', bbox_inches=bbox_inches)


def plot_stackplot(ax, data, distro_list=None, share=False, emphasize=EMPHASIZE):
    """Create stackplot for distribution data with emphasized distro at bottom."""
    if distro_list is None:
        distro_list = DISTROS
    
    # Reorder distro_list to put emphasized distro first (bottom of stack)
    ordered_distros = []
    other_distros = []
    
    for distro in distro_list:
        if distro == emphasize:
            ordered_distros.insert(0, distro)  # Put emphasized distro first
        else:
            other_distros.append(distro)
    
    # Add other distros after the emphasized one
    ordered_distros.extend(other_distros)
    
    # Prepare data and labels
    plot_data = []
    plot_labels = []
    plot_colors = []
    
    for distro in ordered_distros:
        if distro in data.columns:
            if share and 'total' in data.columns:
                plot_data.append(data[distro] / data['total'])
            else:
                plot_data.append(data[distro])
            plot_labels.append(LABELS[distro])
            plot_colors.append(COLORS[distro])
    
    ax.stackplot(data.index, *plot_data, labels=plot_labels, colors=plot_colors)


def plot_lines_with_emphasis(ax, data, distro_list=None, emphasize=EMPHASIZE):
    """Plot lines with emphasis on specific distribution."""
    if distro_list is None:
        distro_list = DISTROS
    
    for distro in distro_list:
        if distro in data.columns:
            if distro == emphasize:
                ax.plot(data[distro], label=LABELS[distro], color=COLORS[distro], linewidth=6, zorder=2)
            else:
                ax.plot(data[distro], label=LABELS[distro], color=COLORS[distro], zorder=2)


def plot_lines_with_trendlines(ax, data, distro_list=None, poly_degree=1, emphasize=EMPHASIZE):
    """Plot lines with polynomial trendlines."""
    if distro_list is None:
        distro_list = DISTROS
    
    # First plot trendlines
    for distro in distro_list:
        if distro in data.columns:
            x = mdates.date2num(data.index)
            z = np.polyfit(x, data[distro], poly_degree)
            p = np.poly1d(z)
            xx = np.linspace(x.min(), x.max(), 100)
            dd = mdates.num2date(xx)
            ax.plot(dd, p(xx), ':', color=COLORS[distro])
    
    # Then plot actual data
    plot_lines_with_emphasis(ax, data, distro_list, emphasize)


def plot_share_lines_with_trendlines(ax, data, distro_list=None, emphasize=EMPHASIZE):
    """Plot share lines with linear trendlines."""
    if distro_list is None:
        distro_list = DISTROS
    
    # Calculate shares
    data_with_total = data.copy()
    if 'total' not in data_with_total.columns:
        data_with_total['total'] = data_with_total.sum(numeric_only=True, axis=1)
    
    # Plot trendlines for shares
    for distro in distro_list:
        if distro in data.columns:
            x = mdates.date2num(data.index)
            share_data = data[distro] / data_with_total['total']
            z = np.polyfit(x, share_data, 1)
            p = np.poly1d(z)
            xx = np.linspace(x.min(), x.max(), 100)
            dd = mdates.num2date(xx)
            ax.plot(dd, p(xx), ':', color=COLORS[distro])
    
    # Plot actual share data
    for distro in distro_list:
        if distro in data.columns:
            share_data = data[distro] / data_with_total['total']
            if distro == emphasize:
                ax.plot(share_data, label=LABELS[distro], color=COLORS[distro], linewidth=6)
            else:
                ax.plot(share_data, label=LABELS[distro], color=COLORS[distro])


def plot_bars_by_age(ax, data, distro_list=None):
    """Plot grouped bar chart by system age."""
    if distro_list is None:
        distro_list = DISTROS
    
    # Filter to only distros that exist in the data
    available_distros = [d for d in distro_list if d in data.columns]
    
    x = np.arange(len(data.index))
    width = 0.12  # Reduced width from 0.15 to 0.12 for less crowding
    num_distros = len(available_distros)
    
    # Create tighter positioning - reduce spacing between bars
    total_width = num_distros * width
    positions = np.linspace(-total_width/2 + width/2, total_width/2 - width/2, num_distros)
    
    for i, distro in enumerate(available_distros):
        ax.bar(x + positions[i], data[distro], width, 
              label=LABELS[distro], color=COLORS[distro])
    
    age_labels = ['< 1 Week', '< 1 Month', '< 6 Months', '> 6 Months']
    ax.set_xticks(x, age_labels)


def create_distribution_share_plot(data, title, filename):
    """Create a complete distribution share area plot."""
    fig, ax = setup_plot()
    
    # Add total column if not present
    if 'total' not in data.columns:
        data = data.copy()
        data['total'] = data.sum(numeric_only=True, axis=1)
    
    plot_stackplot(ax, data, share=True)
    
    add_title_and_timestamp(title)
    plt.xlabel('Date')
    plt.ylabel('Share of Instances')
    plt.legend(title='Distribution', loc='upper left')
    
    save_plot(filename)
    return fig, ax


def create_distribution_total_plot(data, title, filename, y_format='millions'):
    """Create a complete distribution total area plot."""
    fig, ax = setup_plot()
    
    plot_stackplot(ax, data)
    setup_axis_formatting(ax, y_format)
    
    add_title_and_timestamp(title)
    plt.xlabel('Date')
    plt.ylabel('Instances')
    plt.legend(title='Distribution', loc='upper left')
    
    save_plot(filename)
    return fig, ax


def create_line_plot_with_trends(data, title, filename, distro_list=None, 
                                poly_degree=1, y_format='thousands', resample=None):
    """Create a complete line plot with trendlines."""
    fig, ax = setup_plot()
    
    # Calculate trendlines on original data before resampling
    if distro_list is None:
        distro_list = DISTROS
    
    # First plot trendlines on original data
    for distro in distro_list:
        if distro in data.columns:
            x = mdates.date2num(data.index)
            # Handle NaN values by dropping them for polyfit
            valid_mask = ~np.isnan(data[distro])
            if valid_mask.sum() > poly_degree:  # Need more points than degree
                z = np.polyfit(x[valid_mask], data[distro][valid_mask], poly_degree)
                p = np.poly1d(z)
                xx = np.linspace(x.min(), x.max(), 100)
                dd = mdates.num2date(xx)
                ax.plot(dd, p(xx), ':', color=COLORS[distro], linewidth=3, alpha=0.9, zorder=1)
    
    # Resample data if requested
    plot_data = data.resample(resample).mean() if resample else data
    
    # Then plot actual data (potentially resampled)
    plot_lines_with_emphasis(ax, plot_data, distro_list)
    
    # Use quarterly intervals for long-term charts (those with resampling)
    date_interval = 'quarterly' if resample else 'monthly'
    setup_axis_formatting(ax, y_format, date_interval)
    
    add_title_and_timestamp(title)
    plt.xlabel('Date')
    plt.ylabel('Instances')
    plt.legend(title='Distribution')
    
    save_plot(filename)
    return fig, ax


def create_share_line_plot(data, title, filename, distro_list=None):
    """Create a complete share line plot with trendlines."""
    fig, ax = setup_plot()
    
    plot_share_lines_with_trendlines(ax, data, distro_list)
    setup_dates(ax)
    ax.set_ylim(bottom=0)
    
    add_title_and_timestamp(title)
    plt.xlabel('Date')
    plt.ylabel('Share')
    plt.legend(title='Distribution')
    
    save_plot(filename)
    return fig, ax


def create_bar_plot_by_age(data, title, filename):
    """Create a complete bar plot by system age."""
    fig, ax = setup_plot()
    
    plot_bars_by_age(ax, data)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(thousands))
    
    add_title_and_timestamp(title)
    plt.xlabel('System Age')
    plt.ylabel('Instances')
    plt.legend(title='Distribution', loc='upper left')
    
    save_plot(filename)
    return fig, ax