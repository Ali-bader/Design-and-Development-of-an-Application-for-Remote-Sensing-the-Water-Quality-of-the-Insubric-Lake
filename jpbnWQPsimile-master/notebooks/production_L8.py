# Styling notebook

# System
import os
import sys
import tkinter as tk

# Import scripts libraries for the project
sys.path.append('./src/python')

# Import the function to update the notebook style
from nbConfig import (css_styling)

css_styling()

import pandas as pd
import ipywidgets as wg
import wqpSNAPparams_S3 as wqpParams_S3
import wqpSNAPparams_L8 as wqpParams_L8
import wqpSNAPparams_EUMETSAT as wqpParams_EUMETSAT
import wqpSNAPFunctions as wqpSNAP
def tem_L8():
    in_path = f'./in/satellite_imagery/L8'
    out_path = f'./in/wqp/L8'
    cwd_path = wqpSNAP.inputParameters(in_path,out_path)

    # Read the atmospheric correction parameters file
    df_atm = pd.read_csv(os.path.join(cwd_path['in_parameters'],'atmCorr.csv'))
    df_atm['DateTime'] = pd.to_datetime(df_atm['DateTime'], format='%m/%d/%Y %H:%M',errors='coerce')
    df_atm['DateTime'] = df_atm['DateTime'].dt.date
        # Temptative bounding box for the area of interest
    bbox = {
            'minLat' : 45.3,
            'maxLat' : 46.65,
            'minLon' : 7.9,
            'maxLon' : 9.95,
       }

    # Format output processed images
    writeFormat = 'GeoTIFF'
    wqpParams = wqpParams_L8
    output_results1 = []  # Initialize an empty list to store the results
    for root, dirs, files in os.walk(in_path):
        for f in files:
            if f.endswith('MTL.txt'):
                # 1. Read the product
                l8_image = wqpSNAP.snapProduct(os.path.join(root,f),bbox)
                l8_image.readSNAPProduct()
                l8_image.name = l8_image.path.split('/')[-2].split('.')[0]
                params_bandMaths = l8_image.updateSNAPAtmCorr(df_atm,wqpParams.params_bandMaths)
                try:
                   # 2. Update the bounding box for the subset selection
                    params_subset = l8_image.updateSNAPSubset(wqpParams.params_subset)
                    subset_product = wqpSNAP.executeSNAPFunction(l8_image.product, params_subset)
                    # 3. Reproject the subset
    #                 reproject_product = wqpSNAP.executeSNAPFunction(subset_product, wqpParams.params_reproject) 
                    # 4. Resample
                    resample_product = wqpSNAP.executeSNAPFunction(subset_product, wqpParams.params_resample)
                    # 5. Import-Vector
                    importVector_product = wqpSNAP.executeSNAPFunction(resample_product, wqpParams.params_importVector)
                    # 6. BandMaths
                    bandMaths_product = wqpSNAP.executeSNAPFunction(importVector_product, params_bandMaths)
                    bandMaths_product_masks = wqpSNAP.executeSNAPFunction(importVector_product,                                                 wqpParams.params_bandMaths_masks)
                    # 7. BandExtract
                    bandExtract_product_lswt = wqpSNAP.executeSNAPFunction(bandMaths_product,                                                   wqpParams.params_bandExtractor_lswt)
                    bandExtract_product_lswt_mid_high = wqpSNAP.executeSNAPFunction(bandMaths_product,                                         wqpParams.params_bandExtractor_lswt_mid_high)
                    bandExtract_product_lswt_high = wqpSNAP.executeSNAPFunction(bandMaths_product,                                             wqpParams.params_bandExtractor_lswt_high)
                    bandExtract_product_masks = wqpSNAP.executeSNAPFunction(bandMaths_product_masks,                                           wqpParams.params_bandExtractor_masks)
                    # 8. Export bands
                    # Output paths
                    sensorDate = l8_image.name.split('_')[3]
                    out_path_lswt = os.path.join(cwd_path['out_wqp'],'lswt','L8'+'_LSWT_IT_'+sensorDate+'_L1')
                    out_path_lswt_mid_high =                                                                                                   os.path.join(cwd_path['out_wqp_mid_high_clouds'],'lswt','L8'+'_LSWT_IT_'+sensorDate+'_L1')
                    out_path_lswt_high =                                                                                                       os.path.join(cwd_path['out_wqp_high_clouds'],'lswt','L8'+'_LSWT_IT_'+sensorDate+'_L1')
                    out_path_mask = os.path.join(cwd_path['out_masks'],'L8'+'_LSWT_IT_'+sensorDate+'_L1')
                    print(out_path_lswt_high)
                    #Save Bands
                    wqpSNAP.exportProductBands(bandExtract_product_lswt, out_path_lswt, writeFormat)
                    wqpSNAP.exportProductBands(bandExtract_product_lswt_mid_high, out_path_lswt_mid_high, writeFormat)
                    wqpSNAP.exportProductBands(bandExtract_product_lswt_high, out_path_lswt_high, writeFormat)
                    wqpSNAP.exportProductBands(bandExtract_product_masks, out_path_mask, writeFormat)
                    result = {
                        'lswt': out_path_lswt,
                        'lswt_mid_high': out_path_lswt_mid_high,
                        'lswt_high': out_path_lswt_high,
                        'mask': out_path_mask
                    }
                    output_results1.append(result)
                
                    subset_product.dispose() 
                    importVector_product.dispose()
                    resample_product.dispose()
                    bandMaths_product.dispose()
                    bandMaths_product_masks.dispose()
                    bandExtract_product_lswt.dispose()
                    bandExtract_product_lswt_mid_high.dispose()
                    bandExtract_product_lswt_high.dispose()
                    bandExtract_product_masks.dispose()
                
                    del subset_product
                    del importVector_product
                    del resample_product
                    del bandExtract_product_lswt
                    del bandExtract_product_lswt_mid_high
                    del bandExtract_product_lswt_high
                    del bandExtract_product_masks
                    del bandMaths_product
                    del bandMaths_product_masks
                except:
                     # Open a file with access mode 'a'
                    file_object = open(os.path.join(cwd_path['out'],f'error_images_L8.txt'), 'a')
                    file_object.write(l8_image.name)
                    file_object.write("\n")
                    # Close the file
                    file_object.close()
    return output_results1 