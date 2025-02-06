# loc-history
This script generates a output file in CSV format with the number of LOCs (line of codes) over time.

The script go through git repository, doing many checkout, from far beggining to the more recent commit, counting the amount of LOCs of each revision.

> [!NOTE]
> All unsaved changes will be lost. Commit your changes in your local directory before using this tool. As of this writing, it works on the git repo in the current directory and cannot be directed elsewhere. Also, while running, it doesn't care about your keyboard interrupt. You'll have to kill it. 

## Usage

First, you will need to clone this repository in some place, after that, you can do:

```bash
cd path-to-my-repository
git checkout master
python path-to-loc-history/main.py --format=csv --output=dataset.csv
```

You also can do:

```bash
python path-to-loc-history/main.py > dataset.csv
```

The analised files are by default python source files, if you ant the change which files will have the LOCs counted, you can use the "suffix" parameter. For example:

```bash
python path-to-loc-history/main.py --suffix="html,py" > dataset.csv
```

In that case, the LOCs of html and python file will be summed together.


## CSV Output formats
The format is:

```
Date;LOCs
YYYY-MM-DD HH:mm:SSZ;NUMBER OF LOCs
```

For example:

```
Date;LOCs
2015-01-14 17:46:14-03:00;681
```
```
