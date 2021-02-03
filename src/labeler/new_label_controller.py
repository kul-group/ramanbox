import os
from src.raman.sample import Sample
from typing import List
import glob
import xarray as xr
from src.labeler.image_generator import SpectrumImageMaker
from src.raman.constants import Label


class NewLabelController:
    def __init__(self, inputDirectory, output_dir='', spectrumPicFileName='currentSpectrum.png'):
        self.inputDirectory = inputDirectory
        self.output_dir = output_dir
        self.spectrumPicFileName = spectrumPicFileName
        self.index_complete = False

        self.sample_index = 0
        self.spot_index = 0
        self.spectrum_index = 0

        self.sample_list = self._get_sample_list()
        assert len(self.sample_list) > 0, 'no samples loaded :('
        self.current_sample = self.sample_list[self.sample_index]
        if self.current_sample.name is not None:
            self.sample_name = self.current_sample.name
        else:
            self.sample_name = 'Unnamed_Sample_' + str(self.sample_index)

        self.spot_list = self.current_sample.spot_list
        self.current_spot = self.spot_list[self.spot_index]
        self.spectrum_list = self.current_spot.spectrum_list
        self.current_spectrum = self.spectrum_list[self.spectrum_index]

        self.generate_image()

    @property
    def output_filepath(self):
        return os.path.join(self.output_dir, self.sample_name + '.nc')

    def _get_sample_list(self) -> List[Sample]:
        glob_str = os.path.join(self.inputDirectory, "*.nc")
        file_list = glob.glob(glob_str)
        sample_list = []
        for file in file_list:
            sample_list.append(Sample.build_from_netcdf(file))

        return sample_list

    def save_sample(self):
        self.current_sample.save_dataset(self.output_filepath)

    def skip_to_next_unlabeld_spectrum(self):
        while self.current_spectrum.label != Label.UNCAT:
            self.next_spectrum()

    def assign_good_label(self):
        self.current_spectrum.label = Label.GOOD
        self.next_spectrum()

    def assign_bad_label(self):
        self.current_spectrum.label = Label.BAD
        self.next_spectrum()

    def assign_maybe_label(self):
        self.current_spectrum.label = Label.MAYBE
        self.next_spectrum()

    def next_spectrum(self):
        #self.save_sample()
        if self.spectrum_index >= len(self.spectrum_list) - 1:
            if self.spot_index >= len(self.spot_list) - 1:
                if self.sample_index >= len(self.sample_list) - 1:
                    print("complete!")
                    self.index_complete = True
                else:
                    self.sample_index += 1
                self.spot_index = 0
            else:
                self.spot_index += 1
            self.spectrum_index = 0
        else:
            self.spectrum_index += 1

        self.update_current_spectrum()

    def previous_spectrum(self):
        self.index_complete = False
        if self.spectrum_index <= 0:
            if self.spot_index <= 0:
                if self.sample_index <= 0:
                    print("at start!")
                else:
                    self.sample_index -= 1
                self.update_current_spectrum()
                self.spot_index = len(self.spot_list) - 1
            else:
                self.spot_index -= 1
            self.update_current_spectrum()
            self.spectrum_index = len(self.spectrum_list) - 1
        else:
            self.spectrum_index -= 1

        self.update_current_spectrum()

    def update_current_spectrum(self):
        self.current_sample = self.sample_list[self.sample_index]
        self.spot_list = self.current_sample.spot_list
        self.current_spot = self.spot_list[self.spot_index]
        self.spectrum_list = self.current_spot.spectrum_list
        self.current_spectrum = self.spectrum_list[self.spectrum_index]

        if self.current_sample.name is not None:
            self.sample_name = self.current_sample.name
        else:
            self.sample_name = 'Unnamed Sample ' + str(self.sample_index)

        self.generate_image()

    def generate_image(self):
        wavenumber = self.current_spectrum.wavenumbers
        spectrumData = self.current_spectrum.corrected_data
        tmpSpectrumImageMaker = SpectrumImageMaker(wavenumber, spectrumData, filename=self.spectrumPicFileName)
        tmpSpectrumImageMaker.generate_image()

    def get_current_info(self):
        return self.sample_name, self.spot_index, self.spectrum_index
