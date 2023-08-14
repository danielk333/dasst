from matplotlib import pyplot as plt
import numpy as np

num = 10000
x_axis = np.arange(num, dtype=np.float64)
DATA = np.random.randn(num)


'''This should be done so that one can control a simulation visualkistiaon live with keys


'''


class DataShift:
    def __init__(self, line, ax, step_size):
        self.ax = ax
        self.step_size = step_size*2
        self.line = line
        self.step = 0
        self.cid = line.figure.canvas.mpl_connect('key_press_event', self)

    def __call__(self, event):
        print('Pressed ', event.key)
        if event.inaxes!=self.line.axes:
            return

        if event.key == 'n':
            self.step += 0.5
        elif event.key == 'b':
            self.step -= 0.5
        else:
            return

        ind_n = int((self.step + 1)*self.step_size)
        ind_p = int(self.step*self.step_size)

        self.line.set_data(
            x_axis[ind_p:ind_n],
            DATA[ind_p:ind_n],
        )
        self.ax.set_xlim([x_axis[ind_p], x_axis[ind_n]])
        self.line.figure
        self.line.figure.canvas.draw()



fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title('press n to step forward, b to go back')
line_set = ax.plot(x_axis[:500], DATA[:500], '.b')  # empty line
shift = DataShift(line_set[0], ax, step_size = 500)

plt.show()
