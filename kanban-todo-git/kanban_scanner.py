#!/usr/bin/env python3
import os
import re
import json
import subprocess
from datetime import datetime
from pathlib import Path
import argparse

# Configuration basée sur la spécification SKILL.md
WIP_LIMITS = {"To Do": 3, "In Progress": 2, "Review": 1}
MARKERS = ["BUG", "TODO", "IMPROVEMENT"]
EXCLUDED_DIRS = {".git", "node_modules", "dist", "build", "coverage", ".next", "out", ".cache", "__pycache__"}
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
        self.code_items = {} # clef: "TYPE: description", valeur: location

    def scan_codebase(self):
        """Étape 1 & 2 : Scanne le code et groupe les éléments."""
        pattern = re.compile(rf"({'|'.join(MARKERS)}):\s*(.*)")
        
        for filepath in self.root_dir.rglob("*"):
            if not filepath.is_file() or any(part in EXCLUDED_DIRS for part in filepath.parts):
                continue
                
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        match = pattern.search(line)
                        if match:
                            marker_type, desc = match.groups()
                            desc = desc.strip()
                            # Normalisation du chemin (séparateurs Unix)
                            loc = f"{filepath.relative_to(self.root_dir).as_posix()}:{line_num}"
                            key = f"{marker_type}: {desc}"
                            self.code_items[key] = loc
            except (UnicodeDecodeError, PermissionError):
                pass # Ignorer les fichiers binaires ou inaccessibles

    def parse_existing_board(self):
        """Analyse le TODO.md existant pour préserver l'état (idempotence)."""
        if not (self.root_dir / TODO_FILE).exists():
            return

        current_column = None
        item_pattern = re.compile(r"- \[( |x|~)\] (BUG|TODO|IMPROVEMENT): (.*?) \((.*?)\)")

        with open(self.root_dir / TODO_FILE, 'r', encoding='utf-8') as f:
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
                        self.board[current_column].append({
                            "key": key,
                            "type": m_type,
                            "desc": desc,
                            "loc": loc,
                            "state_char": state
                        })

    def sync_board(self):
        """Étape 3 : Met à jour les colonnes sans perdre l'état manuel."""
        existing_keys = {item["key"]: item for col in self.board.values() for item in col}
        
        # 1. Ajouter les nouveaux éléments trouvés dans le code
        for key, loc in self.code_items.items():
            if key not in existing_keys:
                m_type, desc = key.split(": ", 1)
                self.board["To Do"].append({
                    "key": key, "type": m_type, "desc": desc, "loc": loc, "state_char": " "
                })
            else:
                # Mettre à jour la localisation si elle a changé
                existing_keys[key]["loc"] = loc

        # 2. Déplacer vers "Done" les éléments qui ne sont plus dans le code
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
        """Étape 4 & 7 : Génère le rapport Markdown et signale les dépassements WIP."""
        today = datetime.now().strftime("%Y-%m-%d")
        lines = [
            f"# TODO Board > Last updated: {today} via KanbanAgent",
            ""
        ]

        bottlenecks = []
        for col, items in self.board.items():
            limit_text = f" (WIP limit: {WIP_LIMITS[col]})" if col in WIP_LIMITS else ""
            lines.append(f"## {col}{limit_text}")
            
            # Vérification des WIP limits
            if col in WIP_LIMITS and len(items) > WIP_LIMITS[col]:
                bottlenecks.append(f"⚠️ **WIP Advisory**: {col} has {len(items)} items (limit: {WIP_LIMITS[col]})")

            for item in items:
                char = "x" if col == "Done" else ("~" if col in ["In Progress", "Review"] else " ")
                lines.append(f"- [{char}] {item['type']}: {item['desc']} ({item['loc']})")
            lines.append("")

        if bottlenecks:
            lines.append("### Bottleneck Analysis")
            for b in bottlenecks:
                lines.append(f"- {b}")

        with open(self.root_dir / TODO_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
            
        return bottlenecks

    def run(self, output_json=False):
        self.scan_codebase()
        self.parse_existing_board()
        self.sync_board()
        bottlenecks = self.generate_markdown()

        # Construction d'un payload pour l'Agent IA Coordinateur
        agent_payload = {
            "status": "success",
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
            print(f"✅ TODO.md mis à jour avec succès.")
            for alert in bottlenecks:
                print(alert)
            print(f"Tâches prêtes à être dispatchées : {len(self.board['To Do'])}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kanban TODO Scanner for AI Agents")
    parser.add_argument("--json", action="store_true", help="Output JSON for AI coordinator consumption")
    args = parser.parse_args()
    
    agent = KanbanAgentCoordinator()
    agent.run(output_json=args.json)
