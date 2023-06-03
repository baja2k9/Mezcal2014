#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from pylab import *
import os
from os import system, listdir
from math import log
from scipy import average, std, median, random, zeros, clip, array, append, mean
from scipy import histogram, optimize, sqrt, pi, exp, where, split
from scipy import sum, std, resize, size, isnan
from scipy import optimize, shape, indices, arange, ravel, sqrt
from scipy import loadtxt, savetxt, sort
from scipy import interpolate
from numpy import polyfit, poly1d
import pyfits
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import operator
#################################################################################################
class AUTOFOCO():

    image_dir = "/imagenes/autofoco/"
    pinholes_filename = "/imagenes/autofoco/pinhole_locations.txt"


    #focus_positions = loadtxt("/imagenes/autofoco/focus_positions.txt")
    focus_positions=[]
    im_half_width = 50
    sex_bin = "/usr/local/bin/sex"

    raw_red_color = loadtxt("focus/red_mapping.txt")
    raw_green_color = loadtxt("focus/green_mapping.txt")
    raw_blue_color = loadtxt("focus/blue_mapping.txt")

    red_function = interpolate.interp1d(raw_red_color[:,0], raw_red_color[:,1], kind="linear")
    green_function = interpolate.interp1d(raw_green_color[:,0], raw_green_color[:,1], kind="linear")
    blue_function = interpolate.interp1d(raw_blue_color[:,0], raw_blue_color[:,1], kind="linear")
#################################################################################################
    def __init__(self):
        print "Clase AutoFoco "

#################################################################################################
    def moffat_residuals(self,params, z, x, y):
        central_height, center_x, center_y, alpha, beta = params
        r2 = (x - center_x)**2 + (y - center_y)**2
        err = z - (central_height * (1 + (r2/(alpha**2)))**(-beta))
        return err

#################################################################################################
    def fit_moffat(self,center_x, center_y, z, x, y):
        """Returns (central_height, center_x, center_y, alpha, beta
        the moffat parameters of a 2D distribution found by a fit"""

        input_params = [2200.0, center_x, center_y, 2.0, 2.0]
        fit_params, success = optimize.leastsq(self.moffat_residuals, input_params,
            args=(z, x, y), maxfev=10000)
        return fit_params
#################################################################################################
    def make_color(self,val):
        val *= 255
        color = [self.red_function(val)/255., self.green_function(val)/255., self.blue_function(val)/255., 1.0]
        return color
#################################################################################################
    def test_foco(self):
        print 'Test autofoco'

        im_list = listdir(self.image_dir+'/cropped_images')
        image_list = []
        for name in im_list:
            if name[0] != ".": image_list.append(name)
        image_array_sorted = sort(array(image_list))

        pinhole_locations = loadtxt(self.pinholes_filename, dtype=int)

        if len(pinhole_locations.shape) == 1:
            pinhole_locations = array([pinhole_locations])

        final_data = []
        for pinhole in pinhole_locations:
            final_data.append([pinhole[0], [], [], []])

        fig = plt.figure(figsize=(6, 6))
        ax1 = fig.add_subplot(1,1,1)

        color_nums = linspace(0.05, 0.95, len(image_array_sorted)*len(pinhole_locations))
        color_num = 0
        max_central_height = 100
        for image_name in image_array_sorted:
            full_image_name = self.image_dir + '/cropped_images/' + image_name
            print 'procesando :',full_image_name
            hdulist = pyfits.open(full_image_name)
            full_image_data = hdulist[0].data
            hdulist.close()
            for pinhole in pinhole_locations:
                x_cen = pinhole[1]
                y_cen = pinhole[2]

                sub_image_data = full_image_data[y_cen-self.im_half_width:y_cen+self.im_half_width,x_cen-self.im_half_width:x_cen+self.im_half_width]
                submask_data = sub_image_data - median(sub_image_data)

                sub_image_name = "pin_" + str(pinhole[0]) + "_" + image_name
                sub_image_name='/tmp/'+sub_image_name

                output_hdu = pyfits.PrimaryHDU(submask_data)
                output_hdulist = pyfits.HDUList([output_hdu])
                output_hdulist.writeto(sub_image_name)

                z = []
                x = []
                y = []
                x_y = []
                r = []
                for i in range(len(submask_data)):
                    i_pixel = i + 0
                    for j in range(len(submask_data[i])):
                        if submask_data[i][j] != 0:
                            j_pixel = j + 0
                            x.append(j_pixel)
                            y.append(i_pixel)
                            x_y.append([j_pixel, i_pixel])
                            z.append(submask_data[i][j])

                peak_pixel = where(submask_data == submask_data.max())
                center_x = peak_pixel[1][0]
                center_y = peak_pixel[0][0]

                fit_params = self.fit_moffat(center_x, center_y, z, x, y)
                central_height, center_x, center_y, alpha, beta = fit_params
                fwhm_moffat = 2*alpha*sqrt(2**(1/beta) - 1)


                rad = sqrt( (x-center_x)**2 + (y-center_y)**2 )
                if fwhm_moffat > 1:
                    h = where( rad < 1.5 * fwhm_moffat )
                else:
                    h = where( rad < 5 )
                z = array(z)[h]
                x = array(x)[h]
                y = array(y)[h]

                fit_params = self.fit_moffat(center_x, center_y, z, x, y)

                central_height, center_x, center_y, alpha, beta = fit_params
                fwhm_moffat = 2*alpha*sqrt(2**(1/beta) - 1)


                if max(z) > max_central_height:
                     max_central_height = max(z)

                r2 = (x - center_x)**2 + (y - center_y)**2
                fit_vals = (central_height * (1 + (r2/(alpha**2)))**(-beta))

                plot_fit = []
                for n in range(len(r2)):
                    plot_fit.append([r2[n], fit_vals[n], z[n]])

                plot_fit_sorted = sorted(plot_fit, key=operator.itemgetter(0))
                plot_fit_array = array(plot_fit_sorted)

                ax1.plot(plot_fit_array[:,0], plot_fit_array[:,2], linestyle="none", marker="o", color=self.make_color(color_nums[color_num]), alpha=0.7 )

                ax1.plot(plot_fit_array[:,0], plot_fit_array[:,1], linestyle="solid", marker="", color=self.make_color(color_nums[color_num]), alpha=0.7 )

                color_num += 1

                for coordinate in x_y:
                    r.append(sqrt((coordinate[0]-center_x)**2 +
                        (coordinate[1]-center_y)**2))
                fit_data = []

                fwhm_moffat = 2*alpha*sqrt(2**(1/beta) - 1)

                system(self.sex_bin + " " + sub_image_name + " -c focus/enrique_focus.sex")
                sex_file = file("photometry_cat.txt", "r")
                sex_fwhm_data = []
                photometry_data = []
                for line in sex_file:
                    photometry_data.append(line.split())
                    sex_fwhm_data.append(float(line.split()[3]))
                sex_file.close()

                system("rm " + sub_image_name)

                sex_fwhm = -1.0
                for entry in photometry_data:
                    if (abs(float(entry[0]) - center_x - 1) < 25) and (abs(float(entry[1]) - center_y - 1) < 25):
                        sex_fwhm = float(entry[3])

                print "pin_" + str(pinhole[0]) + "_" + image_name
                print "\t fwhm moffat= " + str(fwhm_moffat)
                print "\t sex fwhm= " + str(sex_fwhm)
                # print photometry_data

                final_data[pinhole[0]-1][1].append(image_name)
                final_data[pinhole[0]-1][2].append(fwhm_moffat)
                final_data[pinhole[0]-1][3].append(sex_fwhm)


        system("rm photometry_cat.txt")

        ax1.set_xlim(0,7)
        ax1.set_ylim(0, max_central_height*1.1)
        # ax1.set_ylim(0, 1500)
        ax1.set_xlabel("Radius")
        ax1.set_ylabel("Flux Value")
        canvas = FigureCanvas(fig)
        canvas.print_figure("moffat_fits.pdf", dpi=144)
        close("all")


        fig = plt.figure(figsize=(6, 10))
        ax1 = fig.add_subplot(2,1,1)
        ax2 = fig.add_subplot(2,1,2)

        color_nums = linspace(0.01, 0.99, len(final_data))
        color_num = 0
        focus_position_list = self.focus_positions
        for pinhole in final_data:
            moffat_fwhm_list = pinhole[2]
            sex_fwhm_list = pinhole[3]
            image_list = pinhole[1]

            focus_position_list_moffat = []
            moffat_fwhm_list_vetted = []
            focus_position_list_sex = []
            sex_fwhm_list_vetted = []

            for n in range(len(moffat_fwhm_list)):
                if (moffat_fwhm_list[n] < 50) and (moffat_fwhm_list[n] > 0.3):
                    focus_position_list_moffat.append(focus_position_list[n])
                    moffat_fwhm_list_vetted.append(moffat_fwhm_list[n])

            for n in range(len(sex_fwhm_list)):
                if (sex_fwhm_list[n] < 100) and (sex_fwhm_list[n] > 0.3):
                    focus_position_list_sex.append(focus_position_list[n])
                    sex_fwhm_list_vetted.append(sex_fwhm_list[n])

            #re-sort the focus position and fwhm lists
            moffat_combined_list = []
            for n in range(len(focus_position_list_moffat)):
                moffat_combined_list.append([focus_position_list_moffat[n], moffat_fwhm_list_vetted[n]])
            moffat_combined_list = sorted(moffat_combined_list)
            focus_position_list_moffat = list(array(moffat_combined_list)[:,0])
            moffat_fwhm_list_vetted = list(array(moffat_combined_list)[:,1])

            sex_combined_list = []
            for n in range(len(focus_position_list_sex)):
                sex_combined_list.append([focus_position_list_sex[n], sex_fwhm_list_vetted[n]])
            sex_combined_list = sorted(sex_combined_list)
            focus_position_list_sex = list(array(sex_combined_list)[:,0])
            sex_fwhm_list_vetted = list(array(sex_combined_list)[:,1])

            fit_xs = linspace(min(focus_position_list), max(focus_position_list), 100)
            do_fit_moffat = False
            if len(moffat_fwhm_list_vetted) > 3: do_fit_moffat = True
            do_fit_sex = False
            if len(sex_fwhm_list_vetted) > 3: do_fit_sex = True

            if do_fit_moffat:
                quad_params_moffat = polyfit(focus_position_list_moffat, moffat_fwhm_list_vetted, 2)
                quad_fit_moffat = poly1d(quad_params_moffat)
                best_focus_position_moffat = -1*quad_params_moffat[1] / (2*quad_params_moffat[0])
                moffat_focus_string = "%.3f" % round(best_focus_position_moffat, 3)
                print "Best Moffat focus= ",moffat_focus_string

            if do_fit_sex:
                quad_params_sex = polyfit(focus_position_list_sex, sex_fwhm_list_vetted, 2)
                quad_fit_sex = poly1d(quad_params_sex)
                best_focus_position_sex = -1*quad_params_sex[1] / (2*quad_params_sex[0])
                sex_focus_string = "%.3f" % round(best_focus_position_sex, 3)
                print "Best sex focus= ",sex_focus_string



            ax1.plot(focus_position_list_moffat, moffat_fwhm_list_vetted,
                linestyle = "none", marker="o",
                color=self.make_color(color_nums[color_num]), alpha=0.7,)

            if do_fit_moffat:
                ax1.plot(fit_xs, quad_fit_moffat(fit_xs),
                    linestyle = "solid", marker="",
                    color=self.make_color(color_nums[color_num]), alpha=0.7,
                    label = "#" + str(pinhole[0]) + ", fit= " + moffat_focus_string )


            ax2.plot(focus_position_list_sex, sex_fwhm_list_vetted,
                linestyle = "none", marker="o",
                color=self.make_color(color_nums[color_num]), alpha=0.7)
            if do_fit_sex:
                ax2.plot(fit_xs, quad_fit_sex(fit_xs),
                    linestyle = "dashed", marker="",
                    color=self.make_color(color_nums[color_num]), alpha=0.7,
                    label = "#" + str(pinhole[0]) + ", fit= " + sex_focus_string )

            color_num += 1

        ax1.legend()
        ax1.set_xlabel("Focus Position")
        ax1.set_ylabel("FWHM Measure (moffat)")
        #ax1.set_ylim(0, 4)

        ax2.legend()
        ax2.set_xlabel("Focus Position")
        ax2.set_ylabel("FWHM Measure (sex)")
        #ax2.set_ylim(0, 4)
        canvas = FigureCanvas(fig)
        canvas.print_figure("focus_plot.pdf", dpi=144)

        close("all")
#################################################################################################
    def crop_image(self,image_name):
        #centra las estrella en las imagenes
        self.im_half_width = 75


        full_image_name =os.path.join(self.image_dir,image_name)

        hdulist = pyfits.open(full_image_name)
        full_image_data = hdulist[0].data
        hdulist.close()

        system(self.sex_bin + " " + full_image_name + " -c focus/enrique_focus.sex -CHECKIMAGE_NAME object_images/obj" + image_name)

        sex_file = file("photometry_cat.txt", "r")
        sex_fwhm_data = []
        photometry_data = []
        x_cen = []
        y_cen = []
        for line in sex_file:
            x_cen.append(int(round(float(line.split()[0]))))
            y_cen.append(int(round(float(line.split()[1]))))
        sex_file.close()

        x_cen = mean(x_cen)
        y_cen = mean(y_cen)

        sub_image_data = full_image_data[y_cen-self.im_half_width:y_cen+self.im_half_width,x_cen-self.im_half_width:x_cen+self.im_half_width]

        submask_data = sub_image_data - median(sub_image_data)

        #sub_image_name = "cropped_images/cropped_" + image_name
        sub_image_name = os.path.join(self.image_dir+"cropped_images",'cropped_'+image_name)

        output_hdu = pyfits.PrimaryHDU(submask_data)
        output_hdulist = pyfits.HDUList([output_hdu])
        output_hdulist.writeto(sub_image_name)

        print sub_image_name, x_cen, y_cen

        self.im_half_width = 50
#################################################################################################

#################################################################################################
