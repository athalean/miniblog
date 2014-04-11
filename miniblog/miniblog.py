import os
import re

import dateutil.parser
from jinja2 import Environment, FileSystemLoader


DEFAULT_CATEGORY = "uncategorized"
DEFAULT_TITLE = "unknown title"
DEFAULT_TEMPLATE = 'default.html'


class PageTree(object):
    """
    A tree containing several blog pages
    """
    def __init__(self, content_folder, template_folder):
        self.pages = {}
        self.env = Environment(loader=FileSystemLoader(template_folder))
        self.populate_by_directory(content_folder)

    def populate_by_directory(self, path):
        stack = [path]
        while stack:
            item = stack.pop()
            if os.path.isdir(item):
                stack.extend(os.path.join(item, newitem) for newitem in os.listdir(item) if
                             not newitem.endswith('.meta'))
                continue
            self.add_page(Page(item, self))

    def page_for_path(self, path):
        return self.pages[path]

    def add_page(self, page):
        path = page.path
        if path in self.pages:
            raise ValueError('Duplicate page on path %s.' % path)
        self.pages[path] = page


SPLIT_REX = re.compile(r'[ ,;]')


class PageMeta(object):
    """
    Meta information about a page.
    """

    def __init__(self, page, metadict):
        """
        Call all class methods starting with 'process_'.
        """
        self.page = page
        for name, f in [(name, f) for name, f in self.__class__.__dict__.iteritems() if
                        name.startswith('process_')]:
            f(self, metadict.get(name[8:], None))

    def process_title(self, title):
        self.title = title or DEFAULT_TITLE

    def process_date(self, date):
        self.date = dateutil.parser.parse(date)

    def process_template(self, template):
        env = self.page.tree.env
        if template is None:
            self.template = env.get_template(DEFAULT_TEMPLATE)
            return
        self.template = env.get_template(template)

    def process_tags(self, tags):
        if tags is None:
            self.tags = []
            return
        self.tags = SPLIT_REX.split(tags)

    def process_category(self, category):
        if category is None:
            self.category = DEFAULT_CATEGORY
            return
        self.category = category.lower()

    def process_slug(self, slug):
        if slug is None:
            self.slug = os.path.basename(self.page.file_path).rsplit('.',1)[0]
            return
        self.slug = slug


class Page(object):
    """
    A miniblog page.
    """

    def __init__(self, path, tree):
        self.file_path = path
        self.tree = tree
        self.meta_path = path + ".meta"

        with open(self.meta_path, 'r') as f:
            self._meta = self.process_meta(f.read())

        with open(self.file_path, 'r') as f:
            self._html = self.process_raw(f.read())

        self.path = '/'+self.meta.slug

    def process_raw(self, text):
        """
        Process raw content text (e.g. Markdown) to prepare .content
        """
        self.content = text
        html = self.meta.template.render(page=self, content=text)
        return html

    def process_meta(self, text):
        """
        Process raw metadata file.
        """
        lines = text.split("\n")
        attributes = [line.split(":", 1) for line in lines]
        # build a dict with all values in the .meta file
        metadict = dict((title.lower().strip(), content.strip()) for title, content in attributes)
        return PageMeta(self, metadict)

    @property
    def meta(self):
        if not hasattr(self, '_meta'):
            self._meta = self.process_meta(open(self.meta_path, 'r').read())
        return self._meta

    @property
    def html(self):
        if not hasattr(self, '_html'):
            self._html = self.process_raw(open(self.file_path, 'r').read())
        return self._html