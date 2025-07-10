# -*- coding: utf-8 -*-
"""
Created on Tue Jun 10 18:12:00 2025

@author: pascaliensis with ChatGPT 4o
"""


from rdflib import Graph, RDF, RDFS, OWL

# Load the OWL file
owl_file_path = "data/input.owl"
g = Graph()
g.parse(owl_file_path, format="xml")

# Extract labels for nicer display
label_lookup = {}
for s, _, o in g.triples((None, RDFS.label, None)):
    label_lookup[str(s)] = str(o)

# Extract all individuals and their types (excluding owl:NamedIndividual)
individuals = {}
for s in g.subjects(RDF.type, OWL.NamedIndividual):
    ind_label = label_lookup.get(str(s), str(s).split("/")[-1])
    class_labels = []
    for cls in g.objects(s, RDF.type):
        if cls != OWL.NamedIndividual:
            class_label = label_lookup.get(str(cls), str(cls).split("/")[-1])
            class_labels.append(class_label)
    individuals[ind_label] = class_labels

# Generate HTML list
html_list = "<ul>\n"
for individual, classes in sorted(individuals.items()):
    class_lines = "<br> - " + "<br> - ".join(sorted(classes)) if classes else " (no class found)"
    html_list += f"<li><strong>{individual}</strong>: <sup>{class_lines}</sup></li>\n"
html_list += "</ul>"

# Wrap in HTML document 
# or 🎲 or ♟️
html_document = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Individuals and Their Classes</title>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        ul {{ list-style-type: none; }}
        li::before {{ content: "♞ "; }}    
    </style>
</head>
<body>
    <h1>Individuals and Their Classes</h1>
    {html_list}
<p><a href="https://creativecommons.org/licenses/by/4.0/deed.en">CC-BY 4.0</a> Pascal Martinolli</p>
</body>
</html>
"""

# Save to file
output_file = "docs/Visualisation_OWL_individuals_with_classes.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_document)

print(f"HTML output saved to: {output_file}")
