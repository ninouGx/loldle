# Loldle Solver 2.0 - Complete Refactor 🎮

A professional CLI tool for playing and solving **Loldle** (and variants) using information theory and entropy-based optimization.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Version](https://img.shields.io/badge/version-2.0.0-green.svg)

> **Note**: This is a fan-made project, completely unrelated to Riot Games.

---

## ✨ What's New in 2.0

This is a **complete ground-up refactor** with modern Python practices, SOLID architecture, and production-ready code!

### 🎯 Major Improvements

**Architecture & Code Quality:**
- ✅ Full **SOLID principles** implementation
- ✅ Modular package structure with proper separation of concerns
- ✅ Type hints everywhere for better IDE support and type safety
- ✅ Dataclasses for clean, immutable data models
- ✅ Abstract base classes for extensibility (easy to add Pokemon, Dota, etc.)
- ✅ Proper error handling and validation

**User Experience:**
- ✅ Modern CLI built with **Click** framework
- ✅ Beautiful terminal UI using **Rich** library (colors, tables, panels)
- ✅ Three game modes: Classic, Assisted, and Online Helper
- ✅ Smart character selection with partial name matching
- ✅ Support for both emoji and number input formats

**Performance & Intelligence:**
- ✅ Optimized entropy calculations using information theory
- ✅ Real-time optimal guess recommendations
- ✅ Automatic filtering of impossible characters
- ✅ Calculated optimal first guess: **Xin Zhao** (6.166 bits vs Bel'Veth's ~5.7)

**Developer Experience:**
- ✅ Proper Python packaging with `pyproject.toml`
- ✅ Installable via pip (`pip install -e .`)
- ✅ Command-line entry point (`loldle` command)
- ✅ Comprehensive module documentation
- ✅ Ready for testing framework (pytest structure in place)

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ninouGx/loldle
cd loldle

# Install in development mode
pip install -e .
```

### Basic Usage

```bash
# Show help
loldle --help

# Play in classic mode
loldle play

# Play with AI assistance
loldle play --mode assisted

# Help solve the online version at loldle.net
loldle play --mode online-helper

# Find the optimal first guess
loldle solve

# Show game statistics
loldle info

# Refresh champion data from online sources
loldle refresh-data
```

---

## 🎮 Game Modes

### 1. Classic Mode
Play the guessing game yourself without assistance.
```bash
loldle play --mode classic
```

The computer randomly selects a champion, and you try to guess it. After each guess, you'll see:
- 🟩 Exact match
- 🟧 Partial match (at least one element matches)
- 🟥 No match
- ⬇️ Target is before/lower
- ⬆️ Target is after/higher

### 2. Assisted Mode
Get AI-powered recommendations based on information theory.
```bash
loldle play --mode assisted
```

Features:
- See the optimal first guess (**Xin Zhao** with 6.166 bits of information)
- Get top 5 recommendations ranked by entropy after each guess
- View expected remaining possibilities
- List all possible characters when fewer than 10 remain

### 3. Online Helper Mode
Helps you play on [loldle.net](https://loldle.net/classic).
```bash
loldle play --mode online-helper
```

How it works:
1. Tool suggests the best champion to guess
2. You enter that champion on loldle.net
3. You copy the emoji result from the website
4. Tool analyzes and suggests the next best guess
5. Repeat until you win!

Accepts input in two formats:
- **Emojis**: `🟩🟥🟧⬇️⬆️🟩🟩`
- **Numbers**: `0214000` (0=exact, 1=partial, 2=wrong, 3=before, 4=after)

---

## 📊 How It Works - Information Theory

### Entropy-Based Optimization

The solver uses **Shannon entropy** to find optimal guesses:

```
H = -Σ p(pattern) × log₂(p(pattern))
```

For each candidate guess, it calculates:
1. How many different result patterns are possible
2. The probability of each pattern occurring
3. The expected information gain (entropy)

**Higher entropy = Better guess**

### Example: Optimal First Guess

When you guess **Xin Zhao** as the first champion:
- Creates 100+ different comparison patterns
- Expected information gain: **6.166 bits**
- Average remaining possibilities: **3.1 champions**

This means on average, after guessing Xin Zhao, you'll only have ~3 champions left!

**Top 5 Starting Champions:**
1. **Xin Zhao** - 6.166 bits (⭐ Best)
2. **Talon** - 6.153 bits
3. **Brand** - 6.136 bits
4. **Riven** - 6.106 bits
5. **Cassiopeia** - 6.059 bits

---

## 🏗️ Architecture

The project follows **SOLID principles** with a clean, modular structure:

```
src/loldle/
├── models/          # Data models (Champion, ComparisonResult)
│   ├── base.py      # Abstract Character class
│   └── lol.py       # League of Legends Champion model
├── games/           # Game engines
│   ├── base.py      # Abstract BaseGame class
│   └── lol.py       # Loldle game implementation
├── solvers/         # AI solvers
│   └── entropy.py   # Entropy-based optimal solver
├── data/            # Data loading and management
│   └── loader.py    # CSV/JSON data loaders
├── ui/              # User interface
│   ├── display.py   # Rich-based display functions
│   └── input.py     # User input handling
├── utils/           # Utilities
│   └── constants.py # Enums and constants
└── cli.py           # Click-based CLI interface
```

### Key Design Patterns

- **Strategy Pattern**: Different game variants (LoL, Pokemon) implement `BaseGame`
- **Factory Pattern**: Data loaders create appropriate character models
- **Template Method**: Base classes define game flow, subclasses customize behavior

### Extensibility

Adding a new game variant (e.g., Pokedle) requires only:
1. Create a `Pokemon` model extending `Character`
2. Implement comparison logic
3. Create a `PokedleGame` extending `BaseGame`
4. Add data loaders

The entropy solver and UI automatically work with the new game!

**See [ADDING_VARIANTS.md](ADDING_VARIANTS.md) for a complete step-by-step guide.**

---

## 📁 Data & Auto-Refresh

Champion data is stored in `Data/champions_data.csv`:

```csv
Champion Name;Gender;Position(s);Species;Resource;Range type;Region(s);Release year
Aatrox;Male;Top;Darkin;Manaless;Melee;Runeterra,Shurima;2013
Ahri;Female;Middle;Vastayan;Mana;Ranged;Ionia;2011
```

**Current data**: 163 champions (auto-updated from community sources)

### Refreshing Data

The tool can automatically refresh champion data from online sources:

```bash
# Refresh from community GitHub repositories (recommended)
loldle refresh-data

# Use a specific source
loldle refresh-data --source github

# Refresh without backing up old data
loldle refresh-data --no-backup
```

**Data sources:**
- Community GitHub: [joulsen/loldle-information-theory](https://github.com/joulsen/loldle-information-theory)
- Fallback scrapers for loldle.net

The data is automatically backed up before updating, so you can always revert if needed

---

## 🌐 Browser Extension

A Chrome/Firefox extension is included to help scrape results from loldle.net:

**Installation:**
1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `Extension` folder

**Usage:**
1. Go to [loldle.net/classic](https://loldle.net/classic)
2. Click the extension icon
3. Copy the emoji combination
4. Paste into `loldle play --mode online-helper`

---

## 📈 Old vs New Implementation

### Old (App/loldleApp.py)
- ❌ Single 500-line monolithic file
- ❌ Hardcoded "Bel'Veth" as first guess (~5.7 bits)
- ❌ No type hints
- ❌ Class variables (bug prone)
- ❌ Curses-based UI (limited, hard to use)
- ❌ No proper packaging

### New (src/loldle/)
- ✅ Modular structure (15+ well-organized files)
- ✅ Calculated optimal: "Xin Zhao" (6.166 bits - **8% better!**)
- ✅ Full type hints
- ✅ Proper dataclasses
- ✅ Rich-based modern UI (beautiful, intuitive)
- ✅ Professional pip-installable package

---

## 🔧 Development

### Project Structure

```
loldle/
├── src/loldle/          # ⭐ New modular source code
├── Data/                # Champion data files
├── Extension/           # Chrome extension
├── tests/               # Unit tests (to be added)
├── App/                 # ⚠️ Legacy code (deprecated)
├── pyproject.toml       # Modern packaging config
└── README.md            # You are here!
```

### Dependencies

**Core:**
- click >= 8.1.0 (CLI framework)
- rich >= 13.0.0 (Beautiful terminal output)
- numpy >= 1.24.0 (Numerical calculations)
- beautifulsoup4 >= 4.12.0 (HTML parsing)

**Optional (scraper):**
```bash
pip install -e ".[scraper]"
```
- selenium >= 4.15.0
- webdriver-manager >= 4.0.0

**Development:**
```bash
pip install -e ".[dev]"
```
- pytest >= 7.4.0
- black >= 23.0.0 (code formatting)
- ruff >= 0.1.0 (linting)
- mypy >= 1.5.0 (type checking)

---

## 📚 Resources

**Original Inspiration:**
- [ScienceEtonnante - JE CRAQUE WORDLE !](https://www.youtube.com/watch?v=iw4_7ioHWF4)
- [3Blue1Brown - Solving Wordle using information theory](https://www.youtube.com/watch?v=v68zYyaEmEA)

**Game:**
- Official: [https://loldle.net/classic](https://loldle.net/classic)

---

## 🤝 Contributing

Contributions welcome! The new architecture makes it easy to:
- Add new game variants (Pokemon, Dota, Naruto, etc.)
- Improve entropy calculations
- Add more game modes
- Enhance UI/UX
- Add comprehensive tests
- Update champion data

---

## 🎯 Recent Enhancements & Roadmap

### ✅ Recently Added
- [x] **Auto-refresh data** from community sources
- [x] Multi-source data fetching (GitHub, scraper fallbacks)
- [x] Automatic data backups before updates
- [x] Framework for adding new game variants
- [x] Complete variant addition guide

### 🔮 Future Enhancements
- [ ] Add Pokemon variant (Pokedle) - framework ready!
- [ ] Add Dota variant (Dotadle) - framework ready!
- [ ] Implement async data fetching
- [ ] Add comprehensive test suite
- [ ] Create web UI version
- [ ] Add statistics tracking (win rate, average guesses)
- [ ] Implement different solving strategies
- [ ] Publish to PyPI

---

## 🎓 Understanding the Math

### Why Entropy Matters

**Entropy measures uncertainty**. When we make a guess, we want to **gain the most information** possible, regardless of the result.

**Example**: With 8 champions remaining, an ideal guess would:
- Split them evenly into groups → Maximum information
- Not: Split into 7 vs 1 → Low information (we already "knew" it probably wasn't that 1)

### Expected Remaining Formula

```python
Expected Remaining = Σ (count² / total)
```

Lower is better - it tells us how many champions we expect to have left on average.

---

**Made with ❤️ using Mathematics, Python, and Information Theory!**

**Enjoy optimal Loldle solving! 🎮📊**
