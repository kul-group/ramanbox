from src.labeler.labeler_app import LablerApp
import os
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    inputFolder = os.path.join(os.getcwd(), 'data')
    outputFolder = os.path.join(os.getcwd(), 'data')
    app = LablerApp(master=root, inputFolderName=inputFolder, outputFolderName=outputFolder)
    app.mainloop()
