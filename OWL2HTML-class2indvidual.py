# -*- coding: utf-8 -*-
"""
Created on Tue Jun 10 13:31:13 2025

@author: pascaliensis, with Anthropic Claude Sonnet 4 
"""

# pip install rdflib


from rdflib import Graph, RDF, RDFS, OWL

# Reload the OWL file
owl_file_path = "data/input.owl"
g = Graph()
g.parse(owl_file_path, format="xml")

# Extract classes and subclass relationships
classes = set(g.subjects(RDF.type, OWL.Class))
hierarchy = {}
for cls in classes:
    for parent in g.objects(cls, RDFS.subClassOf):
        if isinstance(parent, str) or parent.startswith("http"):
            hierarchy.setdefault(str(parent), []).append(str(cls))

# Identify root classes
all_children = {child for children in hierarchy.values() for child in children}
roots = set(hierarchy.keys()) - all_children

# Build tree from hierarchy
def build_tree(root, hierarchy):
    return {
        'name': root,
        'children': [build_tree(child, hierarchy) for child in hierarchy.get(root, [])]
    }

forest = [build_tree(root, hierarchy) for root in roots]

# Extract labels
label_lookup = {}
for s, p, o in g.triples((None, RDFS.label, None)):
    label_lookup[str(s)] = str(o)

# Extract individuals by class
individuals_by_class = {}
for s in g.subjects(RDF.type, OWL.NamedIndividual):
    label = label_lookup.get(str(s), str(s).split("/")[-1])
    for cls in g.objects(s, RDF.type):
        if cls != OWL.NamedIndividual:
            individuals_by_class.setdefault(str(cls), []).append(label)

# Function to render tree to HTML with individuals
def tree_to_html_with_individuals(tree):
    uri = tree['name']
    label = label_lookup.get(uri, uri.split("/")[-1])
    individuals = individuals_by_class.get(uri, [])
    individual_text = f": <sup><br> - {';<br> - '.join(individuals)}</sup>" if individuals else ""
    html = f"<li>{label}{individual_text}"
    if tree['children']:
        html += "<ul>" + "".join(tree_to_html_with_individuals(child) for child in tree['children']) + "</ul>"
    html += "</li>"
    return html

# Generate HTML tree
html_tree = "<ul>" + "".join(tree_to_html_with_individuals(t) for t in forest) + "</ul>"

# Wrap in full HTML document
html_document = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>OWL Class Hierarchy with Individuals</title>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        ul {{ list-style-type: none; }}
        li::before {{ content: "📂 "; }}
    </style>
</head>
<body>
    <h1>OWL Class Hierarchy with Individuals</h1>
    {html_tree}
<p><a href="https://creativecommons.org/licenses/by/4.0/deed.en">CC-BY 4.0</a> Pascal Martinolli</p>
</body>
</html>
"""

# Save to file
html_output_path = "docs/Visualisation_OWL_class_tree_with_individuals.html"
with open(html_output_path, "w", encoding="utf-8") as f:
    f.write(html_document)

html_output_path
