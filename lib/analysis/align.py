# interactive drawing
from PIL import ImageTk, Image, ImageDraw
import PIL
from tkinter import *
import time
import numpy as np

from lib.file.ROI_writer import ROIFileWriter
from lib.analysis.laminar_dist import Line


class ImageAlign:
    """ Align RLI and DIC and record the RLI's image boundaries within the DIC image.
        dic_coordinates are the locations of the dic image corners within the 80x80 recording
        frame
    """
    def __init__(self, dic_coordinates, zoom_factor=1):
        self.zoom_factor = zoom_factor
        self.dic_coordinates = dic_coordinates
        self.dic_origin = dic_coordinates[0]

        # a crude projection, but this transformation is hardcoded and should be rectangles anyway
        self.x_dic_line = None
        self.y_dic_line = None
        self.x_dst = None
        self.y_dst = None
        self.create_dic_vectors()

        self.sin_theta = None
        self.cos_theta = None

    def create_dic_vectors(self):
        self.x_dic_line = Line(self.dic_origin, self.dic_coordinates[1])
        self.y_dic_line = Line(self.dic_origin, self.dic_coordinates[2])
        self.x_dst = self.x_dic_line.get_length()
        self.y_dst = self.y_dic_line.get_length()

    def draw_on_image(self, img):
        master = Tk()
        width, height = img.shape
        points_capture = [[]]
        last_capture_time = time.time()

        def paint(event):
            nonlocal last_capture_time
            x1, y1 = (event.x - 1), (event.y - 1)
            x2, y2 = (event.x + 1), (event.y + 1)
            canvas.create_oval(x1, y1, x2, y2, fill="red", width=3)
            draw.line([x1, y1, x2, y2], fill="red", width=3)
            last_time = last_capture_time
            last_capture_time = time.time()
            time_elapsed = last_capture_time - last_time
            if time_elapsed > 0.3 and len(points_capture[-1]) > 0:
                points_capture.append([])
            points_capture[-1].append([int((x1 + x2) / 2), int((y1 + y2) / 2)])

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
        coordinates = self.process_points(points_capture, [width, height])
        return img.resize((width, height)), coordinates

    def process_points(self, points_capture, img_shape):
        coords = {}
        print("Number of shapes drawn:", len(points_capture))
        if len(points_capture) < 5:
            raise Exception("Not enough shapes drawn, draw 5 next time.")
        if len(points_capture) > 5:
            print("Too many shapes drawn. Using only the first 5.")

        electrode = points_capture[0]
        layer_side_1 = points_capture[1]
        layer_side_2 = points_capture[2]
        barrel_side_1 = points_capture[3]
        barrel_side_2 = points_capture[4]

        # electrode: average all the points
        coords["electrode"] = [0, 0]
        for pt in electrode:
            x, y = pt
            coords["electrode"][0] += x
            coords["electrode"][1] += y
        coords["electrode"][0] /= len(electrode)
        coords["electrode"][1] /= len(electrode)

        coords['layer_axis1'] = self.make_axis_endpoints(layer_side_1, img_shape)
        coords['layer_axis2'] = self.make_axis_endpoints(layer_side_2, img_shape)
        coords['barrel_axis1'] = self.make_axis_endpoints(barrel_side_1, img_shape)
        coords['barrel_axis2'] = self.make_axis_endpoints(barrel_side_2, img_shape)
        return coords

    def transform_from_dic_coordinates(self, coordinates, arr_shape):
        x_dst_line = Line([0, 0], [80, 0])
        y_dst_line = Line([0, 0], [0, 80])
        w, h = arr_shape

        for key in coordinates:
            if key == 'electrode':
                pt = coordinates[key]
                pt = self.convert_point_from_dic_coord(pt, w, h, x_dst_line, y_dst_line)
                print("Electrode point:", pt)
                coordinates[key] = [self.point_to_diode_number(pt)]
            else:
                for i in range(2):
                    pt = coordinates[key][i]
                    pt = self.convert_point_from_dic_coord(pt, w, h, x_dst_line, y_dst_line)
                    coordinates[key][i] = self.point_to_diode_number(pt)

        return coordinates

    def point_to_diode_number(self, pt, width=80):
        x, y = pt
        dn = y * width + x
        return dn

    def get_rotation_matrix(self):
        rotation_vector = self.x_dic_line.get_unit_vector()
        theta = np.arctan(rotation_vector[1] / rotation_vector[0])
        self.sin_theta = np.sin(theta)
        self.cos_theta = np.cos(theta)

    def convert_point_from_dic_coord(self, pt, w, h, x_dst_line, y_dst_line):
        # place dic point in recording coordinates

        # scaling
        pt[0] *= self.x_dst / w
        pt[1] *= self.y_dst / h

        # rotation by  theta
        if self.sin_theta is None:
            self.get_rotation_matrix()

        x_old, y_old = pt

        pt[0] = int(self.cos_theta * x_old - self.sin_theta * y_old)
        pt[1] = int(self.sin_theta * x_old + self.cos_theta * y_old)

        # translation from recording origin tp dic origin
        pt[0] += self.dic_origin[0]
        pt[1] += self.dic_origin[1]

        return pt

    @staticmethod
    def make_axis_endpoints(drawn_shape, arr_shape):
        while len(drawn_shape) > 1 and (drawn_shape[-1][0] < 0 or drawn_shape[-1][1] < 0
                                        or drawn_shape[-1][0] >= arr_shape[0]
                                        or drawn_shape[-1][1] >= arr_shape[1]):
            del drawn_shape[-1]
        return [drawn_shape[0], drawn_shape[-1]]

    @staticmethod
    def write_shapes_to_files(coordinates, electrode_file, layer_file, barrel_file):
        # corner files should be written AXIS points FIRST, then "EDGE" points
        #       so as to work with laminar_dist.py construct_axes function
        roi_writer = ROIFileWriter()
        roi_writer.write_regions_to_dat(electrode_file, [coordinates['electrode']])
        axis_la1, edge_la1 = coordinates['layer_axis1']
        axis_la2, edge_la2 = coordinates['layer_axis2']
        roi_writer.write_regions_to_dat(layer_file,
                                        [[axis_la1, axis_la2, edge_la1, edge_la2]])
        axis_ba1, edge_ba1 = coordinates['barrel_axis1']
        axis_ba2, edge_ba2 = coordinates['barrel_axis2']
        roi_writer.write_regions_to_dat(barrel_file,
                                        [[axis_ba1, axis_ba2, edge_ba1, edge_ba2]])

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
    

