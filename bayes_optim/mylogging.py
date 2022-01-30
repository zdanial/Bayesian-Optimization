import sys
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import math


class PictureSaver:
    def __init__(self, path, name_suffix, extension):
        self.path = path
        self.fid = name_suffix
        self.extension = extension

    def save(self, fig, name):
        fig.savefig(self.path + name + self.fid + '.' + self.extension)


MY_PROGRESS_LOG_FILE = 'progress.csv'

def set_logger_file(file_name_str):
    global MY_PROGRESS_LOG_FILE
    MY_PROGRESS_LOG_FILE = file_name_str


def eprintf(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def fprintf(*args, **kwargs):
    with open(MY_PROGRESS_LOG_FILE, 'a') as f:
        f.write(*args, **kwargs)


class MyChartSaver:
    def __init__(self, folder_name, name, bounds, obj_function):
        directory = './'+folder_name+'/'
        self.saver = PictureSaver(directory, "-"+name, "png")
        self.bounds = bounds
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.domain_grid, self.colours = MyChartSaver.__sample_points(0.2, 0.2, bounds, obj_function)

    @staticmethod
    def __sample_points(x_step, y_step, bounds, obj_f):
        x_points = MyChartSaver.__sample_on_axis(bounds[0][0], bounds[0][1], x_step)
        y_points = MyChartSaver.__sample_on_axis(bounds[1][0], bounds[1][1], y_step)
        v = []
        N = len(x_points)*len(y_points)
        eprintf("Number of points on the grid is", N)
        points = [[0. for _ in range(N)] for _ in range(2)]
        values = [0.] * N
        cnt = 0
        for x in x_points:
             for y in y_points:
                points[0][cnt] = x
                points[1][cnt] = y
                values[cnt] = obj_f([x, y])
                cnt += 1
        return points, MyChartSaver.__compute_colours_2(values)
   
    @staticmethod
    def __sample_on_axis(beg, end, step):
        N = int(math.ceil((end - beg) / step))
        ans = [0.] * N
        x0 = beg
        cnt = 0
        while cnt < N:
            ans[cnt] = x0
            x0 += step
            cnt += 1            
        return ans

    @staticmethod
    def __compute_colours_2(Y):
        colours = []
        y_copy = Y.copy()
        y_copy.sort()
        min_value = y_copy[0]
        k = int(0.4 * len(Y))
        m = math.log(0.5) / (y_copy[k] - min_value)
        jet_cmap = mpl.cm.get_cmap(name='jet')
        for y in Y:
            colours.append(jet_cmap(1. - math.exp(m * (y - min_value))))
        return colours
        

    def create_figure_with_domain(self):
        fig = plt.figure()
        plt.xlim(list(self.bounds[0]))
        plt.ylim(list(self.bounds[1]))
        plt.scatter(self.domain_grid[0], self.domain_grid[1], marker='s', c=self.colours)
        return fig

    def add_evaluated_points(self, iter_number, X):
        plt.title(f'Iteration number {iter_number}, last point is ({X[-1][0]:.4f}, {X[-1][1]:.4f})')
        plt.scatter(X[:-1, 0], X[:-1, 1], c='black', marker='X')
        plt.scatter(X[-1][0], X[-1][1], c='red', marker='X')

    def add_mainfold(self, X_transformed, inverser):
        X = inverser.inverse_transform(X_transformed)
        plt.scatter(X[:, 0], X[:, 1], c='green')

    def save(self, iter_number, X):
        fig = self.create_figure_with_domain()
        self.add_evaluated_points(iter_number, X)
        self.saver.save(fig, f"DoE-{iter_number}")

    def save_with_manifold(self, iter_number, X, X_transformed, inverser):
        fig = self.create_figure_with_domain()
        self.add_mainfold(X_transformed, inverser)
        self.add_evaluated_points(iter_number, X)
        self.saver.save(fig, f"DoE-{iter_number}")
        
         
