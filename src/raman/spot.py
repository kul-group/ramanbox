import matplotlib.pyplot as plt
import numpy as np
from itertools import count
from typing import List, Optional, Tuple, Dict
from src.raman.spectrum import Spectrum
import xarray as xr
import pandas as pd

class Spot:
    def __init__(self, spectrum_list: List[Spectrum], position: Optional[Tuple[float, float]] = None,
                 metadata: Optional[Dict] = None, filepath: Optional[str] = None):
        """
        This is a spot spectrum
        :param spectrum_list: A list of the spectra
        :type spectrum_list: List[Spectrum]
        :param position: The spot's position
        :type position: Optional[Tuple[float,float]]
        :param metadata: Dictionary of metadata
        :type metadata: Optional[Dict]
        :param filepath: filepath to the spot .txt file
        :type filepath: str
        """
        self.spectrum_list = spectrum_list
        self.position = position
        self.metadata = metadata
        self.filepath = str(filepath)

    def build_DataArray(self):
        """
        Build a DataArray object from a spot
        :return: a DataArray object
        :rtype: xr.DataArray
        """
        assert len(self.spectrum_list) != 0, 'Spectra list empty, cannot build xarray'
        spectrum_length = self.spectrum_list[0].data_length
        laser_wavelength = self.spectrum_list[0].laser_wavelength

        dims = ['index', 'type', 'wavenumber']
        shape = (len(self.spectrum_list), 2, spectrum_length)
        wavenumbers = self.spectrum_list[0].wavenumbers
        data = np.zeros(shape)
        attributes = {"laser_wavelength": laser_wavelength,
                      "spectrum_length": spectrum_length,
                      "position": self.position,
                      "metadata": self.metadata,
                      "filepath": self.filepath,
                      "labels": {}}

        spectra_indices = []
        for index, spectrum in enumerate(self.spectrum_list):
            # key assumptions to building a spot
            assert spectrum.data_length == spectrum_length, 'all spectra must be same length'
            assert spectrum.laser_wavelength == laser_wavelength, 'all spectra must use same laser wavelength'
            # assert np.testing.assert_array_equal(wavenumbers, spectrum.wavenumbers, err_msg='all spectra in spot must have same wavenumbers', verbose=True)
            np.testing.assert_almost_equal(wavenumbers, spectrum.wavenumbers, 3,
                                           err_msg='all spectra in spot must have same wavenumbers')

            data[index, 0, :] = spectrum.raw_data
            data[index, 1, :] = spectrum.corrected_data
            attributes["labels"][index] = spectrum.label
            spectra_indices.append(index)

        spectrum_type = ['raw', 'corrected']
        coords = [spectra_indices, spectrum_type, wavenumbers]
        return xr.DataArray(data, coords=coords,
                            dims=dims, attrs=attributes)

    def plot(self, axis=None, plot_raw=False, break_after=10) -> None:
        """
        Plot the spectrum in the spot
        :param plot_raw: boolean to determine if you should plot raw or corrected spectra
        :type plot_raw: bool
        :param break_after: how many spectra to print before stopping
        :type break_after: int
        :return: None
        :rtype: None
        """
        offset = 0
        if axis is None:
            fig, axis = plt.subplots(1, 1)

        for index, spectrum in zip(count(), self.spectrum_list):
            x = spectrum.wavenumbers
            if plot_raw:
                y = spectrum.raw_data + offset
            else:
                y = spectrum.corrected_data + offset
            offset += max(spectrum.corrected_data) * 1.1
            axis.plot(x, y, label=f'index {index}')
            if index >= break_after:
                break

        axis.set_xlabel(r"Wavenumbers (cm${\rm ^{-1}}$)")
        axis.set_ylabel("Offset Relative Intensity")
        axis.legend()
        if axis is None:
            fig.show()

    def to_pandas(self, use_corrected=True):
        spec_list = []
        label_list = []
        x_pos_list = []
        y_pos_list = []
        for spectrum in self.spectrum_list:
            spec = spectrum.to_numpy(use_corrected)
            label = spectrum.label

            if self.position is not None:
                x_pos, y_pos = self.position
            else:
                x_pos = None
                y_pos = None
            spec_list.append(spec)
            label_list.append(label)
            x_pos_list.append(x_pos)
            y_pos_list.append(y_pos)

        dict_list = {'spectrum': spec_list, 'label': label_list, 'x_pos': x_pos_list, 'y_pos': y_pos_list}

        return pd.DataFrame(dict_list)
