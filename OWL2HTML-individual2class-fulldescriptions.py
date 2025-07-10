

# -*- coding: utf-8 -*-
"""
Created on Tue Jun 10 2025
Generates HTML listing individuals with their classes, definitions, and descriptions.
@author: pascaliensis with ChatGPT 4o
"""

# pip install markdown2



from rdflib import Graph, RDF, RDFS, OWL, Namespace
from rdflib.namespace import SKOS
import markdown2





def markdown_to_html(md_text):
    """
    Convert Markdown to HTML using the markdown2 library with extras.

    Parameters:
        md_text (str): Markdown content

    Returns:
        str: HTML output
    """
    return markdown2.markdown(md_text, extras=["fenced-code-blocks", "tables", "strike", "task_list", "break-on-newline"])



# Optional: use either DCTERMS or older DC namespace
DC = Namespace("http://purl.org/dc/elements/1.1/")

# Load RDF/OWL file
owl_file_path = "data/input.owl"
g = Graph()
g.parse(owl_file_path, format="xml")

# Extract labels
label_lookup = {
    str(s): str(o)
    for s, _, o in g.triples((None, RDFS.label, None))
}

# Extract SKOS definitions
definition_lookup = {
    str(s): str(o)
    for s, _, o in g.triples((None, SKOS.definition, None))
}

# Extract DC descriptions (for tooltip)
description_lookup = {
    str(s): str(o)
    for s, _, o in g.triples((None, DC.description, None))
}

# Extract individuals and their types
individuals = {}
for s in g.subjects(RDF.type, OWL.NamedIndividual):
    uri = str(s)
    label = label_lookup.get(uri, uri.split("/")[-1])
    class_labels = []

    for cls in g.objects(s, RDF.type):
        if cls != OWL.NamedIndividual:
            cls_label = label_lookup.get(str(cls), str(cls).split("/")[-1])
            class_labels.append(cls_label)

    individuals[uri] = class_labels

# Generate HTML list
html_list = '<ul>\n'
for uri, classes in sorted(individuals.items(), key=lambda x: label_lookup.get(x[0], x[0])):
    label = label_lookup.get(uri, uri.split("/")[-1])
    class_lines = "<br> - " + "<br> - ".join(sorted(classes)) if classes else " (no class found)"
    
    definition = definition_lookup.get(uri, "")
    definition_html = f"<p><em><small>{definition}</small></em></p>" if definition else ""

    description = description_lookup.get(uri, "")
    if description != "" : description = markdown_to_html(description)
    description_html = (
        f'''
        <details class="accordion-desc">
            <summary></summary> 
            <div class="description-content">{description}</div>
        </details>
        ''' if description else ""
    )


    html_list += f'''
    <li>🎲 <strong>{label}</strong>
        {definition_html}
        <p style="margin-left:5em;"><small><b>Types: </b>{class_lines}</small></p>
        <p style="margin-left:5em;"><small>{description_html}</small></p>
    </li>\n'''
html_list += '</ul>'



# Wrap in full HTML document
html_document = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Individuals with Classes</title>
    <style>
    body {{ font-family: Arial, sans-serif; }}
    em {{ color: #555; }}

    ul {{ list-style-type: none; padding-left: 1em; }}
    li {{ margin-bottom: 1em; }}

    /* Accordion just for description */
    .accordion-desc {{
        border: 1px solid #ccc;
        border-radius: 6px;
        margin-top: 8px;
        margin-left: 5em;
        background: #f9f9f9;
        padding: 0.25em 0.5em;
        font-size: small;
    }}

    .accordion-desc summary {{
        font-weight: normal;
        cursor: pointer;
    }}

    .accordion-desc summary:hover {{
        background-color: #eee;
    }}

    .description-content {{
        padding: 0.5em 0 0.5em 1em;
        color: #333;
    }}
</style>



</head>
<body>
    <h1>TTRPG Individuals and Their Classes With Descriptions</h1>
    <p><a href="index.html">More information</a></p>
    <p><a href="https://creativecommons.org/licenses/by/4.0/deed.en">CC-BY 4.0</a>Individuals and Their Classes, Pascal Martinolli, 2025.</p>

    {html_list}
</body>
</html>
"""

# Save HTML to file
output_file = "docs/Visualisation_OWL_individuals_with_fulldescriptions.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_document)

print(f"HTML output saved to: {output_file}")

