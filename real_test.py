import matplotlib.pyplot as plt
import json
import os
import numpy as np
import sys


class CustomPlot:
    def __init__(self):
        args = sys.argv[1:]
        dict_args = {}
        for a in args:
            if a.count('=') > 0:
                splitted_a = a.split('=')
                dict_args[splitted_a[0]] = splitted_a[1]
            else:
                dict_args[a] = True
        print(dict_args)

        self.plt = plt
        self.fig = self.plt.figure()
        self.fig.suptitle('Main title')
        self.fig.set_size_inches(1280 / 80, 800 / 80)
        self.fig.set_dpi(80)
        self.plt.subplots_adjust(left=0.07, right=0.97, bottom=0.12, top=0.95, hspace=0.35)
        self.json_files = []
        self.ind = []
        self.data = []
        self.x_labels = []
        self.y_labels = []
        self.ax = []
        self.width = 0.3
        self.all_data = {}
        self.x_labels_from_meta = []
        self.all_metrics = [
            # 'avg_DocPerSecond', 'perc90_DocPerSecond',
            # 'avg_MbPerSecond', 'perc90_MbPerSecond',
            'responseTime_perc90', 'responseTime_avg'
        ]
        self.colors = 'ygrbkm'
        self.data_of_metrics = {k: [] for k in self.all_metrics}
        self.bars = []
        self.plots = []
        self.max_metrics = {}
        self.run()

    def run(self):
        self.json_files = [name for name in os.listdir() if name.endswith('.json')]
        self.ind = np.arange(len(self.json_files))
        self.data = [self.get_data_from_json(file) for file in self.json_files]
        # TODO: Change 'documents_in_batch' to 'labels' (Used for x ticks)
        self.x_labels_from_meta = [lab for lab in [index['meta_data']['documents_in_batch'] for index in self.data]]
        self.data, self.x_labels_from_meta = self.sort(self.data, self.x_labels_from_meta)
        self.x_labels = [lab for lab in self.data[0].keys() if lab not in ['total', 'meta_data']]
        self.ax = [self.fig.add_subplot(2, 3, i + 1) for i in range(6)]
        self.first_configure_ax()
        self.plot_data()
        self.last_configure_ax()
        self.plt.show()

    @staticmethod
    def sort(data, keys):
        """Sort data by key"""
        sorted_data = []
        dictionary = {k: v for k, v in zip(keys, data)}
        sorted_keys = sorted(dictionary.keys())
        # print(sorted_keys)
        for i in sorted_keys:
            sorted_data.append(dictionary[i])
        return sorted_data, sorted_keys

    @staticmethod
    def get_data_from_json(file):
        with open(file) as fr:
            return json.load(fr)

    def first_configure_ax(self):
        for ax, x_l in zip(self.ax, self.x_labels):
            ax.set_xlabel(x_l)
            ax.set_xticks(self.ind + self.width / 2)
            for tick in ax.get_xticklabels():
                tick.set_rotation(90)
            # ax.set_xticklabels(self.json_files)
            ax.set_xticklabels(self.x_labels_from_meta)

    def last_configure_ax(self):
        for ax, x_l in zip(self.ax, self.x_labels):
            ax.set(ylim=[0, self.max_metrics[x_l] * 1.3])
            ax.set_ylabel(self.y_labels)
        self.ax[0].legend([bar[0] for bar in self.bars], self.all_metrics)

    @staticmethod
    def get_type_from_text(text):
        # print(text)
        if text in ['responseTime_perc90', 'responseTime_avg']:
            return 'seconds'
        elif text in ['perc90_DocPerSecond', 'avg_DocPerSecond']:
            return 'Docs/second'
        elif text in ['perc90_MbPerSecond', 'avg_MbPerSecond']:
            return 'MB/second'
        else:
            return ''

    def plot_data(self):
        for test_name, ax in zip(self.x_labels, self.ax):
            # print(test_name)
            self.all_data[test_name] = {}
            self.max_metrics[test_name] = 0
            for bottom_label, file_data in zip(self.json_files, self.data):
                self.all_data[test_name][bottom_label] = {}
                for metric in self.all_metrics:
                    if metric not in self.all_data[test_name][bottom_label].keys():
                        self.all_data[test_name][bottom_label][metric] = []
                        self.y_labels = self.get_type_from_text(metric)
                    # print(file_data[test_name][metric])
                    self.max_metrics[test_name] = max([file_data[test_name][metric], self.max_metrics[test_name]])
                    self.all_data[test_name][bottom_label][metric].append(file_data[test_name][metric])
                    # self.data_of_metrics[metric].append(file_data[test_name][metric])

        for test_name, ax in zip(self.x_labels, self.ax):
            index_bars = 0
            x = {k: [] for k in self.all_metrics}
            y = {k: [] for k in self.all_metrics}
            for bottom_label, file_data in zip(self.json_files, self.data):
                index_metric = 0
                for metric in self.all_metrics:
                    bar = ax.bar(self.ind[index_bars] + self.width * index_metric,
                                 self.all_data[test_name][bottom_label][metric],
                                 self.width, color=self.colors[index_metric])

                    self.autolabel(bar, ax)
                    self.bars.append(bar)
                    x[metric].append(self.ind[index_bars] + self.width * index_metric)
                    y[metric].append(self.all_data[test_name][bottom_label][metric])
                    index_metric += 1
                index_bars += 1
            for metric in self.all_metrics:
                plot = ax.plot(x[metric], y[metric])
                self.plots.append(plot)

    @staticmethod
    def autolabel(bars, ax):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., 1.05 * height,
                    str(height),
                    ha='center', va='bottom')


if __name__ == '__main__':
    a = CustomPlot()
    # a.run()
