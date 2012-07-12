#!/usr/bin/env python
# -*- coding: utf-8 -*-


import cv
import sys
import numpy



#############################################################################
#MODIFY DEFINES BELOW
#############################################################################

THRESHOLD_VALUE = 81
MAX_THRESHOLD_IMAGE_VALUE = 255

ERODER_PATTERN_SIZE = 2
DILATE_PATTERN_SIZE = 2

#THRESHOLD_TYPE = cv.CV_THRESH_BINARY
#THRESHOLD_TYPE = cv.CV_THRESH_BINARY_INV
THRESHOLD_TYPE = cv.CV_THRESH_OTSU
#THRESHOLD_TYPE = cv.CV_THRESH_TOZERO
#THRESHOLD_TYPE = cv.CV_THRESH_TOZERO_INV
#THRESHOLD_TYPE = cv.CV_THRESH_TRUNC

#cv.CV_THRESH_BINARY      cv.CV_THRESH_OTSU        cv.CV_THRESH_TRUNC
#cv.CV_THRESH_BINARY_INV  cv.CV_THRESH_TOZERO
#cv.CV_THRESH_MASK        cv.CV_THRESH_TOZERO_INV





#filter defines
MINIMAL_NR_OF_POINTS_PER_CELL_FILTER_VALUE = 7
MINIMAL_DEVIATION_OF_CELL_ASPECT_RATIO_IN_PERCENT = 30




#############################################################################




class Point(object):
    """ simple point class to represent a point in a image
    """


    def __init__(self, y, x):
        self.y = y
        self.x = x




class CellObject(object):
    """ cell class represents a cell in a image
    """


    def __init__(self):
        self.point_list = []



    def add_point(self, point):
        self.point_list.append(point)



    def get_emphasis(self):
        x_min, x_max = self.get_point_x_min_max()
        y_min, y_max = self.get_point_y_min_max()

        emphasis_point = Point(0,0)
        emphasis_point.x = x_min + (x_max - x_min) / 2
        emphasis_point.y = y_min + (y_max - y_min) / 2

        return emphasis_point



    def get_point_x_min_max(self):
        x_min = 999999999999999999999999999999999999999999999999999999999999999999999999999999;
        x_max = 0;

        for point in self.point_list:
            if(point.x < x_min):
                x_min = point.x
            if(point.x > x_max):
                x_max = point.x
        return (x_min, x_max)



    def get_point_y_min_max(self):
        y_min = 999999999999999999999999999999999999999999999999999999999999999999999999999999;
        y_max = 0;

        for point in self.point_list:
            if(point.y < y_min):
                y_min = point.y
            if(point.y > y_max):
                y_max = point.y
        return (y_min, y_max)



    def get_nr_of_points(self):
        return len(self.point_list)



    def get_point_by_index(self, index):
        return self.point_list[index]



    def get_bounding_box(self):
        x_min, x_max = self.get_point_x_min_max()
        y_min, y_max = self.get_point_y_min_max()

        width = abs(x_min - x_max)
        height = abs(y_min - y_max)

        return (x_min, y_min, width, height)




class CellAnalyzer(object):
    """ class to analyze images and find interesting cells with filtering
    """


    def __init__(self):
        print "[i] hello from cell analyzer object"



    def load_image(self, image_path, image_type):
        try:
            return cv.LoadImageM(image_path, image_type)
        except:
            print '[!] cant load image!'
            sys.exit(2)



    def load_image_color(self, image_path):
        print '[i] load color image'
        return self.load_image(image_path, cv.CV_LOAD_IMAGE_COLOR)



    def load_image_gray(self, image_path):
        print '[i] load gray image'
        return self.load_image(image_path, cv.CV_LOAD_IMAGE_GRAYSCALE)



    def filter_erode(self, threshold_image):
        print '[i] erode filter'
        erode_threshold_image = cv.CreateImage(cv.GetSize(threshold_image), cv.IPL_DEPTH_8U, cv.CV_8UC1)
        cv.Erode(threshold_image, erode_threshold_image, None, ERODER_PATTERN_SIZE)
        return erode_threshold_image



    def filter_dilate(self, threshold_image):
        print '[i] dilate filter'
        dilate_threshold_image = cv.CreateImage(cv.GetSize(threshold_image), cv.IPL_DEPTH_8U, cv.CV_8UC1)
        cv.Dilate(threshold_image, dilate_threshold_image, None, DILATE_PATTERN_SIZE)
        return dilate_threshold_image



    def calc_threshold_image(self, src_gray_image):
        print '[i] calc threshold image'
        threshold_image = cv.CreateImage(cv.GetSize(src_gray_image), cv.IPL_DEPTH_8U, cv.CV_8UC1)

        #Threshold(src, dst, threshold, maxValue, thresholdType) → None
        cv.Threshold(src_gray_image, threshold_image, THRESHOLD_VALUE, MAX_THRESHOLD_IMAGE_VALUE, THRESHOLD_TYPE)
        return threshold_image



    def calc_horizontal_histogram(self, threshold_image):
        print '[i] calc horizontal histogram'
        horizontal_histogram_image = cv.CreateMat(threshold_image.height, threshold_image.width, cv.CV_8UC1)
        hist_array = numpy.zeros(threshold_image.width)

        #calculate histogram
        for height in range(0, threshold_image.height):
            for width in range(0, threshold_image.width):
                if cv.Get2D(threshold_image, height, width)[0] == MAX_THRESHOLD_IMAGE_VALUE:
                    hist_array[width] += 1

        #create histogram image
        cv.SetZero(horizontal_histogram_image)
        for width in range(0, horizontal_histogram_image.width):
            for i in range(int(hist_array[width])):
                cv.Set2D(horizontal_histogram_image, horizontal_histogram_image.height - i -1, width, MAX_THRESHOLD_IMAGE_VALUE)

        arraySum = 0
        for i in range(len(hist_array)):
            arraySum += hist_array[i]

        return (horizontal_histogram_image, hist_array)



    def __find_neighbors(self, height, width, threshold_image, cell_mark_map, cell_object):

        if (cv.Get2D(threshold_image, height, width)[0] == MAX_THRESHOLD_IMAGE_VALUE):
            cell_mark_map[height][width] = 1
            cell_object.add_point(Point(height, width))
        else:
            return

        print '\n[DEBUG] check interesting pixel position (height %d width %d) in %s function...' % (height, width, sys._getframe().f_code.co_name)
        raw_input( "[DEBUG] press key to continue" )

        #down
        if (height < (threshold_image.height - 1) and cell_mark_map[height + 1][width] == 0):
            print '[DEBUG] go DOWN to pixel position (height %d width %d)...' % (height + 1, width)
            self.__find_neighbors(height + 1, width, threshold_image, cell_mark_map, cell_object)

        #right
        if (width < (threshold_image.width - 1) and cell_mark_map[height][width + 1] == 0):
            print '[DEBUG] go RIGHT to pixel position (height %d width %d)...' % (height, width + 1)
            self.__find_neighbors(height, width + 1, threshold_image, cell_mark_map, cell_object)

        #up
        if (height > 0 and cell_mark_map[height - 1][width] == 0):
            print '[DEBUG] go UP to pixel position (height %d width %d)...' % (height - 1, width)
            self.__find_neighbors(height - 1, width, threshold_image, cell_mark_map, cell_object)



    def find_cells_neighbor_alg(self, threshold_image):
        print '[i] try to find cells in image (neighbor alg)'

        cell_object_list = []
        #cell_mark_map = numpy.zeros((threshold_image.height,threshold_image.width))
        cell_mark_map =  [[0 for width in range(threshold_image.width)] for height in range(threshold_image.height)]

        for width in range(0, threshold_image.width):
            for height in range(0, threshold_image.height):
                if cell_mark_map[height][width] == 1:
                    #print "continue, already marked in object!"
                    continue

                cell_object = CellObject()
                self.__find_neighbors(height, width, threshold_image, cell_mark_map, cell_object)


                if (cell_object.get_nr_of_points()):
                    #print "-> found object with %d points!" % cell_object.get_nr_of_points()

                    cell_object_list.append(cell_object)

        return cell_object_list



    def filter_cells_shape(self, possible_cell_list):
        print '[i] filter cells by shape (circle)'

        filtered_object_list = []
        for possible_cell in possible_cell_list:
            x_pos, y_pos, width, height = possible_cell.get_bounding_box()

            if ((width - height) < 0):
                ratio = float(width) / height
            else:
                ratio = float(height) / width

            if ((100 - ratio * 100) < MINIMAL_DEVIATION_OF_CELL_ASPECT_RATIO_IN_PERCENT):
                filtered_object_list.append(possible_cell)

        print ' -> nr of dropped cells by size shape filter (%s percent cell aspect ratio deviation): %d' % (MINIMAL_DEVIATION_OF_CELL_ASPECT_RATIO_IN_PERCENT, (len(possible_cell_list) - len(filtered_object_list)))
        return filtered_object_list



    def filter_cells_size(self, possible_cell_list):
        print '[i] filter cells by size'

        filtered_object_list = []
        for possible_cell in possible_cell_list:
            if (possible_cell.get_nr_of_points() >= MINIMAL_NR_OF_POINTS_PER_CELL_FILTER_VALUE):
                filtered_object_list.append(possible_cell)

        print ' -> nr of dropped cells by size filter: %d' % (len(possible_cell_list) - len(filtered_object_list))
        return filtered_object_list



    def mark_cells_in_image(self, cell_list, color_image, color):
        print '[i] mark objects in image'

        for cell in cell_list:
            for point_index in range(cell.get_nr_of_points()):
                point = cell.get_point_by_index(point_index)
                cv.Set2D(color_image, point.y, point.x, color)



    def draw_cell_bounding_box_in_image(self, cell_list, color_image, color):
        print '[i] draw bounding box for each cell in image'

        for cell in cell_list:
            x_pos, y_pos, width, height = cell.get_bounding_box()

            #horizontal bounding box lines
            for width_index in range(x_pos, x_pos + width):
                cv.Set2D(color_image, y_pos, width_index, color)
                cv.Set2D(color_image, y_pos + height, width_index, color)

            #vertical bounding box lines
            for height_index in range(y_pos, y_pos + height):
                cv.Set2D(color_image, height_index, x_pos, color)
                cv.Set2D(color_image, height_index, x_pos + width, color)



    def process_image(self, image_path):
        print '[i] process image %s...' % (image_path)


        gray_image = self.load_image_gray(image_path)
        color_image = self.load_image_color(image_path)
        threshold_image = self.calc_threshold_image(gray_image)
        #horizontal_histogram_image, horizontal_histogram_array = self.calc_horizontal_histogram(threshold_image)

        #erode_threshold_image = self.filter_erode(threshold_image)
        #dilate_threshold_image = self.filter_dilate(threshold_image)

        possible_cell_list = []
        possible_cell_list = self.find_cells_neighbor_alg(threshold_image)
        if(len(possible_cell_list) == 0):
            print "[!] no possible cell found in image..."
            #return
        else:
            print "[i] %d possible cells found in image" % len(possible_cell_list)
            for cell in possible_cell_list:
                print " -> nr of points in object: %d" % cell.get_nr_of_points()
                #for point in range(0, obj.get_nr_of_points()):
                    #print "    x: %d | y: %d" % (obj.get_point_by_index(point).x, obj.get_point_by_index(point).y)


        #mark all recognized cells with a bounding box
        self.draw_cell_bounding_box_in_image(possible_cell_list, color_image, (0, 0, 255))


        #filter cells
        possible_cell_list = self.filter_cells_size(possible_cell_list)
        possible_cell_list = self.filter_cells_shape(possible_cell_list)


        #mark interesting cells
        self.mark_cells_in_image(possible_cell_list, color_image, (255, 0, 0))



        cv.ShowImage('gray_image', gray_image)
        cv.SaveImage('gray_image.png', gray_image)

        cv.ShowImage('threshold_image', threshold_image);
        cv.SaveImage('threshold_image.png', threshold_image)

        cv.ShowImage('color_image', color_image)
        cv.SaveImage('color_image.png', color_image)

        #cv.ShowImage('horizontal_histogram_image', horizontal_histogram_image);
        #cv.ShowImage('erode_threshold_image', erode_threshold_image)
        #cv.ShowImage('dilate_threshold_image', dilate_threshold_image)



        print '\n\n[i] final report:'
        print ' * %d interesting cells found in image (filtered) ' % len(possible_cell_list)



        print '\n\n[i] press any key to exit...'
        cv.WaitKey(0)







def print_help():
    print '[i] help:'
    print ' * call application with a image name as parameter'
    print ' * %s <path_to_image>\n' % (sys.argv[0])



if __name__ == "__main__":

    if (len(sys.argv) != 2):
        print '[!] give me path to an image to analyze!'
        print_help()
        sys.exit(1)

    image_name = sys.argv[1]

    cell_analyzer = CellAnalyzer()
    cell_analyzer.process_image(image_name)


    sys.exit(0)

