import os

md_content = """# Kompletní rodokmen rodu Dias (mlynáři v Ivanovicích na Hané a Zlobicích)

Tento dokument shrnuje nejnovější historické objevy a kompletní genealogickou linii rodu Dias až do 17. století. Rodina vlastnila mlýny v Ivanovicích na Hané a později ve Zlobicích.

## Přímá linie předků (od nejstaršího po Bc. Zdeňka Diase)

1. **Václav Mlynář (Václav Dias nejstarší)**
   * Narozen: pravděpodobně kolem r. 1600 nebo dříve
   * Povolání: mlynář v Ivanovicích na Hané
   * *Poznámka: Zmíněn v Lánovém rejstříku (1669-1679) jako předchozí držitel mlýna po Třicetileté válce. Nejstarší doložitelný zakladatel mlynářského rodu.*

2. **Tomáš Dias (Thomas Dijn / Dyas)** (syn Václava)
   * Narozen: cca 1630
   * Manželka: **Marina**
   * Povolání: mlynář v Ivanovicích na Hané
   * *Poznámka: První z rodu psaný církevně pod příjmením Dijn/Dias.*

3. **Jan (Joannes) Dias st.** (syn Tomáše a Mariny)
   * Křest: 25. června 1664 v Ivanovicích
   * Zemřel: před 1717
   * Manželka: **Alžběta (Elisabeth)**
   * *Poznámka: Nejstarší matričně doložený křest člena rodu Diasů.*

4. **Václav (Wenzel) Dias st.** (syn Jana st. a Alžběty)
   * Křest: leden 1694 v Ivanovicích
   * Svatba: 16. února 1717 v Ivanovicích
   * Manželka: **Barbora Dvořáková** (dcera Matěje Dvořáka)

5. **Jan (Joannes) Dias** (syn Václava st. a Barbory)
   * Narozen: cca 1720
   * Zemřel: před 1793
   * Manželka: **Mariana**
   * Povolání: panský mlynář v Ivanovicích

6. **Jakub Dias** (syn Jana a Mariany)
   * Narozen: 1771
   * Zemřel: před 1838
   * Manželka: **Mariana** (* 1771 - † 1849, Zlobice)
   * Povolání: pachtovní mlynář v Ivanovicích

7. **František Dias st.** (syn Jakuba a Mariany)
   * Narozen: 1814
   * Manželka: **Antonia Pospíšilová** (* 1817 - † 1891)
   * Povolání: mlynář ve Zlobicích (č.p. 15), zakladatel zlobické větve rodu.

8. **František Dias ml.** (syn Františka st. a Antonie)
   * Narozen: 3. ledna 1845, Zlobice
   * Zemřel: 1928
   * Manželka: **Mariana Manová** (* 28.5.1854)

9. **Alois Dias** (syn Františka ml. a Mariany)
   * Narozen: 11. května 1888, Zlobice
   * Zemřel: 2. listopadu 1974, Morkovice
   * Svatba: 16. června 1913
   * Manželka: **Josefa Přikrylová** (* 2.2.1889 - † 17.11.1968)

10. **Zdeněk Dias st.** (syn Aloise a Josefy)
    * Narozen: 5. října 1925, Morkovice
    * Zemřel: 2. října 1999
    * Manželka: **Naděžda**

11. **Zdeněk Dias ml.** (syn Zdeňka st. a Naděždy)
    * Narozen: 17. června 1957
    * Manželka: **Renata** (* 1962)

12. **Bc. Zdeněk Dias** (syn Zdeňka ml. a Renaty)
    * Narozen: 1991

---

## Vedlejší příbuzní a další potomci

### Děti Václava st. (1694) a Barbory (mimo Jana, r. 1720)
* **Antonín Dias**: narozen 3. října 1717, mlynář, koupil mlýn č. 6 za 1800 zl., zemřel 28. října 1825. Manželka Rosalia (* 1753 - † 18.11.1825).
* **Václav Dias ml.**: narozen cca 1751, zemřel v 49 letech. Manželka Kateřina Kyselová (koupili usedlost č. 156).

### Další příbuzní z nejstarších matrik (17. stol.) v Ivanovicích
* **Pavel Mlynář (Pavel Dias)**: Současník Václava, zapsaný v Lánových rejstřících na jiném gruntu. Pravděpodobně bratr Tomáše (syn Václava).
* **Jan Dysa, Bartolome Dias, Georgius Dijas, Nicolaus Dias**: Další členové rozvětvené mlynářské a sedlácké rodiny žijící v Ivanovicích na přelomu 17. a 18. století.
"""

desk_path = os.path.expanduser("~/Desktop/Kompletni_Rodokmen_S_Detaily.md")
with open(desk_path, "w", encoding="utf-8") as f:
    f.write(md_content)
    
print("Rodokmen MD aktualizovan.")
