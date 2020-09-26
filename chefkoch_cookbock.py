#!/usr/bin/env python3

from argparse import ArgumentParser
from bs4 import BeautifulSoup
from pathlib import Path


def cleanup(soup):
    logo = soup.find('div', class_='print__logos').parent.parent.parent
    logo.decompose()

    photo = soup.find('figure')
    photo.decompose()


def extract_recipe(soup):
    recipe = soup.find('main').extract()
    cleanup(recipe)

    noBreak = soup.new_tag('div')
    noBreak['class'] = 'noPageBreak'
    noBreak.append(recipe)
    return noBreak


def create_template(f):
    with f.open() as f:
        template = BeautifulSoup(f, features='lxml')

    recipes_end = template.find('main').next_sibling
    recipes_end.insert_before(extract_recipe(template))

    # add style to ensure that none of the recipies has a page break inside for printing
    style = template.new_tag('style')
    style.string = '.noPageBreak { page-break-inside: avoid; }'
    template.find('meta').insert_after(style)

    return template, recipes_end


def create_cookbook(dir_):
    cookbook = dir_ / 'cookbook.html'
    cookbook.unlink(missing_ok=True)

    files = sorted(f for f in dir_.iterdir()
                   if f.is_file() and f.suffix == '.html')
    if not files:
        return

    template, recipes_end = create_template(files.pop(0))

    for f in files:
        with f.open() as f:
            soup = BeautifulSoup(f, features='lxml')
            recipe = extract_recipe(soup)
            recipes_end.insert_before(recipe)

    cookbook.write_text(template.prettify())


def main():
    parser = ArgumentParser(
        description='Collect downloaded print versions of Chefkoch recipes into one html file.')
    parser.add_argument('directories', metavar='DIR', type=Path, nargs='*', default=[Path.cwd()],
                        help='Collects recipes in each directory in cookbook.html. Default is current working directory.')

    args = parser.parse_args()

    for dir_ in args.directories:
        create_cookbook(dir_)


if __name__ == '__main__':
    main()
