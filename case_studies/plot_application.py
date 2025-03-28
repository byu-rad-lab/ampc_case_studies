import matplotlib
# prevent NoneType error for versions of matplotlib 3.1.0rc1+ by calling matplotlib.use()
# For more on why it's nececessary, see
# https://stackoverflow.com/questions/59656632/using-qt5agg-backend-with-matplotlib-3-1-2-get-backend-changes-behavior
matplotlib.use('qt5agg')

# Fix plot font types to work in paper sumbissions (Don't use type 3 fonts)
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
# matplotlib.rcParams['font.size'] = 18

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QTabWidget, QVBoxLayout
from matplotlib.figure import Figure
from typing import List
import signal
import sys
import time


class FigureSpacing:
    def __init__(self, left: float = 0.075, right: float = 0.99,
                 bottom: float = 0.075, top: float = 0.95,
                 wspace: float = 0.25, hspace: float = 0.2):
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.wspace = wspace
        self.hspace = hspace


class TabbedWindow:
    '''
    A class to create a tabbed plot window where the tabs are matplotlib
    figures. When using this class, DO NOT USE plt.show() or plt.pause() as they
    will cause issues with the plot window. Instead, use the methods provided
    by this class.
    '''

    def __init__(self, window_title: str = 'plot window', size: List[int] = [1280, 900]):
        self.main_window = QMainWindow()
        self.main_window.__init__()
        self.main_window.setWindowTitle(window_title)
        self.canvases: List[FigureCanvas] = []
        self.figure_handles: List[Figure] = []
        self.toolbar_handles: List[NavigationToolbar] = []
        self.tab_handles: List[QWidget] = []
        self.current_window = -1
        self.tabs = QTabWidget()
        self.main_window.setCentralWidget(self.tabs)
        self.main_window.resize(*size)

    def addTab(self, tab_title: str, figure: Figure,
               spacing: FigureSpacing = FigureSpacing()):
        new_tab = QWidget()
        layout = QVBoxLayout()
        new_tab.setLayout(layout)

        figure.subplots_adjust(left=spacing.left, right=spacing.right,
                               bottom=spacing.bottom, top=spacing.top,
                               wspace=spacing.wspace, hspace=spacing.hspace)
        new_canvas = FigureCanvas(figure)
        new_toolbar = NavigationToolbar(new_canvas, new_tab)

        layout.addWidget(new_canvas)
        layout.addWidget(new_toolbar)
        self.tabs.addTab(new_tab, tab_title)

        self.toolbar_handles.append(new_toolbar)
        self.canvases.append(new_canvas)
        self.figure_handles.append(figure)
        self.tab_handles.append(new_tab)

    def show(self):
        self.main_window.show()

    def update(self):
        '''
        Replacement for plt.pause(). This will display the plot window for the
        specified delay time (in seconds) and then resume your code.
        '''
        for canvas in self.canvases:
            canvas.draw()
            canvas.flush_events()


class PlotApplication:
    def __init__(self, fontsize: int=10):
        matplotlib.rcParams['font.size'] = fontsize - 2
        matplotlib.rcParams['legend.fontsize'] = fontsize - 2
        matplotlib.rcParams['axes.titlesize'] = fontsize
        matplotlib.rcParams['axes.labelsize'] = fontsize - 2
        self.app = QApplication(sys.argv)
        self.windows: list[TabbedWindow] = []

    def addWindow(self, window: TabbedWindow):
        self.windows.append(window)
        window.show()

    def applyTightLayout(self):
        for win in self.windows:
            for i,fig in enumerate(win.figure_handles):
                win.tabs.setCurrentIndex(i) # tab has to be active to apply tight layout
                fig.tight_layout()
            win.tabs.setCurrentIndex(0)

    def show(self, tight_layout: bool = True):
        if tight_layout:
            self.applyTightLayout()
            # for win in self.windows:
            #     for i,fig in enumerate(win.figure_handles):
            #         win.tabs.setCurrentIndex(i) # tab has to be active to apply tight layout
            #         fig.tight_layout()
            #     win.tabs.setCurrentIndex(0)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.app.exec() # exec_() is for PyQt < 5 and Python < 3. Use exec now

    def pause(self, delay_seconds: float):
        start = time.time()
        for window in self.windows:
            window.update()
        elapsed = time.time() - start
        delay = delay_seconds - elapsed
        if delay < 0:
            delay = 0
        time.sleep(delay)


if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt

    plotter = PlotApplication()
    window1 = TabbedWindow()
    window2 = TabbedWindow()

    # data
    t = np.arange(0, 10, 0.001)
    ysin = np.sin(t)
    ycos = np.cos(t)


    f,ax = plt.subplots()
    line1, = ax.plot(t, ysin, '--')
    ax.set_xlabel('time')
    ax.set_ylabel('sin(t)')
    ax.set_title('Plot of sin(t)')
    window1.addTab("sin", f)

    f,ax = plt.subplots()
    ax.plot(t, t)
    ax.set_xlabel('time')
    ax.set_ylabel('t')
    ax.set_title('Plot of t')
    window1.addTab("time", f)

    plotter.addWindow(window1)

    f,ax = plt.subplots()
    line2, = ax.plot(t, ycos, '--')
    ax.set_xlabel('time')
    ax.set_ylabel('cos(t)')
    ax.set_title('Plot of cos(t)')
    window2.addTab("cos", f)

    f,ax = plt.subplots()
    ax.plot(t, t)
    ax.set_xlabel('time')
    ax.set_ylabel('t')
    ax.set_title('Plot of t')
    window2.addTab("time", f)

    plotter.addWindow(window2)

    # animate
    dt = 0.1
    for k in range(100):
        t += dt
        ysin = np.sin(t)
        line1.set_ydata(ysin)
        ycos = np.cos(t)
        line2.set_ydata(ycos)
        plotter.pause(0.05)
        # time.sleep(0.05)

    plotter.show()
