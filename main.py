from ramanbox.pipeline.pipelines import raw_raster_to_unlabeled_netcdf
import git
import os


if __name__ == "__main__":
    repo = git.Repo('.', search_parent_directories=True)
    root_dir = repo.working_tree_dir
    raw_data_dir = os.path.join(root_dir, 'data', 'raw_data')
    unlabeled_data_dir = os.path.join(root_dir, 'data', 'unlabeled_data')

    # generate netcdf files from raw data
    print(unlabeled_data_dir)
    raw_raster_to_unlabeled_netcdf(raw_data_dir, unlabeled_data_dir)




    # my_builder = SpotBuilder("/Users/dda/Code/RamanBox/data/20200226_moxtek_R6G_3mM_60X_10mW_20x20_scan_1sec_exposure.txt")
    # my_spot = my_builder.build_spot()
    # my_spot.plot()
    # print(my_spot.build_DataArray())
    # folder_path = "/Users/dda/Code/RamanBox/data"
    # sample = Sample.build_sample(folder_path)
    #simple = sample.save_dataset('data/test.nc')
    # simple2 = Sample.build_from_netcdf('data/test.nc')
    # for spot in simple2.spot_list:
    #     for spectrum in spot.spectrum_list:
    # print(spectrum.label)
    #abs_path = '/Users/dda/Code/RamanBox/data/'

    #new_path = "/Users/dda/Code/RamanBox/data/20200226_moxtek_R6G_3mM_60X_10mW_20x20_scan_1sec_exposure.txt"
    #my_sample = SampleBuiuder(new_path).build_sample()
    #my_sample = Sample.build_sample(abs_path) #my_sb.build_sample()
    #print(my_sample.spot_list)
    #dataset = my_sample.build()
    # for a in dataset:
    #     print(dataset[a])
    #my_sample.save_dataset('data/aaple.nc')
    #print(my_sample.to_pandas().drop(columns=['spectrum']))
    #my_sample2 = Sample.build_from_netcdf('output/aaple.nc')
    #print(my_sample2.name)
    # print(my_sample2)
    #print(my_sample.name)
    # my_sample.save_dataset(filename='data/' + 'test' + '.nc')
    #my_sample.plot()

