from ramanbox.raman.processing import SpectrumProcessor, DefaultSpotParser
from ramanbox.raman.spot import Spot
from ramanbox.raman.spectrum import Spectrum


class SpotBuilder:
    def __init__(self, filepath: str, parser_class=DefaultSpotParser):
        self.filepath = filepath
        self.parser = parser_class(filepath)

    def get_position(self):  # maybe encoded in filepath at some point
        """
        NOT IMPLEMENTED
        This gets the position from a filepath
        :return:
        :rtype:
        """
        return 0, 0

    def build_spot(self) -> Spot:
        """
        This builds a spot from a filepath
        :return: A spot created from a .txt file
        :rtype: Spot
        """
        metadata = self.parser.metadata
        spectra = self.parser.spectra
        spectrum_list = []
        for spectrum in spectra:
            new_spectrum = Spectrum(spectrum, SpectrumProcessor(self.parser.laser_wavelength),
                                    self.parser.laser_wavelength)
            spectrum_list.append(new_spectrum)

        new_spot = Spot(spectrum_list=spectrum_list, position=self.get_position(),
                        metadata=metadata, filepath=self.filepath)

        return new_spot

