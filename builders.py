from processing import SpectrumProcessor, DefaultSpotParser, SpotParser
from raman import Spot, Spectrum


class SpotBuilder:
    def __init__(self, filepath, parser_class=DefaultSpotParser):
        self.filepath = filepath
        self.parser = parser_class(filepath)

    def get_position(self):  # maybe encoded in filepath at some point
        return 0, 0

    def build_spot(self) -> Spot:
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

if __name__ == "__main__":
    my_builder = SpotBuilder("/Users/dda/Code/ramanbox/data/20200226_moxtek_R6G_3mM_60X_10mW_20x20_scan_1sec_exposure.txt")
    my_spot = my_builder.build_spot()
    my_spot.plot()