import csv
import matplotlib.pyplot as plt

# Lists to store data
FILES = ['waves_ECG.csv', 'waves_EEG_b10901029.csv', 'waves_EMG_b10901059.csv', \
         'waves_EMG_b10901069.csv']
FIGSIZE_ECG = (20, 10)
FIGSIZE_EEG = (25, 20)
FIGSIZE_EMG = (20, 10)

ECG_mV = []
ECG_BPM = []
EEG = []
EMG = []
i = 0
flag = False

def plot_ECG(name, ECG, BPM):
    # Create the plot
    time = [i for i in range(len(ECG))]
    plt.figure(figsize=FIGSIZE_ECG)
    plt.subplot(2, 1, 1)

    plt.plot(time, ECG, label='ECG Waveform')
    plt.title(f'ECG {name} Waveform')
    plt.xlabel('Time(ms)')
    plt.ylabel('mV')
    plt.grid(True)
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(time, BPM, label='Heart Rate')
    plt.title('ECG BPM {name}')
    plt.xlabel('Time(ms)')
    plt.ylabel('BPM')
    plt.grid(True)
    plt.legend()
    

    # Display the plot
    plt.savefig(f'./output/ECG_{name}.png')

def plot_EEG(name, EEG, idx, color):
    time = [i for i in range(len(EEG[0]))]
    
    plt.subplot(5, 1, idx)
    plt.plot(time, EEG[idx - 1], label=f'EEG {name} Waveform', color=color)
    plt.title(f'EEG {name} Waveform')
    plt.xlabel('Time')
    plt.ylabel('mV')
    plt.grid(True)
    plt.legend()
    plt.gca().set_xticklabels([])  # Hide x-axis values

def plot_EMG(id, EMG):
    time = [i for i in range(len(EMG[0]))]
    plt.figure(figsize=FIGSIZE_EMG)
    plt.subplot(2, 1, 1)

    plt.plot(time, EMG[0], label=f'EMG Waveform', color = 'red')
    plt.title(f'EMG Waveform')
    plt.xlabel('Time')
    plt.ylabel('mV')
    plt.grid(True)
    plt.legend()
    plt.gca().set_xticklabels([])  # Hide x-axis values

    plt.subplot(2, 1, 2)
    plt.plot(time, EMG[1], label=f'EMG Integral', color = 'green')
    plt.title('EMG Integral')
    plt.xlabel('Time')
    plt.ylabel('mV - sec')
    plt.grid(True)
    plt.legend()
    plt.gca().set_xticklabels([])  # Hide x-axis values
    plt.savefig(f'./output/EMG_{id}.png')



# Read data from CSV file
for i in range(len(FILES)):
    if (i == 0):
        with open(f'./data/{FILES[i]}', 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row if present
            data = []
            mV = []
            for row in csv_reader:
                if (float(row[1]) == 0 and flag == False):
                    continue
                elif (float(row[1]) == 0):
                    ECG_mV.append(mV)
                    ECG_BPM.append(data)
                    mV = []
                    data = []
                    i += 1
                    flag = False
                elif (float(row[1]) != 0):
                    flag = True
                    data.append(float(row[1]))
                    mV.append(float(row[0]))
            ECG_BPM.append(data)
            ECG_mV.append(mV)

             
            ECG_BPM = ECG_BPM[:3] + ECG_BPM[5:]
            ECG_mV = ECG_mV[:3] + ECG_mV[5:]
          
    elif (i == 1):
        with open(f'./data/{FILES[i]}', 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row if present
            mV = []
            alpha = []
            beta = []
            delta = []
            theta = []
            for row in csv_reader:
                mV.append(float(row[0]))
                alpha.append(float(row[1]))
                beta.append(float(row[2]))
                delta.append(float(row[3]))
                theta.append(float(row[4]))

            EEG = [mV, alpha, beta, delta, theta]
            
    elif (i == 2 or i == 3):
        EMG = []
        with open(f'./data/{FILES[i]}', 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row if present
            mV = []
            integral = []
            for row in csv_reader:
                mV.append(float(row[0]))
                integral.append(float(row[1]))
            
            EMG = [mV, integral]
        
        if (i == 2):
            plot_EMG('b10901059', EMG)
        else:
            plot_EMG('b10901069', EMG)




print(f'[-]Lying BPM range: [{min(ECG_BPM[0])}, {max(ECG_BPM[0])}]')
print(f'[-]Lying mean BPM: {sum(ECG_BPM[0])/len(ECG_BPM[0])}')
print(f'[-]Sitting BPM range: [{min(ECG_BPM[1])}, {max(ECG_BPM[1])}]')
print(f'[-]Sitting mean BPM: {sum(ECG_BPM[1])/len(ECG_BPM[1])}')
print(f'[-]Inhale BPM range: [{min(ECG_BPM[2][:4000])}, {max(ECG_BPM[2][:4000])}]')
print(f'[-]Inhale mean BPM: {sum(ECG_BPM[2][:4000])/4000}')
print(f'[-]Exhale BPM range: [{min(ECG_BPM[2][4000:8000])}, {max(ECG_BPM[2][4000:8000])}]')
print(f'[-]Exhale mean BPM: {sum(ECG_BPM[2][4000:8000])/4000}')
print(f'[-]Exercise start BPM range: [{min(ECG_BPM[3][:4000])}, {max(ECG_BPM[3][:4000])}]')
print(f'[-]Exercise start mean BPM: {sum(ECG_BPM[3][:4000])/4000}')
print(f'[-]Exercise end BPM range: [{min(ECG_BPM[3][-4000:])}, {max(ECG_BPM[3][-4000:])}]')
print(f'[-]Exercise end mean BPM: {sum(ECG_BPM[3][-4000:])/4000}')


plot_ECG('Supine', ECG_mV[0], ECG_BPM[0])
plot_ECG('Sitting', ECG_mV[1], ECG_BPM[1])
plot_ECG('Deep_Breathe', ECG_mV[2], ECG_BPM[2])
plot_ECG('Exercise', ECG_mV[3], ECG_BPM[3])


plt.figure(figsize=FIGSIZE_EEG)
plot_EEG('', EEG, 1, 'purple')
plot_EEG('alpha', EEG, 2, 'green')
plot_EEG('beta', EEG, 3, 'blue')
plot_EEG('delta', EEG, 4, 'magenta')
plot_EEG('theta', EEG, 5, 'red')
plt.savefig(f'./output/EEG.png')
