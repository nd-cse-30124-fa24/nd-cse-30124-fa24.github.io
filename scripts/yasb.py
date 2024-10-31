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
def generate_schedule(start_date, end_date, class_days, holidays, existing_schedule):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    delta = timedelta(days=1)
    current_date = start_date
    schedule = []

    day_map = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
    class_days_numbers = [day_map[day] for day in class_days]

    # Convert holiday start dates to datetime objects
    holiday_periods = []
    for holiday in holidays:
        holiday_start = datetime.strptime(f"{start_date.year}-{holiday['start']}", '%Y-%m-%d')
        holiday_periods.append((holiday_start, holiday['length'], holiday['name']))

    # Iterate over existing schedule
    for theme in existing_schedule:
        if 'days' in theme:
            new_days = []
            for day in theme['days']:
                day_date = datetime.strptime(day['date'], '%a %m/%d')
                # Check if the current date falls within any holiday period
                holiday_name = None
                for holiday_start, length, name in holiday_periods:
                    if holiday_start <= day_date < holiday_start + timedelta(days=length * 7 // len(class_days)):
                        holiday_name = name
                        break

                if holiday_name:
                    # Add a new theme for the holiday
                    schedule.append({
                        'name': holiday_name,
                        'days': [{'date': day['date'], 'topics': holiday_name}]
                    })
                else:
                    # Keep the existing class day
                    new_days.append(day)

            if new_days:
                schedule.append({'name': theme['name'], 'days': new_days})
        else:
            schedule.append(theme)

    return schedule

def update_schedule_yaml(yaml_path):
    with open(yaml_path, 'r') as file:
        schedule_data = yaml.safe_load(file)

    start_date = schedule_data['semester_start']
    end_date = schedule_data['semester_end']
    class_days = schedule_data['class_days']
    holidays = schedule_data['holidays']
    existing_schedule = schedule_data['schedule']

    # Generate the schedule
    updated_schedule = generate_schedule(start_date, end_date, class_days, holidays, existing_schedule)

    # Update the schedule with generated dates
    schedule_data['schedule'] = updated_schedule

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
