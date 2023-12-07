from jinja2 import Environment, FileSystemLoader


class html_render:
    def __init__(self, template_path):
        self.template_path = template_path

    def make_html(self, title, files):
        file_loader = FileSystemLoader(self.template_path)
        env = Environment(loader=file_loader)
        template = env.get_template("template.html")
        return template.render(title=title, files=files)
