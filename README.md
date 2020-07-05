# CSV Aggregator

## Overview
This basic script takes a set of Agilent QC Reports as CSV files (spaced with tabs) and compiles them into a single CSV file with only the information specified.

The necessary arguments are taken from a config JSON file, whose file path defaults to a local config.json file, but can be pointed to any properly formatted JSON file. To see a sample config.json file, see the sample below.

## The Steps
This script focuses on pulling out a set of common columns between the reports and publishes these once to the output file. It then pulls out the specified columns that differ between the reports, and joins them to the output file. The implementation doesn't do it in quite this order, but rather joins everything line-by-line for performance.

It also uses a provided name map file to label the columns that differ with a human readable name.

Finally, each value in the differing column is optionally transformed by a mathematical function (currently the only transformation supported is a base 2 logarithmic function).

This is all output to a CSV file with a name specified in the config file.

## Sample Config File
```
{
"source_files": ["/path/to/file_1_1.txt", "/path/to/file_1_2.txt", "/path/to/file_1_3.txt"],
"start_line": 10,
"common_headers": ["FeatureNum", "Row", "Col", "accessions", "chr_coord", "SubTypeMask", "SubTypeName", "Start", "Sequence", "ProbeUID", "ControlType", "ProbeName", "GeneName", "SystematicName", "Description"],
"additional_headers": ["gProcessedSignal"],
"name_map_file": "/path/to/name_map_file.csv",
"name_start_line": 5,
"output_file": "aggregated_data.csv"
}
```
* source_files
  * A list of QC Reports. These need to be the absolute paths to these files.
* start_line
  * start_line is the line in the QC Report where the column headers live. This is usually line 10.
* common_headers
  * A list of column headers whose corresponding columns are the same across the reports.
* additional_headers
  * A list of column headers whose corresponding columns will be different across the reports; these are the elements we want to aggregate.
* name_map_file
  * The absolute path to the name_map_file. This file should have (at the very least) a column of file path base names and a column of corresponding sample names.
* name_start_line
  * The line number at which the name mappings begin in the name_map_file (usually line 5)
* output_file
  * The desired name of the output file. Including the .csv extension here is recommended.

## How To Run
* Open Terminal (or another shell)
* Navigate to the directory where aggregator.py lives (should be next to this README).
  * The easiest way to do this is to write: `cd ` (which means "change directory") and then drag the folder icon that contains aggregator.py into the Terminal window.
  * This will paste the file path to the directory into Terminal, and should look something like this: `cd /Users/josephmin/Documents/apps/csv_agg`
  * Press enter or return, and this will take you into the csv_agg directory.
* Run the python code
```
python3 aggregator.py config.json
```
  * Here "python3" means to use Python 3 to run this python script. If you get an error that says "command not found: python3", then please look at "Installing Python".
  * aggregator.py is the name of the python script we want to run using python3
  * config.json is the file path to your config file. It doesn't have to be called config.json, but it does have to be formatted correctly. This can be the absolute path to the config file, but if config.json is inside the same folder as aggregator.py, you can just write config.json.
