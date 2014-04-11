import os
import re

import dateutil.parser
from jinja2 import Environment, FileSystemLoader
import markdown
from markupsafe import Markup

from namespaces import Pages, Categories


DEFAULT_URL = '/blog/%s/'
DEFAULT_TITLE = "unknown title"
DEFAULT_TEMPLATE = 'default.html'


class SiteNamespace(object):
    def __init__(self, content_folder, template_folder):
        self.env = Environment(loader=FileSystemLoader(template_folder), autoescape=True)
        self.pages = Pages(content_folder, self.env)
        self.categories = Categories(self.pages, self.env)

        self.namespaces = (self.categories, self.pages)
        for i in self.namespaces:
            if hasattr(i, 'get_mixins'):
                self.env.globals.update(i.get_mixins())

    def dispatch(self, url):
        for i in self.namespaces:
            p = i.dispatch(url)
            if p is not None:
                return p
        raise ValueError("URL could not be dispatched")

    def get_all(self):
        """
        Generate all possible sites in the namespace
        """
        for i in self.namespaces:
            for k in i.get_all():
                yield k


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
        env = self.page.namespace.env
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
            self.category = None
            return
        self.category = category

    def process_slug(self, slug):
        if slug is None:
            self.slug = os.path.basename(self.page.file_path).rsplit('.', 1)[0]
            return
        self.slug = slug

    def process_path(self, path):
        self.path = path

    def process_static(self, static):
        if static and static.lower() == 'true':
            self.static = True
        else:
            self.static = False


class Page(object):
    """
    A miniblog page.
    """

    def __init__(self, path, namespace):
        self.namespace = namespace
        self.file_path = path
        self.meta_path = path + ".meta"

        try:
            with open(self.meta_path, 'r') as f:
                self._meta = self.process_meta(f.read())
        except IOError:
            raise ValueError("%s has no meta file." % self.file_path)

        self.url = self.meta.path

    def get_path(self):
        """
        Generate a path for the
        """
        if self.meta.path:
            return self.meta.path
        else:
            return DEFAULT_URL % self.meta.slug

    def process_raw(self, text):
        """
        Process raw content text (e.g. Markdown) to prepare .content
        """
        self.content = markdown.markdown(text, safe_mode='escape')
        html = self.meta.template.render(page=self, content=Markup(self.content))
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

    @property
    def path(self):
        if not hasattr(self, '_path'):
            self._path = self.get_path()
        return self._path

    def __repr__(self):
        return "<miniblog.Page '%s'>" % self.meta.title


