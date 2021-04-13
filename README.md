# Disgaea RPG - Mine

## Script Requirements

- Python 3.6+

- UnityPy 1.7+
- requests

```cmd
pip install UnityPy
pip install requests
```

## Asset Download

Run ``download_assets.py`` to download the latest updates.
This script also directly extracts the downloaded assets.
The results are stored by default in ``/assets``


## Master Data Dumping

To get the decrypted and decoded masterdata you have to do following.

### Struct Update/Generation

1. open the Disgaea RPG APK as zip (WinRar, 7Zip, or rename it to .zip)
2. extract ``/lib/armeabi-v7a/libil2cpp.so`` and ``/assets/bin/Data/Managed/Metadata/global-metadata.dat``
3. download [Perfare/Il2CppDumper](https://github.com/Perfare/Il2CppDumper/releases)
4. run ``il2cppdumper.exe <libil2cpp.so path> <global-metadata.dat path> <output_path>`` (you can drag and drop the paths)
5. set the *dump_cs_path* in ``generate_structs.py`` to your output_path from before
6. run ``generate_structy.py`` 

### Master Data Decoding

1. install Disgaea RPG on any Android device and run it until you reach the screen after the login
2. navigate to ``/internal/Android/data/com.boltrend.disgaea.en/files/Boltrend/XDMaster``
3. move all files in this folder to your computer
4. set the *xdmaster_path* in ``export_bin.py`` to the folder you copied the files from before into
5. run ``export_bin.py``