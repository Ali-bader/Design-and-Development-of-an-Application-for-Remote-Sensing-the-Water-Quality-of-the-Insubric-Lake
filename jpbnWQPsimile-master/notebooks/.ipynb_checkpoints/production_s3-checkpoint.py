# Styling notebook

# System
import os
import sys
import tkinter as tk
from datetime import datetime

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


def wqp_s3(start_date_str, end_date_str):
    
    in_path = f'./in/satellite_imagery/S3'
    out_path = f'./in/wqp/S3'
    cwd_path = wqpSNAP.inputParameters(in_path,out_path)

    #Read the mean temperature file
    df_t = pd.read_csv(os.path.join(cwd_path['in_parameters'],'meteoTemp.csv'))
    df_t["Data"] = pd.to_datetime(df_t['Data'] ,format="%d/%m/%Y %H:%M:%S")
    df_t_keys = list(df_t.keys())

    # Temptative bounding box for the area of interest
    bbox = {
            'minLat' : 45.3,
            'maxLat' : 46.65,
            'minLon' : 7.9,
            'maxLon' : 9.95,
       }

    # Format output processed images
    writeFormat = 'GeoTIFF'

    wqpParams = wqpParams_S3
    output_results = []
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        for root, dirs, files in os.walk(in_path):
                for d in dirs:
                    if d != '.ipynb_checkpoints':
                        # 1. Read the product
                        s3_image = wqpSNAP.snapProduct(os.path.join(root, d, 'xfdumanifest.xml'), bbox)
                        s3_image.readSNAPProduct()
                        s3_image.name = s3_image.path.split('/')[-2]
                        print(s3_image.name)
                        try:
                        # Check if image is within the date range
                            image_date_str = s3_image.name.split('_')[8]
                            image_date = datetime.strptime(image_date_str, '%Y%m%dT%H%M%S')

                            if start_date <= image_date <= end_date:
                                
                                
  
                                try:
                              # 2. Update the bounding box for the subset selection
                                    params_subset = s3_image.updateSNAPSubset(wqpParams.params_subset)
                                    subset_product = wqpSNAP.executeSNAPFunction(s3_image.product, params_subset)
                              # 3. Reproject the subset
                                    reproject_product = wqpSNAP.executeSNAPFunction(subset_product, wqpParams.params_reproject)
                              # 4. Update the C2RCC temperature value. C2RCC wqp products
                                    params_C2RCC = s3_image.updateSNAPTemperature(df_t, wqpParams.params_C2RCC)
                                    c2rcc_product = wqpSNAP.executeSNAPFunction(reproject_product, params_C2RCC)
                              # 5. Import vector layer
                                    importVector_product = wqpSNAP.executeSNAPFunction(c2rcc_product, wqpParams.params_importVector)
                              # 6. Band Maths operations
                                    bandMaths_product_C2RCC = wqpSNAP.executeSNAPFunction(importVector_product, wqpParams.params_bandMaths)
                                    bandMaths_product_oa = wqpSNAP.executeSNAPFunction(reproject_product, wqpParams.params_bandMaths_oa)
                                    bandMaths_product_rrs = wqpSNAP.executeSNAPFunction(importVector_product, wqpParams.params_bandMaths_rrs)  
                                    bandMaths_product_masks = wqpSNAP.executeSNAPFunction(importVector_product, wqpParams.params_bandMaths_masks)
                             # 7. Extract bands
                             # Product bands to be extracted
                                    bandExtract_product_chl = wqpSNAP.executeSNAPFunction(bandMaths_product_C2RCC, wqpParams.params_bandExtractor_chl)
                                    bandExtract_product_tsm = wqpSNAP.executeSNAPFunction(bandMaths_product_C2RCC, wqpParams.params_bandExtractor_tsm)
                                    bandExtract_product_chl_no_clip = wqpSNAP.executeSNAPFunction(bandMaths_product_C2RCC, wqpParams.params_bandExtractor_chl_no_clip)
                                    bandExtract_product_tsm_no_clip = wqpSNAP.executeSNAPFunction(bandMaths_product_C2RCC, wqpParams.params_bandExtractor_tsm_no_clip)
                                    bandExtract_product_chl_no_mask = wqpSNAP.executeSNAPFunction(bandMaths_product_C2RCC, wqpParams.params_bandExtractor_chl_no_masks)
                                    bandExtract_product_tsm_no_mask = wqpSNAP.executeSNAPFunction(bandMaths_product_C2RCC, wqpParams.params_bandExtractor_tsm_no_masks)
                                    bandExtract_product_chl_cloud_mask = wqpSNAP.executeSNAPFunction(bandMaths_product_C2RCC, wqpParams.params_bandExtractor_chl_cloud_mask)
                                    bandExtract_product_tsm_cloud_mask = wqpSNAP.executeSNAPFunction(bandMaths_product_C2RCC, wqpParams.params_bandExtractor_tsm_cloud_mask)
                                    bandExtract_product_oa = wqpSNAP.executeSNAPFunction(bandMaths_product_oa, wqpParams.params_bandExtractor_oa)
                             # bandExtract_product_oa = wqpSNAP.executeSNAPFunction(bandMaths_product_oa, wqpParams.params_bandExtractor_oa_18)
                                    bandExtract_product_rrs = wqpSNAP.executeSNAPFunction(bandMaths_product_rrs, wqpParams.params_bandExtractor_rrs)
                                    bandExtract_product_masks = wqpSNAP.executeSNAPFunction(bandMaths_product_masks, wqpParams.params_bandExtractor_masks)
                               # 8. Save bands
                             # Define output paths
                                    sensorName = s3_image.name.split('_')[0]
                                    sensorDate = s3_image.name.split('_')[8]
                                    out_path_chl = os.path.join(cwd_path['out_wqp'],'chl',sensorName+'_CHL_IT_'+sensorDate+'_L1')
                                    out_path_tsm = os.path.join(cwd_path['out_wqp'],'tsm',sensorName+'_TSM_IT_'+sensorDate+'_L1')
                                    out_path_chl_no_clip = os.path.join(cwd_path['out_wqp_no_clip'],'chl',sensorName+'_CHL_IT_'+sensorDate+'_L1')
                                    out_path_tsm_no_clip = os.path.join(cwd_path['out_wqp_no_clip'],'tsm',sensorName+'_TSM_IT_'+sensorDate+'_L1')
                                    out_path_chl_no_mask = os.path.join(cwd_path['out_wqp_no_mask'],'chl',sensorName+'_CHL_IT_'+sensorDate+'_L1')
                                    out_path_tsm_no_mask = os.path.join(cwd_path['out_wqp_no_mask'],'tsm',sensorName+'_TSM_IT_'+sensorDate+'_L1')
                                    out_path_chl_cloud_mask = os.path.join(cwd_path['out_wqp_cloud'],'chl',sensorName+'_CHL_IT_'+sensorDate+'_L1')
                                    out_path_tsm_cloud_mask = os.path.join(cwd_path['out_wqp_cloud'],'tsm',sensorName+'_TSM_IT_'+sensorDate+'_L1')
                                    out_path_mask = os.path.join(cwd_path['out_masks'],sensorName+'_IT_'+sensorDate+'_L1')
                                    out_path_oa = os.path.join(cwd_path['out_oa'],sensorName+'_IT_'+sensorDate+'_L1')
                                    out_path_rrs = os.path.join(cwd_path['out_rrs'],sensorName+'_IT_'+sensorDate+'_L1')
                               # Save Bands
                                    wqpSNAP.exportProductBands(bandExtract_product_chl, out_path_chl, writeFormat)
                                    wqpSNAP.exportProductBands(bandExtract_product_tsm, out_path_tsm, writeFormat)
                                    wqpSNAP.exportProductBands(bandExtract_product_chl_no_clip, out_path_chl_no_clip, writeFormat)
                                    wqpSNAP.exportProductBands(bandExtract_product_tsm_no_clip, out_path_tsm_no_clip, writeFormat)
                                    wqpSNAP.exportProductBands(bandExtract_product_chl_no_mask, out_path_chl_no_mask, writeFormat)
                                    wqpSNAP.exportProductBands(bandExtract_product_tsm_no_mask, out_path_tsm_no_mask, writeFormat)
                                    wqpSNAP.exportProductBands(bandExtract_product_chl_cloud_mask, out_path_chl_cloud_mask, writeFormat)
                                    wqpSNAP.exportProductBands(bandExtract_product_tsm_cloud_mask, out_path_tsm_cloud_mask, writeFormat)
                                    wqpSNAP.exportProductBands(bandExtract_product_masks, out_path_mask, writeFormat)
                                    wqpSNAP.exportProductBands(bandExtract_product_oa, out_path_oa, writeFormat)
                                    wqpSNAP.exportProductBands(bandExtract_product_rrs, out_path_rrs, writeFormat)
                                # Append the result to the output_results list
                                    output_results.append({
                                        'name': s3_image.name,
                                        'out_path_chl': out_path_chl,
                                        'out_path_tsm': out_path_tsm,
                                        'out_path_chl_no_clip': out_path_chl_no_clip,
                                        'out_path_tsm_no_clip': out_path_tsm_no_clip,
                                        'out_path_chl_no_mask': out_path_chl_no_mask,
                                        'out_path_tsm_no_mask': out_path_tsm_no_mask,
                                        'out_path_chl_cloud_mask': out_path_chl_cloud_mask,
                                        'out_path_tsm_cloud_mask': out_path_tsm_cloud_mask,
                                        'out_path_mask': out_path_mask,
                                        'out_path_oa': out_path_oa,
                                        'out_path_rrs': out_path_rrs
                                    })
                                # Clean environment
                                    subset_product.dispose() 
                                    reproject_product.dispose()
                                    c2rcc_product.dispose()
                                    importVector_product.dispose()
                                    bandExtract_product_chl.dispose()
                                    bandExtract_product_tsm.dispose()
                                    bandExtract_product_chl_no_mask.dispose()
                                    bandExtract_product_tsm_no_mask.dispose()
                                    bandExtract_product_chl_cloud_mask.dispose()
                                    bandExtract_product_tsm_cloud_mask.dispose()
                                    bandExtract_product_rrs.dispose()
                                    bandExtract_product_oa.dispose()
                                    bandExtract_product_masks.dispose()
                                    del s3_image
                                    del subset_product
                                    del reproject_product
                                    del c2rcc_product
                                    del importVector_product
                                    del bandExtract_product_chl
                                    del bandExtract_product_tsm
                                    del bandExtract_product_chl_no_mask
                                    del bandExtract_product_tsm_no_mask
                                    del bandExtract_product_chl_cloud_mask
                                    del bandExtract_product_tsm_cloud_mask
                                    del bandExtract_product_rrs
                                    del bandExtract_product_oa
                                    del bandExtract_product_masks
                                except:
                             # Open a file with access mode 'a'
                                    file_object = open(os.path.join(cwd_path['out'],f'error_images_S3.txt'), 'a')
                             # Append 'hello' at the end of file
                                    file_object.write(s3_image.name)
                                    file_object.write("\n")
                            # Close the file
                                    file_object.close()
                        except Exception as e:
                            print("Error:", str(e))
                                
    except Exception as e:
        print("Error:", str(e))
    return output_results    




def wqp_s3_ins(start_date_str, end_date_str):
    
    in_path = f'./in/satellite_imagery/S3'
    out_path = f'./in/wqp/S3'
    cwd_path = wqpSNAP.inputParameters(in_path,out_path)

    #Read the mean temperature file
    df_t = pd.read_csv(os.path.join(cwd_path['in_parameters'],'meteoTemp_ins.csv'))
    df_t["Data"] = pd.to_datetime(df_t['Data'] ,format="%d/%m/%Y %H:%M:%S")
    df_t_keys = list(df_t.keys())

    # Temptative bounding box for the area of interest
    bbox = {
            'minLat' : 45.3,
            'maxLat' : 46.65,
            'minLon' : 7.9,
            'maxLon' : 9.95,
       }

    # Format output processed images
    writeFormat = 'GeoTIFF'

    wqpParams = wqpParams_S3
    output_results = []
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        for root, dirs, files in os.walk(in_path):
                for d in dirs:
                    if d != '.ipynb_checkpoints':
                        # 1. Read the product
                        s3_image = wqpSNAP.snapProduct(os.path.join(root, d, 'xfdumanifest.xml'), bbox)
                        s3_image.readSNAPProduct()
                        s3_image.name = s3_image.path.split('/')[-2]
                        print(s3_image.name)
                        try:
                        # Check if image is within the date range
                            image_date_str = s3_image.name.split('_')[8]
                            image_date = datetime.strptime(image_date_str, '%Y%m%dT%H%M%S')

                            if start_date <= image_date <= end_date:
                                
                                
  
                                try:
                              # 2. Update the bounding box for the subset selection
                                    params_subset = s3_image.updateSNAPSubset(wqpParams.params_subset)
                                    subset_product = wqpSNAP.executeSNAPFunction(s3_image.product, params_subset)
                              # 3. Reproject the subset
                                    reproject_product = wqpSNAP.executeSNAPFunction(subset_product, wqpParams.params_reproject)
                              # 4. Update the C2RCC temperature value. C2RCC wqp products
                                    params_C2RCC = s3_image.updateSNAPTemperature(df_t, wqpParams.params_C2RCC)
                                    c2rcc_product = wqpSNAP.executeSNAPFunction(reproject_product, params_C2RCC)
                              # 5. Import vector layer
                                    importVector_product = wqpSNAP.executeSNAPFunction(c2rcc_product, wqpParams.params_importVector)
                              # 6. Band Maths operations
                                    bandMaths_product_C2RCC = wqpSNAP.executeSNAPFunction(importVector_product, wqpParams.params_bandMaths)
                                    bandMaths_product_oa = wqpSNAP.executeSNAPFunction(reproject_product, wqpParams.params_bandMaths_oa)
                                    bandMaths_product_rrs = wqpSNAP.executeSNAPFunction(importVector_product, wqpParams.params_bandMaths_rrs)  
                                    bandMaths_product_masks = wqpSNAP.executeSNAPFunction(importVector_product, wqpParams.params_bandMaths_masks)
                             # 7. Extract bands
                             # Product bands to be extracted
                                    bandExtract_product_chl = wqpSNAP.executeSNAPFunction(bandMaths_product_C2RCC, wqpParams.params_bandExtractor_chl)
                                    bandExtract_product_tsm = wqpSNAP.executeSNAPFunction(bandMaths_product_C2RCC, wqpParams.params_bandExtractor_tsm)
                                    bandExtract_product_chl_no_clip = wqpSNAP.executeSNAPFunction(bandMaths_product_C2RCC, wqpParams.params_bandExtractor_chl_no_clip)
                                    bandExtract_product_tsm_no_clip = wqpSNAP.executeSNAPFunction(bandMaths_product_C2RCC, wqpParams.params_bandExtractor_tsm_no_clip)
                                    bandExtract_product_chl_no_mask = wqpSNAP.executeSNAPFunction(bandMaths_product_C2RCC, wqpParams.params_bandExtractor_chl_no_masks)
                                    bandExtract_product_tsm_no_mask = wqpSNAP.executeSNAPFunction(bandMaths_product_C2RCC, wqpParams.params_bandExtractor_tsm_no_masks)
                                    bandExtract_product_chl_cloud_mask = wqpSNAP.executeSNAPFunction(bandMaths_product_C2RCC, wqpParams.params_bandExtractor_chl_cloud_mask)
                                    bandExtract_product_tsm_cloud_mask = wqpSNAP.executeSNAPFunction(bandMaths_product_C2RCC, wqpParams.params_bandExtractor_tsm_cloud_mask)
                                    bandExtract_product_oa = wqpSNAP.executeSNAPFunction(bandMaths_product_oa, wqpParams.params_bandExtractor_oa)
                             # bandExtract_product_oa = wqpSNAP.executeSNAPFunction(bandMaths_product_oa, wqpParams.params_bandExtractor_oa_18)
                                    bandExtract_product_rrs = wqpSNAP.executeSNAPFunction(bandMaths_product_rrs, wqpParams.params_bandExtractor_rrs)
                                    bandExtract_product_masks = wqpSNAP.executeSNAPFunction(bandMaths_product_masks, wqpParams.params_bandExtractor_masks)
                               # 8. Save bands
                             # Define output paths
                                    sensorName = s3_image.name.split('_')[0]
                                    sensorDate = s3_image.name.split('_')[8]
                                    out_path_chl = os.path.join(cwd_path['out_wqp'],'chl',sensorName+'_CHL_IT_'+sensorDate+'_L1')
                                    out_path_tsm = os.path.join(cwd_path['out_wqp'],'tsm',sensorName+'_TSM_IT_'+sensorDate+'_L1')
                                    out_path_chl_no_clip = os.path.join(cwd_path['out_wqp_no_clip'],'chl',sensorName+'_CHL_IT_'+sensorDate+'_L1')
                                    out_path_tsm_no_clip = os.path.join(cwd_path['out_wqp_no_clip'],'tsm',sensorName+'_TSM_IT_'+sensorDate+'_L1')
                                    out_path_chl_no_mask = os.path.join(cwd_path['out_wqp_no_mask'],'chl',sensorName+'_CHL_IT_'+sensorDate+'_L1')
                                    out_path_tsm_no_mask = os.path.join(cwd_path['out_wqp_no_mask'],'tsm',sensorName+'_TSM_IT_'+sensorDate+'_L1')
                                    out_path_chl_cloud_mask = os.path.join(cwd_path['out_wqp_cloud'],'chl',sensorName+'_CHL_IT_'+sensorDate+'_L1')
                                    out_path_tsm_cloud_mask = os.path.join(cwd_path['out_wqp_cloud'],'tsm',sensorName+'_TSM_IT_'+sensorDate+'_L1')
                                    out_path_mask = os.path.join(cwd_path['out_masks'],sensorName+'_IT_'+sensorDate+'_L1')
                                    out_path_oa = os.path.join(cwd_path['out_oa'],sensorName+'_IT_'+sensorDate+'_L1')
                                    out_path_rrs = os.path.join(cwd_path['out_rrs'],sensorName+'_IT_'+sensorDate+'_L1')
                               # Save Bands
                                    wqpSNAP.exportProductBands(bandExtract_product_chl, out_path_chl, writeFormat)
                                    wqpSNAP.exportProductBands(bandExtract_product_tsm, out_path_tsm, writeFormat)
                                    wqpSNAP.exportProductBands(bandExtract_product_chl_no_clip, out_path_chl_no_clip, writeFormat)
                                    wqpSNAP.exportProductBands(bandExtract_product_tsm_no_clip, out_path_tsm_no_clip, writeFormat)
                                    wqpSNAP.exportProductBands(bandExtract_product_chl_no_mask, out_path_chl_no_mask, writeFormat)
                                    wqpSNAP.exportProductBands(bandExtract_product_tsm_no_mask, out_path_tsm_no_mask, writeFormat)
                                    wqpSNAP.exportProductBands(bandExtract_product_chl_cloud_mask, out_path_chl_cloud_mask, writeFormat)
                                    wqpSNAP.exportProductBands(bandExtract_product_tsm_cloud_mask, out_path_tsm_cloud_mask, writeFormat)
                                    wqpSNAP.exportProductBands(bandExtract_product_masks, out_path_mask, writeFormat)
                                    wqpSNAP.exportProductBands(bandExtract_product_oa, out_path_oa, writeFormat)
                                    wqpSNAP.exportProductBands(bandExtract_product_rrs, out_path_rrs, writeFormat)
                                # Append the result to the output_results list
                                    output_results.append({
                                        'name': s3_image.name,
                                        'out_path_chl': out_path_chl,
                                        'out_path_tsm': out_path_tsm,
                                        'out_path_chl_no_clip': out_path_chl_no_clip,
                                        'out_path_tsm_no_clip': out_path_tsm_no_clip,
                                        'out_path_chl_no_mask': out_path_chl_no_mask,
                                        'out_path_tsm_no_mask': out_path_tsm_no_mask,
                                        'out_path_chl_cloud_mask': out_path_chl_cloud_mask,
                                        'out_path_tsm_cloud_mask': out_path_tsm_cloud_mask,
                                        'out_path_mask': out_path_mask,
                                        'out_path_oa': out_path_oa,
                                        'out_path_rrs': out_path_rrs
                                    })
                                # Clean environment
                                    subset_product.dispose() 
                                    reproject_product.dispose()
                                    c2rcc_product.dispose()
                                    importVector_product.dispose()
                                    bandExtract_product_chl.dispose()
                                    bandExtract_product_tsm.dispose()
                                    bandExtract_product_chl_no_mask.dispose()
                                    bandExtract_product_tsm_no_mask.dispose()
                                    bandExtract_product_chl_cloud_mask.dispose()
                                    bandExtract_product_tsm_cloud_mask.dispose()
                                    bandExtract_product_rrs.dispose()
                                    bandExtract_product_oa.dispose()
                                    bandExtract_product_masks.dispose()
                                    del s3_image
                                    del subset_product
                                    del reproject_product
                                    del c2rcc_product
                                    del importVector_product
                                    del bandExtract_product_chl
                                    del bandExtract_product_tsm
                                    del bandExtract_product_chl_no_mask
                                    del bandExtract_product_tsm_no_mask
                                    del bandExtract_product_chl_cloud_mask
                                    del bandExtract_product_tsm_cloud_mask
                                    del bandExtract_product_rrs
                                    del bandExtract_product_oa
                                    del bandExtract_product_masks
                                except:
                             # Open a file with access mode 'a'
                                    file_object = open(os.path.join(cwd_path['out'],f'error_images_S3.txt'), 'a')
                             # Append 'hello' at the end of file
                                    file_object.write(s3_image.name)
                                    file_object.write("\n")
                            # Close the file
                                    file_object.close()
                        except Exception as e:
                            print("Error:", str(e))
                                
    except Exception as e:
        print("Error:", str(e))
    return output_results    