from ramanbox.labeler.labeler_app import LablerApp
import os
import tkinter as tk

if __name__ == "__main__":
    unlabeled_data_dir = os.path.join('data', 'unlabeled_data')
    labeled_data_dir = os.path.join('data', 'labeled_data')
    root = tk.Tk()
    inputFolder = labeled_data_dir
    outputFolder = labeled_data_dir
    app = LablerApp(master=root, inputFolderName=inputFolder, outputFolderName=outputFolder)
    app.mainloop()
