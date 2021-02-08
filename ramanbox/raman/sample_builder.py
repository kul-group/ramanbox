from ramanbox.raman.spot import Spot
from ramanbox.raman.spectrum import Spectrum
from ramanbox.raman.processing import SpectrumProcessor, DefaultSpotParser
from ramanbox.raman.sample import Sample
from pathlib import Path

class SampleBuilder:
    """
    This function is useful for the case where each spectrum in a file is its own spot.
    """
    def __init__(self, filepath: str, parser_class=DefaultSpotParser, row_size: int = 20, row_step: int = 1,
                 col_step:int = 1, start_iter: int = 0):
        self.filepath = filepath
        self.parser = parser_class(filepath)
        self.row_size = row_size
        self.row_step = row_step
        self.col_step = col_step
        self.iter = start_iter

    def get_position(self):  # maybe encoded in filepath at some point
        """
        Get a position (fake positions now made)
        :return: position
        :rtype: Tuple[int, int]
        """
        result = (self.iter * self.row_step)% self.row_size, self.iter // (self.row_size * self.row_step)* self.col_step
        self.iter += 1
        return result

    def build_sample(self) -> Sample:
        """
        This builds a spot from a filepath
        :return: A sample created from a .txt file where each spectrum is its own spot
        :rtype: Sample
        """
        metadata = self.parser.metadata
        spectra = self.parser.spectra
        spot_list = []
        for spectrum in spectra:
            new_spectrum_list = [Spectrum(spectrum, SpectrumProcessor(self.parser.laser_wavelength),
                                          self.parser.laser_wavelength)]

            new_spot = Spot(spectrum_list=new_spectrum_list, position=self.get_position(), metadata=metadata,
                            filepath=self.filepath)
            spot_list.append(new_spot)
        name = str(Path(self.filepath).stem)
        return Sample(spot_list, name=name)
