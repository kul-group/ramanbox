# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 21:35:16 2020

@author: dexter
"""
import numpy as np
from collections import OrderedDict


class TotalIndexer():  # this takes an ordered dictionary
    def __init__(self, orDictPatients):
        "note that this takes a list of tuples of various  "
        indexODict = OrderedDict()
        for key, value in orDictPatients.items():
            indexODict[key] = Indexer(value)
        self.indexerIter = indexODict.items().__iter__()
        self.next_patient()
        self.complete = False

    def get_spot_index(self):
        return self.currentIndexer.get_spot_index()

    def get_spectrum_index(self):
        return self.currentIndexer.get_spectrum_index()

    def get_patient_name(self):
        return self.patientName

    def next_patient(self):
        try:
            self.patientName, self.currentIndexer = next(self.indexerIter)
        except StopIteration:
            print("Final Patient file labeled.")
            self.complete = True
            raise

    def forward(self):
        if (self.currentIndexer.complete):
            self.next_patient()
        self.currentIndexer.forward()

    def back(self):
        if (self.currentIndexer.complete):
            self.next_patient()
        self.currentIndexer.back()

    def find_start(self, controller):
        currentComplete = True  # sudo-do-while loop
        while (currentComplete):
            if (self.currentIndexer.complete):
                self.next_patient()
            labelArray = controller.get_spectrum_label_array()
            self.currentIndexer.find_start(labelArray)
            currentComplete = self.currentIndexer.complete


class Indexer():
    "this class keeps track of the current spectrum"

    def __init__(self, patientShape):
        # note about notation I is short for Index

        self.maxSpotI = patientShape[0]  # max value for a spot I
        self.maxSpectrumI = patientShape[1]
        self.maxFlattenedI = patientShape[0] * patientShape[1]

        self.currentSpot = 0
        self.currentSpectrum = 0
        self.currentFlattened = 0

        self.complete = False

    def print_current_indices(self):  # useful for testing purposes
        print("Current spot %d / %d current spectrum %d / %d current flattened %d / %d" %
              (self.currentSpot, self.maxSpotI - 1, self.currentSpectrum, self.maxSpectrumI - 1, self.currentFlattened,
               self.maxFlattenedI - 1))

    def forward(self):
        self.currentFlattened += 1
        self.calc_indices()
        # self.print_current_indices()

    def back(self):
        self.currentFlattened -= 1
        self.calc_indices()
        # self.print_current_indices()

    def save_self(self):
        pass

    def find_start(self, labelArray):
        newFlattened = -1
        j = 0
        for el in np.nditer(labelArray.flatten()):
            if (el == -1):
                newFlattened = j
                break
            j += 1
        if (newFlattened == -1):  # it was never redefined
            self.complete = True
            self.currentFlattened = self.maxFlattenedI - 1
        else:
            self.currentFlattened = newFlattened
        self.calc_indices()

    def build_from_file(self):
        pass

    def calc_indices(self):
        if (self.currentFlattened < 0):
            self.currentFlattened = 0
            return 0
        if (self.currentFlattened >= self.maxFlattenedI):
            self.complete = True
            return 0
        self.currentSpectrum = self.currentFlattened % self.maxSpectrumI
        self.currentSpot = int(self.currentFlattened / self.maxSpectrumI) % self.maxSpotI

    def get_spot_index(self):
        return self.currentSpot

    def get_spectrum_index(self):
        return self.currentSpectrum


# test.nc cases

# myIndexer = Indexer((4,8))
""" #this is a tester for find_start
sampleLabelArray = np.ones((4,8))*-1
for i in range(0,2):
    for j in range(0,8):
        sampleLabelArray[i,j]=2%(j+1)/2 #one or zero 
print(sampleLabelArray)
myIndexer.find_start(sampleLabelArray)
myIndexer.forward()
"""
"""#total indexer tester 
test.nc = OrderedDict()
test.nc['p1'] = (3,4)
test.nc['p2'] = (13,5)
test.nc['p3'] = (6,2)
test.nc['p4'] = (8,1)
#print(test.nc)
myTotalIndexer = TotalIndexer(test.nc)"""
