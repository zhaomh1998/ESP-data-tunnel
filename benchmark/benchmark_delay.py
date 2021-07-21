import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == '__main__':
    with open('output.txt', 'r') as f:
        data = f.readlines()[1:-2]
        data_parsed = np.array([float(i.lstrip('Time: ')) for i in data])
        diffs = 1000 * np.diff(data_parsed)
        plt.figure(figsize=(5, 5))
        sns.histplot(diffs, bins=1000)
        plt.xlabel('ms between two packets RX')
        plt.ylabel('Number of packets')
        plt.title('Wi-Fi UDP Packets Delay Fluctuation Distribution - Computer Hotspot to RPi')
        plt.show()
