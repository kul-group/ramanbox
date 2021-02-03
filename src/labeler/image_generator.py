# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 12:16:53 2020

@author: dexter
"""
import matplotlib.pyplot as plt


class SpectrumImageMaker():
    # this class is responsible for converting numpy arrays to images

    def __init__(self, wavenumber, spectrum_data, filename="output/currentSpectrum.png"):
        self.wavenumber_data = wavenumber
        self.spectrum_data = spectrum_data
        self.filename = filename

    def generate_image(self):
        plt.ioff()
        fig = plt.figure(num=None, figsize=(10, 7.5), dpi=80, facecolor='w', edgecolor='k')
        plt.plot(self.wavenumber_data, self.spectrum_data)
        plt.xlabel("Wavenumber $(cm^{-1})$")
        plt.ylabel("Intensity")
        plt.savefig(self.filename)
        plt.close(fig)

