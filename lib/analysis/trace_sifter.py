# interactive drawing
from PIL import ImageTk, Image, ImageDraw
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PIL
from tkinter import *
from lib.trace import Tracer
import numpy as np


class TraceSifter:
    """ Present traces to user for accept/reject. Record example history. """

    def __init__(self, trace_data, interval, roi_names,
                 stim_time=None,
                 measure_window=None,
                 values=None,
                 metric_name='df/f'):
        self.trace_data = trace_data
        self.interval = interval
        self.roi_names = roi_names
        self.stim_time = stim_time
        self.measure_window = measure_window
        self.values = values
        self.metric_name = metric_name

    '''    def draw_on_image(self, img):
        master = Tk()
        width, height = img.shape

        def paint(event):
            x1, y1 = (event.x - 1), (event.y - 1)
            x2, y2 = (event.x + 1), (event.y + 1)
            canvas.create_oval(x1, y1, x2, y2, fill="red", width=3)
            draw.line([x1, y1, x2, y2], fill="red", width=3)

        # create a tkinter canvas to draw on
        canvas = Canvas(master, width=width * self.zoom_factor, height=height * self.zoom_factor)
        canvas.pack()

        img = PIL.Image.fromarray(img).resize((width * self.zoom_factor, height * self.zoom_factor))
        photo_img = ImageTk.PhotoImage(image=img)

        # create PIL image to draw on
        draw = ImageDraw.Draw(img)

        canvas.create_image(0, 0, image=photo_img, anchor="nw")

        canvas.pack(expand=YES, fill=BOTH)
        canvas.bind("<B1-Motion>", paint)

        master.mainloop()
        return img.resize((width, height))'''

    def present_accept_reject(self):
        accepted = np.zeros(self.trace_data.shape[0], dtype=bool)

        for i in range(self.trace_data.shape[0]):
            accept, contin = self.accept_reject_one_plot(self.trace_data[i], i)
            accepted[i] = accept
            print(accept)
            if not contin:
                return accepted

        return accepted

    def accept_reject_one_plot(self, trace, trace_iterator):
        master = Tk()
        state = [False, True] # accept, continue

        f = Tracer().plot_roi_trace(self.trace_data[trace_iterator],
                                    self.interval,
                                    self.roi_names[trace_iterator],
                                    stim_time=self.stim_time,
                                    measure_window=self.measure_window,
                                    value=self.values[trace_iterator],
                                    metric_name=self.metric_name)

        plot = FigureCanvasTkAgg(f, master=master)
        canvas = Canvas(master)
        plot.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        def accept_reject(event):
            """Move the image with W,A,S,D"""
            if event.char == "a" or event.keysym == "Left":
                state[0] = False
                master.destroy()
            elif event.char == "d" or event.keysym == "Right":
                state[0] = True
                master.destroy()
            elif event.char == 'q':
                state[1] = False
                master.destroy()

        canvas.focus_set()
        canvas.bind("<Key>", accept_reject)
        canvas.pack(expand=YES, fill=BOTH)

        master.mainloop()
        return state


class TraceLearner:

    def __init__(self):
        self.examples = None
        self.labels = None

    def add_examples(self, examples, labels):
        if self.examples is None:
            pass
        else:
            pass

    def train_model(self):
        pass

    def predict_labels(self, examples):
        pass
