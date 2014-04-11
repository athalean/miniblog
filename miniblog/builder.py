import codecs
import os

from miniblog import SiteNamespace

def filename_for_url(output_folder, url):
    if url.endswith('/'):
        url += 'index.html'
    return os.path.join(output_folder, *url.split('/'))


def build_site(output_folder, content_folder, template_folder):
    namespace = SiteNamespace(content_folder, template_folder)
    for url, content in namespace.get_all():
        filename = filename_for_url(output_folder, url)
        dirname = os.path.dirname(filename)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        with codecs.open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
            print "Writing " + url + "..."