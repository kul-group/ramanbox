from abc import ABC
from abc import abstractmethod
import numpy as np

# smoothing imports
from scipy.sparse import csc_matrix, eye, diags
from scipy.sparse.linalg import spsolve
from typing import Tuple, Dict, List
from src.constants import PositionType

class SpectrumProcessor:  # eventually build ABC
    def __init__(self, laser_wavelength: float) -> None:
        self.laser_wavelength = laser_wavelength

    def get_wavenumber(self, wavelengths: np.array, input_type: PositionType) -> np.array:
        if input_type == PositionType.WAVENUMBER:
            return wavelengths

        assert input_type == PositionType.WAVELENGTH, 'wrong position type, cannot do conversion'
        return (1 / self.laser_wavelength - 1 / wavelengths) * (10e9 / 10e2)  # cm^-1` relative wavenumbers

    def correct_baseline(self, spectrum_array: np.array) -> np.array:
        baseline = self._airPLS(spectrum_array, lambda_=200, itermax=30)
        return spectrum_array - baseline

    def remove_cosmic_rays(self, spectrum_array: np.array) -> np.array:
        return spectrum_array  # TODO: actually implement

    def smooth_spectrum(self, spectrum_array: np.array) -> np.array:
        return self._ws_wrapper(spectrum_array, 10)

    def normalize(self, spectrum_array:np.array) -> np.array:
        return spectrum_array/np.trapz(spectrum_array)

    def correct_spectrum(self, spectrum_array:np.array) -> np.array:
        return self.normalize(self.smooth_spectrum(self.correct_baseline(self.remove_cosmic_rays(spectrum_array))))


    def _ws_wrapper(self, x, lambda_=5, porder=1):
        m = x.shape[0]
        w = np.ones(m)
        return self._WhittakerSmooth(x, w, lambda_, porder)

    def _WhittakerSmooth(self, x, w, lambda_, differences=1):
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

    def _airPLS(self, x, lambda_=100, porder=1, itermax=10):
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
            z = self._WhittakerSmooth(x, w, lambda_, porder)
            d = x - z
            dssn = np.abs(d[d < 0].sum())
            if (dssn < 0.001 * (abs(x)).sum() or i == itermax):
                if (i == itermax): print('WARING max iteration reached! at i = %d j = %d' % (i, j))
                break
            w[d >= 0] = 0  # d>0 means that this point is part of a peak, so its weight is set to 0 in order to ignore it
            w[d < 0] = np.exp(i * np.abs(d[d < 0]) / dssn)
            w[0] = np.exp(i * (d[d < 0]).max() / dssn)
            w[-1] = w[0]
        return z


class SpotParser(ABC):
    """
    This is an abstract base class for a Raman Input Parser.
    It allows this code to be tailored to the unique file formats that
    one might encounter when loading in Raman spectra.
    """
    @abstractmethod
    def __init__(self, filepath):
        pass

    @property
    @abstractmethod
    def spectrum_length(self) -> int:
        pass

    @property
    @abstractmethod
    def laser_wavelength(self) -> float:
        pass

    @abstractmethod
    def get_metadata_and_spectrum(self, filepath) -> Tuple[Dict, List[List[float]]]:
        pass


class DefaultSpotParser(SpotParser):
    """
    This is a specific RamanInputParser that inherits from the abstract base class.
    This practice of inheritance ensures that it impliments the correct methods
    to work with the RamanSpot Class
    """

    def __init__(self, filepath):
        self._spectrum_length = 1024
        self._laser_wavelength = 785
        self.metadata, self.spectra = self.get_metadata_and_spectrum(filepath)

    @property
    def spectrum_length(self):
        return self._spectrum_length

    @property
    def laser_wavelength(self) -> float:
        return self._laser_wavelength

    @spectrum_length.setter
    def spectrum_length(self, value):
        self._spectrum_length = value

    @laser_wavelength.setter
    def laser_wavelength(self, value):
        self._laser_wavelength = value


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

