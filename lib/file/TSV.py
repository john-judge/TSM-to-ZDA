import csv
import numpy as np


class RegionExporter:

    def __init__(self):
        pass

    def export(self, filename, regions):
        """ Write an ImageZ regions .TSV file. Regions is a doubly-nested list of points [y,x] """
        region_names = ["Region_" + str(i) for i in range(len(regions))]
        max_pixel_count_len = max([len(r) for r in regions])
        with open(filename, 'wt') as output_file:
            tsv_writer = csv.writer(output_file, delimiter='\t')
            tsv_writer.writerow(region_names)
            for row_ct in range(max_pixel_count_len):
                row = []
                for i in range(len(regions)):
                    if row_ct < len(regions[i]):
                        row.append(regions[1][row_ct])  # x location of pixel
                        row.append(regions[0][row_ct])  # y location of pixel
                    else:
                        row.append('')
                        row.append('')
                    tsv_writer.writerow(row)