#!/usr/bin/env python3

import argparse, csv, math, json, os, queue
from contextlib import ExitStack

def get_name_map(name_map_file_path, name_start_line):
    name_map = {}
    with open(name_map_file_path, 'r') as name_map_file:
        map_reader = csv.reader(name_map_file, delimiter=',')
        row_num = 0
        for row in map_reader:
            row_num += 1
            if row_num < name_start_line:
                continue
            else:
                # Hardcoded for now, we expect input to be clean
                name_map[row[0]] = row[1]
    return name_map

def log(str_val):
    return str(math.log(float(str_val), 2))

def main():
    parser = argparse.ArgumentParser(description='Aggregate Agilent data from multiple CSV files.')
    parser.add_argument('config_file_path', nargs='?', metavar='config', default='config.json',
                       help='Path to the config json file')
    args = parser.parse_args()

    configs = {}
    with open(args.config_file_path) as config_json_file:
        configs = json.load(config_json_file)

    name_map = get_name_map(configs["name_map_file"], configs["name_start_line"])
    common_headers = set(configs['common_headers'])
    additional_headers = set(configs['additional_headers'])
    common_columns = set([])
    additional_columns = set([])
    supported_transforms = {'log': log}
    if configs['transform'] and configs['transform'].lower() in supported_transforms.keys():
        transform = supported_transforms[configs['transform']]

    # Open the write context first, so we always have access to the output
    with open(configs['output_file'], 'w', newline='\n') as output_file:
        csv_writer = csv.writer(output_file, delimiter=',')
        # Then open an ExitStack of read contexts to open all readers
        with ExitStack() as stack:
            source_file_names = [
                os.path.splitext(os.path.basename(filename))[0]
                for filename in configs['source_files']
            ]
            input_files = [
                stack.enter_context(open(filename, 'r', newline='\n'))
                for filename in configs['source_files']
            ]
            csv_readers = [
                csv.reader(csv_file, delimiter='\t')
                for csv_file in input_files
            ]
            row_num = 0
            to_write = []
            first_reader = csv_readers.pop(0)
            first_file_name = source_file_names.pop(0)
            for row in first_reader:
                to_write = []
                row_num += 1
                if row_num < configs["start_line"]:
                    # Make sure we move through the other csv files too
                    for csv_reader in csv_readers:
                        next(csv_reader)
                    continue

                for i in range(len(row)):
                    # If we're at the header row, set which columns we need.
                    # This is our first file, so set the common headers and the
                    # additional headers.
                    if row_num == configs["start_line"]:
                        if row[i] in common_headers:
                            common_columns.add(i)
                            to_write.append(row[i])
                        elif row[i] in additional_headers:
                            additional_columns.add(i)
                            # Map name, and write new name here
                            to_write.append(name_map[first_file_name] + '_' + row[i])
                    else:
                        if i in common_columns:
                            to_write.append(row[i])
                        elif i in additional_columns:
                            if transform:
                                to_write.append(transform(row[i]))
                            else:
                                to_write.append(row[i])

                for i in range(len(csv_readers)):
                    csv_reader = csv_readers[i]
                    filename = source_file_names[i]
                    additional_row = next(csv_reader)
                    for j in range(len(additional_row)):
                        # If we're at the header row, set which columns we need.
                        # Here we just need the new line
                        if row_num == configs["start_line"]:
                            if additional_row[j] in additional_headers:
                                to_write.append(name_map[filename] + '_' + additional_row[j])
                        else:
                            if j in additional_columns:
                                if transform:
                                    to_write.append(transform(additional_row[j]))
                                else:
                                    to_write.append(additional_row[j])
                csv_writer.writerow(to_write)



if __name__ == '__main__':
    main()
