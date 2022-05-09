# The MIT License (MIT)
#
# Copyright (c) 2015-present Rapptz
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
from docutils import nodes
from docutils.parsers.rst import Directive, directives, states
from docutils.parsers.rst.roles import set_classes


class details(nodes.General, nodes.Element):
    pass

class summary(nodes.General, nodes.Element):
    pass

def visit_details_node(self, node):
    self.body.append(self.starttag(node, 'details', CLASS=node.attributes.get('class', '')))

def visit_summary_node(self, node):
    self.body.append(self.starttag(node, 'summary', CLASS=node.attributes.get('summary-class', '')))
    self.body.append(node.rawsource)

def depart_details_node(self, node):
    self.body.append('</details>\n')

def depart_summary_node(self, node):
    self.body.append('</summary>')

class DetailsDirective(Directive):
    final_argument_whitespace = True
    optional_arguments = 1

    option_spec = {
        'class': directives.class_option,
        'summary-class': directives.class_option,
    }

    has_content = True

    def run(self):
        set_classes(self.options)
        self.assert_has_content()

        text = '\n'.join(self.content)
        node = details(text, **self.options)

        if self.arguments:
            summary_node = summary(self.arguments[0], **self.options)
            summary_node.source, summary_node.line = self.state_machine.get_source_and_line(self.lineno)
            node += summary_node

        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]

def setup(app):
    app.add_node(details, html=(visit_details_node, depart_details_node))
    app.add_node(summary, html=(visit_summary_node, depart_summary_node))
    app.add_directive('details', DetailsDirective)
