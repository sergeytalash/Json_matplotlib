import matplotlib.pyplot as plt
import json
import os
import numpy as np
import sys
from itertools import combinations_with_replacement as comb, product


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
        print('args: {}'.format(dict_args))

        self.plt = plt
        self.fig = self.plt.figure()

        self.fig.set_size_inches(1280 / 80, 800 / 80)
        self.fig.set_dpi(80)
        self.plt.subplots_adjust(left=0.07, right=0.97, bottom=0.12, top=0.90, hspace=0.35)
        self.json_files = []
        self.ind = []
        self.data = []
        self.x_labels = []
        self.y_labels = []
        self.ax = []
        # TODO: Change 'documents_in_batch' to 'labels' (Used for x ticks)
        self.x_label_from_file = 'documents_in_batch'
        self.all_metrics = [
            'avg_DocPerSecond',
            'perc90_DocPerSecond',
            'avg_MbPerSecond',
            'perc90_MbPerSecond',
            'responseTime_perc90',
            'responseTime_avg'
        ]
        if len(self.all_metrics) < 2:
            self.text_rotation = 0
        else:
            self.text_rotation = 90
        # Change width regarding to number of metrics and make some space between data from different files(batches)
        self.width = 1 / (len(self.all_metrics) + 1)
        self.fig.suptitle('Main title')
        self.all_data = {}
        self.x_labels_from_meta = []
        self.colors = ['#f39c12',
                       '#27ae60',
                       '#8e44ad',
                       '#3498db',
                       '#16a085',
                       '#e74c3c',
                       ]
        # self.colors = self.generate_color()[4::]
        self.data_of_metrics = {k: [] for k in self.all_metrics}
        self.bars = []
        self.plots = []
        self.max_metrics = {}
        self.run()

    def run(self):
        self.json_files = [name for name in os.listdir() if name.endswith('.json')]
        self.ind = np.arange(len(self.json_files))
        self.data = [self.get_data_from_json(file) for file in self.json_files]
        self.x_labels_from_meta = [lab for lab in [index['meta_data'][self.x_label_from_file] for index in self.data]]
        self.data, self.x_labels_from_meta = self.sort(self.data, self.x_labels_from_meta)
        self.x_labels = [lab for lab in self.data[0].keys() if lab not in ['total', 'meta_data']]
        self.ax = [self.fig.add_subplot(2, 3, i + 1) for i in range(6)]
        self.first_configure_ax()
        self.plot_data()
        self.last_configure_ax()
        self.fig.savefig('image.png')
        self.plt.show()
        self.plt.close(self.fig)

    @staticmethod
    def generate_color():
        color_vars = ['00', 'C8', 'FF']
        return ['#' + ''.join(i) for i in list(product(color_vars, repeat=3))]

    @staticmethod
    def sort(data, keys):
        """Sort data by key"""
        dictionary = {k: v for k, v in zip(keys, data)}
        sorted_keys = sorted(dictionary.keys())
        sorted_data = [dictionary[i] for i in sorted_keys]
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
            try:
                ax.set_xticklabels(self.x_labels_from_meta)
            except Exception as err:
                ax.set_xticklabels(self.json_files)
                print(err)

    def last_configure_ax(self):
        for ax, x_l in zip(self.ax, self.x_labels):
            ax.set(ylim=[0, self.max_metrics[x_l] * 1.3])
            ax.set_ylabel(self.y_labels)
        self.ax[1].legend([bar[0] for bar in self.bars], self.all_metrics, loc='upper center',
                          bbox_to_anchor=(0.5, 1.15),
                          ncol=len(self.all_metrics),
                          fancybox=True,
                          shadow=True
                          )

    @staticmethod
    def get_type_from_text(text):
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
            self.all_data[test_name] = {}
            self.max_metrics[test_name] = 0
            for bottom_label, file_data in zip(self.json_files, self.data):
                self.all_data[test_name][bottom_label] = {}
                for metric in self.all_metrics:
                    if metric not in self.all_data[test_name][bottom_label].keys():
                        self.all_data[test_name][bottom_label][metric] = []
                        self.y_labels = self.get_type_from_text(metric)
                    self.max_metrics[test_name] = max([file_data[test_name][metric], self.max_metrics[test_name]])
                    self.all_data[test_name][bottom_label][metric].append(file_data[test_name][metric])

        for test_name, ax in zip(self.x_labels, self.ax):
            index_bars = 0
            x_dict = {k: [] for k in self.all_metrics}
            y_dict = {k: [] for k in self.all_metrics}
            for bottom_label, file_data in zip(self.json_files, self.data):
                index_metric = 0
                for metric in self.all_metrics:
                    x = self.ind[index_bars] + self.width * index_metric
                    y = self.all_data[test_name][bottom_label][metric]
                    x_dict[metric].append(x)
                    y_dict[metric].append(y)
                    bar = ax.bar(x, y, self.width, color=self.colors[index_metric])
                    self.autolabel_bar(bar, ax, self.max_metrics[test_name], self.text_rotation)
                    self.bars.append(bar)
                    index_metric += 1
                index_bars += 1
            for metric in self.all_metrics:
                # If the metric value do not exceed 30% of the maximum bar, then do not plot
                if max(y_dict[metric])[0] / self.max_metrics[test_name] > 0.3:
                    plot = ax.plot(x_dict[metric], y_dict[metric])
                    self.plots.append(plot)

    @staticmethod
    def autolabel_bar(bars, ax, max_value, text_rotation):
        """Draw value above bar"""
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2.,
                    0.05 * max_value + height,
                    str(height),
                    ha='center', va='bottom').set_rotation(text_rotation)


if __name__ == '__main__':
    CustomPlot()
