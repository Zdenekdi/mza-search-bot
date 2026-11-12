import json

nodes = [
    # Level 0
    {"id": 1, "label": "Thomas Dyas\nz Bubnů", "group": "male", "title": "Nejstarší předek", "level": 0},
    {"id": 2, "label": "Anna Maria\n(* cca 1648, † 1708)", "group": "female", "title": "Manželka Thomase", "level": 0},
    
    # Level 1
    {"id": 3, "label": "Joannes Dyas\nMlynář (1710)", "group": "male", "title": "Syn Thomase a Anny Marie", "level": 1},
    
    # Level 2
    {"id": 4, "label": "Jakub Dias\n(* cca 1774, † 1838)", "group": "male", "title": "Pachtýř v Ivanovicích", "level": 2},
    {"id": 5, "label": "Elisabeth\n(† 1807)", "group": "female", "title": "1. manželka Jakuba", "level": 2},
    {"id": 6, "label": "Mariana\n(* cca 1771, † 1849)", "group": "female", "title": "2. manželka Jakuba", "level": 2},
    
    # Level 3 (Děti Jakuba a jejich manželé)
    {"id": 7, "label": "František Dias\n(* cca 1811)", "group": "male", "title": "Mlynářský mistr, Zlobice č.p. 15", "level": 3},
    {"id": 16, "label": "Theresia / Antonia", "group": "female", "title": "Manželka Františka", "level": 3},
    
    {"id": 8, "label": "Carl Dias", "group": "male", "title": "Pachtýř ve Zlobicích", "level": 3},
    {"id": 14, "label": "Elisabeth (m. Carla)", "group": "female", "title": "Manželka Carla", "level": 3},
    
    {"id": 9, "label": "Franz Dias\n(* cca 1799, † 1817)", "group": "male", "title": "Mlynářský tovaryš", "level": 3},
    {"id": 10, "label": "Johann Dias\n(* 1831, † 1831)", "group": "male", "title": "Zemřel na křeče", "level": 3},
    {"id": 11, "label": "Wenzel Dias", "group": "male", "title": "Sekerník z Vyškova", "level": 3},
    {"id": 12, "label": "Franziska Djas", "group": "female", "title": "Dcera", "level": 3},
    {"id": 13, "label": "Marianna Dias\n(* cca 1823, † 1872)", "group": "female", "title": "Dcera z č.p. 34", "level": 3},

    # Level 4 (Vnoučata Jakuba)
    {"id": 17, "label": "František Dias ml.", "group": "male", "title": "Syn a pokračovatel", "level": 4},
    {"id": 18, "label": "Joseph Dias\n(* 1838, † 1840)", "group": "male", "title": "Zemřel jako dítě", "level": 4},
    {"id": 19, "label": "Magdalena Franziska", "group": "female", "title": "Dcera Františka", "level": 4},
    {"id": 20, "label": "Antonia Dias\n(* cca 1828, † 1856)", "group": "female", "title": "Dcera z č.p. 30", "level": 4},
    {"id": 15, "label": "Rosalia Dias\n(† 1838)", "group": "female", "title": "Dcera Carla z č.p. 15", "level": 4},

    # Level 5
    {"id": 21, "label": "Jaroslav Dias", "group": "male", "title": "Dědeček", "level": 5},
    
    # Level 6
    {"id": 22, "label": "Zdeněk Dias st.", "group": "male", "title": "Otec", "level": 6},
    
    # Level 7
    {"id": 23, "label": "Bc. Zdeněk Dias\n(* 1991)", "group": "user", "title": "Pokračovatel rodu", "level": 7}
]

edges = [
    {"from": 1, "to": 2, "label": "manželé", "dashes": True},
    {"from": 1, "to": 3, "label": "otec"},
    {"from": 2, "to": 3, "label": "matka"},
    
    {"from": 3, "to": 4, "label": "otec"},
    
    {"from": 4, "to": 5, "label": "1. manželství", "dashes": True},
    {"from": 4, "to": 6, "label": "2. manželství", "dashes": True},
    
    {"from": 4, "to": 7, "label": "otec"},
    {"from": 6, "to": 7, "label": "matka"},
    {"from": 4, "to": 8, "label": "otec"},
    {"from": 6, "to": 8, "label": "matka"},
    {"from": 4, "to": 9, "label": "otec"},
    {"from": 5, "to": 9, "label": "matka"}, # Assuming first wife based on dates (1799)
    {"from": 4, "to": 10, "label": "otec"},
    {"from": 6, "to": 10, "label": "matka"},
    {"from": 4, "to": 11, "label": "otec"},
    {"from": 4, "to": 12, "label": "otec"},
    {"from": 4, "to": 13, "label": "otec"},
    {"from": 6, "to": 13, "label": "matka"},
    
    {"from": 8, "to": 14, "label": "manželé", "dashes": True},
    {"from": 8, "to": 15, "label": "otec"},
    {"from": 14, "to": 15, "label": "matka"},
    
    {"from": 7, "to": 16, "label": "manželé", "dashes": True},
    {"from": 7, "to": 17, "label": "otec"},
    {"from": 16, "to": 17, "label": "matka"},
    {"from": 7, "to": 18, "label": "otec"},
    {"from": 16, "to": 18, "label": "matka"},
    {"from": 7, "to": 19, "label": "otec"},
    {"from": 16, "to": 19, "label": "matka"},
    {"from": 7, "to": 20, "label": "otec"},
    {"from": 16, "to": 20, "label": "matka"},
    
    {"from": 17, "to": 21, "label": "přímá linie", "dashes": True},
    {"from": 21, "to": 22, "label": "otec"},
    {"from": 22, "to": 23, "label": "otec"}
]

html_template = f"""
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <title>Kompletní Grafický Rodokmen Dias</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            font-family: 'Outfit', sans-serif;
            color: white;
            overflow: hidden;
        }}
        #header {{
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            text-align: center;
            z-index: 10;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 15px 30px;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }}
        h1 {{ margin: 0; font-size: 24px; letter-spacing: 2px; }}
        p {{ margin: 5px 0 0 0; font-size: 14px; opacity: 0.8; }}
        #mynetwork {{
            width: 100vw;
            height: 100vh;
        }}
        .controls {{
            position: absolute;
            bottom: 20px;
            right: 20px;
            z-index: 10;
            background: rgba(0,0,0,0.5);
            padding: 10px;
            border-radius: 10px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div id="header">
        <h1>Kompletní Rodokmen Dias</h1>
        <p>Manželé vedle sebe, všechny extrahované generace z matrik</p>
    </div>
    
    <div class="controls">
        Kolečkem myši oddalujte/přibližujte. Tažením myší přesouvejte uzel.
    </div>

    <div id="mynetwork"></div>

    <script type="text/javascript">
        var nodes = new vis.DataSet({json.dumps(nodes)});
        var edges = new vis.DataSet({json.dumps(edges)});

        var container = document.getElementById('mynetwork');
        var data = {{
            nodes: nodes,
            edges: edges
        }};
        var options = {{
            nodes: {{
                shape: 'box',
                margin: 15,
                font: {{ size: 16, face: 'Outfit', color: '#ffffff', multi: true }},
                borderWidth: 2,
                shadow: true
            }},
            edges: {{
                width: 2,
                color: {{ color: 'rgba(255,255,255,0.4)', highlight: '#e6c27a' }},
                font: {{ align: 'middle', color: '#ffffff', strokeWidth: 0, size: 12 }},
                arrows: {{ to: {{ enabled: true, scaleFactor: 0.5 }} }},
                smooth: {{ type: 'cubicBezier', forceDirection: 'vertical', roundness: 0.4 }}
            }},
            groups: {{
                male: {{
                    color: {{ background: 'rgba(20, 50, 80, 0.7)', border: '#4facfe', highlight: {{ background: '#4facfe', border: '#ffffff' }} }}
                }},
                female: {{
                    color: {{ background: 'rgba(80, 20, 50, 0.7)', border: '#f093fb', highlight: {{ background: '#f093fb', border: '#ffffff' }} }}
                }},
                user: {{
                    color: {{ background: 'rgba(150, 100, 0, 0.8)', border: '#ffd700', highlight: {{ background: '#ffd700', border: '#ffffff' }} }},
                    font: {{ size: 20, bold: true }}
                }}
            }},
            layout: {{
                hierarchical: {{
                    direction: 'UD',
                    sortMethod: 'directed',
                    levelSeparation: 150,
                    nodeSpacing: 250,
                    treeSpacing: 300
                }}
            }},
            physics: {{
                enabled: true,
                hierarchicalRepulsion: {{
                    nodeDistance: 250,
                    springLength: 150
                }}
            }}
        }};
        var network = new vis.Network(container, data, options);
    </script>
</body>
</html>
"""

with open("/Users/zdenekdias/Desktop/Ultimatni_Graficky_Rodokmen_Komplet.html", "w") as f:
    f.write(html_template)
print("Updated HTML with spouses on the same level.")
