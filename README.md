# loc-history
This script generates a output file in CSV or JSON format with the number of LOCs (line of codes) over time.

The script go through git repository, doing many checkout, from far beggining to the more recent commit, counting the amount of LOCs of each revision.

## Usage

First, you will need to clone this repository in some place, after that, you can do:

```bash
cd path-to-my-repository
git checkout master
python path-to-loc-history/main.py --format=csv --output=dataset.csv
```

You also can do:

```bash
python path-to-loc-history/main.py --format=csv > dataset.csv
```

The analised files are by default python source files, if you ant the change which files will have the LOCs counted, you can use the "suffix" parameter. For example:

```bash
python path-to-loc-history/main.py --suffix="html,py" --format=csv > dataset.csv
```

In that case, the LOCs of html and python file will be summed together.


## Output formats
Actually two output formats are supported:

#### CSV
Whose format is:

```
Date;LOCs
YYYY-MM-DD HH:mm:SSZ;NUMBER OF LOCs
```

For example:

```
Date;LOCs
2015-01-14 17:46:14-03:00;681
```

#### JSON
Whose format is:

```
{
    "YYYY-MM-DD HH:mm:SSZ": NUMBER OF LOCs
}
```

For example:

```
{
   "2015-01-14 17:46:14-03:00": 681,
}
```
