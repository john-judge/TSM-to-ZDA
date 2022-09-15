# interactive drawing
from PIL import ImageTk, Image, ImageDraw
import PIL
from tkinter import *


class ImageAlign:
    """ Align RLI and DIC and record the RLI's image boundaries within the DIC image. """
    def __init__(self, zoom_factor=4):
        self.zoom_factor = zoom_factor

    def draw_on_image(self, img):
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
        return img.resize((width, height))

    def drag_to_align(self, back_img, drag_img):
        master = Tk()
        width, height = back_img.shape

        nw_drag_corner = [0, 0]
        shift_by = 1

        canvas = Canvas(master, width=width * self.zoom_factor, height=height * self.zoom_factor)
        canvas.pack()

        back_img = PIL.Image.fromarray(back_img).resize((width * self.zoom_factor, height * self.zoom_factor))
        photo_img = ImageTk.PhotoImage(image=back_img)
        print(photo_img)
        canvas.create_image(0, 0, image=photo_img, anchor="nw")

        drag_img = PIL.Image.fromarray(drag_img).resize((width * self.zoom_factor, height * self.zoom_factor)).convert("RGBA")
        drag_img.putalpha(128)
        photo_drag_img = ImageTk.PhotoImage(image=drag_img)
        drag_img_canvas = canvas.create_image(0, 0, image=photo_drag_img, anchor="nw")

        def move(event):
            """Move the image with W,A,S,D"""
            global drag_shown
            if event.char == "a" or event.keysym == "Left":
                canvas.move(drag_img_canvas, -1 * shift_by, 0)
                nw_drag_corner[0] -= shift_by
            elif event.char == "d" or event.keysym == "Right":
                canvas.move(drag_img_canvas, shift_by, 0)
                nw_drag_corner[0] += shift_by
            elif event.char == "w" or event.keysym == "Up":
                canvas.move(drag_img_canvas, 0, -1 * shift_by)
                nw_drag_corner[1] -= shift_by
            elif event.char == "s" or event.keysym == "Down":
                canvas.move(drag_img_canvas, 0, shift_by)
                nw_drag_corner[1] += shift_by
            elif event.char == " ":
                canvas.itemconfig(drag_img_canvas, state='hidden')
            else:
                canvas.itemconfig(drag_img_canvas, state='normal')

        canvas.focus_set()
        canvas.pack(expand=YES, fill=BOTH)
        canvas.bind("<Key>", move)

        master.mainloop()
        return nw_drag_corner

