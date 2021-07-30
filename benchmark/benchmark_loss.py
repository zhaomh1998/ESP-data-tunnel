import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == '__main__':
    df = pd.read_csv('loss.log', names=['ax', 'ay', 'az', 'gx', 'gy', 'gz', 'temp', 'us', 'hz'])
    loss_rates = df['hz'].value_counts()
    x = loss_rates.index.to_numpy()
    y = loss_rates.to_numpy()
    y = np.round(((500 - y) / 500) * 100, 2)
    plt.scatter(x, y)
    plt.xlabel('TX Hz')
    plt.ylabel('RX Loss Rate (%)')
    plt.title('IMU Data Packet via WiFi UDP Loss Benchmark')
    plt.grid()
    plt.show()
