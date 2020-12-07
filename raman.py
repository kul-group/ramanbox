# standard library imports
import os

# related third party imports
# standard anaconda libs
import glob as glob
import matplotlib.pyplot as plt
import numpy as np
from scipy import sparse
from scipy.sparse import csc_matrix, eye, diags
from scipy.sparse.linalg import spsolve
from abc import ABC
from abc import abstractmethod, abstractproperty
# additional libs
from typing import Dict, List, Tuple
import xarray as xr


class RamanInputParser(ABC):
    """
    This is an abstract base class for a Raman Input Parser.
    It allows this code to be tailored to the unique file formats that
    one might encounter when loading in Raman spectra.
    """
    @property
    @abstractmethod
    def spectrum_length(self) -> int:
        pass

    @abstractmethod
    def get_metadata_and_spectrum(self, filepath) -> Tuple[Dict, List[List[float]]]:
        pass


class TatuRamanParser(RamanInputParser):
    """
    This is a specific RamanInputParser that inherits from the abstract base class.
    This practice of inheritance ensures that it impliments the correct methods
    to work with the RamanSpot Class
    """
    def __init__(self):
        self.spectrum_length = 1024

    def get_metadata_and_spectrum(self, filepath):
        """

        :param filepath: A filepath to a text file containing Raman data
        :return: metadata in a dictionary and a list of different spectra in a datalist
        """
        with open(filepath) as infile:  # opens file and then stores
            metadata = self.get_metadata(infile)
            datalist = self.get_file_spectra(infile)
        return metadata, datalist

    @staticmethod
    def get_metadata(file_iterator):
        """
        Takes a file_iterator and parses out the metadata
        :param file_iterator: A fileiterator to iterate through (has side effects)
        :return: A dictionary containing the metadata
        """
        metadata_values = {}  # creates dictionary to return
        for line in file_iterator:
            if (line == "\n"):  # determines when metadata ends and spectra data begins
                return metadata_values
            data_name = []
            data_values = []
            colon_encountered = False
            iterline = iter(line)
            for c in iterline:
                if not colon_encountered and c == ":":
                    colon_encountered = True
                    c = next(iterline)
                    while c == " ":
                        c = next(iterline)  # iterates through all whitespace between key and date
                if not colon_encountered:  # if you are iterating through the key
                    data_name.append(c)
                    continue
                else:
                    if c == "\n":  # skip newline characters
                        continue
                    data_values.append(c)
                    continue

            metadata_values["".join(data_name)] = "".join(data_values)  # adds name and value to a dictionary
        return metadata_values

    def get_file_spectra(self, file_iterator):
        """

        :param file_iterator: A file iterator where the metadata has been skipped
        :return: a list of lists containing spectra
        """
        i = 0
        data_list = []
        data_array = np.zeros((1024, 2), dtype=float)  # this is for storing the data

        for line in file_iterator:
            if (line == "\n"):  # skips new line characters at the begining of the file
                continue
            splt_line = line.split("	")
            if (len(splt_line) != 3):  # skips nondata
                print(line)
                continue
                # if you go through one whole dataset  if(len(wavelength_list)!=0 and wavelength<wavelength_list[-1]):
                # #if the wavelengths go back to the start point, restart things
            if i >= self.spectrum_length:
                data_list.append(data_array)
                data_array = np.zeros((1024, 2), dtype=float)  # clears data array for next round
                i = 0
            wavelength = float(splt_line[0])
            intensity = float(splt_line[1])
            data_array[i, 0] = wavelength
            data_array[i, 1] = intensity

            i += 1
        return data_list


class RamanSpot:
    """
    Raman spot is a class which represents the collection of spectra in a Raman file
    Each spot in a SERS spectra has multiple spectra associated with it.
    """

    def __init__(self, input_filepath, ramam_input_parser=TatuRamanParser):  # initalizes a Raman object from a text file
        """
        :param filename: The name of the text file to turn into a Raman Spot object
        :param data_dir: The directory where the text file is stored
        """
        self.input_filepath = input_filepath
        self.ramam_input_parser_obj = ramam_input_parser()
        self.metadata_values, self.data_list = \
            self.ramam_input_parser_obj.get_metadata_and_spectrum(self.input_filepath)


class Raman_Folder:
    """
    A raman folder contains multiple text files, of Raman spots. Each folder typically represents a
    single patient. This code loads in all of the spot files in a single folder and then saves the
    data in an xarray format, which can be loaded in by a patient data function
    """
    def __init__(self, data_dir, folder_name, laser_wavelength=785):

        self.folder_name = folder_name
        glob_cmd = os.path.join(data_dir, folder_name, "*.txt")
        self.file_list = glob.glob(glob_cmd)
        self.raman_spot_dict = {}
        self.laser_wavelength = laser_wavelength  # nm
        for filepath in self.file_list:
            spot_index = filepath.find("SPOT", 0, len(filepath))
            key = filepath[spot_index + 4:spot_index + 7]
            self.raman_spot_dict[key] = RamanSpot(filepath)

        self.xrdata = None
        self.build_xarray()

    def build_xarray(self):
        """
        Builds an xarray object containing all of the spectra in a spot
        :return:
        """

        spot_name_dict = {}
        spot_name_list = []  # this is a list containing all of the names of the spots scanned

        # find the dimensions of 3d array
        max_spectra_num = 0  # this block finds the max number of spectra in a spot (usually 19 or 20)
        for value in self.raman_spot_dict.values():
            tmp_spectra_num = len(value.data_list)

            if tmp_spectra_num > max_spectra_num:
                max_spectra_num = tmp_spectra_num

        spectra_num = max_spectra_num
        spots_num = len(self.raman_spot_dict)  # this calculates the number of spots in the Raman Folder
        spectra_points_num = 1024  # this is the number of points in a spectra
        # this declares the 3d numpy array that will now be filled
        data = np.zeros((spots_num, spectra_num,
                         spectra_points_num))  # this builds a numpy array to store the values
        i = 0
        for key, raman_spot in self.raman_spot_dict.items():
            spot_name_dict[i] = key
            spot_name_list.append(key)
            j = 0
            for spectra in raman_spot.data_list:
                if j == 0 and i == 0:  # stores the wavelenghts once
                    wavelengths = np.array(spectra[:, 0])  # stores x values in an array
                data[i, j, :] = spectra[:, 1]
                j += 1
            i += 1

        # the code in build_xarray in patient
        wavenumbers = (1 / (self.laser_wavelength) - 1 / wavelengths) * (10e9 / 10e2)  # cm^-1` relative wavenumbers
        self.xrdata = xr.DataArray(data=data, dims=('spot', 'spectrum', 'point'),
                                   coords={'point': wavenumbers, 'spot': spot_name_list})


class Patient_Data:
    """
    Performs plotting, baseline correction, and other processing on Raman spectra
    """
    def __init__(self, filename):
        self.filename = filename  # stores filename for storage later
        # opens dataset from file
        dataset = xr.open_dataset(filename)
        dataset.close()
        self.xarray_name = list(dataset.data_vars.keys())[0]  # gets first xrarray in dataset
        self.raw = dataset['raw']
        self.baseline = dataset.get('baseline', None)
        self.corrected = dataset.get('corrected', None)
        self.normalization_constnat = 1
        self.xarray = dataset['raw']  # xarray
        self.data = self.xarray.data.copy()  # numpy array

        self.average_data = np.mean(self.data, axis=1)  # calculates avearge data
        self.std_data = np.std(self.data, axis=1)  # calculates standard deviation
        self.spot_name_list = self.xarray.coords["spot"].data.tolist()
        self.wavenumbers = self.xarray.coords["point"].data.tolist()
        # plotting parameters
        self.offset_amnt = 100
        self.yrange = [0, 2000]
        self.spectra_num = self.data.shape[0]  # sets spectra number for plotting

        self.norm = dataset.get('norm', xr.DataArray(data=np.ones((self.data.shape[0], self.data.shape[1])),
                                                     dims=('spot', 'spectrum'), coords={'spot': self.spot_name_list}))

    def plot_averages(self, error_bars=True):
        plt.figure(num=None, figsize=(10, 7.5), dpi=80, facecolor='w', edgecolor='k')
        offset = 0
        for j in range(0, self.spectra_num):
            x = self.wavenumbers  # (1e6)/(self.laser_wavelength-self.wavelengths)#convert to wavelength guess of parameters 400 is wavelenth of laser used
            y = self.average_data[j, :]
            y_error = self.std_data[j, :]
            y = y + offset
            plt.plot(x, y, label="Spot: " + self.spot_name_list[j] + " id: " + str(j))

            if (error_bars):
                plt.fill_between(x, y - y_error, y + y_error, alpha=0.5)
            offset += self.offset_amnt

        plt.legend()
        plt.xlabel("Wavenumber $(cm^{-1})$")
        plt.ylabel("offset intensity")
        plt.ylim(self.yrange)

    def plot_spot(self, spot_id):
        plt.figure(num=None, figsize=(10, 7.5), dpi=80, facecolor='w', edgecolor='k')
        offset = 100
        for j in range(0, self.data.shape[1]):  # self.data_shape[1] equals the number of spectra in a spot
            x = self.wavenumbers  # convert to wavelength guess of parameters 400 is wavelenth of laser used
            y = self.data[spot_id, j, :]
            y = y + offset
            plt.plot(x, y, label="spectra index: " + str(j))
            offset += self.offset_amnt  # np.ptp(y,axis=0)

        plt.legend()
        plt.xlabel("Wavenumber $(cm^{-1})$")
        plt.ylabel("Offset Intensity")
        plt.ylim(self.yrange)

    def baseline_als(self, y, lam, p, niter=10):  # baseline correction algorthmn
        L = len(y)
        D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L - 2))
        w = np.ones(L)
        z = None
        for i in range(niter):
            W = sparse.spdiags(w, 0, L, L)
            Z = W + lam * D.dot(D.transpose())
            z = spsolve(Z, w * y)
            w = p * (y > z) + (1 - p) * (y < z)
        return z

    def correct_baseline(self, lamnda=200, p=0.0025, itermax=25):  # a simplistic correct baseline algorthmn
        #  if self.baseline is not None:
        #      return None
        baseline = self.raw.copy()
        corrected = self.raw.copy()
        for i in range(0, self.data.shape[0]):
            for j in range(0, self.data.shape[1]):
                z = self.airPLS(self.raw.data[i, j, :], lambda_=200, itermax=30, i=i, j=j)
                baseline[i, j, :] = z
                corrected.data[i, j, :] = self.raw.data[i, j, :] - z

        self.baseline = baseline
        self.corrected = corrected
        self.data = self.corrected.data
        self.average_data = np.mean(self.data, axis=1)  # calculates avearge data
        self.std_data = np.std(self.data, axis=1)  # calculates standard deviation

    def normalize(self):
        # build an xarray containing the normalization constant for each spectra
        # dim = (spot numbers, spectra numbers)
        left_bound = self.find_nearest(self.wavenumbers,
                                       400)  # finds index of 400 wavnumbers and cuts out of normalization

        for i in range(0, self.data.shape[0]):
            for j in range(0, self.data.shape[1]):
                self.norm[i, j] = np.trapz(self.data[i, j, left_bound:])
                self.corrected[i, j, :] = 4000 * self.corrected[i, j, :] / self.norm[
                    i, j]  # 4000 is for ease of plotting
        self.data = self.corrected.copy()
        self.average_data = np.mean(self.data, axis=1)  # calculates avearge data
        self.std_data = np.std(self.data, axis=1)  # calculates standard deviation

    def smooth(self, windowSize=41, orderOfPoly=3):
        for i in range(0, self.data.shape[0]):
            for j in range(0, self.data.shape[1]):
                # self.corrected[i,j,:] = signal.savgol_filter(self.data[i,j,:],windowSize,orderOfPoly)
                self.corrected[i, j, :] = self.ws_wrapper(self.data[i, j, :], 10)

    def get_corrected(self):
        if self.corrected is None:
            self.correct_baseline()
        return self.corrected.data

    # useful function for locating wavenumbers, taken from the internet
    def find_nearest(self, array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return idx

    def save_data(self):
        data_dict = {}
        data = [self.raw, self.baseline, self.corrected, self.norm]
        data_names = ["raw", "baseline", "corrected", 'norm']
        for d in data:
            if d is None:
                print("Error: correct baseline before saving")

        for i in range(0, len(data)):
            data_dict[data_names[i]] = data[i]
        dataset = xr.Dataset(data_dict)
        dataset.to_netcdf(self.filename)

        '''
        airPLS.py Copyright 2014 Renato Lombardo - renato.lombardo@unipa.it
        Baseline correction using adaptive iteratively reweighted penalized least squares

        This program is a translation in python of the R source code of airPLS version 2.0
        by Yizeng Liang and Zhang Zhimin - https://code.google.com/p/airpls
        Reference:
        Z.-M. Zhang, S. Chen, and Y.-Z. Liang, Baseline correction using adaptive iteratively reweighted penalized least squares. Analyst 135 (5), 1138-1146 (2010).

        Description from the original documentation:

        Baseline drift always blurs or even swamps signals and deteriorates analytical results, particularly in multivariate analysis.  It is necessary to correct baseline drift to perform further data analysis. Simple or modified polynomial fitting has been found to be effective in some extent. However, this method requires user intervention and prone to variability especially in low signal-to-noise ratio environments. The proposed adaptive iteratively reweighted Penalized Least Squares (airPLS) algorithm doesn't require any user intervention and prior information, such as detected peaks. It iteratively changes weights of sum squares errors (SSE) between the fitted baseline and original signals, and the weights of SSE are obtained adaptively using between previously fitted baseline and original signals. This baseline estimator is general, fast and flexible in fitting baseline.


        LICENCE
        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU Lesser General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU Lesser General Public License for more details.

        You should have received a copy of the GNU Lesser General Public License
        along with this program.  If not, see <http://www.gnu.org/licenses/>
        '''

    def WhittakerSmooth(self, x, w, lambda_, differences=1):
        '''
        Penalized least squares algorithm for background fitting

        input
            x: input data (i.e. chromatogram of spectrum)
            w: binary masks (value of the mask is zero if a point belongs to peaks and one otherwise)
            lambda_: parameter that can be adjusted by user. The larger lambda is,  the smoother the resulting background
            differences: integer indicating the order of the difference of penalties

        output
            the fitted background vector
        '''
        X = np.matrix(x)
        m = X.size
        i = np.arange(0, m)
        E = eye(m, format='csc')
        D = E[1:] - E[:-1]  # numpy.diff() does not work with sparse matrix. This is a workaround.
        W = diags(w, 0, shape=(m, m))
        A = csc_matrix(W + (lambda_ * D.T * D))
        B = csc_matrix(W * X.T)
        background = spsolve(A, B)
        return np.array(background)

    def airPLS(self, x, lambda_=100, porder=1, itermax=10, i=0, j=0):
        '''
        Adaptive iteratively reweighted penalized least squares for baseline fitting

        input
            x: input data (i.e. chromatogram of spectrum)
            lambda_: parameter that can be adjusted by user. The larger lambda is,  the smoother the resulting background, z
            porder: adaptive iteratively reweighted penalized least squares for baseline fitting

        output
            the fitted background vector
        '''
        m = x.shape[0]
        w = np.ones(m)
        for i in range(1, itermax + 1):
            z = self.WhittakerSmooth(x, w, lambda_, porder)
            d = x - z
            dssn = np.abs(d[d < 0].sum())
            if (dssn < 0.001 * (abs(x)).sum() or i == itermax):
                if (i == itermax): print('WARING max iteration reached! at i = %d j = %d' % (i, j))
                break
            w[
                d >= 0] = 0  # d>0 means that this point is part of a peak, so its weight is set to 0 in order to ignore it
            w[d < 0] = np.exp(i * np.abs(d[d < 0]) / dssn)
            w[0] = np.exp(i * (d[d < 0]).max() / dssn)
            w[-1] = w[0]
        return z

    def ws_wrapper(self, x, lambda_=5, porder=1):
        m = x.shape[0]
        w = np.ones(m)
        return self.WhittakerSmooth(x, w, lambda_, porder)
