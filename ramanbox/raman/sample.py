from typing import List, Optional, Dict
from ramanbox.raman.spot import Spot
from ramanbox.raman.processing import DefaultSpotParser
import glob
from ramanbox.raman.builders import SpotBuilder
import os
import xarray as xr
from ramanbox.raman.constants import PositionType, Label
from ramanbox.raman.processing import DataSpecProcessor
from ramanbox.raman.spectrum import Spectrum
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def convert_dict_labels_to_list(label_dict: Dict[int, Label]) -> List[str]:
    """
    Converts a dict to labels for the serialization
    :param label_dict: A dictionary of labels
    :type label_dict: Dict[int, Label]
    :return: list of a strings of the form "int;Label.value"
    :rtype: List[str]
    """
    str_list = []
    for key, value in label_dict.items():
        tmp_str = str(key) + ';' + str(value.value)
        str_list.append(tmp_str)
    return str_list

def convert_list_to_dict(my_list):
    """
    Converts a list of strings back to a Dict[int, Label]
    :param my_list: list of str labels
    :type my_list: List[str]
    :return: Dictionary of index, Label pairs
    :rtype: Dict[int, Label]
    """
    new_dict = {}
    if not isinstance(my_list, list):  # label is just a string
        tmp_str = my_list
        split = tmp_str.split(';')
        key = int(split[0])
        value = int(split[1])
        new_dict[key] = Label(value)
        return new_dict

    for tmp_str in my_list:
        split = tmp_str.split(';')
        key = int(split[0])
        value = int(split[1])
        new_dict[key] = Label(value)

    return new_dict


class Sample:
    def __init__(self, spot_list: List[Spot], metadata: Optional[Dict] = None, filepath: Optional[str] = None,
                 name=None) -> None:
        """
        This is a sample list.
        :param spot_list: list of spots
        :type spot_list: List[Spot]
        :param metadata: dictionary of metadata
        :type metadata: Dict[str, str]
        :param filepath: a filepath to a folder containing the text files of the spots
        :type filepath: str
        :param name: name of the Sample being created
        :type name: Optional[str]
        """
        self.spot_list = spot_list
        self.metadata = metadata
        self.filepath = filepath
        self.name = name

    def plot(self, axis=None, plot_raw=False, break_after=10, subplots_shape=(3,3)) -> None:
        fig, axes = plt.subplots(*subplots_shape, dpi=300, figsize=(8,8))
        for spot, axis in zip(self.spot_list, axes.flatten()):
            spot.plot(axis=axis, plot_raw=plot_raw, break_after=break_after)
        fig.show()

    @staticmethod
    def build_sample(folder_path: str, parser_class=DefaultSpotParser, metadata=None, name=None) -> "Sample":
        """
        This builds a sample from a folder containing .txt files
        :param folder_path: folder path
        :type folder_path: str
        :param parser_class: a class needed for parsing the data
        :type parser_class: SpotParser
        :param metadata: a dictionary of metadata for the spot
        :type metadata: Dict
        :param name: The name of the sample
        :type name: str
        :return: A newly created sample
        :rtype: "Sample"
        """
        assert os.path.isdir(folder_path), 'folder_path must point to a directory and not a single file'
        file_list = glob.glob(os.path.join(folder_path, '*.txt'))
        spot_list = []
        for file in file_list:
            spot_list.append(SpotBuilder(file, parser_class).build_spot())

        return Sample(spot_list, metadata=metadata, filepath=folder_path, name=name)


    def build_Dataset(self) -> xr.Dataset:
        """
        Build a Dataset xarray object from current object
        :return: an xr.Dataset object containing all of the information in this class
        :rtype:  xr.Dataset
        """

        dict_vars = {}
        for index, spot in enumerate(self.spot_list):
            dict_vars[str(index)] = spot.build_DataArray()

        return xr.Dataset(dict_vars, attrs=self.metadata)

    def buildFlatDataset(self):
        dict_vars = {}
        i = 0
        for spot_index, spot in enumerate(self.spot_list):
            for spectrum in spot.spectrum_list:
                dict_vars[str(i)] = spectrum.build_DataArray(spot_index)
                i += 1

        return xr.Dataset(dict_vars, attrs=self.metadata)

    def save_dataset(self, filename: str) -> None:
        """
        Save the current dataset as a netcdf file
        :param filename: name of the output filename
        :type filename: str
        :return: None
        :rtype: None
        """
        dataset = self.build_Dataset()
        dataset.attrs['name'] = str(self.name)
        for index in dataset:
            dataset[index].attrs.pop('metadata')  # metadata is not currently saved
            dataset[index].attrs['labels'] = convert_dict_labels_to_list(dataset[index].attrs['labels'])

        dataset.to_netcdf(filename)



    @staticmethod
    def build_from_netcdf(filepath: str, engine='netcdf4') -> "Sample":
        """
       Build a Sample object from a netcdf file
        :param filepath: filepath to the netcdf object
        :type filepath: str
        :return: None
        :rtype: None
        """
        dataset = xr.open_dataset(filepath, engine=engine)
        dataset.close()
        name = dataset.attrs['name']
        spot_list = []
        for index in dataset:
            # build a spot
            spectrum_list = []
            position = dataset[index].attrs['position']
            metadata = None
            filepath = dataset[index].attrs['filepath']
            dataset[index].attrs['labels'] = convert_list_to_dict(dataset[index].attrs['labels'])
            for spec_index, spec_data in enumerate(dataset[index]):
                raw_data = np.zeros((len(spec_data.loc['raw']), 2))
                raw_data[:, 1] = spec_data.loc['raw']
                corrected_data = spec_data.loc['corrected']
                wavenumbers = spec_data.wavenumber.values
                raw_data[:, 0] = wavenumbers
                laser_wavelength = spec_data.attrs['laser_wavelength']
                label = spec_data.attrs['labels'][spec_index]
                position_type = PositionType.WAVENUMBER
                processor = DataSpecProcessor(laser_wavelength, corrected_data, wavenumbers)
                new_spectrum = Spectrum(raw_data, processor, laser_wavelength, label, position_type)
                spectrum_list.append(new_spectrum)

            new_spot = Spot(spectrum_list, position, metadata, filepath)
            spot_list.append(new_spot)

        return Sample(spot_list, dataset.attrs, filepath, name)

    def to_pandas(self, use_corrected=True):
        complete_df = pd.DataFrame()
        for spot in self.spot_list:
            spot_df = spot.to_pandas(use_corrected)
            spot_df['name'] = self.name
            complete_df = complete_df.append(spot_df, ignore_index=True)

        assert complete_df is not None, 'complete df is none, spot list must be empty!'
        return complete_df
