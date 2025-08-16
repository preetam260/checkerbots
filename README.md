# ♟️ Checker-bots

An interactive **Checkers game with AI-powered bots**, built with **Python, PyQt5, and Pygame**.  
Includes heuristic and search-based strategies (`AlgoBot`, `Group1`, `Group2`) with support for  
latency measurement, simulation benchmarking, and plug-and-play bot design.

---

## 🚀 Features
- 🎮 Interactive GUI (PyQt5 + Pygame) for smooth gameplay.
- 🤖 Multiple AI strategies:
  - `AlgoBot` → heuristic + search-based
  - `Group1` & `Group2` → alternative bot implementations
  - `RandomBot` → baseline
- 📊 Simulation framework to benchmark bots against each other.
- ⚡ Performance metrics:
  - Average FPS (~9 FPS in default config)
  - Execution time per game (~5s)
  - Win rate across 500+ games (>70% for `AlgoBot` vs. baseline bots)
  - Move decision latency (avg & 99th percentile)

---

## 📦 Installation
```bash
# clone repo
git clone https://github.com/yourusername/Checker-bots.git
cd Checker-bots

# create virtual env (optional but recommended)
python -m venv venv
source venv/bin/activate   # on mac/linux
venv\Scripts\activate      # on windows

# install dependencies
pip install -r requirements.txt
