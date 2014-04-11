import os

CATEGORY_PATTERN = "/category/%s/"


class Pages(object):
    """
    A namespace containing several blog pages and meta pages (comments, tags, etc.)
    Combines blog posts and static pages. Static pages have page.meta.static == True.
    """

    def __init__(self, content_folder, environment):
        self.pages = {}
        self.env = environment
        self.populate_by_directory(content_folder)
        self.get_sorted_pages()

    def populate_by_directory(self, content_folder):
        """
        Include all files that
        """
        from miniblog import Page

        for path, dirs, files in os.walk(content_folder):
            for file in files:
                if not file.endswith('.meta'):
                    self.add_page(Page(os.path.join(path, file), self))

    def get_mixins(self):
        """
        Get template mixins. In this case, the ten most recent pages.
        """
        latest_pages = [page for page in self.get_sorted_pages() if not page.meta.static][:10]
        return {'latest_pages': latest_pages}

    def dispatch(self, path):
        page = self.pages.get(path, None)
        if page:
            return page.html
        return None

    def add_page(self, page):
        path = page.path
        if path in self.pages:
            raise ValueError('Duplicate page on path %s.' % path)
        self.pages[path] = page

    def get_sorted_pages(self):
        """
        Return all page objects sorted by date
        """
        if not hasattr(self, '_sorted'):
            self._sorted = sorted(self.pages.itervalues(), key=lambda p: p.meta.date or 0,
                                  reverse=True)
            length = len(self._sorted)
            for i, p in enumerate(self._sorted):
                p.next = self._sorted[i - 1] if i > 0 else None
                p.prev = self._sorted[i + 1] if i < length - 1 else None
        return self._sorted

    def get_all(self):
        """
        Get the HTML of every page in the container with path.
        """
        return ((path, page.html) for path, page in self.pages.iteritems())


class Category(object):
    """
    A category of pages.
    """

    def __init__(self, name, slug):
        self.name = name
        self.slug = slug
        self.pages = []
        self.url = CATEGORY_PATTERN % self.slug

    def add_page(self, p):
        self.pages.append(p)
        p.meta.category = self

    def __repr__(self):
        return "<Category '%s'>" % self.name


class Categories(object):
    """
    Namespace for category pages. Generated from a Pages namespace.
    """

    def __init__(self, pagecontainer, environment):
        self.categories = {}
        self.env = environment
        for p in pagecontainer.get_sorted_pages():
            category = p.meta.category
            if category:
                slug = category.replace(" ", '-').lower()
                self.categories.setdefault(slug, Category(category, slug)).add_page(p)

    def dispatch(self, url):
        cat_base = (CATEGORY_PATTERN % '')[:-1]
        if not url.startswith(cat_base):
            return None
        category = url[len(cat_base):-1]
        category = self.categories.get(category)
        if category is None:
            return None
        return self.render_category(category)

    def render_category(self, category):
        if category == '':
            return self.overview()
        return repr(category.pages)

    def overview(self):
        return repr(self.categories.keys())

    def get_all(self):
        yield (CATEGORY_PATTERN % '')[:-1], self.overview()
        for category in self.categories.itervalues():
            yield category.url, self.render_category(category)

    def get_mixins(self):
        """
        Get template mixins. In this case, all categories with their links
        """
        return {'categories': self.categories.values()}