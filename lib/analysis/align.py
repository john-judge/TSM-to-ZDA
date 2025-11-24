# interactive drawing
from PIL import ImageTk, Image, ImageDraw
import PIL
from tkinter import *
import time
import numpy as np
#from shapely.geometry import Polygon
import cv2

from lib.file.ROI_writer import ROIFileWriter
from lib.analysis.laminar_dist import Line


class ImageAlign:
    """ Align RLI and DIC and record the RLI's image boundaries within the DIC image.
        dic_coordinates are the locations of the dic image corners within the 80x80 recording
        frame
    """
    def __init__(self, rig='new', zoom_factor=1):
        """ If rig is 'new', then the dic coordinates are the corners of the DIC image
                within the [0,80] x [0,80] square
            Buf if the rig is 'old', the coordinates are the corders of the PhotoZ image
                within the [0.00, 1.00] x [0.00, 1.00]  """
        self.rig = rig
        new_rig_dic_coordinates = [[8, 6], [80, 12], [2, 69], [76, 74]]
        old_rig_dic_coordinates = [[.245, .032], [.915, .042], [.240, .722], [.905, .732]]
        self.zoom_factor = zoom_factor
        self.dic_coordinates = old_rig_dic_coordinates
        if rig == 'new':
            self.dic_coordinates = new_rig_dic_coordinates
        self.dic_origin = self.dic_coordinates[0]

        # a crude projection, but this transformation is hardcoded and should be rectangles anyway
        self.x_dic_line = None
        self.y_dic_line = None
        self.x_dst = None
        self.y_dst = None
        self.create_dic_vectors()

        self.sin_theta = None
        self.cos_theta = None

    def draw_on_images_wrapper_2(self, img, fluor_img, identifier, roi_layer_files, brush_size=1):
        i1, c1 = self.draw_electrode_on_image(img, identifier)
        rois = {}
        for layer in roi_layer_files:
            i_roi, c_roi = self.draw_single_roi_on_image(img, identifier=identifier + " " + layer.split('/')[-1],
                                                         process_points=False, brush_size=brush_size)
            rois[layer] = [np.array(i_roi), c_roi]
        return np.array(i1), c1, rois

    def draw_on_images_wrapper(self, img, fluor_img, identifier):
        i1, c1 = self.draw_electrode_on_image(img, identifier)
        i2, c2 = self.draw_layers_barrels_on_image(fluor_img, identifier)
        return i1, c1, i2, c2

    def draw_single_roi_on_image(self, img, identifier="",process_points=True, brush_size=1):
        """ Return a modified img and a list of points representing ROI enclosure """
        i1, c1 = self.draw_on_image(img, "ROI", identifier, process_points=process_points, brush_size=brush_size)
        return i1, c1

    def draw_electrode_on_image(self, img, identifier):
        return self.draw_on_image(img, "electrode", identifier + " Electrode Annotation")

    def draw_layers_barrels_on_image(self, img, identifier):
        return self.draw_on_image(img, "layers", identifier + " Layer/Barrel Annotation")

    def draw_on_image(self, img, draw_type, window_title, process_points=True, brush_size=1):
        """ draw_type either 'electrode' or 'layers' or 'ROI'
            'ROI' is an enclosure
        """
        master = Tk()
        master.title(window_title)
        width, height = img.shape
        points_capture = [[]]
        last_capture_time = time.time()

        def paint(event):
            nonlocal last_capture_time
            x1, y1 = (event.x - 1), (event.y - 1)
            x2, y2 = (event.x + 1), (event.y + 1)
            #draw.line([x1, y1, x2, y2], fill="red", width=3)
            canvas.create_oval(x1, y1, x2, y2, fill='red', width=brush_size)
            last_time = last_capture_time
            last_capture_time = time.time()
            time_elapsed = last_capture_time - last_time
            if time_elapsed > 0.3 and len(points_capture[-1]) > 0:
                points_capture.append([])
            for bsx in range(-brush_size // 2, brush_size // 2 + 1):
                for bsy in range(-brush_size // 2, brush_size // 2 + 1):
                    points_capture[-1].append([int((x1 + x2) / 2) + bsx, int((y1 + y2) / 2) + bsy])
        
        def draw_initial_image():
            # create a tkinter canvas to draw on
            canvas.create_image(0, 0, image=photo_img, anchor="nw")
            if self.rig != 'new':
                # then draw borders for annotation limits
                dcs = []
                for dcc in self.dic_coordinates:
                    dcs.append([dcc[0] * img.size[0], dcc[1] * img.size[1]])
                for ic, jc in [[0, 1], [1, 3], [3, 2], [2, 0]]:
                    canvas.create_line(dcs[ic][0], dcs[ic][1], dcs[jc][0], dcs[jc][1], fill="red", width=3)

        def clear_points(event):
            nonlocal points_capture
            points_capture = [[]]
            canvas.delete("all")
            draw_initial_image()


        # create a tkinter canvas to draw on
        canvas = Canvas(master, width=height * self.zoom_factor, height=width * self.zoom_factor)
        canvas.pack()

        img = PIL.Image.fromarray(img).resize((height * self.zoom_factor, width * self.zoom_factor))
        photo_img = ImageTk.PhotoImage(image=img)

        # create PIL image to draw on
        draw = ImageDraw.Draw(img)
        draw_initial_image()
        canvas.pack(expand=YES, fill=BOTH)
        canvas.bind("<B1-Motion>", paint)
        canvas.bind("<Button-3>", clear_points)

        master.mainloop()
        if process_points:
            coordinates = self.process_points(points_capture, [width, height], draw_type)
        else:
            coordinates = points_capture
        return img.resize((height, width)), coordinates

    def process_points(self, points_capture, img_shape, draw_type):
        """ draw_type either 'electrode' or 'layers' or 'ROI' """

        if draw_type == 'ROI':
            return self.process_roi_enclosure(points_capture, img_shape)

        num_points_needed = [1, 1]
        if draw_type == 'layers':
            num_points_needed = [4, 8]
        coords = {}
        if draw_type != 'electrode':
            print("Number of shapes drawn:", len(points_capture))
        if len(points_capture) < num_points_needed[0]:
            raise Exception(
                "Not enough shapes drawn, draw " + str(num_points_needed[0]) + " to " +
                str(num_points_needed[1]) + " next time.")
        if len(points_capture) > num_points_needed[1]:
            print("Too many shapes drawn. Using only the first " + str(num_points_needed[1]) + ".")

        if draw_type == 'electrode':

            electrode = points_capture[0]

            # electrode: average all the points
            coords["electrode"] = [0, 0]
            for pt in electrode:
                x, y = pt
                coords["electrode"][0] += x
                coords["electrode"][1] += y
            coords["electrode"][0] /= len(electrode)
            coords["electrode"][1] /= len(electrode)

            return coords

        # else process layer boundary points
        layer_side_1 = points_capture[0]
        layer_side_2 = points_capture[1]
        # barrel_side_1 = points_capture[2]
        # barrel_side_2 = points_capture[3]

        coords['layer_axis1'] = self.make_axis_endpoints(layer_side_1, img_shape)
        coords['layer_axis2'] = self.make_axis_endpoints(layer_side_2, img_shape)
        # coords['barrel_axis1'] = self.make_axis_endpoints(barrel_side_1, img_shape)
        # coords['barrel_axis2'] = self.make_axis_endpoints(barrel_side_2, img_shape)

        for j in range(2, len(points_capture)):
            coords['barrel_axis' + str(j-1)] = self.make_axis_endpoints(points_capture[j], img_shape)
        return coords

    def transform_from_dic_coordinates(self, coordinates, arr_shape, multi_pt_rois=False):
        """ Coordinates are from draw_on_images_wrapper
            ARR_SHAPE is dimensions of the DIC image """
        w, h = arr_shape
        for key in coordinates:
            if key == 'electrode':
                pt = coordinates[key]
                pt = self.convert_point_from_dic_coord(pt, w, h)
                print("Electrode point:", pt)
                dn = self.point_to_diode_number(pt)
                if dn is None:
                    return []
                coordinates[key] = [dn]
            else:
                if not multi_pt_rois:
                    new_coords = {}
                    for i in range(len(coordinates[key])):
                        pt = coordinates[key][i]
                        pt = self.convert_point_from_dic_coord(pt, w, h)
                        dn = self.point_to_diode_number(pt)
                        if dn is not None:
                            new_coords[dn] = True
                    coordinates[key] = [d for d in new_coords.keys()]
                else:
                    new_coords = {}
                    for i in range(len(coordinates[key])):
                        
                        roi = coordinates[key][i]
                        new_roi = {}
                        for pt in roi:
                            pt = self.convert_point_from_dic_coord(pt, w, h)
                            dn = self.point_to_diode_number(pt)
                            if dn is not None:
                                new_roi[dn] = True
                        coordinates[key][i] = [d for d in new_roi.keys()]
        return coordinates

    def point_to_diode_number(self, pt, width=80):
        x, y = pt
        dn = y * width + x
        if dn < 0 or dn >= width * width:
            return None
        return dn

    def get_rotation_matrix(self):
        rotation_vector = self.x_dic_line.get_unit_vector()
        theta = np.arctan(rotation_vector[1] / rotation_vector[0])
        self.sin_theta = np.sin(theta)
        self.cos_theta = np.cos(theta)

    def create_dic_vectors(self):
        """ in new rig, these vectors trace out the DIC image within the 80x80 recording image
            in old rig, these vectors trace out the 80x80 recording image within the DIC image """
        self.x_dic_line = Line(self.dic_origin, self.dic_coordinates[1])
        self.y_dic_line = Line(self.dic_origin, self.dic_coordinates[2])
        self.x_dst = self.x_dic_line.get_length()
        self.y_dst = self.y_dic_line.get_length()

    def convert_point_from_dic_coord(self, pt, w, h):
        """ place dic point in recording (TSM or PhotoZ) coordinates
            PT: the point to convert to 80x80 coordinates
            W: width of DIC image
            H: heigt of DIC image
            X_DST_LINE: line from 0,0 -> 80, 0
            Y_DST_LINE: line from 0,0 -> 0, 80
        OLD RIG: self.dic_coordinates are the proportions of PhotoZ img corners within DIC image """
        if self.sin_theta is None:
            self.get_rotation_matrix()
        if self.rig == 'new':
            # scaling
            pt[0] *= self.x_dst / w
            pt[1] *= self.y_dst / h
            # rotation by theta
            x_old, y_old = pt
            pt[0] = int(self.cos_theta * x_old - self.sin_theta * y_old)
            pt[1] = int(self.sin_theta * x_old + self.cos_theta * y_old)
            # translation from recording origin tp dic origin
            pt[0] += self.dic_origin[0]
            pt[1] += self.dic_origin[1]
            return pt
        else:  # old rig
            # convert PT to proportion units
            pt[0] *= 1 / w
            pt[1] *= 1 / h
            # convert to origin-relative
            pt[0] -= (self.dic_origin[0])
            pt[1] -= self.dic_origin[1]
            # rotate into 80x80 frame. Note flipped signs
            x_old, y_old = pt
            pt[0] = self.cos_theta * x_old + self.sin_theta * y_old
            pt[1] = -self.sin_theta * x_old + self.cos_theta * y_old
            # scale to 80x80. self.x_dst is the fraction of DIC that equates to 80 px PhotoZ
            pt = [(x * 80 / self.x_dst) for x in pt]

            # fine tuning (empirical offsets)
            pt[0] = pt[0] * (65 / 80) - 3
            pt[1] = pt[1] * (80 / 66)
            return [int(pt[0]), int(pt[1])]

    @staticmethod
    def process_roi_enclosure(points_capture, img_shape):
        """ points_capture is a list of points forming a polygon in an
            image of shape img_shape
            Outputs a list of all points enclosed in this polygon
        """
        poly = Polygon(points_capture[0])
        mask = np.zeros(img_shape)
        vertex_points = [[x, y] for x, y in zip(*poly.boundary.coords.xy)]
        mask = cv2.fillPoly(mask, np.array([vertex_points]).astype(np.int32), color=1)
        print(mask)
        enclosed_points = []
        for i in range(img_shape[0]):
            for j in range(img_shape[1]):
                if mask[i, j] != 0:
                    enclosed_points.append([i, j])
        return enclosed_points

    @staticmethod
    def make_axis_endpoints(drawn_shape, arr_shape):
        while len(drawn_shape) > 1 and (drawn_shape[-1][0] < 0 or drawn_shape[-1][1] < 0
                                        or drawn_shape[-1][0] >= arr_shape[0]
                                        or drawn_shape[-1][1] >= arr_shape[1]):
            del drawn_shape[-1]
        return [drawn_shape[0], drawn_shape[-1]]

    @staticmethod
    def write_shapes_to_files_rois(coordinates, electrode_file):
        # coordinates maps layer_file names to lists of lists of points (diode numbers)
        roi_writer = ROIFileWriter()
        if 'electrode' in coordinates:
            roi_writer.write_regions_to_dat(electrode_file, [coordinates['electrode']])

        for layer_file in coordinates:
            if layer_file == 'electrode':
                continue
            roi_writer.write_regions_to_dat(layer_file,
                                            coordinates[layer_file])

    @staticmethod
    def write_shapes_to_files(coordinates, electrode_file, layer_file, barrel_file, preserve_initial_order=False):
        # corner files should be written AXIS points FIRST, then "EDGE" points
        #       so as to work with laminar_dist.py construct_axes function
        roi_writer = ROIFileWriter()
        roi_writer.write_regions_to_dat(electrode_file, [coordinates['electrode']])
        axis_la1, edge_la1 = coordinates['layer_axis1']
        axis_la2, edge_la2 = coordinates['layer_axis2']
        layer_shape_list = [axis_la1, axis_la2, edge_la1, edge_la2]
        if preserve_initial_order:
            layer_shape_list = [axis_la1, edge_la1, axis_la2, edge_la2]
        roi_writer.write_regions_to_dat(layer_file,
                                        [layer_shape_list])

        barrel_shape_list = []
        for key in coordinates:
            if 'barrel_axis' in key:
                axis_ba, edge_ba = coordinates[key]
                barrel_shape_list.append(axis_ba)
                barrel_shape_list.append(edge_ba)
        roi_writer.write_regions_to_dat(barrel_file,
                                        [barrel_shape_list])

    @staticmethod
    def write_roi_to_files(coordinates, roi_file):
        roi_writer = ROIFileWriter()
        roi_writer.write_regions_to_dat(roi_file, [coordinates])

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
    

