from scipy import signal

import matplotlib.pyplot as plt
import pandas as pd


def drop_column(df, column_name):
    """
    Drop a column from a dataframe if it exists
    """

    if column_name in df.columns:
        df = df.drop(columns=[column_name])
    return df


def drop_zero_columns(df):
    """
    Drop all columns from a dataframe if they are composed of only zeros
    """

    return df.loc[:, (df != 0).any(axis=0)]


def get_column(df, column_name):
    """
    Get a column from a dataframe if it exists
    """

    if column_name in df.columns:
        return df[column_name]
    return None


def get_headers(df):
    """
    Passes a dataframe and returns the headers for it
    """

    return df.columns.values


def data_normalization(dataframe):
    """
    Bring the dataframe values in the range [0, 1]
    Needed in order for the date to work in a butterworth filter
    """

    return dataframe.apply(lambda x: (x - x.min()) / (x.max() - x.min()))


def get_pandas_data_set(selected_data_set):
    """
    Passes in the index of the data set we want to use
    The list is statically built based on the files we have in ./resurse/
    """

    csv_sets = [
        "Tibi1_rest1_[2017.06.14-11.25.26].csv",
        "TUI04_2back_[2017.06.14-11.11.18].csv",
        "TUI4_VTE_1Random_[2017.06.14-11.15.03].csv",
        "TUI4_VTE_Boxes_[2017.06.14-11.20.56].csv",
        "TUI4_VTE_Complex_[2017.06.14-11.22.59].csv",
        "TUI4_VTE_Rest_[2017.06.14-11.07.20].csv",
        "TUI5_3Back-[2017.05.24-15.48.50].csv",
        "Irina-1-14.04.18.22.08.52.csv",
        "Irina-2-14.04.18.22.12.13.csv",
        "Irina-2back-14.04.18.22.19.03.csv",
        "Irina-3back-14.04.18.22.21.01.csv"
    ]

    csv_file = (
        "resurse/"
        "{0}".format(csv_sets[selected_data_set])
    )

    _delimiter = ','
    if ';' in open(csv_file).read():
        _delimiter = ';'

    df = pd.read_csv(
        csv_file,
        delimiter=_delimiter
    )

    # if data is from the test data set
    time = get_column(df, 'Time (s)')

    df = drop_column(df, 'Time (s)')
    df = drop_column(df, 'Sampling Rate')
    df = drop_column(df, 'Reference')

    # if the data is from the epoc
    time = get_column(df, 'TIME_STAMP_ms')

    df = drop_zero_columns(df)
    df = drop_column(df, 'TIME_STAMP_ms')
    df = drop_column(df, 'TIME_STAMP_s')
    df = drop_column(df, 'COUNTER')

    return data_normalization(df), time


def plot_power_spectrum_periodogram(data):
    """
    Create a power spectrum using the periodogram method
    When plotting, we are limiting the printed frequency to 256 for clarity
    The selected frequency is half of the sampling rate
    """

    _sampling_rate = 512.0
    f, pxx = signal.periodogram(
        data,
        fs=_sampling_rate,
        window='flattop',
        scaling='spectrum'
        )

    plt.semilogy(f, pxx)
    plt.show()


def plot_data(x_data, y_data, color='r'):
    """
    A simple method to quickly plot basic data
    It helps with not forgetting to plot() and show()
    """

    plt.plot(x_data, y_data, color)
    plt.show()


def butter_bandpass(
        lowcut_freq,
        highcut_freq,
        sampling_rate,
        order
        ):
    """
    Return the desired butterworth bandpass filter
    """

    _nyq = 0.5 * sampling_rate
    _low = lowcut_freq/_nyq
    _high = highcut_freq/_nyq

    a, b = signal.butter(
        N=order,
        Wn=[_low, _high],
        btype='bandpass'
        )

    return a, b


def butter_bandpass_filter(data_vector):
    """
    Filters the signal with the designated butterworth bandpass filter
    """

    _lowcut_freq = 0.5
    _highcut_freq = 5.0
    _sampling_rate = 128
    _order = 4

    a, b = butter_bandpass(
        _lowcut_freq,
        _highcut_freq,
        _sampling_rate,
        _order
        )
    y = signal.lfilter(a, b, data_vector)

    return y


def get_butter(df):
    """
    Filters the dataframe with a butterworth bandpass filter
    """

    for column in df.columns.values:
        df_column = df[column]
        df[column] = butter_bandpass_filter(df_column)

    return df


df, time_df = get_pandas_data_set(7)
selected_df = 'F3'
plt.figure(1)
plt.plot(time_df, df[selected_df], 'b')
df = get_butter(df)
plot_data(time_df, df[selected_df])
