import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

clock_err_max = 1e8  # Drop rows more having more clock err than this

if __name__ == '__main__':
    df = pd.read_csv('bench_clock_2.log', delimiter='\t',
                     names=['host_time', 'real_us', 'us', 'ms', 'rtc_time']).dropna()
    df = df.astype('float')

    df_diff = df - df.iloc[0].values.squeeze()
    clock_error = (df_diff['host_time'] * 1e6) - df_diff['real_us']
    print('Err rows: ' + repr(clock_error[abs(clock_error) > clock_err_max].index))
    clock_error = clock_error[abs(clock_error) < clock_err_max]
    df_diff_cleaned = df_diff.loc[clock_error.index]
    plt.scatter(df_diff_cleaned['host_time'], clock_error / 1e3, s=1, alpha=0.007)
    # sns.distplot(clock_error, bins=500)
    plt.xlabel('Time since start (s)')
    plt.ylabel('Time difference between host and MCU (ms)')
    plt.title('Time Series - Clock difference between host and MCU')
    plt.grid()

    plt.figure()
    # sns.distplot(clock_error/1e3, bins=200)
    plt.hist(clock_error/1e3, bins=500)
    plt.xlabel('Time difference between host and MCU (ms)')
    plt.ylabel('N Samples')
    plt.title('Distribution - Clock difference between host and MCU')

    plt.tight_layout()
    plt.show()
