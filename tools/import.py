#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2014 Niall Kavanagh <niall@kst.com>. All rights reserved.
"""

import boto.dynamodb2
from boto.dynamodb2.fields import HashKey, RangeKey, KeysOnlyIndex, AllIndex
from boto.dynamodb2.table import Table
from boto.dynamodb2.types import NUMBER
import argparse


def import_csv(filename, tablename):
    parser = argparse.ArgumentParser(description='Imports a GTFS feed to \
                                     DynamoDB')

    parser.add_argument('path', help='path to unzipped GTFS data')

    parser.add_argument('--urls', default='urls.txt', help='')

    args = parser.parse_args()


def main():
    pass

if __name__ == "__main__":
    main()
