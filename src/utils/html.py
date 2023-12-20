from jinja2 import Environment, FileSystemLoader


class html_render:
    def __init__(self, template_path, template_name):
        self.template_path = template_path
        self.template_name = template_name if template_name else "template.html"

    def load_template(self, template_name):
        self.template_name = template_name

    def make_html(self, title, files):
        file_loader = FileSystemLoader(self.template_path)
        env = Environment(loader=file_loader)
        template = env.get_template(self.template_name)
        return template.render(title=title, files=files)
