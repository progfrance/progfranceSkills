#!/usr/bin/env python3
import os
import re
import json
import subprocess
from datetime import datetime
from pathlib import Path
import argparse

# Configuration
WIP_LIMITS = {"To Do": 3, "In Progress": 2, "Review": 1}
# "BUG" a été retiré des marqueurs à chercher dans le texte
MARKERS = ["TODO", "IMPROVEMENT"] 
# Ajout des environnements virtuels aux exclusions
EXCLUDED_DIRS = {".git", "node_modules", "dist", "build", "coverage", ".next", "out", ".cache", "__pycache__", ".venv", "venv", "env"}
TODO_FILE = "TODO.md"

class KanbanAgentCoordinator:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.board = {
            "To Do": [],
            "In Progress": [],
            "Review": [],
            "Done": []
        }
        self.code_items = {} 

    def scan_codebase(self):
        """Scanne uniquement les fichiers ciblés (TODO, BUG, IMPROVEMENT) et groupe les éléments."""
        pattern = re.compile(rf"({'|'.join(MARKERS)}):\s*(.*)")
        
        # Le fichier Kanban de sortie à ignorer pour ne pas faire de boucle infinie
        output_file_path = (self.root_dir / TODO_FILE).resolve()

        for filepath in self.root_dir.rglob("*"):
            # Condition : doit être un fichier, et pas dans un dossier exclu
            if not filepath.is_file() or any(part in EXCLUDED_DIRS for part in filepath.parts):
                continue
                
            # Exclure le fichier TODO.md généré par le script lui-même
            if filepath.resolve() == output_file_path:
                continue

            # NOUVELLE REGLE : uniquement les fichiers contenant TODO, BUG ou IMPROVEMENT dans leur nom
            filename_upper = filepath.name.upper()
            if not any(kw in filename_upper for kw in ["TODO", "BUG", "IMPROVEMENT"]):
                continue
                
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        match = pattern.search(line)
                        if match:
                            marker_type, desc = match.groups()
                            desc = desc.strip()
                            loc = f"{filepath.relative_to(self.root_dir).as_posix()}:{line_num}"
                            key = f"{marker_type}: {desc}"
                            self.code_items[key] = loc
            except (UnicodeDecodeError, PermissionError):
                pass 

    def parse_existing_board(self):
        """Analyse le TODO.md à la racine pour préserver l'état."""
        todo_path = self.root_dir / TODO_FILE
        if not todo_path.exists():
            return

        current_column = None
        # Mise à jour de la regex pour ne matcher que les MARKERS restants
        item_pattern = re.compile(rf"- \[( |x|~)\] ({'|'.join(MARKERS)}): (.*?) \((.*?)\)")

        with open(todo_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("## To Do"): current_column = "To Do"
                elif line.startswith("## In Progress"): current_column = "In Progress"
                elif line.startswith("## Review"): current_column = "Review"
                elif line.startswith("## Done"): current_column = "Done"
                elif line.startswith("- ["):
                    match = item_pattern.match(line.strip())
                    if match:
                        state, m_type, desc, loc = match.groups()
                        key = f"{m_type}: {desc}"
                        if current_column:
                            self.board[current_column].append({
                                "key": key, "type": m_type, "desc": desc, "loc": loc, "state_char": state
                            })

    def sync_board(self):
        """Met à jour les colonnes sans perdre l'état manuel."""
        existing_keys = {item["key"]: item for col in self.board.values() for item in col}
        
        for key, loc in self.code_items.items():
            if key not in existing_keys:
                m_type, desc = key.split(": ", 1)
                self.board["To Do"].append({
                    "key": key, "type": m_type, "desc": desc, "loc": loc, "state_char": " "
                })
            else:
                existing_keys[key]["loc"] = loc

        for col in ["To Do", "In Progress", "Review"]:
            items_to_keep = []
            for item in self.board[col]:
                if item["key"] not in self.code_items:
                    item["state_char"] = "x"
                    self.board["Done"].append(item)
                else:
                    items_to_keep.append(item)
            self.board[col] = items_to_keep

    def generate_markdown(self):
        """Génère le rapport Markdown final."""
        today = datetime.now().strftime("%Y-%m-%d")
        lines = [f"# TODO Board > Last updated: {today} via KanbanAgent", ""]

        bottlenecks = []
        for col, items in self.board.items():
            limit_text = f" (WIP limit: {WIP_LIMITS[col]})" if col in WIP_LIMITS else ""
            lines.append(f"## {col}{limit_text}")
            
            if col in WIP_LIMITS and len(items) > WIP_LIMITS[col]:
                bottlenecks.append(f"⚠️ **WIP Advisory**: {col} has {len(items)} items (limit: {WIP_LIMITS[col]})")

            for item in items:
                char = "x" if col == "Done" else ("~" if col in ["In Progress", "Review"] else " ")
                lines.append(f"- [{char}] {item['type']}: {item['desc']} ({item['loc']})")
            lines.append("")

        if bottlenecks:
            lines.append("### Bottleneck Analysis")
            for b in bottlenecks: lines.append(f"- {b}")

        with open(self.root_dir / TODO_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
            
        return bottlenecks

    def run(self, output_json=False):
        self.scan_codebase()
        self.parse_existing_board()
        self.sync_board()
        bottlenecks = self.generate_markdown()

        agent_payload = {
            "status": "success",
            "directory_scanned": str(self.root_dir),
            "wip_alerts": bottlenecks,
            "metrics": {
                "todo_count": len(self.board["To Do"]),
                "in_progress_count": len(self.board["In Progress"]),
                "review_count": len(self.board["Review"]),
            },
            "available_tasks": self.board["To Do"]
        }

        if output_json:
            print(json.dumps(agent_payload, indent=2))
        else:
            print(f"✅ TODO.md mis à jour (Scan du dossier : {self.root_dir})")
            for alert in bottlenecks: print(alert)
            print(f"Tâches prêtes : {len(self.board['To Do'])}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kanban TODO Scanner")
    parser.add_argument("directory", nargs="?", default=".", help="Dossier à scanner (défaut: '.')")
    parser.add_argument("--json", action="store_true", help="Output JSON for AI")
    args = parser.parse_args()
    
    agent = KanbanAgentCoordinator(root_dir=args.directory)
    agent.run(output_json=args.json)
