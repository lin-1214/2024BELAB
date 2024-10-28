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
    

    # Create subplots for frequency domain analysis
    fig, axs = plt.subplots(4, 2, figsize=(15, 12))
    wave_names = ['Alpha', 'Beta', 'Delta', 'Theta']
    
    # Frequency bands
    bands = {
        'Alpha': (8, 13),
        'Beta': (13, 30),
        'Delta': (0.5, 4),
        'Theta': (4, 8)
    }

    # Plot frequency spectrum for each wave type
    for i, wave_type in enumerate(wave_names):
        # Eyes Closed
        freqs_closed, power_closed = get_power_spectrum(EEG[i*2])
        # Eyes Open
        freqs_open, power_open = get_power_spectrum(EEG[i*2 + 1])
        
        # Normalize powers for plotting
        power_closed_norm = power_closed / np.max(power_closed)
        power_open_norm = power_open / np.max(power_open)
        
        # Plot Eyes Closed
        axs[i, 0].plot(freqs_closed, power_closed_norm)
        axs[i, 0].set_title(f'{wave_type} - Eyes Closed')
        axs[i, 0].set_xlabel('Frequency (Hz)')
        axs[i, 0].set_ylabel('Normalized Power')
        axs[i, 0].grid(True)
        axs[i, 0].set_xlim(-100, 100)  # Changed x-axis limits
        axs[i, 0].set_ylim(0, 1)
        axs[i, 0].set_yticks(np.arange(0, 1.2, 0.2))
        axs[i, 0].set_xticks(np.arange(-100, 101, 50))  # Set x-axis ticks
        
        # Plot Eyes Open
        axs[i, 1].plot(freqs_open, power_open_norm)
        axs[i, 1].set_title(f'{wave_type} - Eyes Open')
        axs[i, 1].set_xlabel('Frequency (Hz)')
        axs[i, 1].set_ylabel('Normalized Power')
        axs[i, 1].grid(True)
        axs[i, 1].set_xlim(-100, 100)  # Changed x-axis limits
        axs[i, 1].set_ylim(0, 1)
        axs[i, 1].set_yticks(np.arange(0, 1.2, 0.2))
        axs[i, 1].set_xticks(np.arange(-100, 101, 50))  # Set x-axis ticks

    plt.suptitle(f'EEG Frequency Analysis - Eyes Closed vs Open', y=1.02)
    plt.tight_layout()
    
    # Save the figure
    os.makedirs('./output', exist_ok=True)
    plt.savefig(f'./output/frequency_analysis_{f[:-4]}.png', dpi=300, bbox_inches='tight')
    plt.close()


    # Print power comparison for each wave type
    print(f"\nResults for {f}:")
    for wave_type in wave_names:
        freqs_closed, power_closed = get_power_spectrum(EEG[wave_names.index(wave_type)*2])
        freqs_open, power_open = get_power_spectrum(EEG[wave_names.index(wave_type)*2 + 1])
        
        power_closed_band = get_band_power(freqs_closed, power_closed, bands[wave_type])
        power_open_band = get_band_power(freqs_open, power_open, bands[wave_type])
        
        print(f"\n{wave_type} wave:")
        print(f"Eyes Closed power: {power_closed_band:.2e}")
        print(f"Eyes Open power: {power_open_band:.2e}")
        print(f"Closed/Open ratio: {power_closed_band/power_open_band:.2f}")
