from src.raman.sample_builder import SampleBuilder

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
    #         print(spectrum.label)
    abs_path = '/Users/dda/Code/ramanbox/data/20200226_moxtek_R6G_3mM_60X_10mW_20x20_scan_1sec_exposure.txt'
    my_sb = SampleBuilder(abs_path)
    my_sample = my_sb.build_sample()
    simple2 = my_sample
    print(simple2.__dict__.keys())
    for spot in simple2.spot_list:
        print(spot.__dict__.keys())
        for spectrum in spot.spectrum_list:
            print(spectrum.__dict__.keys())
            break
        break