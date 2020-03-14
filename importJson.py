import json

from bs4 import BeautifulSoup
from slimit import ast
from slimit.parser import Parser as JavascriptParser
from slimit.visitors import nodevisitor

with open('generals.io _ Season Rankings.html', 'r') as f:
    html = f.read()
soup = BeautifulSoup(html, 'html.parser')
tree = JavascriptParser().parse(soup.script.string)
obj = next(node.right for node in nodevisitor.visit(tree)
           if (isinstance(node, ast.Assign) and
               node.left.to_ecma() == 'window.__PRELOADED_STATE__'))
# HACK: easy way to parse the javascript object literal
data = json.loads(obj.to_ecma())  # NOTE: json format may be slightly different
# # assert data['activity']['type'] == 'read'
print(data)