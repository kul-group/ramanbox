# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 09:06:21 2020

@author: dexter
"""
from ramanbox.labeler.label_controller import LabelController
import tkinter as tk
import os


class LablerApp(tk.Frame):
    """
    This class class runs the Tker app that visualizes the spectra for categorization
    """

    def __init__(self, master=None, inputFolderName='', outputFolderName='',
                 spectrumFileName=os.path.join("output", "currentSpectrum.png")):
        """
        Initializes the lablerApp
        """

        super().__init__(master)  # initates super constructor
        self.winfo_toplevel().title("Labeler")  # sets window title
        self.spectrumFileName = spectrumFileName  # sets spectrumFileName
        self.controler = LabelController(inputFolderName, outputFolderName, self.spectrumFileName)
        self.bind_all("<Key>", self.on_key_pressed)  # calls detect key press func

        self.master = master  # sets master input to
        self.pack()
        self.create_widgets()
        self.create_labels()
        self.update()

    def create_widgets(self):
        # adds photo to the Frame
        self.photo = tk.PhotoImage(file=self.spectrumFileName)
        self.mylabel = tk.Label(self.master, image=self.photo)
        self.mylabel.pack()

        # adds buttons (this code could be changed, but it is very readable now)
        self.good_btn = tk.Button(self, fg="blue")
        self.good_btn["text"] = "Good (1)"
        self.good_btn["command"] = self.click_good
        self.good_btn.pack(side="left")

        self.bad_btn = tk.Button(self, fg="red")
        self.bad_btn["text"] = "Bad (2)"
        self.bad_btn["command"] = self.click_bad
        self.bad_btn.pack(side="left")

        self.maybe_btn = tk.Button(self, fg="purple")
        self.maybe_btn["text"] = "Maybe (3)"
        self.maybe_btn["command"] = self.click_maybe
        self.maybe_btn.pack(side="left")

        self.back_btn = tk.Button(self)
        self.back_btn["text"] = "Back (b)"
        self.back_btn["command"] = self.click_back
        self.back_btn.pack(side="left")

        self.back_btn = tk.Button(self)
        self.back_btn["text"] = "Skip to Next Unlabeled"
        self.back_btn["command"] = self.skip_to_next_unlabeled
        self.back_btn.pack(side="left")

        self.back_btn = tk.Button(self)
        self.back_btn["text"] = "Save Labels (s)"
        self.back_btn["command"] = self.save_labels
        self.back_btn.pack(side="left")

        # adds a quit button
        self.quit = tk.Button(self, text="Quit", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="left")

    def create_labels(self):
        # labels can only display return of a StringVar object

        self.spotNumVar = tk.StringVar()
        self.spectrumNumVar = tk.StringVar()
        self.patientNameVar = tk.StringVar()
        self.spectrumLabelVar = tk.StringVar()

        # defines labelframe where spectrum, spot, patient index/name are displayed
        # these are not assigned values until later
        self.specProperties = tk.LabelFrame(self.master, text='Spectrum Properties')
        self.specProperties.pack(fill='both', expand='yes', side='bottom')

        self.spotNumLabel = tk.Label(self.specProperties, text=self.spotNumVar.get())
        self.spotNumLabel.pack(side='left')

        self.spectrumNumLabel = tk.Label(self.specProperties, text=self.spectrumNumVar.get())
        self.spectrumNumLabel.pack(side='left')

        self.patientNameLabel = tk.Label(self.specProperties, text=self.patientNameVar.get())
        self.patientNameLabel.pack(side='left')

        # Label for the label (good, bad maybe, none) assigned to the spectrum
        self.spectrumLabelLabel = tk.Label(self.specProperties, text=self.spectrumLabelVar.get())
        self.spectrumLabelLabel.pack(side='left')

    def skip_to_next_unlabeled(self):
        self.controler.skip_to_next_unlabeld_spectrum()
        self.update()

    def save_labels(self):
        self.controler.save_sample()

    def click_general(self, value):
        self.update()
        return 0  # I have no idea why this needs to be here, but it acts as a break statement

    def click_good(self):
        self.controler.assign_good_label()
        self.click_general(1)

    def click_bad(self):
        self.controler.assign_bad_label()
        self.click_general(0)

    def click_maybe(self):
        self.controler.assign_maybe_label()
        self.click_general(2)

    def click_back(self):
        self.controler.previous_spectrum()
        self.click_general(-1)

    def on_key_pressed(self, e):
        key = e.keysym
        if (key == '1'):
            self.click_good()
        if (key == '2'):
            self.click_bad()
        if (key == '3'):
            self.click_maybe()
        if (key == 'b'):
            self.click_back()
        if (key=='s'):
            self.save_labels()

    def update(self):
        pName, spotIndex, spectrumIndex = self.controler.get_current_info()
        # update image
        self.photo = tk.PhotoImage(file=self.spectrumFileName)
        self.mylabel.configure(image=self.photo)  # = tk.Label(self.master,image=self.photo)
        self.mylabel.image = self.photo

        # update spectra properties
        # set variables
        self.spotNumVar.set("Spot Number: " + str(spotIndex))
        self.spectrumNumVar.set("Spectra Number: " + str(spectrumIndex))
        self.patientNameVar.set("Patient Name: " + pName)
        self.spectrumLabelVar.set("Current Label: " + self.controler.current_spectrum.label.name)
        # set them to label values
        self.spectrumNumLabel['text'] = self.spectrumNumVar.get()
        self.spotNumLabel['text'] = self.spotNumVar.get()
        self.patientNameLabel['text'] = self.patientNameVar.get()
        self.spectrumLabelLabel['text'] = self.spectrumLabelVar.get()
