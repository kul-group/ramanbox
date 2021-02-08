import os
from pathlib import Path
from src.raman.sample_builder import SampleBuilder
from src.raman.sample import Sample


def raw_raster_to_unlabeled_netcdf(input_dir: str, output_dir: str) -> None:
    _raw_raster_to_unlabeled_netcdf(input_dir, output_dir, SampleBuilder)


def raw_sample_to_unlabeled_netcdf(input_dir: str, output_dir: str) -> None:
    _raw_raster_to_unlabeled_netcdf(input_dir, output_dir, Sample.build_sample)


def _raw_raster_to_unlabeled_netcdf(input_dir: str, output_dir: str, sample_builder) -> None:
    file_list = Path(input_dir).rglob('*.txt')

    for file in file_list:
        print(f'loading {file}')
        tmp_sb = sample_builder(file)
        tmp_sample = tmp_sb.build_sample()
        new_filename = tmp_sample.name + '.nc'
        output_file = os.path.join(output_dir, new_filename)
        tmp_sample.save_dataset(output_file)
        print(f"wrote output file {new_filename} to {output_dir}")
