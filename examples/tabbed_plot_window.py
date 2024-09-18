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
    def __init__(self, left: float = 0.06, right: float = 0.99,
                 bottom: float = 0.055, top: float = 0.97,
                 wspace: float = 0.25, hspace: float = 0.2):
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.wspace = wspace
        self.hspace = hspace


class TabbedPlotWindow:
    '''
    A class to create a tabbed plot window where the tabs are matplotlib
    figures. When using this class, DO NOT USE plt.show() or plt.pause() as they
    will cause issues with the plot window. Instead, use the methods provided
    by this class.
    '''

    def __init__(self, window_title: str = 'plot window', size: List[int] = [1280, 900],
                 fontsize: int=12):
        matplotlib.rcParams['font.size'] = fontsize
        self.app = QApplication(sys.argv)
        self.MainWindow = QMainWindow()
        self.MainWindow.__init__()
        self.MainWindow.setWindowTitle(window_title)
        self.canvases: List[FigureCanvas] = []
        self.figure_handles: List[Figure] = []
        self.toolbar_handles: List[NavigationToolbar] = []
        self.tab_handles: List[QWidget] = []
        self.current_window = -1
        self.tabs = QTabWidget()
        self.MainWindow.setCentralWidget(self.tabs)
        self.MainWindow.resize(*size)
        self.MainWindow.show()

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
        '''
        Replacement for plt.show(). This is blocking code that will display
        the plot window and keep it open until the window is closed or until
        ctrl+c is pressed.
        '''
        # kill the program with ctrl+c
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        # run the application
        # for fig in self.figure_handles:
        #     fig.tight_layout()
        self.app.exec_()

    def pause(self, delay_seconds: float):
        '''
        Replacement for plt.pause(). This will display the plot window for the
        specified delay time (in seconds) and then resume your code.
        '''
        start = time.time()
        for canvas in self.canvases:
            canvas.draw()
            canvas.flush_events()
        elapsed = time.time() - start
        delay = delay_seconds - elapsed
        if delay < 0:
            delay = 0
        time.sleep(delay)


if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt

    pw = TabbedPlotWindow()

    # data
    t = np.arange(0, 10, 0.001)
    ysin = np.sin(t)
    ycos = np.cos(t)

    # figure 1: sin(t)
    f,ax = plt.subplots()
    line1, = ax.plot(t, ysin, '--')
    ax.set_xlabel('time')
    ax.set_ylabel('sin(t)')
    ax.set_title('Plot of sin(t)')
    pw.addTab("sin", f)

    # figure 2: cos(t)
    f,ax = plt.subplots()
    line2, = ax.plot(t, ycos, '--')
    ax.set_xlabel('time')
    ax.set_ylabel('cos(t)')
    ax.set_title('Plot of cos(t)')
    pw.addTab("cos", f)

    # animate
    dt = 0.1
    for k in range(100):
        t += dt
        ysin = np.sin(t)
        line1.set_ydata(ysin)
        ycos = np.cos(t)
        line2.set_ydata(ycos)
        pw.pause(0.05)

    pw.show()
