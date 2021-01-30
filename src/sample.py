from typing import List, Optional, Dict
from src.spot import Spot
from src.processing import DefaultSpotParser
import glob
from src.builders import SpotBuilder
import os
import xarray as xr
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
            dict_vars[index] = spot.build_DataArray()

        return xr.Dataset(dict_vars, attrs=self.metadata)


    def buildFlatDataset(self):
        dict_vars = {}
        i = 0
        for spot_index, spot in enumerate(self.spot_list):
            for spectrum in spot.spectrum_list:
                dict_vars[i] = spectrum.build_DataArray(spot_index)

        return xr.Dataset(dict_vars, attrs=self.metadata)
