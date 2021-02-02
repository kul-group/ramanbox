import numpy as np
from src.processing import ABCSpecProcessor
from src.constants import PositionType, Label
import xarray as xr
from typing import Optional

class Spectrum:
    def __init__(self, raw_data: np.array, processor: ABCSpecProcessor,
                 laser_wavelength: float, label: Label = Label.UNCAT,
                 position_type: PositionType = PositionType.WAVELENGTH) -> None:
        self.data_length = len(raw_data)
        self.raw_data = raw_data[:, 1]
        self.raw_positions = raw_data[:, 0]
        self.processor = processor
        self.laser_wavelength = laser_wavelength
        self.position_type = position_type
        # actually do the processing here
        self.wavenumbers = processor.get_wavenumber(self.raw_positions, position_type)
        self.corrected_data = processor.correct_spectrum(self.raw_data)
        self.label = label

    def build_DataArray(self, spot: Optional[int] = None) -> xr.DataArray:
        attrs = {'data_length': self.data_length,
                 'laser_wavelength': self.laser_wavelength,
                 'label': self.label}
        if spot:
            attrs['spot'] = spot
        combined = np.vstack((self.raw_data, self.corrected_data)).T
        data_types = ['raw', 'corrected']
        return xr.DataArray(combined, coords=[self.wavenumbers, data_types],
                            dims=['wavenumber', 'spectrum'], attrs=attrs)
