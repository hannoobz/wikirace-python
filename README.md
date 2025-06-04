# WikiRace Solver

A web-based tool that finds the shortest path between two Wikipedia pages using hyperlinks, inspired by the [WikiGame](https://www.thewikigame.com/). Built with Flask, Beautiful Soup, and Tailwind CSS.

## Features

- Auto-suggest for start and target pages via Wikipedia API
- Pathfinding between pages via internal hyperlink crawling
- Clean UI with Catppuccin dark theme
- Direct clickable path result to Wikipedia pages

## Project Structure
```
├── instance
├── requirements.txt
├── venv
└── wikirace
    ├── __init__.py
    ├── package.json
    ├── package-lock.json
    ├── solver.py
    ├── static
    │   ├── dist
    │   │   └── output.css
    │   └── src
    │       └── input.css
    └── templates
        ├── _head.html
        ├── index.html
        ├── _navbar.html
        └── solve.html
```


## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/hannoobz/wikirace-python.git
cd wikirace-python
```

### 2. Install dependencies
```bash
virtualenv venv
source ./venv/bin/activate
pip install -r requirements.txt
cd ./wikirace
npm i
npx @tailwindcss/cli -i ./static/src/input.css -o ./static/dist/output.css
cd ..
```

### 3. Run the app

```bash
flask --app wikirace run
```

Go to: http://localhost:5000
