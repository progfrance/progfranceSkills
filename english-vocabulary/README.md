# 🎓 AI Vocab Builder - Claude Code Skill

**Advanced AI-powered vocabulary learning skill for Claude Code**

[![GitHub License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-brightgreen)](https://claude.com/claude-code)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](CHANGELOG.md)

---

## 📚 Overview

**AI Vocab Builder** is a professional Claude Code skill designed to help students and learners master English vocabulary at multiple proficiency levels. It provides daily structured vocabulary lessons with comprehensive examples, pronunciation guides, and study materials in both Markdown and PDF formats.

Perfect for:
- 🎯 School students (Grade 6-12)
- 📖 ESL/EFL learners
- 🏆 Exam preparation (matric, TOEFL, IELTS)
- 💼 Professional English learners
- 👨‍🏫 Teachers and educators

---

## ✨ Features

### 📋 Multiple Proficiency Levels
- **Basic Level** - Beginner vocabulary (35 words)
- **Medium Level** - Intermediate vocabulary (35 words)
- **Matric Level** - Advanced vocabulary (35 words)

### 📚 Daily Learning System
- ✅ 35 new words per day (customizable)
- ✅ Simple, clear meanings
- ✅ Pronunciation guides (IPA format)
- ✅ 3 contextual examples per word
- ✅ Usage frequency ratings
- ✅ Subject/context area tags

### 📝 Multiple Output Formats
- ✅ Markdown (.md) files for editing
- ✅ PDF files for printing
- ✅ Organized daily files by date (YYYY-MM-DD)
- ✅ Automatic file creation and updates

### 🧪 Daily Testing System
- ✅ 15 questions per day
- ✅ Multiple choice questions (5)
- ✅ Fill-in-the-blank questions (5)
- ✅ Sentence-based questions (5)
- ✅ Immediate feedback and scoring
- ✅ Performance analysis

### 📊 Comprehensive Results
- ✅ Detailed answer key
- ✅ Score calculation (out of 15)
- ✅ Percentage grade
- ✅ Words mastered tracking
- ✅ Words to practice identification
- ✅ Performance summary (Excellent/Good/Needs Practice)

---

## 🚀 Installation

### Quick Start

1. **Clone this repository:**
```bash
git clone https://github.com/AyeshaHashim/ai-vocab-builder.git
cd ai-vocab-builder
```

2. **Copy SKILL.md to your Claude Code skills directory:**

**On Windows:**
```bash
copy SKILL.md "%USERPROFILE%\.claude\skills\english-vocabulary\SKILL.md"
```

**On macOS/Linux:**
```bash
cp SKILL.md ~/.claude/skills/english-vocabulary/SKILL.md
```

3. **Reload Claude Code** to activate the skill

### Detailed Installation Guide

See [INSTALLATION.md](docs/INSTALLATION.md) for step-by-step instructions.

---

## 💻 Usage

### Basic Usage

Invoke the skill in Claude Code:

```bash
/english-vocabulary
```

Or directly:

```
/english-vocabulary "Start vocabulary learning"
```

### Learning Flow

1. **Stage 1: Learning Phase**
   - Receive 35 new vocabulary words
   - Each word includes meaning, pronunciation, and examples
   - Take time to read and understand

2. **Stage 2: Testing Phase**
   - Answer 15 test questions
   - Multiple choice, fill-in-blanks, sentence questions
   - Immediate feedback on answers

3. **Stage 3: Results Phase**
   - View detailed results and scoring
   - See which words you mastered
   - Identify words to practice

### Advanced Usage

See [USAGE.md](docs/USAGE.md) for detailed usage examples and scenarios.

---

## 📖 Examples

### Example 1: Basic Level Learning

```
User: /english-vocabulary
System: Starting vocabulary learning...

BASIC VOCABULARY - 2026-01-14
Level: Basic (Grade 1-5 / Beginners)

Word 1: Apple
Meaning: A round red or green fruit that grows on trees.
Examples:
1. I eat an apple every morning.
2. She has a red apple in her bag.
3. Apples grow on trees in the garden.

[... 34 more words ...]
```

### Example 2: Taking the Daily Test

```
User: [Finishes reading 35 words]
System: Now let's test your vocabulary! Answer these 15 questions.

SECTION A: MULTIPLE CHOICE

1. What does "abundant" mean?
   A) Very small
   B) Having plenty of something
   C) Hard to find
   D) Expensive

[... 14 more questions ...]
```

### Example 3: Viewing Results

```
System: VOCABULARY TEST RESULTS
================================

SCORE: 12 / 15
PERCENTAGE: 80%
GRADE: GOOD

WORDS MASTERED (12):
✓ abundant, beautiful, diligent, eloquent, frugal...

WORDS TO PRACTICE (3):
✗ genuine, humble, inevitable

SUMMARY: Good work! Keep practicing these words.
```

See [examples/](examples/) for more detailed examples.

---

## 📋 Vocabulary Levels

### Level 1: Basic (35 words)
For beginners and young learners

**Sample words:**
Apple, Beautiful, Book, Bread, Brother, Butterfly, Cake, Cat, Chair, Clean...

**Perfect for:** Grade 1-5, ESL beginners

### Level 2: Medium (35 words)
For intermediate learners

**Sample words:**
Abandon, Ability, Absent, Absolute, Abstract, Accident, Acknowledge, Acquire, Adapt, Adequate...

**Perfect for:** Grade 6-10, intermediate English courses

### Level 3: Matric (35 words)
For advanced secondary students

**Sample words:**
Advocate, Ambivalent, Benign, Clandestine, Deleterious, Eloquent, Ephemeral, Exacerbate, Facilitate...

**Perfect for:** Grade 11-12, university prep, TOEFL/IELTS

---

## 📁 File Structure

```
ai-vocab-builder/
├── README.md                    # This file
├── SKILL.md                     # Main skill definition
├── LICENSE                      # MIT License
├── CHANGELOG.md                 # Version history
├── docs/
│   ├── INSTALLATION.md          # Installation guide
│   ├── USAGE.md                 # Usage guide
│   ├── EXAMPLES.md              # Detailed examples
│   └── LEVELS.md                # Vocabulary level details
├── examples/
│   ├── basic-level-2026-01-14.md
│   ├── medium-level-2026-01-14.md
│   ├── matric-level-2026-01-14.md
│   └── test-example.txt
└── .gitignore                   # Git ignore file
```

---

## 🎯 Requirements

- **Claude Code** - Latest version
- **Text Editor** - For viewing/editing Markdown files
- **PDF Reader** - For viewing PDF output (optional)
- **Git** - For cloning repository

---

## 📊 Study Statistics

- **Total Vocabulary Words:** 105 words across 3 levels
- **Words per Day:** 35 words
- **Questions per Day:** 15 questions
- **Daily Time Commitment:** 15-25 minutes
- **Proficiency Levels:** 3 (Basic, Medium, Matric)

---

## 🤝 Contributing

Contributions are welcome! If you'd like to:
- Add new vocabulary words
- Improve examples
- Report bugs
- Suggest features

Please open an [Issue](https://github.com/AyeshaHashim/ai-vocab-builder/issues) or [Pull Request](https://github.com/AyeshaHashim/ai-vocab-builder/pulls)

---

## 📝 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Ayesha Hashim**
- GitHub: [@AyeshaHashim](https://github.com/AyeshaHashim)
- Email: ayeshasyesda06@gmail.com

---

## 🔗 Links

- **Repository:** https://github.com/AyeshaHashim/ai-vocab-builder
- **Claude Code:** https://claude.com/claude-code
- **Installation Guide:** [docs/INSTALLATION.md](docs/INSTALLATION.md)
- **Usage Guide:** [docs/USAGE.md](docs/USAGE.md)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

---

## ⭐ Show Your Support

If you find this skill helpful, please:
- ⭐ Star this repository
- 🔄 Share with others
- 📝 Leave feedback
- 🐛 Report issues

---

## 📞 Support

For questions or issues:
1. Check [INSTALLATION.md](docs/INSTALLATION.md)
2. Check [USAGE.md](docs/USAGE.md)
3. Open an [Issue](https://github.com/AyeshaHashim/ai-vocab-builder/issues)
4. Contact: ayeshasyesda06@gmail.com

---

**Happy Learning! 🎓**

Made with ❤️ for English learners everywhere.
