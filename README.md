# memoQ Payment Report Generator

Python automation script creating monthly/overall memoQ payment reports

## How-to

In the terminal, run:

```shell
git clone https://github.com/0xboz/memoq_payment_report_generator.git
cd memoq_payment_report_generator
```

Download the csv files from memoQ web interface, and save them to a directory named `data/` under `memoq_payment_report_generator/`.

**NOTE**: You might need to make a few changes in those csv files using **VS Code**. Make sure the project code (`E00XXX`) in each file consistent with the one listed on [MemoQ web interface](https://terra.memoqworld.com/memoqweb/).

```shell
# Debian 10
python3 run.py
```

The reports are in the directory `report/`.
