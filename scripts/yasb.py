#!/usr/bin/env python3

# Copyright (c) 2022 Peter Bui <pbui@nd.edu>

# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

""" Yet Another Static Blogger """

import collections
import itertools
import sys

import dateutil.parser
import tornado.template
import markdown
import markdown.extensions.codehilite
import markdown.extensions.toc
import yaml

from datetime import datetime, timedelta

# Page

PageFields = 'title prefix icon navigation internal external body'.split()
Page       = collections.namedtuple('Page', PageFields)

def load_page_from_yaml(path):
    data     = yaml.safe_load(open(path))
    external = data.get('external', {}) or {}

    for k, v in external.items():
        data['external'][k] = yaml.safe_load(open(v))

    if 'prefix' not in data:
        data['prefix'] = ''

    return Page(**data)

def render_page(page):
    hilite = markdown.extensions.codehilite.CodeHiliteExtension(noclasses=True)
    toc    = markdown.extensions.toc.TocExtension(permalink=True)
    loader = tornado.template.Loader('templates')
    layout = u'''
{{% extends "base.tmpl %}}

{{% block body %}}
{}
{{% end %}}
'''.format(markdown.markdown(page.body, extensions=['extra', toc, hilite]))

    template = tornado.template.Template(layout, loader=loader)
    settings = {
        'page'      : page,
        'dateutil'  : dateutil,
        'itertools' : itertools,
    }
    print(template.generate(**settings).decode())

# Function to generate class dates
def generate_schedule(start_date, end_date, class_days):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    delta = timedelta(days=1)
    current_date = start_date
    schedule = []

    day_map = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
    class_days_numbers = [day_map[day] for day in class_days]

    while current_date <= end_date:
        if current_date.weekday() in class_days_numbers:
            schedule.append(current_date.strftime('%a %m/%d'))
        current_date += delta

    return schedule

def update_schedule_yaml(yaml_path):
    with open(yaml_path, 'r') as file:
        schedule_data = yaml.safe_load(file)

    # Access the start and end dates and class days from the YAML file
    start_date = schedule_data['semester_start']
    end_date = schedule_data['semester_end']
    class_days = schedule_data['class_days']

    # Generate the schedule
    generated_dates = generate_schedule(start_date, end_date, class_days)
    date_index = 0

    # Update the schedule with generated dates
    for theme in schedule_data['schedule']:
        if isinstance(theme, dict) and 'days' in theme:
            for day in theme['days']:
                if date_index < len(generated_dates):
                    day['date'] = generated_dates[date_index]
                    date_index += 1

    # Write the updated schedule back to the YAML file
    with open(yaml_path, 'w') as file:
        yaml.dump(schedule_data, file)

# Main Execution

def main():
    # Update the schedule.yaml with generated dates
    update_schedule_yaml('static/yaml/schedule.yaml')

    for path in sys.argv[1:]:
        page = load_page_from_yaml(path)
        render_page(page)

if __name__ == '__main__':
    main()

# vim: set sts=4 sw=4 ts=8 expandtab ft=python:
