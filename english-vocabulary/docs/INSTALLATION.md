# 📦 Installation Guide

**Complete installation instructions for AI Vocab Builder Skill**

---

## 🚀 Quick Install (5 minutes)

### Step 1: Clone Repository
```bash
git clone https://github.com/AyeshaHashim/ai-vocab-builder.git
cd ai-vocab-builder
```

### Step 2: Copy Skill File
Choose your operating system:

**Windows:**
```bash
copy SKILL.md "%USERPROFILE%\.claude\skills\english-vocabulary\SKILL.md"
```

**macOS:**
```bash
cp SKILL.md ~/.claude/skills/english-vocabulary/SKILL.md
```

**Linux:**
```bash
cp SKILL.md ~/.claude/skills/english-vocabulary/SKILL.md
```

### Step 3: Reload Claude Code
- Restart Claude Code application, OR
- Reload skills in settings

### Done! ✅
The skill is now available as `/english-vocabulary`

---

## 📝 Manual Installation (Step-by-Step)

### Prerequisites
- Claude Code installed
- Git installed (optional, but recommended)
- Text editor (VS Code, Notepad++, etc.)

### Without Git

1. **Download this repository**
   - Click "Code" → "Download ZIP"
   - Extract the ZIP file

2. **Create skill directory**
   - Navigate to `.claude/skills/`
   - Create folder: `english-vocabulary`

3. **Copy SKILL.md**
   - Copy `SKILL.md` from downloaded folder
   - Paste into `.claude/skills/english-vocabulary/`

4. **Restart Claude Code**

---

## 🔍 Finding .claude Directory

The `.claude` directory location depends on your OS:

### Windows
```
C:\Users\[YourUsername]\.claude\skills\
```

Example: `C:\Users\AyeshaHashim\.claude\skills\`

### macOS
```
/Users/[YourUsername]/.claude/skills/
```

Example: `/Users/AyeshaHashim/.claude/skills/`

### Linux
```
/home/[YourUsername]/.claude/skills/
```

Example: `/home/ayesha/.claude/skills/`

---

## ✅ Verification

### Check Installation

1. **Open Claude Code**
2. **Type:** `/` to see available skills
3. **Look for:** `english-vocabulary` in the list
4. **Click it:** Should show the skill description

### If Skill Not Appearing

1. **Verify file location:**
   - Should be: `.claude/skills/english-vocabulary/SKILL.md`

2. **Check file name:**
   - Must be exactly: `SKILL.md` (case-sensitive)

3. **Restart Claude Code:**
   - Close application completely
   - Reopen Claude Code

4. **Check SKILL.md format:**
   - Should start with YAML frontmatter:
   ```yaml
   ---
   name: english-vocabulary
   description: ...
   ---
   ```

---

## 📂 Directory Structure After Installation

```
.claude/
└── skills/
    └── english-vocabulary/
        ├── SKILL.md                  ← Copy this file here
        ├── 2026-01-14.md             ← Optional: daily vocab
        ├── 2026-01-14.pdf            ← Optional: daily vocab PDF
        └── ...
```

---

## 🔧 Troubleshooting

### Skill Not Showing Up

**Problem:** Skill doesn't appear in `/` command list

**Solutions:**
1. Verify exact file path: `.claude/skills/english-vocabulary/SKILL.md`
2. Check filename: Must be `SKILL.md` (case-sensitive)
3. Verify YAML frontmatter at top of file
4. Restart Claude Code completely
5. Check Claude Code version is up-to-date

**Debug:**
```bash
# Check if file exists (macOS/Linux)
ls ~/.claude/skills/english-vocabulary/SKILL.md

# Check if file exists (Windows)
dir "%USERPROFILE%\.claude\skills\english-vocabulary\SKILL.md"
```

### Invalid Skill Format

**Problem:** Skill appears but shows error

**Solution:**
- Open `SKILL.md` in text editor
- Check first lines have YAML frontmatter:
  ```yaml
  ---
  name: english-vocabulary
  description: ...
  ---
  ```
- Ensure no extra spaces or formatting

### Permission Denied

**Problem:** Cannot copy file to `.claude` directory

**Solutions:**
1. Run editor as Administrator (Windows)
2. Use `sudo` for Linux/macOS
3. Check folder permissions

---

## 📥 Optional: Additional Files

### Vocabulary Data Files

You can also add daily vocabulary files:

1. **Download from repository:**
   - `2026-01-14.md` (Markdown format)
   - `2026-01-14.pdf` (PDF format)

2. **Copy to skill directory:**
   ```
   .claude/skills/english-vocabulary/
   ├── SKILL.md
   ├── 2026-01-14.md
   └── 2026-01-14.pdf
   ```

3. **Reference in Claude Code:**
   - The skill will automatically detect these files
   - Use them for daily learning

---

## 🔄 Updating the Skill

### To Update to Latest Version

1. **Navigate to repository:**
   ```bash
   cd ai-vocab-builder
   ```

2. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

3. **Copy updated SKILL.md:**
   ```bash
   # Windows
   copy SKILL.md "%USERPROFILE%\.claude\skills\english-vocabulary\SKILL.md"

   # macOS/Linux
   cp SKILL.md ~/.claude/skills/english-vocabulary/SKILL.md
   ```

4. **Restart Claude Code**

---

## ⚙️ Advanced Setup (Optional)

### Environment Variables (Optional)

You can set environment variables for the skill:

```bash
# macOS/Linux
export CLAUDE_SKILLS_DIR="~/.claude/skills"

# Windows
set CLAUDE_SKILLS_DIR=%USERPROFILE%\.claude\skills
```

### Multi-Level Installation

Install multiple vocabulary levels:

```
.claude/skills/
├── english-vocabulary-basic/
│   └── SKILL.md
├── english-vocabulary-medium/
│   └── SKILL.md
└── english-vocabulary-matric/
    └── SKILL.md
```

---

## 📞 Need Help?

If you encounter issues:

1. **Check this file:** [Installation Guide](INSTALLATION.md)
2. **Check Usage Guide:** [Usage Guide](../docs/USAGE.md)
3. **Open an Issue:** [GitHub Issues](https://github.com/AyeshaHashim/ai-vocab-builder/issues)
4. **Contact:** ayeshasyesda06@gmail.com

---

## ✅ Installation Checklist

- [ ] Cloned repository (or downloaded ZIP)
- [ ] Located `.claude/skills/` directory
- [ ] Created `english-vocabulary` folder
- [ ] Copied `SKILL.md` file
- [ ] Restarted Claude Code
- [ ] Verified skill appears in `/` command
- [ ] Ready to use `/english-vocabulary` command

**Ready to start learning! 🎓**
