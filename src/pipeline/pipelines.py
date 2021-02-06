import os
from pathlib import Path
from src.raman.sample_builder import SampleBuilder


def raw_raster_to_unlabled_netcdf(input_dir: str, output_dir: str) -> None:
    file_list = Path(input_dir).rglob('*.txt')

    for file in file_list:
        print(f'loading {file}')
        tmp_sb = SampleBuilder(file)
        tmp_sample = tmp_sb.build_sample()
        new_filename = tmp_sample.name + '.nc'
        output_file = os.path.join(output_dir, new_filename)
        tmp_sample.save_dataset(output_file)
        print(f"wrote output file {new_filename} to {output_dir}")


