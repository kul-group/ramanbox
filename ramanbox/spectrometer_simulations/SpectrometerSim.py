from ramanbox.raman.sample import Sample
from ramanbox.raman.constants import Label

class SpectrometerSim:
    def __init__(self, netcdf_filepath: str) -> None:
        self._sample = Sample.build_from_netcdf(netcdf_filepath)
        self._pandas = self._sample.to_pandas()
        self._pandas['Predicted_Label'] = Label.UNCAT
        self._pandas_iter = self._pandas.iterrows()
        self._complete = False

        self._current_row = None
        self._current_index = None
        self.current_corrected_spectrum = None
        self.x_pos = None
        self.y_pos = None

    def _get_next(self) -> None:
        try:
            self._current_index, self._current_row = next(self._pandas_iter)
            self.x_pos = self._current_row['x_pos']
            self.y_pos = self._current_row['y_pos']
        except StopIteration:
            self._complete = True
            self.save()
            return None

        self.current_corrected_spectrum = self._current_row['spectrum']

    def get_next(self):
        self._pandas.iloc[self._sample]['Predicted_Label'] = Label.BAD
        self._get_next()

    def get_more(self):
        self._pandas.iloc[self._sample]['Predicted_Label'] = Label.GOOD
        self._get_next()

    def save(self, output_path='output.csv'):
        self._pandas.to_csv(output_path)