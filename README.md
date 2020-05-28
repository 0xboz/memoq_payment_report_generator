# Terra Translation Report Generator

Python automation script creating monthly/overall payment reports of Terra Translation

## How-to

In the terminal, run:

```shell
git clone https://github.com/0xboz/terra_translation_report_generator.git
cd terra_translation_report_generator
chmod +x run.py
```

Download the csv files from Terra Translation, and save them to a directory named `data/` under `terra_translation_report_generator/`.

**NOTE**: You might need to make a few changes in those csv files using **VS Code**. Make sure the project code (`E00XXX`) in each file consistent with the one listed on [Terra Translation MemoQ](https://terra.memoqworld.com/memoqweb/).

```shell
# Debian 10
python3 run.py
```

The reports are in the directory `report/`.
