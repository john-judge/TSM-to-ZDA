import os
import numpy as np
import shutil
import matplotlib.pyplot as plt
import threading
from abc import ABC, abstractmethod
import pyautogui as pa

from lib.analysis.laminar_dist import *
from lib.analysis.align import ImageAlign
from lib.file.ROI_writer import ROIFileWriter
from lib.utilities import *
from lib.file.TIF import *
from lib.camera_settings import CameraSettings
from ZDA_Adventure.utility import *
from ZDA_Adventure.tools import *
from ZDA_Adventure.measure_properties import TraceProperties


class BaseROIAnnotator(ABC):
    def __init__(self, data_dir, brush_size=20, skip_existing=False, 
                 output_keyword="roi_annotator", date_format='yyyy-mm-dd', 
                 camera_program=4, which_rig='old', 
                 rois_files_to_choose=('L23', 'L4', "L5"), 
                 load_align_tifs=False,
                 verbose=False, progress=None,
                 skip_draw_annotations=False,
                 **kwargs):
        self.data_dir = data_dir
        self.brush_size = brush_size
        self.skip_existing = skip_existing
        self.output_keyword = output_keyword
        self.date_format = date_format
        self.camera_program = camera_program
        self.which_rig = which_rig
        self.rois_files_to_choose = rois_files_to_choose
        self.load_align_tifs = load_align_tifs
        self.skip_draw_annotations = skip_draw_annotations
        self.verbose = verbose
        self.progress = progress
        self.stop_event = kwargs.get('stop_event', threading.Event())
        from lib.analysis.roi_annotator_rec_id_skip_list import rec_id_skip_list
        self.rec_id_skip_list = rec_id_skip_list.copy()

    @abstractmethod
    def _process_single_location(self, image_data, slic_id, loc_id, output_dir, 
                                 already_drawn_slic_loc, date, rec_id, zda_file_path, subdir):
        """Process a single location - must be implemented by subclass."""
        pass

    def _parse_date(self, subdir):
        """Parse date from subdirectory name."""
        date = ""
        # take from end of subdir name
        
        date = subdir.split("/")[-1]
        if '-' not in date:
            print(f"Parsed date: {date}")
            return date
        try:
            date = [int(x) for x in date.split("-")]
            if self.date_format != 'yyyy-mm-dd':
                date[2] += 2000  # full year format
            else:
                date = [date[1], date[2], date[0]]
            date = "/".join([str(d) for d in date])
        except Exception as e:
            print(e, "could not process date.")
        print(f"Parsed date: {date}")
        return date
    
    def _load_tif_images(self, dic_dir, slic_id):
        """Load TIF images from directory."""
        image_data = {}
        cam_settings = CameraSettings().get_program_settings(self.camera_program)
        binning = int(2048 / 400)  # if want size similar to RLI
        TIFLoader(dic_dir, 
                  cam_settings, 
                  binning, 
                  crop=False, 
                  flip_horiz=True).load_files(image_data, 
                                              slice_target=slic_id,
                                              verbose=self.verbose)
        return image_data
    
    def _load_rli_from_zda(self, zda_file_path, slic_id, loc_id):
        """Load RLI image from zda file."""
        try:
            loader = DataLoader(zda_file_path, rli_only=True)
            rli_data = loader.rli
            # rli_data contains 'rli_low', 'rli_high', 'rli_max'
            # Use rli_high as the default RLI image
            if 'rli_high' in rli_data:
                rli_image = np.array(rli_data['rli_high'], dtype=np.uint16)
                # Reshape to image dimensions
                width = loader.width
                height = loader.height
                rli_image = rli_image.reshape((height, width))
                return rli_image
        except Exception as e:
            if self.verbose:
                print(f"Error loading RLI from zda file: {e}")
        return None
    
    def _visualize_electrode(self, dic_electrode, coords_electrode, img_aligner, skip_show=False):
        """Visualize electrode location on DIC image."""
        if not skip_show:
            plt.imshow(dic_electrode, cmap='gray')
        if 'electrode' not in coords_electrode:
            print("No electrode coordinates found.")
            return []
        x_el, y_el = coords_electrode['electrode']
        if not skip_show:
            plt.plot(x_el, y_el, marker="*", color='red')
        dcs = []
        if self.which_rig != 'new' and self.load_align_tifs: 
            # show the portion of frame which is PhotoZ
            photoZ_frame_coords = img_aligner.dic_coordinates
            for dc_c in photoZ_frame_coords:
                x_c = dc_c[0] * dic_electrode.shape[1]
                y_c = dc_c[1] * dic_electrode.shape[0]
                dcs.append([x_c, y_c])
            for ic, jc in [[0,1],[1,3],[3,2],[2,0]]:
                if not skip_show:
                    plt.plot([dcs[ic][0], dcs[jc][0]], [dcs[ic][1], dcs[jc][1]], 
                             color="white", 
                             linewidth=3)
        if not skip_show:
            plt.show()
        return dcs
    
    def _visualize_rois(self, rois_img_coord_dict, img_aligner, dcs, skip_show=False):
        """Visualize barrel ROIs layer-by-layer."""
        roi_coords = {}
        for layer_label in rois_img_coord_dict:
            img_roi, coord_roi = rois_img_coord_dict[layer_label]
            roi_coords[layer_label] = coord_roi
            if not skip_show:
                plt.imshow(img_roi, cmap='gray')
            print("Layer:", layer_label)
            
        if self.which_rig != 'new' and len(dcs) > 0:  
            # show the portion of frame which is PhotoZ
            for ic, jc in [[0,1],[1,3],[3,2],[2,0]]:
                if not skip_show:
                    plt.plot([dcs[ic][0], dcs[jc][0]], [dcs[ic][1], dcs[jc][1]], 
                             color="white", 
                             linewidth=3)
            if not skip_show:
                plt.show()
        return roi_coords

    def _prepare_image_data(self, dic_dir, zda_file_path, slic_id, loc_id):
        """
        Prepare image data based on load_align_tifs option.
        If True, load and align TIF files.
        If False, use RLI from zda file.
        """
        if self.load_align_tifs:
            # Load TIF images and align them to zda recording
            print("Loading and aligning TIF images...")
            return self._load_tif_images(dic_dir, slic_id)
        else:
            # Load RLI from zda file only
            print("Loading RLI from ZDA file...")
            image_data = {}
            rli_image = self._load_rli_from_zda(zda_file_path, slic_id, loc_id)
            if rli_image is not None:
                # Create nested dictionary structure to match TIF loader output
                if slic_id not in image_data:
                    image_data[slic_id] = {}
                image_data[slic_id][loc_id] = {'rli': rli_image}
            return image_data
    
    def _normalize_image(self, image):
        """Normalize image to 0-255 range for drawing."""
        image = np.array(image, dtype=np.uint16)
        image = ((image - np.min(image)) / (np.max(image) - np.min(image)) * 255).astype(np.uint8)
        return np.array(image, dtype=np.uint8)
        
    def _load_fluor_electrode_images(self, image_data, slic_id, loc_id):
        """Load fluorescence and electrode images from image data."""
        if self.load_align_tifs:
            fluor, dic_electrode = None, None
            if 'f' in image_data[slic_id][loc_id]:
                fluor = image_data[slic_id][loc_id]['f']
            elif 'fe' in image_data[slic_id][loc_id]:
                fluor = image_data[slic_id][loc_id]['fe']

            dic_electrode = None
            if 'e' in image_data[slic_id][loc_id]:
                dic_electrode = image_data[slic_id][loc_id]['e']
            else:
                dic_electrode = fluor
                
            if self.which_rig != 'new':
                fluor = dic_electrode
            return fluor, dic_electrode
        else:
            # Load RLI image only
            rli_image = image_data[slic_id][loc_id]['rli']
            return None, rli_image
        
    def process_zda_files(self):
        """
        Process all ZDA files in data directory, calling _process_single_location
        for each slice/location pair.
        
        Returns:
            list: List of skipped recording IDs
        """
        # count total ZDA files for progress tracking
        cancel_button = False
        total_zda_files = 0
        for subdir, dirs, files in os.walk(self.data_dir):
            for zda_file in os.listdir(subdir):
                if zda_file.endswith('.zda'):
                    total_zda_files += 1
        if self.progress:
            self.progress.set_current_total(total_zda_files)

        for subdir, dirs, files in os.walk(self.data_dir):
            print("\n", subdir)
            dic_dir = subdir + "/archive/"
            selected_zda_dir = subdir + "/"
            already_drawn_slic_loc = {}
            
            # Parse date from directory name
            date = self._parse_date(subdir)

            # Process each ZDA file in the directory
            for zda_file in os.listdir(selected_zda_dir):
                if not zda_file.endswith('.zda'):
                    continue
                if self.stop_event.is_set():
                    break
                    
                rec_id = zda_file.split('.')[0]
                if subdir+rec_id in self.rec_id_skip_list:
                    continue
                if subdir in self.rec_id_skip_list:
                    continue  # skip entire subdir, manually added
                    
                print("\n", subdir)
                slic_id, loc_id, _ = [int(x) for x in rec_id.split("_")]
                print("Processing:", slic_id, loc_id)
                
                # Create output directory
                output_dir = selected_zda_dir + "/analysis" + rec_id + "/"
                try:
                    os.makedirs(output_dir)
                except Exception:
                    pass

                # Prepare image data based on load_align_tifs option
                zda_file_path = selected_zda_dir + zda_file
                image_data = self._prepare_image_data(dic_dir, zda_file_path, slic_id, loc_id)

                # Process each slice and location
                for slic in image_data:
                    for loc in image_data[slic]:
                        if slic != slic_id or loc != loc_id:
                            continue
                        
                        cancel_button = self._process_single_location(
                            image_data, slic_id, loc_id, output_dir,
                            already_drawn_slic_loc, date, rec_id, zda_file_path, subdir
                        )

                if cancel_button:
                    break
                
                image_data.clear()
                self.rec_id_skip_list.append(subdir+rec_id)
                if self.progress:
                    self.progress.increment_progress_value(1)
            if cancel_button or self.stop_event.is_set():
                break
        
        if self.progress:
            self.progress.complete()

        self._secondary_processing()
        return self.rec_id_skip_list
    
    def _secondary_processing(self):
        """Perform any secondary processing after initial annotation."""
        pass


class BarrelLayerROIAnnotator(BaseROIAnnotator):
    """Annotator for barrel layer ROI identification."""
    
    def __init__(self, data_dir, brush_size=4, skip_existing=False, 
                 output_keyword="roi_annotator", date_format='yyyy-mm-dd', 
                 camera_program=4, which_rig='old', 
                 rois_files_to_choose=('L23', 'L4', "L5"), verbose=True,
                 skip_draw_annotations=False, 
                 load_align_tifs=False,
                 progress=None, **kwargs):
        super().__init__(data_dir, brush_size=brush_size,
                         skip_existing=skip_existing, 
                         output_keyword=output_keyword, 
                         date_format=date_format, 
                         camera_program=camera_program, 
                         which_rig=which_rig, 
                         rois_files_to_choose=rois_files_to_choose, 
                         verbose=verbose, 
                         load_align_tifs=load_align_tifs,
                         skip_draw_annotations=skip_draw_annotations,
                         progress=progress, **kwargs)
    def _copy_existing_annotations(self, src_dir, output_dir):
        """Copy existing annotations from previous processing."""
        electrode_file = src_dir + "electrode.dat"
        roi_layer_files = [src_dir + "rois_layer_" + layer_label + ".dat" 
                          for layer_label in self.rois_files_to_choose]

        # copy if exists
        if os.path.exists(electrode_file):
            shutil.copy(electrode_file, output_dir + "electrode.dat")
        for i, roi_file in enumerate(roi_layer_files):
            layer_label = self.rois_files_to_choose[i]
            roi_file_output = output_dir + "rois_layer_" + layer_label + ".dat"
            if os.path.exists(roi_file):
                shutil.copy(roi_file, roi_file_output)

        print("Copied previous annotations over.")
    
    def _process_single_location(self, image_data, slic_id, loc_id, output_dir, 
                                 already_drawn_slic_loc, date, rec_id, zda_file_path, subdir):
        """Process a single location for barrel layer annotation."""
        if slic_id not in image_data or loc_id not in image_data[slic_id]:
            return False
        cancel_button = False
        
        
        print(slic_id, loc_id)

        # if already drawn, no need to ask user again
        if str(slic_id)+"_"+str(loc_id) in already_drawn_slic_loc:
            src_dir = already_drawn_slic_loc[str(slic_id)+"_"+str(loc_id)]
            self._copy_existing_annotations(src_dir, output_dir)
            return

        # Extract fluorescence and electrode images
        fluor, dic_electrode = self._load_fluor_electrode_images(image_data, slic_id, loc_id)

        orig_arr_shape = np.array(dic_electrode, dtype=np.uint16).shape
        dic_electrode = self._normalize_image(dic_electrode)

        # Create file paths
        electrode_file = output_dir + "electrode.dat"
        roi_layer_files = [output_dir + "rois_layer_" + layer_label + ".dat" 
                          for layer_label in self.rois_files_to_choose]

        if not self.skip_draw_annotations:
            # Initialize image aligner
            zoom_factor = 1 if self.load_align_tifs else 7
            img_aligner = ImageAlign(rig=self.which_rig, zoom_factor=zoom_factor, no_align=(not self.load_align_tifs))
            
            # Ask user to annotate
            dic_electrode, coords_electrode, rois_img_coord_dict, cancel_button = \
                img_aligner.draw_on_images_wrapper_2(
                    dic_electrode, 
                    fluor, 
                    date + " " + rec_id + " ",
                    roi_layer_files,
                    brush_size=self.brush_size)

            # Visualize electrode
            dcs = self._visualize_electrode(dic_electrode, coords_electrode, img_aligner, skip_show=True)

            # Visualize barrel ROIs
            roi_coords = self._visualize_rois(rois_img_coord_dict, img_aligner, dcs, skip_show=True)

            try:
                os.makedirs(output_dir)
            except OSError:
                pass
            
            print(roi_coords)
            
            # Transform coordinates -- Actual alignment work done here
            print("\n \tcoords_electrode", coords_electrode)
            coords_electrode = img_aligner.transform_from_dic_coordinates(coords_electrode, orig_arr_shape)
            coords_rois = img_aligner.transform_from_dic_coordinates(roi_coords, orig_arr_shape, multi_pt_rois=True)
            
            # Combine coordinate dictionaries
            for k in coords_electrode:
                coords_rois[k] = coords_electrode[k]

            print(coords_rois.keys())

            # Write electrode and corners to file
            img_aligner.write_shapes_to_files_rois(coords_rois, electrode_file)
            print("Wrote files to", output_dir)

        # Mark this slice/loc already drawn 
        already_drawn_slic_loc[str(slic_id)+"_"+str(loc_id)] = output_dir
        return cancel_button


class MaxSNRROIAnnotator(BaseROIAnnotator):
    """Annotator for 5x5 Maximal SNR ROI identification.
    In the first sweep, for each slice/location, the user
         annotates the electrode location and locations of the soma centers.

    A later sweep will be done to draw the soma ROIs around the centers, 
    using the maximal SNR method in 5x5 patches around the centers. This
    process is run for each recording under the slice/location, using the 
    same centers each time. As these are drawn, they are saved to .dat files
    and also drawn on the images for visual confirmation (saved as png files).
    
    """
    
    def __init__(self, data_dir, brush_size=4, skip_existing=False, 
                 output_keyword="roi_annotator", date_format='yyyy-mm-dd', 
                 camera_program=4, which_rig='old', roi_scan_radius=1,
                 rois_files_to_choose=('soma'), verbose=False, 
                 load_align_tifs=False, progress=None, **kwargs):
        super().__init__(data_dir, brush_size=brush_size, 
                         skip_existing=skip_existing, 
                         output_keyword=output_keyword, 
                         date_format=date_format, 
                         camera_program=camera_program, 
                         which_rig=which_rig, 
                         rois_files_to_choose=rois_files_to_choose, 
                         verbose=verbose, 
                         load_align_tifs=load_align_tifs,
                         progress=progress, **kwargs)
        
        self.slice_location_to_soma_centers = {}
        self.roi_scan_radius = roi_scan_radius # 1 -> 3x3, 2 -> 5x5, etc.
        if 'measure_window_start' in kwargs:
            self.measure_window_start = kwargs['measure_window_start']
        if 'measure_window_width' in kwargs:
            self.measure_window_width = kwargs['measure_window_width']
        if 'skip_window_start' in kwargs:
            self.skip_window_start = kwargs['skip_window_start']
        if 'skip_window_width' in kwargs:
            self.skip_window_width = kwargs['skip_window_width']


    def _copy_existing_mapping(self, slic_id, loc_id, rec_id, date,zda_file_path):
        """ instead of copying previous annotations, 
            we just note the soma centers mapping for this slice/location, copying over the roi file path
            to a new entry of slice_location_to_soma_centers"""
        src_key = date + "_" + str(slic_id)+"_"+str(loc_id)
        if src_key in self.slice_location_to_soma_centers:
            self.slice_location_to_soma_centers[src_key]['zda_file_paths'][rec_id] = zda_file_path
    
    def save_png_with_electrode_and_soma_rois(self, rli_img, electrode_coords, rois, date, rec_id):
        """ Save a PNG image visualizing the electrode and soma ROIs on the RLI image. """
        plt.imshow(rli_img, cmap='gray')
        if 'electrode' in electrode_coords:
            x_el, y_el = electrode_coords['electrode']
            plt.plot(x_el, y_el, marker="*", color='red', label='Electrode')
        
        roi_colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow']
        for i, roi in enumerate(rois):
            color = roi_colors[i % len(roi_colors)]
            for px in roi:
                plt.plot(px[0], px[1], marker='o', color=color, alpha=0.3, markersize=2)
        
        date_formatted = date.replace("/", "-")
        plt.title(f"RLI with Electrode and Soma ROIs - {date_formatted} {rec_id}")
        plt.xlabel("X (pixels)")
        plt.ylabel("Y (pixels)")
        output_png_path = f"{self.data_dir}/visualization_{self.output_keyword}/{date_formatted}_{rec_id}_electrode_soma_rois.png"
        plt.savefig(output_png_path)
        plt.close()

    def _compute_roi_snr(self, zda_arr, roi):
        """ Compute the SNR for a given patch and ROI.
            Average the ROI into a single trace, then compute SNR. """
        roi_traces = np.array([zda_arr[px[0], px[1]] for px in roi])
        roi_avg_trace = np.mean(roi_traces, axis=0) 
        tp = TraceProperties(roi_avg_trace, 
                             self.measure_window_start, 
                             self.measure_window_width,
                                0.5,  # assume 2000 Hz
                                )
        tp_snr = tp.get_SNR()
        return tp_snr

    def _build_max_snr_roi(self, zda_arr, x, y):
        """ Compute the maximal SNR ROI within a 5x5 patch."""
        # first look at 3x3 around center, greedily add pixels that increase current SNR
        current_roi = [[x,y]]
        if self.roi_scan_radius > 0:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i == 0 and j == 0:
                        continue
                    curr_avg_snr = self._compute_roi_snr(zda_arr, current_roi)
                    test_roi = current_roi + [[x+i, y+j]]
                    test_avg_snr = self._compute_roi_snr(zda_arr, test_roi)
                    if test_avg_snr > curr_avg_snr:
                        current_roi.append([x+i, y+j])
        # then look at 5x5 border pixels, greedily add pixels that increase current SNR
        if self.roi_scan_radius > 1:
            for i in range(-2, 3):
                for j in range(-2, 3):
                    if i >=-1 and i <=1 and j >=-1 and j <=1:
                        continue
                    curr_avg_snr = self._compute_roi_snr(zda_arr, current_roi)
                    test_roi = current_roi + [[x+i, y+j]]
                    test_avg_snr = self._compute_roi_snr(zda_arr, test_roi)
                    if test_avg_snr > curr_avg_snr:
                        current_roi.append([x+i, y+j])
        return current_roi

    def _secondary_processing(self):
        """ Second sweep to draw soma ROIs around previously annotated centers. """
        pa.alert("Maximizing SNR for ROIs around the centers you annotated. " +\
                 " This may take a while. Visualizations will be saved to: " +\
                    f"{self.data_dir}/visualization_{self.output_keyword}/")
        # create output directory for visualizations
        try:
            os.makedirs(f"{self.data_dir}/visualization_{self.output_keyword}/")
        except OSError:
            pass
        img_aligner = ImageAlign(rig=self.which_rig, zoom_factor=7, no_align=True)
        for date_slic_loc_key in self.slice_location_to_soma_centers:
            subdir = self.slice_location_to_soma_centers[date_slic_loc_key]['subdir']
            electrode_coords = self.slice_location_to_soma_centers[date_slic_loc_key]['electrode_coords']
            roi_centers = self.slice_location_to_soma_centers[date_slic_loc_key]['soma_centers']
            for rec_id in self.slice_location_to_soma_centers[date_slic_loc_key]['zda_file_paths']:
                zda_file_path = self.slice_location_to_soma_centers[date_slic_loc_key]['zda_file_paths'][rec_id]
                date, slic_id, loc_id = date_slic_loc_key.split("_")
                
                # load full zda file
                print("Loading ZDA file for SNR computation:", zda_file_path)
                dl = DataLoader(zda_file_path)
                zda_arr = dl.get_data(rli_division=False)
                tools = Tools()
                zda_arr = tools.Polynomial(startPt=self.skip_window_start,
                            numPt=self.skip_window_width,
                            Data=zda_arr)
                zda_arr = tools.Rli_Division(Data=zda_arr, RLI=dl.get_rli())
                zda_arr = tools.T_filter(Data=zda_arr)
                zda_arr = tools.S_filter(Data=zda_arr, sigma=1)

                zda_arr = np.mean(zda_arr, axis=0)  # average across trials
                rli_img = np.array(dl.rli['rli_high']).reshape((dl.height, dl.width))

                rois = []
                print("  roi centers:", roi_centers)
                # For each soma center, extract 5x5 patch and compute maximal SNR ROI
                for center in roi_centers:
                    x_center, y_center = int(center[0]), int(center[1])
                    print(f" Built soma ROI from center at: {x_center}, {y_center} ")
                    # Compute maximal SNR ROI in the patch (placeholder function)
                    roi = self._build_max_snr_roi(zda_arr, x_center, y_center)

                    print("\troi size:", len(roi))

                    rois.append(roi)

                self.save_png_with_electrode_and_soma_rois(rli_img, electrode_coords, rois, date, rec_id)
                
                # use img_aligner.point_to_diode_number to transform to diode numbers
                for i in range(len(rois)):
                    rois[i] = [img_aligner.point_to_diode_number(px) for px in rois[i]]

                # write ROIs to file
                date_formatted = date.replace("/", "-")
                output_dir = f"{subdir}/{self.output_keyword}_{date_formatted}_{rec_id}.dat"
                roi_writer = ROIFileWriter()
                roi_writer.write_regions_to_dat(output_dir, rois)
    
    def _process_single_location(self, image_data, slic_id, loc_id, output_dir, 
                                 already_drawn_slic_loc, date, rec_id, zda_file_path, subdir):
        """Process a single location for 5x5 Maximal SNR annotation."""
        if slic_id not in image_data or loc_id not in image_data[slic_id]:
            return False
        cancel_button = False
        
        
        print(slic_id, loc_id)

        # if already drawn, no need to ask user again
        if str(slic_id)+"_"+str(loc_id) in already_drawn_slic_loc:
            src_dir = already_drawn_slic_loc[str(slic_id)+"_"+str(loc_id)]
            self._copy_existing_mapping(slic_id, loc_id, rec_id, date, zda_file_path)
            return

        # Extract fluorescence and electrode images
        fluor, dic_electrode = self._load_fluor_electrode_images(image_data, slic_id, loc_id)

        orig_arr_shape = np.array(dic_electrode, dtype=np.uint16).shape
        dic_electrode = self._normalize_image(dic_electrode)

        # Create file paths
        electrode_file = output_dir + "electrode.dat"

        # only one roi file for soma centers
        if not type(self.rois_files_to_choose) == str:
            self.rois_files_to_choose = self.rois_files_to_choose[0]
        roi_files = [output_dir + "rois_" + self.rois_files_to_choose + ".dat"]

        if not self.skip_draw_annotations:
            # Initialize image aligner
            zoom_factor = 1 if self.load_align_tifs else 7
            img_aligner = ImageAlign(rig=self.which_rig, zoom_factor=zoom_factor, no_align=(not self.load_align_tifs))
            
            # Ask user to annotate
            dic_electrode, coords_electrode, rois_img_coord_dict, cancel_button = \
                img_aligner.draw_on_images_wrapper_2(
                    dic_electrode, 
                    fluor, 
                    date + " " + rec_id + " ",
                    roi_files,
                    brush_size=self.brush_size)

            # Visualize electrode
            dcs = self._visualize_electrode(dic_electrode, coords_electrode, img_aligner, skip_show=True)

            # Visualize barrel ROIs
            roi_coords = self._visualize_rois(rois_img_coord_dict, img_aligner, dcs, skip_show=True)
            grouped_roi_coords = roi_coords[list(roi_coords.keys())[0]]  # only one 'soma'

            ''' roi_mask = np.zeros_like(dic_electrode)
            for px in roi_coords:
                roi_mask[px[0], px[1]] = 1
            
            # group adjacent points into single ROIs, using flood fill algorithm
            grouped_roi_coords = []
            visited = np.zeros_like(roi_mask, dtype=bool)
            def flood_fill(x, y):
                stack = [[x, y]]
                group = []
                while len(stack) > 0:
                    px, py = stack.pop()
                    if visited[px, py]:
                        continue
                    visited[px, py] = True
                    group.append([px, py])
                    for dx, dy in [[-1,0],[1,0],[0,-1],[0,1]]:
                        nx, ny = px + dx, py + dy
                        if nx >= 0 and nx < dic_electrode.shape[1] \
                            and ny >= 0 and ny < dic_electrode.shape[0] \
                                and roi_mask[nx, ny] == 1:
                            stack.append([nx, ny])
                return group
            for px in roi_coords:
                if not visited[px[0], px[1]]:
                    group = flood_fill(px[0], px[1])
                    grouped_roi_coords.append(group)'''

            #print("  grouped roi coords before finding centers:", grouped_roi_coords)

            # turn each grouped ROI into its center point
            grouped_roi_coords = [
                [int(np.mean([coord[0] for coord in group])), 
                 int(np.mean([coord[1] for coord in group]))]
                for group in grouped_roi_coords
            ]

            roi_coords = grouped_roi_coords
            electrode_pt = coords_electrode['electrode']
            #print(" roi_coords (centers):", roi_coords)

            try:
                os.makedirs(output_dir)
            except OSError:
                pass
                        
            # Transform coordinates -- Actual alignment work done here
            coords_electrode_dn = img_aligner.transform_from_dic_coordinates(coords_electrode, orig_arr_shape)
            
            # Write electrode and corners to file
            img_aligner.write_shapes_to_files_rois({}, electrode_file)
            print("Wrote files to", output_dir)

        # recording mapping of slice/location to soma centers and zda file path
        self.slice_location_to_soma_centers[date + "_" +str(slic_id)+"_"+str(loc_id)] = {
            'electrode_coords': electrode_pt,
            'subdir': subdir,
            'soma_centers': roi_coords,
            'zda_file_paths': {rec_id: zda_file_path}
        }
        # Mark this slice/loc already drawn 
        already_drawn_slic_loc[str(slic_id)+"_"+str(loc_id)] = output_dir
        return cancel_button
