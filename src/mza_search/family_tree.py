import os
import re

class FamilyTreeManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.persons = []
        self.load_from_markdown()

    def load_from_markdown(self):
        if not os.path.exists(self.filepath):
            print(f"File {self.filepath} not found.")
            return

        with open(self.filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Simple regex based parser for the structured markdown
        person_blocks = re.split(r'##\s+\d+\.', content)
        
        for block in person_blocks[1:]: # Skip the first chunk (header)
            lines = block.strip().split('\n')
            name_line = lines[0].strip()
            # Clean up name (e.g. "Jakub Dias (nejstarší potvrzený předek)" -> "Jakub Dias")
            name_match = re.match(r'([^\(]+)', name_line)
            name = name_match.group(1).strip() if name_match else name_line
            
            person = {
                "Jméno": name,
                "Status": "",
                "Profese": "",
                "Narození": "",
                "Úmrtí": "",
                "Svatba": "",
                "Manželka": "",
                "Klíčové zjištění pro výzkum": ""
            }

            for line in lines[1:]:
                line = line.strip()
                if line.startswith('- **'):
                    key_match = re.match(r'-\s*\*\*([^\*]+)\*\*\s*(.*)', line)
                    if key_match:
                        key = key_match.group(1).replace(':', '').strip()
                        val = key_match.group(2).strip()
                        if key in person:
                            person[key] = val
            
            self.persons.append(person)

    def get_context_string(self):
        """Returns a string representation for AI context."""
        context = "Známe tyto osoby z našeho rodokmenu (propojujte s nimi, pokud najdete shodu):\n"
        for p in self.persons:
            context += f"- Osoba: {p['Jméno']}\n"
            if p.get('Manželka'):
                context += f"  Manželka (nebo partner): {p['Manželka']}\n"
            if p.get('Profese'):
                context += f"  Profese: {p['Profese']}\n"
            if p.get('Narození'):
                context += f"  Narození: {p['Narození']}\n"
            if p.get('Svatba'):
                context += f"  Svatba: {p['Svatba']}\n"
            if p.get('Úmrtí'):
                context += f"  Úmrtí: {p['Úmrtí']}\n"
        return context

if __name__ == "__main__":
    import sys
    # For testing
    filepath = sys.argv[1] if len(sys.argv) > 1 else '/Users/zdenekdias/.gemini/antigravity/brain/8f3194fc-d68c-48cd-91e7-f2e4c11f74bd/dias_family_tree.md'
    mgr = FamilyTreeManager(filepath)
    print("Parsed persons:")
    print(mgr.persons)
    print("\n--- AI Context ---")
    print(mgr.get_context_string())
