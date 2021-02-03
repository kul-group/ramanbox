from src.raman.sample_builder import SampleBuilder
from src.raman.sample import Sample

if __name__ == "__main__":
    # my_builder = SpotBuilder("/Users/dda/Code/ramanbox/data/20200226_moxtek_R6G_3mM_60X_10mW_20x20_scan_1sec_exposure.txt")
    # my_spot = my_builder.build_spot()
    # my_spot.plot()
    # print(my_spot.build_DataArray())
    # folder_path = "/Users/dda/Code/ramanbox/data"
    # sample = Sample.build_sample(folder_path)
    #simple = sample.save_dataset('data/test.nc')
    # simple2 = Sample.build_from_netcdf('data/test.nc')
    # for spot in simple2.spot_list:
    #     for spectrum in spot.spectrum_list:
    # print(spectrum.label)
    abs_path = '/Users/dda/Code/ramanbox/data/20200226_moxtek_R6G_3mM_60X_10mW_20x20_scan_1sec_exposure.txt'
    my_sb = SampleBuilder(abs_path)

    #new_path = "/Users/dda/Code/ramanbox/data/20200226_moxtek_R6G_3mM_60X_10mW_20x20_scan_1sec_exposure.txt"
    my_sample = my_sb.build_sample() #my_sb.build_sample()
    dataset = my_sample.build_Dataset()
    my_sample.save_dataset('data/aaple.nc')
    # my_sample2 = Sample.build_from_netcdf('output/my_test.nc')
    # print(my_sample2)
    #print(my_sample.name)
    # my_sample.save_dataset(filename='data/' + 'test' + '.nc')
    #my_sample.plot()
