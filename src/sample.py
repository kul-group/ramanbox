from typing import List, Optional, Dict
import copy
from src.spot import Spot
from src.processing import DefaultSpotParser
import glob
from src.builders import SpotBuilder
import os
import xarray as xr
from src.constants import PositionType, Label
from src.processing import DataSpecProcessor
from src.spectrum import Spectrum
import numpy as np


def convert_dict_labels_to_list(label_dict):
    str_list = []
    for key, value in label_dict.items():
        tmp_str = str(key) + ';' + str(value.value)
        str_list.append(tmp_str)
    return str_list

def convert_list_to_dict(my_list):
    new_dict = {}
    for tmp_str in my_list:
        split = tmp_str.split(';')
        key = int(split[0])
        value = int(split[1])
        new_dict[key] = Label(value)

    return new_dict


class Sample:
    def __init__(self, spot_list: List[Spot], metadata: Optional[Dict] = None, filepath: Optional[str] = None,
                 name=None):
        self.spot_list = spot_list
        self.metadata = metadata
        self.filepath = filepath
        self.name = name

    def plot(self):
        pass

    @staticmethod
    def build_sample(folder_path: str, parser_class=DefaultSpotParser, metadata=None, name=None) -> "Sample":
        file_list = glob.glob(os.path.join(folder_path, '*.txt'))
        spot_list = []
        for file in file_list:
            spot_list.append(SpotBuilder(file, parser_class).build_spot())

        return Sample(spot_list, metadata=metadata, filepath=folder_path, name=name)

    def build_Dataset(self):
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

    def save_dataset(self, filename):
        dataset = self.build_Dataset()

        for index in dataset:
            #for key, value in dataset[index].attrs['metadata'].items():
                # if key not in dataset[index]:  # DO NOT OVERRIDE KEYS!
                #     dataset[index].attrs[key] = value
            dataset[index].attrs.pop('metadata')
            dataset[index].attrs['labels'] = convert_dict_labels_to_list(dataset[index].attrs['labels'])
            # dataset[index].attrs.pop('labels')

        dataset.to_netcdf(filename)



    @staticmethod
    def build_from_netcdf(filepath: str, name: Optional[str] = None):
        dataset = xr.open_dataset(filepath)
        dataset.close()
        spot_list = []
        for index in dataset:
            # build a spot
            spectrum_list = []
            position = dataset[index].attrs['position']
            # metadata = dataset[index].attrs
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

