#!/usr/bin/python
# -*- coding: utf-8 -*-
import pandas
import json
from tabulate import tabulate

def parse_to_list(body):
    try:
        df = pandas.DataFrame.from_records(body)
        return tabulate(df, headers='keys', tablefmt='psql', showindex=False)
    except ValueError as e:
        # for dataframe the dict must be flat and all lists of the same length
        # TODO myb do this with treelib in the future, needs to implement parser
        j = json.dumps(body, indent=4, sort_keys=True)
        for x in ['{', '}', ',', '"']:
            j = j.replace(x, '')
        return j.strip('\n\t')
    except:
        return body



