from src.labeler.labeler_app import LablerApp
import os
import tkinter as tk
import git

if __name__ == "__main__":
    repo = git.Repo('.', search_parent_directories=True)
    root_dir = repo.working_tree_dir
    unlabeled_data_dir = os.path.join(root_dir, 'data', 'unlabeled_data')
    labeled_data_dir = os.path.join(root_dir, 'data', 'labeled_data')

    root = tk.Tk()
    inputFolder = labeled_data_dir
    outputFolder = labeled_data_dir
    app = LablerApp(master=root, inputFolderName=inputFolder, outputFolderName=outputFolder)
    app.mainloop()
