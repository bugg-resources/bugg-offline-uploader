A script to upload audio files to Bugg that have been recorded offline.

```
python3 ./bugg/bugg.py --folder ./Downloads/SD-Card-Data/
```

And follow the on screen prompts.

The folder structure is expected to be in the layout that the Bugg recording device uses:

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
