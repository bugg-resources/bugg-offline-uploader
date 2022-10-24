A script to upload audio files to Bugg that have been recorded offline.

To run the code:
```
python3 ./bugg/bugg.py --folder ./Downloads/data/
```

## Setting device locations

At the start of the upload for each device, the script will ask you to set the device location on the [app.bugg.xyz](app.bugg.xyz) website. 

If the device's location has not previously been registered on the web app, make sure you do this before continuing with the upload.

Even if it has, this is a good time to double check the location has been set correctly.

## Uploading data from one device

The folder structure is expected to be in the layout that the Bugg recording device uses:

    data
    ├── audio
    │   └── demo
    │       ├── bugg_RPiID-10000000123456
    │       │   └── conf_1126d6b
    │       │       ├── 2022-02-22T17_32_42.598Z.mp3
    │       │       └── 2022-02-22T17_37_45.631Z.mp3
    └── config.json

## Uploading data from multiple devices

You can batch upload from multiple Buggs if all the devices were using the same `config.json` files. 

In this case, the folder structure should be:

    data
    ├── audio
    │   └── demo
    │       ├── bugg_RPiID-10000000123456
    │       │   └── conf_1126d6b
    │       │       ├── 2022-02-22T17_32_42.598Z.mp3
    │       │       └── 2022-02-22T17_37_45.631Z.mp3
    │       └── bugg_RPiID-100000007891011
    │           └── conf_1126d6b
    │               ├── 2022-02-22T17_33_27.103Z.mp3
    │               └── 2022-02-22T17_38_19.394Z.mp3
    └── config.json
