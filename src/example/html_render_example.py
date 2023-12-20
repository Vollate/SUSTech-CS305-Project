from utils import html

render = html.html_render("templates","template.html")
title = "foo"
files = [{"path": "p1", "name": "n1"}, {"path": "p2", "name": "n2"}]
out = render.make_main_page(title, files)
print(out)
