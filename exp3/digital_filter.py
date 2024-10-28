import csv
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import os


# Function to compute power spectrum
def get_power_spectrum(signal_data):
    n = len(signal_data)
    freqs = np.fft.fftfreq(n, 1/fs)
    fft_vals = np.fft.fft(signal_data)
    power = np.abs(fft_vals)**2
    
    # Shift the frequencies and power spectrum
    freqs = np.fft.fftshift(freqs)
    power = np.fft.fftshift(power)
    
    return freqs, power

# Optional: Add statistical analysis of power in each frequency band
def get_band_power(freqs, power, band):
    mask = (freqs >= band[0]) & (freqs <= band[1])
    return np.mean(power[mask])

# Function to apply bandpass filter
# Butterworth filter
def apply_bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyquist = fs * 0.5
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = signal.butter(order, [low, high], btype='band')
    return signal.filtfilt(b, a, data)

bands = {
    'Alpha': (8, 13),    # Alpha: 8-13 Hz
    'Beta': (13, 30),    # Beta: 13-30 Hz
    'Delta': (0.5, 4),   # Delta: 0.5-4 Hz
    'Theta': (4, 8)      # Theta: 4-8 Hz
}


FILES = ["waves_EEG_b10901029.csv"]
for f in FILES:
    EEG = []
    with open(f'./data/{f}', 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header row if present
        alpha = []
        beta = []
        delta = []
        theta = []
        for row in csv_reader:
            alpha.append(float(row[1]))
            beta.append(float(row[2]))
            delta.append(float(row[3]))
            theta.append(float(row[4]))

        # Find the minimum length among all segments to ensure consistent lengths
        min_length = min(
            len(alpha) // 3,
            len(beta) // 3,
            len(delta) // 3,
            len(theta) // 3
        )

        # Create segments with consistent lengths
        EEG = [
            alpha[:min_length],                    # Alpha (Eyes Closed)
            alpha[min_length:2*min_length],        # Alpha (Eyes Open)
            beta[:min_length],                     # Beta (Eyes Closed)
            beta[min_length:2*min_length],         # Beta (Eyes Open)
            delta[:min_length],                    # Delta (Eyes Closed)
            delta[min_length:2*min_length],        # Delta (Eyes Open)
            theta[:min_length],                    # Theta (Eyes Closed)
            theta[min_length:2*min_length]         # Theta (Eyes Open)
        ]

    # Parameters for frequency analysis
    fs = 100  # Sampling frequency (Hz)
    

    # Apply bandpass filters to each segment
    filtered_EEG = []
    wave_names = ['Alpha', 'Beta', 'Delta', 'Theta']
    
    # Plot frequency spectrum for each wave type
    for i, wave_type in enumerate(wave_names):
        # Get the appropriate frequency band
        band = bands[wave_type]
        
        # Filter Eyes Closed data
        filtered_closed = apply_bandpass_filter(EEG[i*2], band[0], band[1], fs)
        # Filter Eyes Open data
        filtered_open = apply_bandpass_filter(EEG[i*2 + 1], band[0], band[1], fs)
        
        filtered_EEG.extend([filtered_closed, filtered_open])

    # Use filtered_EEG instead of EEG for the rest of the analysis
    EEG = filtered_EEG

    # Create figures with proper spacing
    fig1, axs1 = plt.subplots(4, 2, figsize=(15, 12), constrained_layout=True)  # Alpha/Beta comparison
    fig2, axs2 = plt.subplots(4, 2, figsize=(15, 12), constrained_layout=True)  # Theta/Delta comparison

    # Function to plot wave data (to ensure consistency)
    def plot_wave_data(wave_type, raw_data, filtered_data, start_idx, axes):
        # Get frequency data
        freqs_closed_raw, power_closed_raw = get_power_spectrum(raw_data[0])
        freqs_open_raw, power_open_raw = get_power_spectrum(raw_data[1])
        freqs_closed_filtered, power_closed_filtered = get_power_spectrum(filtered_data[0])
        freqs_open_filtered, power_open_filtered = get_power_spectrum(filtered_data[1])
        
        # Normalize powers
        power_closed_raw_norm = power_closed_raw / np.max(power_closed_raw)
        power_open_raw_norm = power_open_raw / np.max(power_open_raw)
        power_closed_filtered_norm = power_closed_filtered / np.max(power_closed_filtered)
        power_open_filtered_norm = power_open_filtered / np.max(power_open_filtered)
        
        # Define brighter but not too intense colors
        raw_color = '#4169E1'    # Royal Blue
        filtered_color = '#CD5C5C'    # Indian Red
        
        # Clear the axes before plotting
        axes[start_idx, 0].clear()
        axes[start_idx, 1].clear()
        axes[start_idx + 1, 0].clear()
        axes[start_idx + 1, 1].clear()
        
        # Raw data plots
        axes[start_idx, 0].plot(freqs_closed_raw, power_closed_raw_norm, color=raw_color, linewidth=1.5)
        axes[start_idx, 0].set_title(f'{wave_type} - Eyes Closed (Raw)', fontsize=12)
        axes[start_idx, 0].set_xlabel('Frequency (Hz)')
        axes[start_idx, 0].set_ylabel('Normalized Power')
        axes[start_idx, 0].grid(True)
        axes[start_idx, 0].set_xlim(-100, 100)
        axes[start_idx, 0].set_ylim(0, 1)
        
        axes[start_idx + 1, 0].plot(freqs_open_raw, power_open_raw_norm, color=raw_color, linewidth=1.5)
        axes[start_idx + 1, 0].set_title(f'{wave_type} - Eyes Open (Raw)', fontsize=12)
        axes[start_idx + 1, 0].set_xlabel('Frequency (Hz)')
        axes[start_idx + 1, 0].set_ylabel('Normalized Power')
        axes[start_idx + 1, 0].grid(True)
        axes[start_idx + 1, 0].set_xlim(-100, 100)
        axes[start_idx + 1, 0].set_ylim(0, 1)
        
        # Filtered data plots
        axes[start_idx, 1].plot(freqs_closed_filtered, power_closed_filtered_norm, color=filtered_color, linewidth=1.5)
        axes[start_idx, 1].set_title(f'{wave_type} - Eyes Closed (Filtered)', fontsize=12)
        axes[start_idx, 1].set_xlabel('Frequency (Hz)')
        axes[start_idx, 1].set_ylabel('Normalized Power')
        axes[start_idx, 1].grid(True)
        axes[start_idx, 1].set_xlim(-100, 100)
        axes[start_idx, 1].set_ylim(0, 1)
        
        axes[start_idx + 1, 1].plot(freqs_open_filtered, power_open_filtered_norm, color=filtered_color, linewidth=1.5)
        axes[start_idx + 1, 1].set_title(f'{wave_type} - Eyes Open (Filtered)', fontsize=12)
        axes[start_idx + 1, 1].set_xlabel('Frequency (Hz)')
        axes[start_idx + 1, 1].set_ylabel('Normalized Power')
        axes[start_idx + 1, 1].grid(True)
        axes[start_idx + 1, 1].set_xlim(-100, 100)
        axes[start_idx + 1, 1].set_ylim(0, 1)

    # Plot Alpha and Beta
    for i, wave_type in enumerate(['Alpha', 'Beta']):
        # Get raw data
        raw_closed = EEG[i*2]
        raw_open = EEG[i*2 + 1]
        
        # Filter the data
        band = bands[wave_type]
        filtered_closed = apply_bandpass_filter(raw_closed, band[0], band[1], fs)
        filtered_open = apply_bandpass_filter(raw_open, band[0], band[1], fs)
        
        # Plot using the helper function
        plot_wave_data(
            wave_type,
            [raw_closed, raw_open],
            [filtered_closed, filtered_open],
            i*2,
            axs1
        )

    # Plot Theta and Delta
    for i, wave_type in enumerate(['Theta', 'Delta']):
        # Get raw data
        raw_closed = EEG[(i+2)*2]
        raw_open = EEG[(i+2)*2 + 1]
        
        # Filter the data
        band = bands[wave_type]
        filtered_closed = apply_bandpass_filter(raw_closed, band[0], band[1], fs)
        filtered_open = apply_bandpass_filter(raw_open, band[0], band[1], fs)
        
        # Plot using the helper function
        plot_wave_data(
            wave_type,
            [raw_closed, raw_open],
            [filtered_closed, filtered_open],
            i*2,
            axs2
        )

    # Add suptitles
    fig1.suptitle('Alpha and Beta Waves - Raw vs Filtered Comparison', y=1.02, fontsize=16)
    fig2.suptitle('Theta and Delta Waves - Raw vs Filtered Comparison', y=1.02, fontsize=16)

    # Save the figures
    os.makedirs('./output', exist_ok=True)
    fig1.savefig(f'./output/alpha_beta_comparison_{f[:-4]}.png', dpi=300, bbox_inches='tight')
    fig2.savefig(f'./output/theta_delta_comparison_{f[:-4]}.png', dpi=300, bbox_inches='tight')
    plt.close('all')






