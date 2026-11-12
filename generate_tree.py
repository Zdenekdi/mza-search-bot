import re
from datetime import datetime

# A script to generate the final Markdown family tree and GEDCOM file based on the collected data

markdown_content = """# Komplexní Rodokmen rodiny Dias (Ivanovice na Hané, Zlobice, Morkovice)

Tento dokument představuje nejucelenější syntézu všech nalezených matričních záznamů od počátku 18. století až po současnost. 
Spojuje starou mlynářskou větev z Ivanovic na Hané s novější větví ze Zlobic a Morkovic.

## 1. Nejstarší generace (Ivanovice na Hané) - Zakladatelé rodu na Moravě
Nejstarší nalezené záznamy z let 1700–1750 ukazují, že rodina Diasů byla v Ivanovicích hluboce usazena a věnovala se mlynářství (mlýny na Svitávce).

*   **Jiří Dyas (starší)**
    *   *Narozen:* cca 1670–1680 (odhad)
    *   *Děti:* Jiří Dyas (ženatý 1724 s Annou Václavovou Hauska)

*   **Jakub (Jacobus) Dyas** & **Mariana**
    *   *Svatba:* Únor 1709 (Ivanovice na Hané)
    *   *Povolání:* Mlynáři
    *   *Děti:* Rosina (pokřtěna 7. ledna 1710)

*   **Jan (Joannes) Dyas**
    *   *Narozen:* cca 1680–1690
    *   *Povolání:* "Müller" (mlynář)
    *   *Záznamy:* 18. prosince 1710 se mu narodilo dítě. Další záznamy zmiňují Jana Dyžnu (1706), kterému zemřela dcera Alžběta a narodila se Apollonia. Může jít o téhož muže.

*   **Šimon (Symon) Dyas** (zmiňován 1717) a **František (Franciscus) Dyaß** (sňatek 20. února 1718).

---

## 2. Přímá linie předků (Mlynáři z Ivanovic na Hané)

### Generace I: Václav (Waclaw) Dyas st. a Anna
Nejstarší s jistotou doložený zástupce hlavní mlynářské linie v Ivanovicích a Zlobicích.
*   **Václav (Waclaw) Dyas** (* cca 1695)
*   **Manželka:** Anna
*   **Povolání:** "mlynowrßy na Svitawce" (mlynář na Svitávce v Ivanovicích)
*   **Záznamy:** 24. července 1722 křest syna Adama. U záznamu je poznámka "Zlobice", což ukazuje na rané propojení těchto dvou obcí v historii rodu.
*   **Děti:**
    *   Adam Dyas (* 1722)
    *   Pravděpodobně Václav (Wenceslaus) Dijas ml. (viz níže)

### Generace II: Václav (Wenceslaus) Dijas ml. a Františka
*   **Václav (Wenceslaus) Dijas** (* cca 1720–1730)
*   **Manželka:** Františka (nebo mohl mít bratry Thomase, Josepha atd., protože jméno Václav a profese se dědily).
*   **Poznámka:** Uveden v matrice jako otec Jakuba Diase. 

### Generace III: Jakub Dias a Mariana
*   **Jakub Dias** (* cca 1756 – † před listopadem 1838)
*   **Manželka:** Mariana (* cca 1771 – † 1849, zemřela ve věku 78 let ve Zlobicích)
*   **Povolání:** Pachtýř (nájemní mlynář) na panském mlýně v Ivanovicích na Hané.
*   **Děti:**
    *   František Dias (* cca 1811)
    *   Další pravděpodobní sourozenci: Jan (* cca 1780?), Thomas (pokud nejde o strýce).

---

## 3. Rozvětvení do Zlobic (Generace IV a V)

### Generace IV: František Dias a Antonia
Tato generace představuje klíčový přesun rodiny do Zlobic, kde pokračují v mlynářském řemesle.
*   **František Dias** (* cca 1811, pravděpodobně Ivanovice na Hané)
*   **Manželka:** Antonia, rozená Pospíšil (* cca 1817, Zlobice – † 1891, Zlobice 82)
*   **Svatba:** listopad 1838, Zlobice (uveden jako 27letý svobodný mlynář).
*   **Povolání:** Mlynářský mistr ve Zlobicích.
*   **Děti:**
    *   **František Dias st.** (* 3. ledna 1845, Zlobice)
    *   **Antonia Diasová** (* 1848, Zlobice – † 1858, Zlobice, zemřela v 10 letech na choleru)
    *   **Jan (Johann) Dias** (* listopad 1850, Zlobice – † 1851, Zlobice)
    *   **Anton Dias** (* září 1853, Zlobice – † 1856, Zlobice)

### Generace V: František Dias st. a Mariana
*   **František Dias st.** (* 3. ledna 1845, Zlobice – † 1928)
*   **Manželka:** Mariana, rozená Man (* 28. května 1854, Zlobice)
*   **Svatba:** 4. února 1873, Zlobice
*   **Povolání:** Půlláník ve Zlobicích č.p. 18. Původně vyučený mlynář, později hospodář.
*   **Děti:**
    *   **František Dias ml.** (* 1876, Zlobice) – starosta, člen rolnické strany
    *   **Ludvík Dias** (* 1880, Zlobice) – krejčí
    *   **Karel Dias** (* 1883, Zlobice) – obuvník, padl v I. světové válce
    *   **Alois Dias** (* 11. května 1888, Zlobice – † 2. listopadu 1974)
    *   (Záznamy naznačují i další děti: Antonia, Karel zemřelý brzy atd.)

---

## 4. Novodobá historie (Zlobice -> Morkovice -> Současnost)

### Generace VI: Alois Dias a Josefa
*   **Alois Dias** (* 11. května 1888, Zlobice – † 2. listopadu 1974)
*   **Manželka:** Josefa, rozená Přikrylová (* 2. února 1889, Nítkovice – † 17. listopadu 1968)
*   **Svatba:** 16. června 1913
*   **Děti:** 
    *   Vlastimil Dias (* 1920)
    *   Zdeněk Dias st. (* 1925)

### Generace VII: Zdeněk Dias st.
*   **Zdeněk Dias st.** (* 5. října 1925, Morkovice – † 2. října 1999)
*   **Povolání:** Sedlář, čalouník (mistr ve fabrice v Morkovicích)
*   **Manželka:** Naděžda
*   **Děti:** Zdeněk Dias ml. (* 1957)

### Generace VIII: Zdeněk Dias ml. a Renata
*   **Zdeněk Dias ml.** (* 17. června 1957)
*   **Manželka:** Renata (* 1962)
*   **Děti:**
    *   Adéla Diasová (* 1989)
    *   **Bc. Zdeněk Dias** (* 1991) - iniciátor tohoto genealogického výzkumu.

---
"""

with open("/Users/zdenekdias/.gemini/antigravity/brain/8f3194fc-d68c-48cd-91e7-f2e4c11f74bd/Kompletni_Rodokmen_S_Detaily.md", "w") as f:
    f.write(markdown_content)

print("Markdown rodokmen uspesne vygenerovan.")
