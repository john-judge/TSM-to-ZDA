import os
import numpy as np
import shutil
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod

from lib.analysis.laminar_dist import *
from lib.analysis.align import ImageAlign

from lib.utilities import *
from lib.file.TIF import *
from lib.file.camera_settings import CameraSettings

class BaseROIAnnotator(ABC):
    def __init__(self, data_dir, brush_size=20, skip_existing=False, 
                 output_keyword="roi_annotator", date_format='yyyy-mm-dd', 
                 camera_program='default', which_rig='old', 
                 rois_files_to_choose=('L23', 'L4', "L5"), verbose=False):
        self.data_dir = data_dir
        self.brush_size = brush_size
        self.skip_existing = skip_existing
        self.output_keyword = output_keyword
        self.date_format = date_format
        self.camera_program = camera_program
        self.which_rig = which_rig
        self.rois_files_to_choose = rois_files_to_choose
        self.verbose = verbose
        from lib.analysis.roi_annotator_rec_id_skip_list import rec_id_skip_list
        self.rec_id_skip_list = rec_id_skip_list.copy()

    @abstractmethod
    def _process_single_location(self, image_data, slic_id, loc_id, output_dir, 
                                 already_drawn_slic_loc, date, rec_id):
        """Process a single location - must be implemented by subclass."""
        pass

    def _parse_date(self, subdir):
        """Parse date from subdirectory name."""
        date = ""
        try:
            char_select = -len(self.date_format)
            date = subdir.split("_Usable")[0][char_select:]
            date = [int(x) for x in date.split("-")]
            if self.date_format != 'yyyy-mm-dd':
                date[2] += 2000  # full year format
            else:
                date = [date[1], date[2], date[0]]
            date = "/".join([str(d) for d in date])
        except Exception as e:
            print(e, "could not process date.")
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
    
    def process_zda_files(self):
        """
        Process all ZDA files in data directory, calling _process_single_location
        for each slice/location pair.
        
        Returns:
            list: List of skipped recording IDs
        """
        for subdir, dirs, files in os.walk(self.data_dir):
            if 'archive' not in dirs:
                continue
                
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

                # Load TIF images
                image_data = self._load_tif_images(dic_dir, slic_id)

                # Process each slice and location
                for slic in image_data:
                    for loc in image_data[slic]:
                        if slic != slic_id or loc != loc_id:
                            continue
                        
                        self._process_single_location(
                            image_data, slic_id, loc_id, output_dir,
                            already_drawn_slic_loc, date, rec_id
                        )
                
                image_data.clear()
                self.rec_id_skip_list.append(subdir+rec_id)
        
        return self.rec_id_skip_list


class BarrelLayerROIAnnotator(BaseROIAnnotator):
    """Annotator for barrel layer ROI identification."""
    
    def __init__(self, data_dir, brush_size=4, skip_existing=False, 
                 output_keyword="roi_annotator", date_format='yyyy-mm-dd', 
                 camera_program='default', which_rig='old', 
                 rois_files_to_choose=('L23', 'L4', "L5"), verbose=False,
                 skip_draw_annotations=False):
        super().__init__(data_dir, brush_size, skip_existing, output_keyword, 
                         date_format, camera_program, which_rig, 
                         rois_files_to_choose, verbose)
        self.skip_draw_annotations = skip_draw_annotations
    
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
    
    def _normalize_image(self, image):
        """Normalize image to 0-255 range for drawing."""
        image = np.array(image, dtype=np.uint16)
        image = ((image - np.min(image)) / (np.max(image) - np.min(image)) * 255).astype(np.uint8)
        return np.array(image, dtype=np.uint8)
    
    def _visualize_electrode(self, dic_electrode, coords_electrode, img_aligner):
        """Visualize electrode location on DIC image."""
        plt.imshow(dic_electrode, cmap='gray')
        x_el, y_el = coords_electrode['electrode']
        plt.plot(x_el, y_el, marker="*", color='red')
        dcs = []
        if self.which_rig != 'new':  # show the portion of frame which is PhotoZ
            photoZ_frame_coords = img_aligner.dic_coordinates
            for dc_c in photoZ_frame_coords:
                x_c = dc_c[0] * dic_electrode.shape[1]
                y_c = dc_c[1] * dic_electrode.shape[0]
                dcs.append([x_c, y_c])
            for ic, jc in [[0,1],[1,3],[3,2],[2,0]]:
                plt.plot([dcs[ic][0], dcs[jc][0]], [dcs[ic][1], dcs[jc][1]], 
                         color="white", 
                         linewidth=3)
        plt.show()
        return dcs
    
    def _visualize_rois(self, rois_img_coord_dict, img_aligner, dcs):
        """Visualize barrel ROIs layer-by-layer."""
        roi_coords = {}
        for layer_label in rois_img_coord_dict:
            img_roi, coord_roi = rois_img_coord_dict[layer_label]
            roi_coords[layer_label] = coord_roi
            plt.imshow(img_roi, cmap='gray')
            print("Layer:", layer_label)
            
        if self.which_rig != 'new':  # show the portion of frame which is PhotoZ
            for ic, jc in [[0,1],[1,3],[3,2],[2,0]]:
                plt.plot([dcs[ic][0], dcs[jc][0]], [dcs[ic][1], dcs[jc][1]], 
                         color="white", 
                         linewidth=3)
            plt.show()
        return roi_coords
    
    def _process_single_location(self, image_data, slic_id, loc_id, output_dir, 
                                 already_drawn_slic_loc, date, rec_id):
        """Process a single location for barrel layer annotation."""
        if slic_id not in image_data or loc_id not in image_data[slic_id]:
            return
        
        print(slic_id, loc_id)

        # if already drawn, no need to ask user again
        if str(slic_id)+"_"+str(loc_id) in already_drawn_slic_loc:
            src_dir = already_drawn_slic_loc[str(slic_id)+"_"+str(loc_id)]
            self._copy_existing_annotations(src_dir, output_dir)
            return

        # Extract fluorescence and electrode images
        fluor = None
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

        orig_arr_shape = np.array(dic_electrode, dtype=np.uint16).shape
        dic_electrode = self._normalize_image(dic_electrode)

        # Create file paths
        electrode_file = output_dir + "electrode.dat"
        roi_layer_files = [output_dir + "rois_layer_" + layer_label + ".dat" 
                          for layer_label in self.rois_files_to_choose]

        if not self.skip_draw_annotations:
            # Initialize image aligner
            img_aligner = ImageAlign(rig=self.which_rig)
            
            # Ask user to annotate
            dic_electrode, coords_electrode, rois_img_coord_dict = \
                img_aligner.draw_on_images_wrapper_2(
                    dic_electrode, 
                    fluor, 
                    date + " " + rec_id + " ",
                    roi_layer_files,
                    brush_size=self.brush_size)

            # Visualize electrode
            dcs = self._visualize_electrode(dic_electrode, coords_electrode, img_aligner)

            # Visualize barrel ROIs
            roi_coords = self._visualize_rois(rois_img_coord_dict, img_aligner, dcs)

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


class MaxSNRROIAnnotator(BaseROIAnnotator):
    """Annotator for 5x5 Maximal SNR ROI identification."""
    
    def __init__(self, data_dir, brush_size=4, skip_existing=False, 
                 output_keyword="roi_annotator", date_format='yyyy-mm-dd', 
                 camera_program='default', which_rig='old', 
                 rois_files_to_choose=(), verbose=False):
        super().__init__(data_dir, brush_size, skip_existing, output_keyword, 
                         date_format, camera_program, which_rig, 
                         rois_files_to_choose, verbose)
    
    def _process_single_location(self, image_data, slic_id, loc_id, output_dir, 
                                 already_drawn_slic_loc, date, rec_id):
        """Process a single location for 5x5 Maximal SNR annotation."""
        # TODO: Implement 5x5 Maximal SNR annotation logic
        pass