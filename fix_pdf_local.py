import base64
import json
import os
import urllib.request

mermaid_code = """
graph TD
    classDef root fill:#ffcc99,stroke:#333,stroke-width:2px,color:black;
    classDef branch fill:#e6f2ff,stroke:#66b3ff,stroke-width:2px,color:black;
    classDef main fill:#b3e6b3,stroke:#33cc33,stroke-width:2px,color:black;
    classDef current fill:#ffd700,stroke:#cca300,stroke-width:3px,color:black;

    ROOT_17["Nejstarší zmapovaní předci<br/>(konec 17. století)"]:::root
    ROOT_17 --- BARBARA["Barbara Dies<br/>(*cca 1687 – †1792)<br/>Zlobice"]:::branch
    ROOT_17 --- THOMAS["Thomas Dyas<br/>(Praha, Bubny)"]:::branch
    THOMAS --- ANNA["Anna Maria<br/>(*cca 1648 – †1708)<br/>manželka Thomase"]:::branch
    
    ROOT_17 -.-> ZLOB_ANC["Zlobická větev (18. století)"]:::root
    ZLOB_ANC --- IOANN["Jan (Ioann) Dias"]:::branch
    ZLOB_ANC --- MARIANNA_R["Marianna Řeznarová<br/>(dcera Jiřího Řeznara)"]:::branch
    IOANN --- ANTONIUS["Antonín Dias<br/>(pokřtěn 1783, Zlobice)"]:::branch
    MARIANNA_R --- ANTONIUS
    
    ROOT_17 -.-> WEN_FR["Ivanovická větev (konec 18. století)"]:::root
    WEN_FR --- VACLAV["Václav (Wenceslaus) Dijas<br/>(Ivanovice)"]:::main
    WEN_FR --- FRANTISKA["Františka"]:::main
    
    VACLAV --> JAKUB["Jakub Dias<br/>(Panský mlynář, Ivanovice)"]:::main
    FRANTISKA --> JAKUB
    
    JAKUB --- MARIANA_K["Mariana Kinzová<br/>(*cca 1771 – †1849, Zlobice)"]:::main
    
    MARIANA_K --> FRANTISEK["František Dias (*cca 1811)<br/>(Mistr mlynářský, Zlobice)"]:::main
    JAKUB --> FRANTISEK
    
    MARIANA_K --> IGNAC["Ignác Dias<br/>(pokřtěn v Ivanovicích)"]:::branch
    JAKUB --> IGNAC
    
    WEN_FR --- MARTIN["Martin Dias<br/>(Svatba 1798 s Marianou Tisslovnou)"]:::branch
    WEN_FR --- DYAS_1833["Neznámý Dyas<br/>(Svatba 1833 s Franziskou)"]:::branch

    FRANTISEK --- WIFE1["1. Anna Dvořáková<br/>(Svatba 1838)"]:::main
    FRANTISEK --- WIFE2["2. Mariana<br/>(Svatba 1844)"]:::main
    
    FRANTISEK -.-> LATE_19["Potomci a pokračovatelé rodu<br/>(Konec 19. a začátek 20. století)"]:::root
    
    LATE_19 --- JAN["Jan Dias<br/>(Mlynář v Ivanovicích do r. 1911)"]:::branch
    LATE_19 --- ADOLF["Adolf Dyas<br/>(Svatba 1925, Anežka Procházková)"]:::branch
    LATE_19 --- LUDVIK["Ludvík Dyas<br/>(Svatba 1925, Ludmila Smékalová)"]:::branch
    
    LATE_19 -.-> JAROSLAV["Jaroslav Dias<br/>(Dědeček)"]:::main
    JAROSLAV --> ZDENEK_SR["Zdeněk Dias<br/>(Otec)"]:::main
    ZDENEK_SR --> ZDENEK_JR["Bc. Zdeněk Dias (*1991)<br/>(Vy)"]:::current
"""

state = {
    "code": mermaid_code,
    "mermaid": {"theme": "default"}
}
json_state = json.dumps(state)
b64_state = base64.urlsafe_b64encode(json_state.encode('utf-8')).decode('utf-8')
img_url = f"https://mermaid.ink/img/{b64_state}"

# Download image
req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        img_data = response.read()
    img_b64 = base64.b64encode(img_data).decode('utf-8')
    img_src = f"data:image/jpeg;base64,{img_b64}"
    print("Obrázek stažen úspěšně.")
except Exception as e:
    print(f"Chyba stahování: {e}")
    img_src = ""

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Rodokmen rodiny Diasů</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; color: #333; }}
        h1, h2 {{ color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
        .center {{ text-align: center; margin-top: 30px; }}
        img {{ max-width: 100%; height: auto; }}
    </style>
</head>
<body>
    <h1>Rodokmen rodiny Diasů – Výsledky hloubkové analýzy matrik</h1>
    <p>Tento dokument je výsledkem rozsáhlé automatizované analýzy 17 historických matrik z oblasti Ivanovic na Hané, Zlobic a okolí (MZA).</p>
    
    <h2>1. Nejstarší generace a raná přítomnost (17. století)</h2>
    <ul>
        <li><strong>Barbara Dies (* cca 1687 – † 13. července 1792)</strong>: Prabába rodu (zemřela ve Zlobicích v 105 letech).</li>
        <li><strong>DIAS 1696</strong>: Nejstarší nalezený písemný záznam z MZA.</li>
        <li><strong>Thomas Dyas a Anna Maria (* cca 1648 – † 23. dubna 1708)</strong>: Pražská mlynářská větev (Bubny).</li>
    </ul>

    <h2>2. Prapředci z přelomu 18. a 19. století</h2>
    <ul>
        <li><strong>Václav (Wenceslaus) Dijas a Františka</strong>: Nově objevení rodiče panského mlynáře Jakuba Diase (Ivanovice).</li>
        <li><strong>Jan (Ioann) Dias a Marianna Řeznarová</strong>: Zlobická větev.</li>
    </ul>

    <h2>3. Panský mlynář Jakub Dias a Mariana Kinzová</h2>
    <ul>
        <li><strong>Jakub Dias</strong> (syn Václava a Františky): Pachtýř (nájemní mlynář) na panském mlýně v Ivanovicích na Hané.</li>
        <li><strong>Manželka: Mariana Kinzová</strong> (* cca 1771 – † 18. února 1849): Zemřela jako vdova ve Zlobicích u syna Františka.</li>
    </ul>

    <h2>4. Mistr mlynářský František Dias (Zlobice)</h2>
    <ul>
        <li><strong>František Dias</strong>: Mistr mlynářský ve Zlobicích (budova č.p. 15), narozen cca 1811.</li>
        <li>Svatby: S Annou Dvořákovou (1838) a s Marianou (1844).</li>
    </ul>

    <h2>5. Mlynářská a novodobá rodová návaznost (19. a 20. století)</h2>
    <ul>
        <li><strong>Jan Dias</strong>: Mlynář v Ivanovicích do r. 1911.</li>
        <li><strong>Adolf a Ludvík Dyas</strong>: Sňatky 1925 v Ivanovicích.</li>
    </ul>

    <h2>6. Grafický rodokmen</h2>
    <div class="center">
        <img src="{img_src}" alt="Rodokmen">
    </div>
</body>
</html>
"""

with open("/tmp/dias_family_tree_fixed2.html", "w") as f:
    f.write(html_content)

print("Vytvořeno HTML pro tisk do PDF")
