# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 12:22:25 2020

@author: dexter
"""
from src.labeler.image_generator import *

import os.path
from os import path
from collections import OrderedDict
from pathlib import Path


class LabelerController():

    def __init__(self, inputDirectory, outputDirectory='', spectrumPicFileName='test.nc.png'):
        self.inputDirectory = inputDirectory
        self.outputDirectory = outputDirectory
        self.spectrumPicFileName = spectrumPicFileName
        self.patientDict = OrderedDict()
        self.labelsDict = OrderedDict()
        self.load_patient_data()  # makes self.totalIndexer
        self.generateImage()

    def generateImage(self):
        pName, spotIndex, spectrumIndex = self.get_current_info()
        wavenumber = self.patientDict[pName].wavenumbers
        spectrumData = self.patientDict[pName].corrected[spotIndex, spectrumIndex, :]
        tmpSpectrumImageMaker = SpectrumImageMaker(wavenumber, spectrumData, filename=self.spectrumPicFileName)
        tmpSpectrumImageMaker.generate_image()

    def generate_filename(self, pName):
        filename = os.path.join(self.outputDirectory, pName + '_array.npy')
        return filename

    def saveLabels(self):
        Path(self.outputDirectory).mkdir(parents=True, exist_ok=True)
        pName, spotIndex, spectrumIndex = self.get_current_info()
        filename = self.generate_filename(pName)
        np.save(filename, self.labelsDict[pName])

    def load_patient_data(self):
        globCmd = os.path.join(self.inputDirectory, "*.nc")
        fileList = glob.glob(globCmd)
        patientSizeDict = OrderedDict()

        for f in fileList:
            key = f.split("netcdf/")[1]
            key = key.split(".nc")[0]
            newPatient = Patient_Data(f)
            self.patientDict[key] = newPatient
            patientSizeDict[key] = newPatient.data.shape[0:2]

            filename = self.generate_filename(key)
            if (path.exists(filename)):
                self.labelsDict[key] = np.load(filename)
            else:
                self.labelsDict[key] = np.ones((newPatient.data.shape[0:2])) * -1

        self.totalIndexer = TotalIndexer(patientSizeDict)
        self.totalIndexer.find_start(self)

    def good_click(self):
        self.click(1)

    def bad_click(self):
        self.click(0)

    def maybe_click(self):
        self.click(2)

    def back_click(self):
        self.totalIndexer.back()
        self.saveLabels()
        self.generateImage()

    def get_current_info(self):
        pName = self.totalIndexer.get_patient_name()
        spotIndex = self.totalIndexer.get_spot_index()
        spectrumIndex = self.totalIndexer.get_spectrum_index()
        return pName, spotIndex, spectrumIndex

    def click(self, value):
        pName, spotIndex, spectrumIndex = self.get_current_info()
        self.labelsDict[pName][spotIndex, spectrumIndex] = value
        self.saveLabels()
        self.totalIndexer.forward()
        self.generateImage()

    def get_spectrum_assignment(self):
        pName, spotIndex, spectrumIndex = self.get_current_info()
        return self.labelsDict[pName][spotIndex, spectrumIndex]

    def get_spectrum_label_array(self):
        pName, spotIndex, spectrumIndex = self.get_current_info()
        return self.labelsDict[pName]
