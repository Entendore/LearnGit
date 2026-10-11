# git_dojo.py — GitDojo: a complete interactive Git learning app (PySide6)
# pip install PySide6   (and git on PATH for the sandbox / labs)

import sys, os, json, html, random, shutil, shlex, subprocess, tempfile
from string import Template
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QPointF, QRectF, QUrl
from PySide6.QtGui import (QBrush, QColor, QFont, QFontDatabase, QPainter, QPen,
                           QPolygonF, QPainterPath, QDesktopServices)
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QProgressBar,
    QPushButton, QScrollArea, QSizePolicy, QStackedWidget, QTabWidget, QTextBrowser,
    QTextEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
)

# ──────────────────────────────────────────────────────────────── THEME
THEMES = {
 "dark": {"bg":"#1b1c20","text":"#e8e8e8","sidebar":"#141519","hover":"#22242a",
          "accent":"#f05033","accent_hover":"#ff6a4b","on_accent":"#ffffff","heading":"#ffffff",
          "panel":"#202227","border":"#2e3138","selected":"#3b3e46","button":"#2c2f36",
          "button_border":"#3a3e47","button_hover":"#373b44","button_pressed":"#24262c",
          "disabled_text":"#6b6f77","disabled_bg":"#222429","disabled_border":"#2b2e34",
          "green":"#2e7d46","green_hover":"#379a56","input":"#17181d","console":"#0e0f13",
          "alt":"#1b1d22","sub":"#9aa0aa","card":"#202228","scroll":"#3a3e47","scroll_hover":"#4a4f5a"},
 "light": {"bg":"#f2f3f5","text":"#212429","sidebar":"#e4e6ea","hover":"#d8dbe1",
           "accent":"#e0452a","accent_hover":"#f05033","on_accent":"#ffffff","heading":"#1b1c20",
           "panel":"#ffffff","border":"#cdd1d8","selected":"#d9dce2","button":"#e6e8ec",
           "button_border":"#c9cdd4","button_hover":"#d9dce2","button_pressed":"#cfd3da",
           "disabled_text":"#9aa0a8","disabled_bg":"#eceef1","disabled_border":"#d5d8de",
           "green":"#2e7d46","green_hover":"#379a56","input":"#ffffff","console":"#27282c",
           "alt":"#f6f7f9","sub":"#5c626b","card":"#ffffff","scroll":"#c2c6cd","scroll_hover":"#aeb3bc"},
}

_SS_TEMPLATE = Template("""
* { outline: none; }
QMainWindow { background:$bg; }
QWidget { background:transparent; color:$text; font-size:${size}px; }
QListWidget#sidebar { background:$sidebar; border:none; padding-top:6px; }
QListWidget#sidebar::item { padding:12px 10px; margin:3px 8px; border-radius:8px; color:$text; }
QListWidget#sidebar::item:hover { background:$hover; }
QListWidget#sidebar::item:selected { background:$accent; color:$on_accent; font-weight:bold; }
QLabel#brand { font-size:19px; font-weight:800; padding:14px 12px 10px 12px; color:$heading; }
QListWidget { background:$panel; border:1px solid $border; border-radius:8px; }
QListWidget::item { padding:9px 8px; border-radius:6px; margin:2px 4px; }
QListWidget::item:selected { background:$selected; color:$text; }
QListWidget::item:hover { background:$hover; }
QPushButton { background:$button; border:1px solid $button_border; border-radius:8px; padding:8px 16px; }
QPushButton:hover { background:$button_hover; border-color:$button_border; }
QPushButton:pressed { background:$button_pressed; }
QPushButton:disabled { color:$disabled_text; background:$disabled_bg; border-color:$disabled_border; }
QPushButton[accent="true"] { background:$accent; border:none; color:$on_accent; font-weight:600; }
QPushButton[accent="true"]:hover { background:$accent_hover; }
QPushButton[green="true"] { background:$green; border:none; color:$on_accent; font-weight:600; }
QPushButton[green="true"]:hover { background:$green_hover; }
QTextBrowser, QTextEdit, QPlainTextEdit { background:$input; border:1px solid $border; border-radius:8px; padding:6px; selection-background-color:$accent; }
QTextEdit#console { background:$console; border-radius:10px; padding:10px; }
QLineEdit { background:$input; border:1px solid $border; border-radius:8px; padding:9px 12px; }
QLineEdit:focus { border:1px solid $accent; }
QTreeWidget { background:$input; border:1px solid $border; border-radius:8px; alternate-background-color:$alt; }
QTreeWidget::item { padding:4px; }
QTreeWidget::item:selected { background:$selected; }
QHeaderView::section { background:$panel; color:$sub; border:none; padding:7px; font-weight:bold; }
QProgressBar { background:$input; border:1px solid $border; border-radius:6px; text-align:center; }
QProgressBar::chunk { background:$accent; border-radius:4px; }
QFrame[card="true"] { background:$card; border:1px solid $border; border-radius:12px; }
QTabWidget::pane { border:1px solid $border; border-radius:8px; background:$input; top:-1px; }
QTabBar::tab { background:$panel; color:$text; padding:8px 16px; border:1px solid $border; border-bottom:none; border-top-left-radius:8px; border-top-right-radius:8px; margin-right:2px; }
QTabBar::tab:selected { background:$accent; color:$on_accent; font-weight:600; }
QTabBar::tab:hover:!selected { background:$hover; }
QScrollBar:vertical { background:transparent; width:10px; margin:2px; }
QScrollBar::handle:vertical { background:$scroll; border-radius:5px; min-height:30px; }
QScrollBar::handle:vertical:hover { background:$scroll_hover; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
QScrollBar:horizontal { background:transparent; height:10px; margin:2px; }
QScrollBar::handle:horizontal { background:$scroll; border-radius:5px; min-width:30px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width:0; }
QToolTip { background:$button; color:$text; border:1px solid $border; padding:4px; }
QLabel#h1 { font-size:30px; font-weight:800; color:$heading; }
QLabel#h2 { font-size:18px; font-weight:700; color:$heading; }
QLabel#sub { color:$sub; }
QLabel#why { background:$card; border-left:3px solid $accent; padding:10px; border-radius:6px; }
""")

def make_stylesheet(theme="dark", size=14):
    v = dict(THEMES.get(theme, THEMES["dark"]))
    v["size"] = size
    return _SS_TEMPLATE.safe_substitute(v)

STYLESHEET = make_stylesheet()

LESSON_CSS = """
h1 { color:#ff7a5c; font-size:22px; margin-bottom:6px; }
h2 { color:#ffd166; font-size:16px; margin-top:16px; }
p, li { line-height:1.55; }
code { color:#ffd166; font-family:Consolas,Menlo,monospace; }
pre { background:#101116; border:1px solid #2c2f36; border-radius:8px;
      padding:10px 12px; font-family:Consolas,Menlo,monospace; color:#a5d6ff; }
.tip { background:#1d2b45; border-left:4px solid #4d8dd6;
       padding:8px 12px; border-radius:4px; margin-top:12px; }
"""

# ──────────────────────────────────────────────────────────────── PROGRESS
class ProgressStore:
    DEFAULTS = {
        "completed_lessons": [], "quiz_best": 0, "mastered_cards": [],
        "practice_done": [], "lesson_quiz_best": {}, "card_boxes": {},
        "settings": {"theme": "dark", "size": 14},
        "conflict_lab_done": False, "rebase_lab_done": False, "reflog_lab_done": False,
        "pickrevert_lab_done": False, "bisect_lab_done": False, "stash_lab_done": False,
        "lesson_notes": {}, "bookmarks": [],
    }
    def __init__(self):
        self.path = Path.home() / ".gitdojo_progress.json"
        self.data = json.loads(json.dumps(self.DEFAULTS))
        try:
            self.data.update(json.loads(self.path.read_text(encoding="utf-8")))
        except Exception:
            pass
        for k, v in self.DEFAULTS.items():
            self.data.setdefault(k, v)
        boxes = self.data.setdefault("card_boxes", {})
        for cid in self.data.get("mastered_cards", []):
            boxes.setdefault(cid, 4)
    def save(self):
        try:
            self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
        except Exception:
            pass
    def reset(self):
        self.data = json.loads(json.dumps(self.DEFAULTS))
        self.save()

# ──────────────────────────────────────────────────────────────── HELPERS
def mono_font(size=11):
    f = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
    f.setPointSize(size)
    return f

def make_button(text, slot, accent=False, prop=None):
    b = QPushButton(text)
    if accent:
        b.setProperty("accent", True)
    if prop:
        b.setProperty(prop, True)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.clicked.connect(slot)
    return b

_EMPTY = []
_ONE = [("write", "a.txt", "base\n"), "git add .", 'git commit -m "base"']
_TWO = _ONE + [("write", "a.txt", "base\nmore\n"), "git add .", 'git commit -m "second"']

def _cbranch(c):
    r = c.run("git rev-parse --abbrev-ref HEAD", echo=False, notify=False)
    return r.stdout.strip() if r and r.returncode == 0 else ""

def _ccount(c):
    log = c.run("git log --oneline", echo=False, notify=False)
    return len(log.stdout.strip().splitlines()) if log and log.returncode == 0 else 0

def _ftext(c, name):
    p = (c.dir / name) if c.dir else None
    if p and p.exists():
        return p.read_text(encoding="utf-8", errors="ignore")
    return ""

def _last_subject(c):
    r = c.run("git log -1 --pretty=%s", echo=False, notify=False)
    return r.stdout.strip() if r and r.returncode == 0 else ""

# ──────────────────────────────────────────────────────────────── PRACTICE CHECKS
def _chk_init(c):
    r = c.run("git rev-parse --is-inside-work-tree", echo=False, notify=False)
    ok = r is not None and r.returncode == 0 and "true" in r.stdout
    return ok, ("Nice! This folder is now a Git repository." if ok else "Not a repo yet — run `git init`.")

def _chk_identity(c):
    n = c.run("git config user.name", echo=False, notify=False)
    e = c.run("git config user.email", echo=False, notify=False)
    if n and n.returncode == 0 and n.stdout.strip() and e and e.returncode == 0 and e.stdout.strip():
        return True, f"Identity set: {n.stdout.strip()} <{e.stdout.strip()}>."
    return False, 'Set both: `git config user.name "…"` and `git config user.email "…"`.'

def _chk_staged(c):
    st = c.run("git status --porcelain", echo=False, notify=False)
    for l in (st.stdout.splitlines() if st else []):
        if len(l) >= 2 and l[0] not in (" ", "?", "!"):
            return True, "Great — you have a staged change ready to commit."
    return False, "No staged changes yet. Click ＋ New file, then run `git add .`."

def _chk_committed(c):
    r = c.run("git rev-parse HEAD", echo=False, notify=False)
    if r and r.returncode == 0:
        return True, "Committed! Your history now has a snapshot."
    return False, 'No commit yet. Stage something and run `git commit -m "…"`.'

def _chk_branch_dev(c):
    if _cbranch(c) == "dev":
        return True, "You're on branch dev. Well done!"
    b = c.run("git branch", echo=False, notify=False)
    if b and "dev" in b.stdout:
        return False, "Branch dev exists but you're elsewhere. Run `git switch dev`."
    return False, "Create and switch in one step: `git switch -c dev`."

def _chk_merged(c):
    p = (c.dir / "app.txt") if c.dir else None
    if p and p.exists() and "feature line" in p.read_text(encoding="utf-8", errors="ignore"):
        return True, "Merged! app.txt now contains the feature change."
    return False, "Make sure you're on main and run `git merge feature`."

def _chk_remote(c):
    r = c.run("git remote", echo=False, notify=False)
    if r and "origin" in r.stdout:
        return True, "Remote 'origin' is configured."
    return False, "Add it: `git remote add origin <url>`."

def _chk_reset_soft(c):
    log = c.run("git log --oneline", echo=False, notify=False)
    n = len(log.stdout.strip().splitlines()) if log and log.returncode == 0 else 99
    st = c.run("git status --porcelain", echo=False, notify=False)
    staged = any(len(l) >= 2 and l[0] not in (" ", "?", "!") for l in (st.stdout.splitlines() if st else []))
    if n == 1 and staged:
        return True, "Last commit undone, and the changes are still staged."
    if n == 1 and not staged:
        return False, "Commit undone but not staged — use `git reset --soft HEAD~1`."
    return False, "There should be exactly 1 commit left. Try `git reset --soft HEAD~1`."

def _chk_stash_back(c):
    p = (c.dir / "a.txt") if c.dir else None
    if p and p.exists() and "wip" in p.read_text(encoding="utf-8", errors="ignore"):
        return True, "Stashed and popped back — change restored."
    return False, "Stash it, then `git stash pop`."

def _chk_tagged(c):
    r = c.run("git tag", echo=False, notify=False)
    if r and "v1.0" in r.stdout:
        return True, "Tag v1.0 created."
    return False, 'Create it: `git tag -a v1.0 -m "Release 1.0"`.'

def _chk_rebased(c):
    log = c.run("git log --oneline", echo=False, notify=False)
    if log and "main work" in log.stdout and _cbranch(c) == "feature":
        return True, "Rebased! feature now sits on top of main."
    if _cbranch(c) != "feature":
        return False, "Switch to feature first: `git switch feature`."
    return False, "On feature, run `git rebase main`."

def _chk_clone(c):
    p = (c.dir / "clone1" / "a.txt") if c.dir else None
    try:
        if p and p.exists() and "base" in p.read_text(encoding="utf-8"):
            return True, "Cloned! clone1/ is a working copy of origin/."
    except Exception:
        pass
    return False, "`git clone origin clone1`"

def _chk_name_dojo(c):
    r = c.run("git config user.name", echo=False, notify=False)
    if r and r.stdout.strip() == "Git Dojo":
        return True, "user.name is now 'Git Dojo'."
    return False, 'Run `git config user.name "Git Dojo"`.'

def _chk_add_one(c):
    st = c.run("git status --porcelain", echo=False, notify=False)
    status = {}
    for l in (st.stdout.splitlines() if st else []):
        if len(l) >= 3:
            status[l[3:].strip()] = l[:2]
    a, b = status.get("a.txt", ""), status.get("b.txt", "")
    if a[:1] == "A" and b.startswith("??"):
        return True, "Perfect — a.txt staged, b.txt left out."
    return False, "Stage only a.txt: `git add a.txt`."

def _chk_clean_tree(c):
    st = c.run("git status --porcelain", echo=False, notify=False)
    if st is not None and not st.stdout.strip():
        return True, "Clean! Everything is committed."
    return False, "Stage & commit everything so `git status` is empty."

def _chk_a_staged(c):
    st = c.run("git status --porcelain", echo=False, notify=False)
    for l in (st.stdout.splitlines() if st else []):
        if l.endswith("a.txt") and l[0] in "MAR":
            return True, "Nice — the change is staged."
    return False, "Review with `git diff`, then `git add a.txt`."

def _chk_restored(c):
    if _ftext(c, "a.txt") == "base\n":
        return True, "Restored — a.txt matches the commit."
    return False, "Discard the edit: `git restore a.txt`."

def _chk_subject_polish(c):
    if _last_subject(c) == "polish":
        return True, "Committed as 'polish'."
    return False, 'Commit it: `git commit -m "polish"`.'

def _chk_count(c):
    if _ftext(c, "count.txt").strip() == str(_ccount(c)):
        return True, f"Correct — {_ccount(c)} commits."
    return False, "Count with `git log --oneline`, write the number to count.txt."

def _chk_author_email(c):
    if "practice@gitdojo.local" in _ftext(c, "author.txt"):
        return True, "That's the author email."
    return False, "`git show`, find 'Author:', write the email to author.txt."

def _chk_blame_hash(c):
    exp = c.run("git rev-parse --short=7 HEAD", echo=False, notify=False)
    exp = exp.stdout.strip() if exp and exp.returncode == 0 else ""
    if exp and _ftext(c, "hash.txt").strip() == exp:
        return True, f"Correct — {exp}."
    return False, "`git blame a.txt`, copy the short hash into hash.txt."

def _chk_recovered(c):
    r = c.run("git log recovered -1 --pretty=%s", echo=False, notify=False)
    if r and r.returncode == 0 and "lost-commit" in r.stdout:
        return True, "Recovered! 'recovered' points to the lost commit."
    return False, "Find the hash in `git reflog`, then `git branch recovered <hash>`."

def _chk_bisecting(c):
    r = c.run("git rev-parse --is-bisecting", echo=False, notify=False)
    if r and r.returncode == 0 and "true" in r.stdout:
        return True, "Bisect started — Git checked out a commit to test."
    return False, "`git bisect start`, `git bisect bad`, `git bisect good <first-sha>`."

def _chk_fetched(c):
    r = c.run("git branch -r", echo=False, notify=False)
    if r and "origin/main" in r.stdout:
        return True, "Fetched — origin/main now exists locally."
    return False, "`git fetch origin`"

def _chk_pulled(c):
    if _ftext(c, "o.txt") == "from origin\n":
        return True, "Pulled — o.txt merged in."
    return False, "`git pull origin main`"

def _chk_push(c):
    r = c.run("git ls-remote origin", echo=False, notify=False)
    if r and "refs/heads/main" in r.stdout:
        return True, "Pushed! origin now has your main branch."
    return False, "`git push -u origin main`"

def _chk_cleaned(c):
    p = (c.dir / "junk.txt") if c.dir else None
    if not (p and p.exists()):
        return True, "junk.txt removed."
    return False, "`git clean -n` to preview, then `git clean -f`."

def _chk_branch_bugfix(c):
    b = c.run("git branch", echo=False, notify=False)
    if b and "bugfix" in b.stdout and _cbranch(c) == "main":
        return True, "Branch bugfix created; you stayed on main."
    return False, "Create it without switching: `git branch bugfix`."

def _chk_on_dev2(c):
    if _cbranch(c) == "dev2":
        return True, "Switched to dev2."
    return False, "`git switch -c dev2`"

def _chk_picked(c):
    log = c.run("git log --oneline", echo=False, notify=False)
    if log and "pick-me" in log.stdout and _cbranch(c) == "main":
        return True, "Cherry-picked 'pick-me' onto main."
    return False, "`git log feature` for the hash, then `git cherry-pick <hash>`."

def _chk_reverted(c):
    if _last_subject(c) == "second":
        return True, "Patch applied as a real commit via git am."
    return False, "Apply it: `git am 0001-second.patch`."

def _chk_mergebase(c):
    exp = c.run("git merge-base main feature", echo=False, notify=False)
    exp = exp.stdout.strip() if exp and exp.returncode == 0 else ""
    if exp and _ftext(c, "base.txt").strip() == exp:
        return True, "That's the common ancestor of main and feature."
    return False, "Run `git merge-base main feature`, write the SHA to base.txt."

def _chk_grep(c):
    if _ftext(c, "answer.txt").strip() == "haystack.txt":
        return True, "Correct — haystack.txt contains 'needle'."
    return False, "Run `git grep needle`, then write the filename into answer.txt."

def _chk_lsfiles_count(c):
    r = c.run("git ls-files", echo=False, notify=False)
    n = len(r.stdout.strip().splitlines()) if r and r.returncode == 0 else 0
    if _ftext(c, "count.txt").strip() == str(n):
        return True, f"Correct — {n} tracked files."
    return False, "Count the lines of `git ls-files`, write the number to count.txt."

def _chk_describe(c):
    exp = c.run("git describe", echo=False, notify=False)
    exp = exp.stdout.strip() if exp and exp.returncode == 0 else ""
    if exp and _ftext(c, "desc.txt").strip() == exp:
        return True, f"Correct — {exp}."
    return False, "Run `git describe`, write the result into desc.txt."

def _chk_shortlog_count(c):
    if _ftext(c, "count.txt").strip() == str(_ccount(c)):
        return True, f"Correct — {_ccount(c)} commits by the author."
    return False, "Use `git shortlog -s`, sum the counts, write it to count.txt."

def _chk_note(c):
    r = c.run("git notes show", echo=False, notify=False)
    if r and r.returncode == 0 and "review" in r.stdout.lower():
        return True, "Note attached to HEAD."
    return False, 'Add a note: `git notes add -m "review me"`.'

def _chk_symbolicref(c):
    exp = c.run("git symbolic-ref HEAD", echo=False, notify=False)
    exp = exp.stdout.strip() if exp and exp.returncode == 0 else ""
    if exp and _ftext(c, "answer.txt").strip() == exp:
        return True, "Correct — HEAD points to refs/heads/main."
    return False, "Run `git symbolic-ref HEAD`, write the output to answer.txt."

def _chk_apply(c):
    if "added line" in _ftext(c, "a.txt"):
        return True, "Patch applied — a.txt gained the new line."
    return False, "Apply it: `git apply change.patch`."

def _chk_am(c):
    if _last_subject(c) == "second":
        return True, "Patch applied as a commit via git am."
    return False, "Apply it: `git am 0001-second.patch`."

def _chk_cherry(c):
    r = c.run("git cherry main feature", echo=False, notify=False)
    plus = len([l for l in r.stdout.splitlines() if l.startswith("+")]) if r and r.returncode == 0 else 0
    if _ftext(c, "answer.txt").strip() == str(plus):
        return True, f"Correct — {plus} commit(s) ahead of main."
    return False, "Count the '+' lines of `git cherry main feature`, write to answer.txt."

def _chk_difftool(c):
    r = c.run("git config diff.tool", echo=False, notify=False)
    if r and r.returncode == 0 and r.stdout.strip():
        return True, f"diff.tool is set to '{r.stdout.strip()}'."
    return False, "Set one: `git config diff.tool vimdiff`."

def _chk_mergetool(c):
    r = c.run("git config merge.tool", echo=False, notify=False)
    if r and r.returncode == 0 and r.stdout.strip():
        return True, f"merge.tool is set to '{r.stdout.strip()}'."
    return False, "Set one: `git config merge.tool vimdiff`."

def _chk_sendemail(c):
    ans = _ftext(c, "answer.txt").strip().lower()
    if "format-patch" in ans or "format patch" in ans:
        return True, "Correct — send-email ships format-patch output."
    return False, "send-email sends patches made by git format-patch. Write 'format-patch' to answer.txt."

def _chk_svn(c):
    ans = _ftext(c, "answer.txt").strip().lower()
    if ans in ("subversion", "svn"):
        return True, "Correct — git-svn bridges Git and Subversion."
    return False, "git-svn bridges Git with Subversion. Write 'Subversion' to answer.txt."

def _chk_requestpull(c):
    r = c.run("git request-pull HEAD~1 .", echo=False, notify=False)
    if r and r.returncode == 0:
        return True, "request-pull generated a pull-request summary."
    return False, "Run `git request-pull HEAD~1 .`."

def _chk_credhelper(c):
    r = c.run("git config credential.helper", echo=False, notify=False)
    if r and r.returncode == 0 and r.stdout.strip():
        return True, f"credential.helper set to '{r.stdout.strip()}'."
    return False, "Set one: `git config credential.helper store`."

def _chk_rerere(c):
    r = c.run("git config rerere.enabled", echo=False, notify=False)
    if r and r.returncode == 0 and r.stdout.strip().lower() == "true":
        return True, "rerere is enabled."
    return False, "Enable it: `git config rerere.enabled true`."

def _chk_rangediff(c):
    r = c.run("git range-diff HEAD~1..HEAD HEAD~1..HEAD", echo=False, notify=False)
    if r and r.returncode == 0:
        return True, "range-diff compared the two ranges."
    return False, "Run `git range-diff HEAD~1..HEAD HEAD~1..HEAD`."

def _chk_replace(c):
    r = c.run("git replace -l", echo=False, notify=False)
    if r and r.returncode == 0 and r.stdout.strip():
        return True, "A replacement ref exists."
    return False, "Create one: `git replace HEAD HEAD~1`."

def _chk_fastexport(c):
    r = c.run("git fast-export --all", echo=False, notify=False)
    n = len([l for l in r.stdout.splitlines() if l.startswith("commit ")]) if r and r.returncode == 0 else 0
    if n and _ftext(c, "answer.txt").strip() == str(n):
        return True, f"Correct — {n} commit(s) in the export stream."
    return False, "Run `git fast-export --all`, count the 'commit' lines, write to answer.txt."

def _chk_submodule(c):
    gm = (c.dir / ".gitmodules") if c.dir else None
    if gm and gm.exists():
        return True, "Submodule added (.gitmodules created)."
    return False, "Add it: `git submodule add ./origin libs/mylib`."

def _chk_detached(c):
    if _cbranch(c) == "HEAD":
        return True, "You're in detached HEAD — viewing an old commit directly."
    return False, "Check out an older commit: `git checkout HEAD~1`."

def _chk_removed(c):
    st = c.run("git status --porcelain", echo=False, notify=False)
    for l in (st.stdout.splitlines() if st else []):
        if l.startswith("D") and "a.txt" in l:
            return True, "a.txt is staged for deletion."
    return False, "Remove it: `git rm a.txt`."

def _chk_renamed(c):
    st = c.run("git status --porcelain", echo=False, notify=False)
    for l in (st.stdout.splitlines() if st else []):
        if l.startswith("R") and "b.txt" in l:
            return True, "Renamed a.txt → b.txt (staged)."
    if _ftext(c, "b.txt") and c.dir and not (c.dir / "a.txt").exists():
        return True, "Renamed a.txt → b.txt."
    return False, "Rename it: `git mv a.txt b.txt`."

def _chk_tree_obj(c):
    if _ftext(c, "answer.txt").strip().lower() == "tree":
        return True, "Correct — mktree creates tree objects."
    return False, "mktree builds a tree object. Write 'tree' to answer.txt."

def _chk_tag_obj(c):
    if _ftext(c, "answer.txt").strip().lower() == "tag":
        return True, "Correct — mktag creates tag objects."
    return False, "mktag builds a tag object. Write 'tag' to answer.txt."

def _chk_packs(c):
    r = c.run("git count-objects -v", echo=False, notify=False)
    packs = 0
    if r and r.returncode == 0:
        for line in r.stdout.splitlines():
            if line.startswith("packs:"):
                try: packs = int(line.split(":")[1].strip())
                except ValueError: pass
    if packs and _ftext(c, "answer.txt").strip() == str(packs):
        return True, f"Correct — {packs} pack(s)."
    return False, "Run `git repack -a`, then `git count-objects -v`. Write the 'packs:' number to answer.txt."

def _chk_unpack_stdin(c):
    if _ftext(c, "answer.txt").strip().lower() == "stdin":
        return True, "Correct — unpack-objects reads the pack from stdin."
    return False, "unpack-objects reads pack data from stdin. Write 'stdin' to answer.txt."

def _chk_inpack(c):
    r = c.run("git count-objects -v", echo=False, notify=False)
    inpack = 0
    if r and r.returncode == 0:
        for line in r.stdout.splitlines():
            if line.startswith("in-pack:"):
                try: inpack = int(line.split(":")[1].strip())
                except ValueError: pass
    if inpack and _ftext(c, "answer.txt").strip() == str(inpack):
        return True, f"Correct — {inpack} objects live in packs."
    return False, "Run `git count-objects -v`, write the 'in-pack:' number to answer.txt."

def _chk_loose(c):
    r = c.run("git count-objects", echo=False, notify=False)
    cnt = r.stdout.split()[0] if r and r.returncode == 0 and r.stdout.split() else ""
    if cnt != "" and _ftext(c, "answer.txt").strip() == cnt:
        return True, f"Correct — {cnt} loose object(s) remain."
    return False, "Run `git prune-packed`, then `git count-objects`. Write the first number to answer.txt."

# ──────────────────────────────────────────────────────────────── LESSONS (topic)
LESSONS = [
 {"id": "l1", "cat": "Concepts", "title": "What is Git?",
  "body": """<h1>What is Git?</h1>
<p>Git is a <b>distributed version control system</b>: it records snapshots of your project over time.</p>
<h2>Why use it?</h2><ul>
<li><b>Full history</b> — every change is a <i>commit</i>.</li>
<li><b>Undo anything</b> — roll back to any state.</li>
<li><b>Branches</b> — experiment safely in parallel.</li>
<li><b>Collaboration</b> — merge work from many people.</li></ul>
<h2>Key ideas</h2><ul>
<li><b>Commit</b> — a snapshot plus who/when/why.</li>
<li><b>Repository</b> — your folder plus its history (the hidden <code>.git</code>).</li>
<li><b>Distributed</b> — every clone has the complete history.</li></ul>
<pre>$ git --version</pre>
<div class="tip">💡 Git thinks in <b>snapshots</b>: each commit captures the full state.</div>""",
  "commands": [("git --version", "Check your Git installation"),
               ("git help <command>", "Open the manual"),
               ("git <command> -h", "Quick summary")],
  "practice": {"goal": "Turn the sandbox into a repository.",
               "steps": ["Run `git init`."],
               "hints": ["Type `git init` below and press Enter."],
               "setup": _EMPTY, "check": _chk_init},
  "quiz": [
    {"q": "Git stores your project as a series of…",
     "options": ["Deltas/patches", "Full snapshots", "Compressed zips", "Text logs"], "answer": 1,
     "why": "Each commit captures the full state."},
    {"q": "Where does Git keep the history?",
     "options": ["In the cloud", "In a hidden .git folder", "In a .history file", "On GitHub"], "answer": 1,
     "why": "The .git directory holds every commit."},
    {"q": "A commit is best described as…",
     "options": ["A branch", "A remote", "A saved snapshot", "A backup zip"], "answer": 2,
     "why": "A commit is an immutable snapshot plus metadata."},
    {"q": "Being 'distributed' means…",
     "options": ["Every clone has full history", "Files split across servers", "You must be online", "One editor"], "answer": 0,
     "why": "Every clone is a complete repository."}]},

 {"id": "l2", "cat": "Getting Started", "title": "First-time setup",
  "body": """<h1>First-time setup</h1>
<p>Tell Git who you are — it's stamped onto every commit:</p>
<pre>$ git config --global user.name "Ada Lovelace"
$ git config --global user.email "ada@example.com"
$ git config --global init.defaultBranch main</pre>
<h2>Create a repository</h2>
<pre>$ git init           # new repo
$ git clone &lt;url&gt;    # copy an existing one</pre>""",
  "commands": [('git config --global user.name "Name"', "Set your identity"),
               ('git config --global user.email "you@example.com"', "Set your email"),
               ("git init", "Create a new repository"),
               ("git clone <url>", "Copy an existing repository")],
  "practice": {"goal": "Configure your Git identity.",
               "steps": ['Run `git config user.name "Your Name"`',
                         'Run `git config user.email "you@example.com"`'],
               "hints": ["Set both name and email."],
               "setup": _EMPTY, "check": _chk_identity},
  "quiz": [
    {"q": "Which command creates a new repository?",
     "options": ["git init", "git start", "git new", "git make"], "answer": 0,
     "why": "git init creates the .git directory."},
    {"q": "git config user.name sets…",
     "options": ["Your password", "The name on your commits", "The repo name", "The branch"], "answer": 1,
     "why": "It's the author identity."},
    {"q": "Which downloads an existing repo?",
     "options": ["git init", "git download", "git clone <url>", "git pull"], "answer": 2,
     "why": "clone copies a repo with full history."},
    {"q": "init.defaultBranch controls…",
     "options": ["Repo location", "Commit count", "Remote URL", "The first branch name"], "answer": 3,
     "why": "It sets the default branch name."}]},

 {"id": "l3", "cat": "Snapshotting", "title": "Staging & status",
  "body": """<h1>Working tree, staging, HEAD</h1>
<ul><li><b>Working directory</b> — your files as you see them.</li>
<li><b>Staging area (index)</b> — what goes into the next commit.</li>
<li><b>HEAD</b> — the last commit on your current branch.</li></ul>
<pre>$ git status               # what changed?
$ git add notes.txt        # stage one file
$ git add .                # stage everything
$ git diff                 # unstaged vs last commit
$ git diff --staged        # staged vs last commit</pre>
<div class="tip">💡 Staging lets you craft commits deliberately.</div>""",
  "commands": [("git status", "See what changed / is staged"),
               ("git add <file>", "Stage a file"),
               ("git add .", "Stage all changes"),
               ("git diff", "Unstaged vs last commit"),
               ("git diff --staged", "Staged vs last commit")],
  "practice": {"goal": "Create a file and stage it.",
               "steps": ["Click ＋ New file", "Run `git add .`"],
               "hints": ["Create a file first, then `git add .`."],
               "setup": _EMPTY, "check": _chk_staged},
  "quiz": [
    {"q": "git add puts changes into…",
     "options": ["History", "The staging area", "The remote", "A backup"], "answer": 1,
     "why": "add stages changes for the next commit."},
    {"q": "git diff --staged compares…",
     "options": ["Working tree vs index", "Index vs last commit", "Two remotes", "Tags"], "answer": 1,
     "why": "--staged shows what's queued."},
    {"q": "An untracked file shows as…",
     "options": ["??", "A", "M", "D"], "answer": 0,
     "why": "?? marks untracked files."},
    {"q": "git add . stages…",
     "options": ["Deleted only", "Nothing", "All new/modified", "One file"], "answer": 2,
     "why": "The dot means everything below cwd."}]},

 {"id": "l4", "cat": "Snapshotting", "title": "Commits & history",
  "body": """<h1>Committing</h1>
<pre>$ git commit -m "Add login validation"
$ git commit -am "…"       # stage tracked + commit
$ git commit --amend       # redo the last commit</pre>
<h2>Good messages</h2><ul>
<li>Imperative mood: “Fix bug”, not “Fixed bug”.</li>
<li>Short subject (~50 chars); explain <i>why</i> in the body.</li></ul>
<h2>Reading history</h2>
<pre>$ git log
$ git log --oneline --graph --all</pre>""",
  "commands": [('git commit -m "msg"', "Commit staged changes"),
               ("git commit --amend", "Modify the last commit"),
               ("git log", "View history"),
               ("git log --oneline", "Compact history")],
  "practice": {"goal": "Make your first commit.",
               "steps": ["A file is already staged", 'Run `git commit -m "my first commit"`'],
               "hints": ["The message can be anything."],
               "setup": [("write", "hello.txt", "hello\n"), "git add ."],
               "check": _chk_committed},
  "quiz": [
    {"q": "git commit records…",
     "options": ["Staged changes as a snapshot", "Unstaged changes", "Only new files", "The remote"], "answer": 0,
     "why": "Only staged content goes in."},
    {"q": "git log --oneline shows…",
     "options": ["One line per commit", "Only tags", "Only merges", "File contents"], "answer": 0,
     "why": "Compact hash + subject."},
    {"q": "git commit --amend…",
     "options": ["Deletes history", "Redoes the last commit", "Creates a tag", "Pushes"], "answer": 1,
     "why": "amend folds changes into the last commit."},
    {"q": "Good commit messages use…",
     "options": ["Imperative mood", "Past tense", "Future tense", "All caps"], "answer": 0,
     "why": "“Fix bug”, “Add feature”."}]},

 {"id": "l5", "cat": "Branching & Merging", "title": "Branching",
  "body": """<h1>Branching</h1>
<p>A branch is a movable pointer to a commit. <code>main</code> is the usual default.</p>
<pre>$ git branch                  # list (* = current)
$ git branch feature-login    # create
$ git switch feature-login    # switch
$ git switch -c fix-123       # create + switch
$ git branch -d feature-login # delete merged branch</pre>
<div class="tip">💡 Branch off <code>main</code> → work → merge back → delete.</div>""",
  "commands": [("git branch", "List branches"),
               ("git branch <name>", "Create a branch"),
               ("git switch <name>", "Switch to a branch"),
               ("git switch -c <name>", "Create and switch"),
               ("git branch -d <name>", "Delete a branch")],
  "practice": {"goal": "Create a branch dev and switch to it.",
               "steps": ["Run `git switch -c dev`"],
               "hints": ["-c creates and switches."],
               "setup": _ONE, "check": _chk_branch_dev},
  "quiz": [
    {"q": "A branch is…",
     "options": ["A copy of the remote", "A movable pointer to a commit", "A backup", "A folder"], "answer": 1,
     "why": "Branches are lightweight pointers."},
    {"q": "Create and switch to dev in one step…",
     "options": ["git switch -c dev", "git branch dev", "git dev", "git switch dev"], "answer": 0,
     "why": "-c combines create + switch."},
    {"q": "Creating a branch is…",
     "options": ["Slow", "Impossible after commits", "Cheap and fast", "Only for main"], "answer": 2,
     "why": "It's just a pointer."},
    {"q": "Which shows your current branch?",
     "options": ["git log", "git branch", "git clone", "git tag"], "answer": 1,
     "why": "git branch marks the current one with *."}]},

 {"id": "l6", "cat": "Branching & Merging", "title": "Merging & conflicts",
  "body": """<h1>Merging</h1>
<pre>$ git switch main
$ git merge feature-login</pre>
<ul><li><b>Fast-forward</b>: pointer just advances.</li>
<li><b>Three-way merge</b>: creates a merge commit.</li></ul>
<h2>Conflicts</h2>
<pre>&lt;&lt;&lt;&lt;&lt;&lt;&lt; HEAD
const timeout = 30;
=======
const timeout = 60;
&gt;&gt;&gt;&gt;&gt;&gt;&gt; feature-login</pre>
<p>Edit, remove markers, then <code>git add</code> and <code>git commit</code>.</p>
<div class="tip">💡 <code>git merge --abort</code> backs out safely.</div>""",
  "commands": [("git merge <branch>", "Merge into current branch"),
               ("git merge --abort", "Cancel a conflicted merge"),
               ("git status", "See conflicting files"),
               ("git add <file>", "Mark resolved")],
  "practice": {"goal": "Merge branch 'feature' into main.",
               "steps": ["You're on main", "Run `git merge feature`"],
               "hints": ["Make sure you're on main first."],
               "setup": [("write", "app.txt", "base\n"), "git add .", 'git commit -m "base"',
                         "git switch -c feature",
                         ("write", "app.txt", "base\nfeature line\n"), "git add .",
                         'git commit -m "add feature line"', "git switch main"],
               "check": _chk_merged},
  "quiz": [
    {"q": "Merges integrate into…",
     "options": ["The current branch", "Always main", "The remote", "A new repo"], "answer": 0,
     "why": "The checked-out branch receives the merge."},
    {"q": "Conflicts occur when…",
     "options": ["Every merge", "Both sides changed the same lines", "Repo is large", "Offline"], "answer": 1,
     "why": "Overlapping edits need human help."},
    {"q": "Fast-forward happens when…",
     "options": ["There's a conflict", "You use --no-ff", "Target hasn't diverged", "Repo empty"], "answer": 2,
     "why": "The pointer just advances."},
    {"q": "After resolving a conflict you…",
     "options": ["git add then commit", "Delete the repo", "Clone again", "Do nothing"], "answer": 0,
     "why": "Stage the resolution, then commit."}]},

 {"id": "l7", "cat": "Remotes", "title": "Remotes: clone, push, pull",
  "body": """<h1>Working with remotes</h1>
<p>A <b>remote</b> is another copy of the repo. The default name is <code>origin</code>.</p>
<pre>$ git clone https://github.com/user/repo.git
$ git remote -v
$ git remote add origin &lt;url&gt;
$ git push -u origin main
$ git fetch                 # download, don't merge
$ git pull                  # fetch + integrate</pre>
<div class="tip">💡 <code>fetch</code> is safe; <code>pull</code> also changes your branch.</div>""",
  "commands": [("git remote -v", "List remotes"),
               ("git remote add origin <url>", "Add a remote"),
               ("git push -u origin <branch>", "Push + set upstream"),
               ("git fetch", "Download without merging"),
               ("git pull", "Fetch + integrate")],
  "practice": {"goal": "Add a remote named origin.",
               "steps": ["Run `git remote add origin https://example.com/repo.git`"],
               "hints": ["Any URL works here."],
               "setup": _EMPTY, "check": _chk_remote},
  "quiz": [
    {"q": "The default remote name is…",
     "options": ["origin", "master", "upstream", "remote"], "answer": 0,
     "why": "clone uses 'origin'."},
    {"q": "git pull is roughly…",
     "options": ["push + commit", "fetch + merge", "clone", "add + commit"], "answer": 1,
     "why": "pull downloads then integrates."},
    {"q": "git fetch…",
     "options": ["Uploads", "Downloads without merging", "Deletes", "Commits"], "answer": 1,
     "why": "It updates remote-tracking refs only."},
    {"q": "push -u does what extra?",
     "options": ["Deletes the branch", "Sets upstream", "Creates a tag", "Renames"], "answer": 1,
     "why": "-u remembers the target."}]},

 {"id": "l8", "cat": "Undoing", "title": "Undoing things",
  "body": """<h1>Undoing</h1>
<pre>$ git restore --staged file   # unstage (keep edits)
$ git restore file            # discard edits (⚠)
$ git reset --soft  HEAD~1    # undo commit, keep staged
$ git reset --mixed HEAD~1    # undo + unstage
$ git reset --hard  HEAD~1    # undo + discard (⚠)
$ git revert &lt;sha&gt;            # new commit that undoes</pre>
<div class="tip">💡 <code>revert</code> for shared history; <code>reset</code> for local.</div>""",
  "commands": [("git restore <file>", "Discard working changes"),
               ("git restore --staged <file>", "Unstage a file"),
               ("git reset --soft HEAD~1", "Undo commit, keep staged"),
               ("git reset HEAD~1", "Undo commit and unstage"),
               ("git reset --hard HEAD~1", "Undo and discard"),
               ("git revert <commit>", "Undo with a new commit")],
  "practice": {"goal": "Undo the last commit but keep changes staged.",
               "steps": ["Two commits exist", "Run `git reset --soft HEAD~1`"],
               "hints": ["--soft keeps the changes staged."],
               "setup": _TWO, "check": _chk_reset_soft},
  "quiz": [
    {"q": "Reset that keeps changes staged…",
     "options": ["--soft", "--mixed", "--hard", "--merge"], "answer": 0,
     "why": "--soft leaves the index untouched."},
    {"q": "Safe undo for shared history…",
     "options": ["git revert", "git reset --hard", "git push -f", "Delete .git"], "answer": 0,
     "why": "revert adds a commit, no rewriting."},
    {"q": "git restore file.txt…",
     "options": ["Discards working edits", "Unstages", "Deletes the file", "Commits"], "answer": 0,
     "why": "Without --staged it reverts the file."},
    {"q": "git reset defaults to…",
     "options": ["--mixed", "--soft", "--hard", "--keep"], "answer": 0,
     "why": "--mixed unstages but keeps files."}]},

 {"id": "l9", "cat": "Stashing", "title": "Stashing & cleaning",
  "body": """<h1>Stashing</h1>
<pre>$ git stash push -m "wip"
$ git stash list
$ git stash pop
$ git clean -n     # preview
$ git clean -f     # delete untracked</pre>""",
  "commands": [('git stash push -m "wip"', "Shelve changes"),
               ("git stash list", "List stashes"),
               ("git stash pop", "Apply + remove latest"),
               ("git clean -n", "Preview untracked deletion")],
  "practice": {"goal": "Stash a change, then bring it back.",
               "steps": ["a.txt has a 'wip' change", "Run `git stash push -m \"wip\"`", "Run `git stash pop`"],
               "hints": ["Stash first, then pop."],
               "setup": _ONE + [("write", "a.txt", "a\nwip\n")],
               "check": _chk_stash_back},
  "quiz": [
    {"q": "git stash is for…",
     "options": ["Setting work aside", "Pushing", "Tagging", "Cloning"], "answer": 0,
     "why": "It shelves uncommitted changes."},
    {"q": "git stash pop…",
     "options": ["Lists stashes", "Applies + removes latest", "Deletes a branch", "Commits"], "answer": 1,
     "why": "pop = apply + drop."},
    {"q": "git clean removes…",
     "options": ["Untracked files", "Commits", "Branches", "Tracked files"], "answer": 0,
     "why": "Only untracked files."},
    {"q": "Before git clean -f you should…",
     "options": ["git clean -n", "git push", "git tag", "git stash"], "answer": 0,
     "why": "-n previews deletions."}]},

 {"id": "l10", "cat": "Tags & Releases", "title": "Tags & inspecting history",
  "body": """<h1>Tags & inspection</h1>
<pre>$ git tag
$ git tag -a v1.0 -m "Release 1.0"
$ git show &lt;sha&gt;
$ git blame file
$ git reflog</pre>
<div class="tip">💡 <code>git reflog</code> remembers commits for ~90 days.</div>""",
  "commands": [("git tag", "List tags"),
               ('git tag -a v1.0 -m "msg"', "Create annotated tag"),
               ("git show <ref>", "Inspect a commit/tag"),
               ("git blame <file>", "Line-by-line authorship"),
               ("git reflog", "History of HEAD moves")],
  "practice": {"goal": "Create an annotated tag v1.0.",
               "steps": ['Run `git tag -a v1.0 -m "Release 1.0"`'],
               "hints": ["Annotated tags use -a and -m."],
               "setup": _ONE, "check": _chk_tagged},
  "quiz": [
    {"q": "Which lists tags?",
     "options": ["git tag", "git tags", "git list", "git label"], "answer": 0,
     "why": "git tag with no args lists."},
    {"q": "Find 'lost' commits after a bad reset…",
     "options": ["git reflog", "git log", "git status", "git show"], "answer": 0,
     "why": "reflog tracks every HEAD move."},
    {"q": "git blame shows…",
     "options": ["All branches", "Who last changed each line", "The remote", "Messages only"], "answer": 1,
     "why": "Per-line authorship."},
    {"q": "Tags are used for…",
     "options": ["Staging", "Stashing", "Cleaning", "Marking releases"], "answer": 3,
     "why": "Permanent pointers for releases."}]},

 {"id": "l11", "cat": "Branching & Merging", "title": "Rebasing",
  "body": """<h1>Rebasing</h1>
<p><code>git rebase</code> replays your commits on top of another base.</p>
<pre>$ git switch feature
$ git rebase main</pre>
<ul><li>Pro: clean, linear history.</li>
<li>Con: rewrites commits — never rebase shared branches.</li></ul>
<pre>$ git rebase -i HEAD~3</pre>
<div class="tip">💡 Golden rule: rebase private, merge public.</div>""",
  "commands": [("git rebase <branch>", "Replay onto a branch"),
               ("git rebase -i <rev>", "Interactive rebase"),
               ("git rebase --continue", "Resume after conflict"),
               ("git rebase --abort", "Cancel the rebase")],
  "practice": {"goal": "Rebase branch 'feature' onto main.",
               "steps": ["`git switch feature`", "`git rebase main`"],
               "hints": ["Be on feature first."],
               "setup": [("write", "a.txt", "a\n"), "git add .", 'git commit -m "base"',
                         "git switch -c feature", ("write", "f.txt", "feature\n"),
                         "git add .", 'git commit -m "feature work"',
                         "git switch main", ("write", "b.txt", "main work\n"),
                         "git add .", 'git commit -m "main work"'],
               "check": _chk_rebased},
  "quiz": [
    {"q": "rebase produces…",
     "options": ["A linear history", "More merge commits", "Tags", "Stashes"], "answer": 0,
     "why": "It replays instead of merging."},
    {"q": "After a rebase conflict you…",
     "options": ["git rebase --continue", "git rebase --delete", "git push", "git stash"], "answer": 0,
     "why": "--continue resumes."},
    {"q": "You should NOT rebase…",
     "options": ["Shared/public branches", "Local feature branches", "Any branch", "HEAD"], "answer": 0,
     "why": "Rewriting shared history breaks others."},
    {"q": "rebase -i lets you…",
     "options": ["Squash/reword/reorder", "Push", "Clone", "Stash"], "answer": 0,
     "why": "Interactive editing of commits."}]},
]

# ──────────────────────────────────────────────────────────────── LESSONS (commands)
COMMAND_LESSONS = [
 {"id": "c_clone", "cat": "Getting Started", "title": "git clone — copy a repository",
  "body": """<h1>git clone</h1>
<p>Copies an entire repository (all history). Works with URLs <i>and</i> local paths.</p>
<pre>$ git clone &lt;url&gt;
$ git clone --depth 1 &lt;url&gt;   # shallow
$ git clone -b dev &lt;url&gt;      # specific branch</pre>""",
  "commands": [("git clone <url>", "Clone a repository"),
               ("git clone <url> <dir>", "Clone into a folder"),
               ("git clone --depth 1 <url>", "Shallow clone"),
               ("git clone -b <branch> <url>", "Clone a branch")],
  "practice": {"goal": "Clone the local 'origin' repo into clone1.",
               "steps": ["A repo exists at ./origin", "Run `git clone origin clone1`"],
               "hints": ["clone works with local paths too."],
               "setup": [("run_in", "origin", "git init -b main"),
                         ("run_in", "origin", 'git config user.name "O"'),
                         ("run_in", "origin", 'git config user.email "o@o"'),
                         ("write_in", "origin", "a.txt", "base\n"),
                         ("run_in", "origin", "git add ."),
                         ("run_in", "origin", 'git commit -m "base"')],
               "check": _chk_clone},
  "quiz": [
    {"q": "git clone copies…",
     "options": ["Only the latest file", "The repo with full history", "Just the README", "Only branches"], "answer": 1,
     "why": "A complete copy."},
    {"q": "git clone --depth 1 creates…",
     "options": ["A full clone", "A shallow clone", "A bare repo", "A remote"], "answer": 1,
     "why": "--depth limits history."}]},

 {"id": "c_config", "cat": "Getting Started", "title": "git config — read & set settings",
  "body": """<h1>git config</h1>
<p>Reads/writes settings at three scopes: <code>--local</code>, <code>--global</code>, <code>--system</code>.</p>
<pre>$ git config user.name "Ada"
$ git config --global user.name "Ada"
$ git config user.name
$ git config --list</pre>""",
  "commands": [("git config <key> <value>", "Set a value"),
               ("git config --global <key> <value>", "Set for your user"),
               ("git config <key>", "Read a value"),
               ("git config --list", "List all")],
  "practice": {"goal": "Set user.name to 'Git Dojo'.",
               "steps": ['Run `git config user.name "Git Dojo"`'],
               "hints": ["No --global needed here."],
               "setup": _EMPTY, "check": _chk_name_dojo},
  "quiz": [
    {"q": "Highest-priority scope…",
     "options": ["--system", "--global", "--local", "Equal"], "answer": 2,
     "why": "Local overrides global."},
    {"q": "git config --list…",
     "options": ["Deletes settings", "Shows all settings", "Sets a value", "Resets"], "answer": 1,
     "why": "Prints every effective value."}]},

 {"id": "c_add", "cat": "Snapshotting", "title": "git add — stage changes",
  "body": """<h1>git add</h1>
<pre>$ git add file.txt
$ git add .
$ git add -p      # hunk-by-hunk</pre>
<h2>Options</h2><ul><li><code>-p</code> — stage hunks.</li>
<li><code>-A</code> — all incl. deletions.</li>
<li><code>-u</code> — tracked only.</li></ul>""",
  "commands": [("git add <file>", "Stage a file"),
               ("git add .", "Stage all"),
               ("git add -A", "All incl. deletions"),
               ("git add -u", "Tracked only"),
               ("git add -p", "Stage hunks")],
  "practice": {"goal": "Stage a.txt but not b.txt.",
               "steps": ["Two untracked files exist", "Run `git add a.txt`"],
               "hints": ["Don't use `git add .`."],
               "setup": [("write", "a.txt", "a\n"), ("write", "b.txt", "b\n")],
               "check": _chk_add_one},
  "quiz": [
    {"q": "git add -p lets you…",
     "options": ["Stage hunks", "Push", "Delete", "Branch"], "answer": 0,
     "why": "Selective staging."},
    {"q": "Stages only tracked changes…",
     "options": ["git add .", "git add -u", "git add -A", "git add -p"], "answer": 1,
     "why": "-u ignores new files."}]},

 {"id": "c_status", "cat": "Snapshotting", "title": "git status — inspect state",
  "body": """<h1>git status</h1>
<pre>$ git status
$ git status -s
$ git status --ignored</pre>
<div class="tip">💡 A clean status means everything is saved.</div>""",
  "commands": [("git status", "Branch + changes"),
               ("git status -s", "Short format"),
               ("git status --ignored", "Include ignored")],
  "practice": {"goal": "Get a clean working tree.",
               "steps": ["Modified a.txt + untracked b.txt", "Stage and commit both"],
               "hints": ["`git add .` then commit."],
               "setup": _ONE + [("write", "a.txt", "base\nchanged\n"), ("write", "b.txt", "new\n")],
               "check": _chk_clean_tree},
  "quiz": [
    {"q": "git status tells you…",
     "options": ["Branch + changes", "The remote URL", "Disk usage", "All commits"], "answer": 0,
     "why": "State summary."},
    {"q": "Untracked appears as…",
     "options": ["??", "M", "D", "A"], "answer": 0,
     "why": "?? in short format."}]},

 {"id": "c_diff", "cat": "Snapshotting", "title": "git diff — compare changes",
  "body": """<h1>git diff</h1>
<pre>$ git diff
$ git diff --staged
$ git diff main dev
$ git diff HEAD~2 HEAD</pre>""",
  "commands": [("git diff", "Unstaged vs last commit"),
               ("git diff --staged", "Staged vs last commit"),
               ("git diff <a> <b>", "Between two refs"),
               ("git diff --stat", "Summary")],
  "practice": {"goal": "Review a change, then stage it.",
               "steps": ["a.txt was modified", "Run `git diff`", "Run `git add a.txt`"],
               "hints": ["Look at the + / - lines."],
               "setup": _ONE + [("write", "a.txt", "base\nchanged\n")],
               "check": _chk_a_staged},
  "quiz": [
    {"q": "git diff --staged compares…",
     "options": ["Working tree vs index", "Index vs last commit", "Two remotes", "Tags"], "answer": 1,
     "why": "What's queued."},
    {"q": "git diff (no args) shows…",
     "options": ["Staged", "Unstaged", "Nothing", "The log"], "answer": 1,
     "why": "Working-tree changes."}]},

 {"id": "c_commit", "cat": "Snapshotting", "title": "git commit — record a snapshot",
  "body": """<h1>git commit</h1>
<pre>$ git commit -m "Fix bug"
$ git commit -am "…"
$ git commit --amend</pre>""",
  "commands": [('git commit -m "msg"', "Commit staged"),
               ("git commit -am \"msg\"", "Stage tracked + commit"),
               ("git commit --amend", "Redo last commit"),
               ("git commit --fixup <sha>", "Mark for later squash")],
  "practice": {"goal": "Commit the staged change as 'polish'.",
               "steps": ["A change is staged", 'Run `git commit -m "polish"`'],
               "hints": ["Message must be exactly `polish`."],
               "setup": _ONE + [("write", "a.txt", "base\nmore\n"), "git add ."],
               "check": _chk_subject_polish},
  "quiz": [
    {"q": "git commit records…",
     "options": ["Staged as a snapshot", "Unstaged", "New files only", "The remote"], "answer": 0,
     "why": "Staged content."},
    {"q": "--amend…",
     "options": ["Deletes history", "Redoes last commit", "Creates a tag", "Pushes"], "answer": 1,
     "why": "Folds into the last commit."}]},

 {"id": "c_restore", "cat": "Snapshotting", "title": "git restore — discard / unstage",
  "body": """<h1>git restore</h1>
<pre>$ git restore file.txt          # discard (⚠)
$ git restore --staged file.txt # unstage
$ git restore --source HEAD~1 .</pre>""",
  "commands": [("git restore <file>", "Discard changes"),
               ("git restore --staged <file>", "Unstage"),
               ("git restore --source <rev> <file>", "Restore from a commit")],
  "practice": {"goal": "Discard your edit to a.txt.",
               "steps": ["a.txt was modified", "Run `git restore a.txt`"],
               "hints": ["This throws away the edit."],
               "setup": _ONE + [("write", "a.txt", "base\noops\n")],
               "check": _chk_restored},
  "quiz": [
    {"q": "git restore file.txt…",
     "options": ["Discards edits", "Unstages", "Deletes file", "Commits"], "answer": 0,
     "why": "Reverts to committed state."},
    {"q": "Unstage but keep edits…",
     "options": ["git restore --staged <file>", "git restore <file>", "git clean", "git rm"], "answer": 0,
     "why": "--staged affects only the index."}]},

 {"id": "c_log", "cat": "History & Inspection", "title": "git log — browse history",
  "body": """<h1>git log</h1>
<pre>$ git log
$ git log --oneline
$ git log --graph --all
$ git log -p file.txt
$ git log --author="Ada"</pre>""",
  "commands": [("git log", "Full history"),
               ("git log --oneline", "Compact"),
               ("git log --graph --all --oneline", "Visual graph"),
               ("git log -n 5", "Last 5"),
               ("git log -p <file>", "History with diffs")],
  "practice": {"goal": "Count the commits.",
               "steps": ["Three commits exist", "Run `git log --oneline`", "Write the count to count.txt"],
               "hints": ["One line per commit."],
               "setup": [("write", "a.txt", "1\n"), "git add .", 'git commit -m "one"',
                         ("write", "a.txt", "2\n"), "git add .", 'git commit -m "two"',
                         ("write", "a.txt", "3\n"), "git add .", 'git commit -m "three"'],
               "check": _chk_count},
  "quiz": [
    {"q": "git log --oneline shows…",
     "options": ["One line per commit", "Only tags", "Only merges", "File contents"], "answer": 0,
     "why": "Compact output."},
    {"q": "Branch graph…",
     "options": ["git log --graph --all", "git log -p", "git log --author", "git status"], "answer": 0,
     "why": "--graph draws the structure."}]},

 {"id": "c_show", "cat": "History & Inspection", "title": "git show — inspect one object",
  "body": """<h1>git show</h1>
<pre>$ git show
$ git show &lt;sha&gt;
$ git show v1.0
$ git show HEAD:file.txt</pre>""",
  "commands": [("git show", "Show HEAD"),
               ("git show <sha>", "Show a commit"),
               ("git show <rev>:<file>", "File at a revision"),
               ("git show --stat", "Changed-file summary")],
  "practice": {"goal": "Find HEAD's author email.",
               "steps": ["Run `git show`", "Write the email to author.txt"],
               "hints": ["Look at the Author line."],
               "setup": _ONE, "check": _chk_author_email},
  "quiz": [
    {"q": "git show <sha> displays…",
     "options": ["Commit metadata + diff", "All branches", "The remote", "git status"], "answer": 0,
     "why": "One object in full."},
    {"q": "git show HEAD:file.txt shows…",
     "options": ["File as of HEAD", "Working copy", "The diff", "Blame"], "answer": 0,
     "why": "Content at a revision."}]},

 {"id": "c_blame", "cat": "History & Inspection", "title": "git blame — line authorship",
  "body": """<h1>git blame</h1>
<pre>$ git blame file.txt
$ git blame -L 10,20 file.txt
$ git blame -w file.txt</pre>""",
  "commands": [("git blame <file>", "Line authorship"),
               ("git blame -L <a>,<b> <file>", "Line range"),
               ("git blame -w <file>", "Ignore whitespace")],
  "practice": {"goal": "Find the commit behind line 1 of a.txt.",
               "steps": ["Run `git blame a.txt`", "Write the short hash to hash.txt"],
               "hints": ["The hash is the first column."],
               "setup": _ONE, "check": _chk_blame_hash},
  "quiz": [
    {"q": "git blame shows…",
     "options": ["Who last changed each line", "All commits", "Branch graph", "Remotes"], "answer": 0,
     "why": "Per-line attribution."},
    {"q": "git blame -L 10,20…",
     "options": ["Blames lines 10-20", "Blames 10 files", "Shows log", "Deletes lines"], "answer": 0,
     "why": "Restricts to a range."}]},

 {"id": "c_reflog", "cat": "History & Inspection", "title": "git reflog — the safety net",
  "body": """<h1>git reflog</h1>
<p>Records every place HEAD has been — even 'lost' commits.</p>
<pre>$ git reflog
$ git checkout HEAD@{2}</pre>
<div class="tip">💡 After a bad reset, reflog can recover commits.</div>""",
  "commands": [("git reflog", "History of HEAD moves"),
               ("git reflog show <branch>", "Branch reflog"),
               ("git checkout HEAD@{n}", "Jump to an earlier HEAD")],
  "practice": {"goal": "Recover a dropped commit.",
               "steps": ["'lost-commit' was reset away", "Find it with `git reflog`", "Run `git branch recovered <hash>`"],
               "hints": ["reflog lists the dropped commit."],
               "setup": _ONE + [("write", "a.txt", "base\nlost\n"), "git add .",
                                'git commit -m "lost-commit"', "git reset --hard HEAD~1"],
               "check": _chk_recovered},
  "quiz": [
    {"q": "reflog records…",
     "options": ["Every HEAD position", "Only tags", "Only remotes", "File contents"], "answer": 0,
     "why": "All HEAD movements."},
    {"q": "reflog is best for…",
     "options": ["Recovering bad resets", "Pushing", "Cloning", "Staging"], "answer": 0,
     "why": "It finds orphaned commits."}]},

 {"id": "c_reset", "cat": "Undoing", "title": "git reset — move branches",
  "body": """<h1>git reset</h1>
<pre>$ git reset --soft  HEAD~1
$ git reset         HEAD~1
$ git reset --hard  HEAD~1   # ⚠
$ git reset file.txt</pre>""",
  "commands": [("git reset --soft <rev>", "Keep index+files"),
               ("git reset <rev>", "Unstage (mixed)"),
               ("git reset --hard <rev>", "Discard changes"),
               ("git reset <file>", "Unstage a file")],
  "practice": {"goal": "Undo last commit, keep changes staged.",
               "steps": ["Two commits exist", "Run `git reset --soft HEAD~1`"],
               "hints": ["--soft keeps them staged."],
               "setup": _TWO, "check": _chk_reset_soft},
  "quiz": [
    {"q": "Keeps changes staged…",
     "options": ["--soft", "--mixed", "--hard", "--merge"], "answer": 0,
     "why": "--soft leaves the index."},
    {"q": "Deletes a ref…",
     "options": ["git rm <ref>", "git update-ref --rm", "git update-ref -d <ref>", "git reflog -d"], "answer": 2,
     "why": "Not applicable to reset — but -d deletes refs."}]},

 {"id": "c_revert", "cat": "Undoing", "title": "git revert — safe undo",
  "body": """<h1>git revert</h1>
<p>Creates a <i>new</i> commit that undoes an earlier one — safe for shared branches.</p>
<pre>$ git revert &lt;sha&gt;
$ git revert --no-edit HEAD</pre>""",
  "commands": [("git revert <sha>", "Undo with a new commit"),
               ("git revert --no-edit <sha>", "No editor"),
               ("git revert <a>..<b>", "Revert a range")],
  "practice": {"goal": "Revert the last commit.",
               "steps": ["Two commits exist", "Run `git revert --no-edit HEAD`"],
               "hints": ["--no-edit skips the editor."],
               "setup": _TWO, "check": _chk_reverted},
  "quiz": [
    {"q": "git revert…",
     "options": ["Adds an undo commit", "Deletes history", "Rewrites", "Pushes"], "answer": 0,
     "why": "Additive and safe."},
    {"q": "Best for shared history…",
     "options": ["git revert", "git reset --hard", "git push -f", "Delete .git"], "answer": 0,
     "why": "No rewriting."}]},

 {"id": "c_clean", "cat": "Undoing", "title": "git clean — remove untracked",
  "body": """<h1>git clean</h1>
<pre>$ git clean -n
$ git clean -f
$ git clean -fd</pre>
<div class="tip">💡 Always run <code>-n</code> before <code>-f</code>.</div>""",
  "commands": [("git clean -n", "Preview"),
               ("git clean -f", "Delete untracked"),
               ("git clean -fd", "Also directories"),
               ("git clean -fx", "Also ignored")],
  "practice": {"goal": "Remove untracked junk.txt.",
               "steps": ["junk.txt is untracked", "`git clean -n`", "`git clean -f`"],
               "hints": ["-f removes untracked files."],
               "setup": _ONE + [("write", "junk.txt", "junk\n")],
               "check": _chk_cleaned},
  "quiz": [
    {"q": "git clean removes…",
     "options": ["Untracked files", "All commits", "Branches", "Remotes"], "answer": 0,
     "why": "Only untracked."},
    {"q": "Runs automatically in…",
     "options": ["git clone", "git gc", "git pull", "git diff"], "answer": 1,
     "why": "gc includes prune-packed/clean."}]},

 {"id": "c_branch", "cat": "Branching & Merging", "title": "git branch — manage branches",
  "body": """<h1>git branch</h1>
<pre>$ git branch
$ git branch dev
$ git branch -d dev
$ git branch -D dev
$ git branch -m old new</pre>""",
  "commands": [("git branch", "List local branches"),
               ("git branch <name>", "Create"),
               ("git branch -d <name>", "Delete merged"),
               ("git branch -D <name>", "Force delete"),
               ("git branch -a", "Local + remote")],
  "practice": {"goal": "Create branch bugfix without switching.",
               "steps": ["Run `git branch bugfix`"],
               "hints": ["Stay on main."],
               "setup": _ONE, "check": _chk_branch_bugfix},
  "quiz": [
    {"q": "git branch -d refuses if…",
     "options": ["Not merged", "Empty", "No commits", "Local"], "answer": 0,
     "why": "Protects unmerged work."},
    {"q": "git branch -a shows…",
     "options": ["Local + remote-tracking", "Only tags", "Only main", "Reflog"], "answer": 0,
     "why": "-a includes remotes."}]},

 {"id": "c_switch", "cat": "Branching & Merging", "title": "git switch — change branches",
  "body": """<h1>git switch</h1>
<pre>$ git switch dev
$ git switch -c dev
$ git switch -</pre>""",
  "commands": [("git switch <branch>", "Switch"),
               ("git switch -c <branch>", "Create + switch"),
               ("git switch -", "Previous branch"),
               ("git switch --detach <sha>", "Detach at a commit")],
  "practice": {"goal": "Create and switch to dev2.",
               "steps": ["Run `git switch -c dev2`"],
               "hints": ["-c creates and switches."],
               "setup": _ONE, "check": _chk_on_dev2},
  "quiz": [
    {"q": "git switch -c dev…",
     "options": ["Creates dev + switches", "Deletes dev", "Renames dev", "Pushes dev"], "answer": 0,
     "why": "create + switch."},
    {"q": "git switch - does…",
     "options": ["Previous branch", "Deletes", "Creates tag", "Stashes"], "answer": 0,
     "why": "The dash = previous."}]},

 {"id": "c_merge", "cat": "Branching & Merging", "title": "git merge — integrate branches",
  "body": """<h1>git merge</h1>
<pre>$ git merge feature
$ git merge --no-ff feature
$ git merge --squash feature
$ git merge --abort</pre>""",
  "commands": [("git merge <branch>", "Merge into current"),
               ("git merge --no-ff <branch>", "Force merge commit"),
               ("git merge --squash <branch>", "Squash to staged"),
               ("git merge --abort", "Abort conflict")],
  "practice": {"goal": "Merge 'feature' into main.",
               "steps": ["You're on main", "Run `git merge feature`"],
               "hints": ["Be on main first."],
               "setup": [("write", "app.txt", "base\n"), "git add .", 'git commit -m "base"',
                         "git switch -c feature",
                         ("write", "app.txt", "base\nfeature line\n"), "git add .",
                         'git commit -m "add feature line"', "git switch main"],
               "check": _chk_merged},
  "quiz": [
    {"q": "--no-ff…",
     "options": ["Always makes a merge commit", "Skips conflicts", "Deletes branch", "Pushes"], "answer": 0,
     "why": "Prevents fast-forward."},
    {"q": "--squash…",
     "options": ["Stages without committing", "Makes many commits", "Aborts", "Rebases"], "answer": 0,
     "why": "Collapses to staged changes."}]},

 {"id": "c_rebase", "cat": "Branching & Merging", "title": "git rebase — replay commits",
  "body": """<h1>git rebase</h1>
<pre>$ git rebase main
$ git rebase -i HEAD~3
$ git rebase --continue
$ git rebase --abort</pre>
<div class="tip">⚠ Never rebase shared branches.</div>""",
  "commands": [("git rebase <branch>", "Replay onto a branch"),
               ("git rebase -i <rev>", "Interactive"),
               ("git rebase --continue", "Resume"),
               ("git rebase --abort", "Cancel")],
  "practice": {"goal": "Rebase 'feature' onto main.",
               "steps": ["`git switch feature`", "`git rebase main`"],
               "hints": ["Be on feature first."],
               "setup": [("write", "a.txt", "a\n"), "git add .", 'git commit -m "base"',
                         "git switch -c feature", ("write", "f.txt", "feature\n"),
                         "git add .", 'git commit -m "feature work"',
                         "git switch main", ("write", "b.txt", "main work\n"),
                         "git add .", 'git commit -m "main work"'],
               "check": _chk_rebased},
  "quiz": [
    {"q": "rebase produces…",
     "options": ["Linear history", "More merges", "Tags", "Stashes"], "answer": 0,
     "why": "Replays commits."},
    {"q": "After a conflict…",
     "options": ["git rebase --continue", "git rebase --delete", "git push", "git stash"], "answer": 0,
     "why": "Resumes the rebase."}]},

 {"id": "c_cherry", "cat": "Branching & Merging", "title": "git cherry-pick — copy a commit",
  "body": """<h1>git cherry-pick</h1>
<pre>$ git cherry-pick &lt;sha&gt;
$ git cherry-pick a..b
$ git cherry-pick -n &lt;sha&gt;</pre>""",
  "commands": [("git cherry-pick <sha>", "Apply one commit"),
               ("git cherry-pick <a>..<b>", "Apply a range"),
               ("git cherry-pick -n <sha>", "Apply without committing")],
  "practice": {"goal": "Cherry-pick 'pick-me' onto main.",
               "steps": ["You're on main", "`git log feature` for the hash", "`git cherry-pick <hash>`"],
               "hints": ["Get the hash from feature."],
               "setup": _ONE + ["git switch -c feature",
                                ("write", "f.txt", "pick me\n"), "git add .",
                                'git commit -m "pick-me"', "git switch main"],
               "check": _chk_picked},
  "quiz": [
    {"q": "cherry-pick…",
     "options": ["Applies a commit to current branch", "Deletes", "Tags", "Stashes"], "answer": 0,
     "why": "Re-applies a commit."},
    {"q": "-n does…",
     "options": ["Applies without committing", "Skips", "Aborts", "Pushes"], "answer": 0,
     "why": "Leaves changes staged."}]},

 {"id": "c_stash", "cat": "Stashing", "title": "git stash — shelve work",
  "body": """<h1>git stash</h1>
<pre>$ git stash push -m "wip"
$ git stash list
$ git stash pop
$ git stash apply stash@{1}</pre>""",
  "commands": [('git stash push -m "msg"', "Shelve"),
               ("git stash list", "List"),
               ("git stash pop", "Apply + remove"),
               ("git stash drop", "Delete latest")],
  "practice": {"goal": "Stash a change, then restore it.",
               "steps": ["a.txt has a 'wip' change", "`git stash push -m \"wip\"`", "`git stash pop`"],
               "hints": ["Stash, then pop."],
               "setup": _ONE + [("write", "a.txt", "a\nwip\n")],
               "check": _chk_stash_back},
  "quiz": [
    {"q": "stash is for…",
     "options": ["Setting work aside", "Pushing", "Tagging", "Cloning"], "answer": 0,
     "why": "Shelves uncommitted changes."},
    {"q": "pop…",
     "options": ["Applies + removes", "Lists", "Deletes branch", "Commits"], "answer": 0,
     "why": "apply + drop."}]},

 {"id": "c_remote", "cat": "Remotes", "title": "git remote — manage remotes",
  "body": """<h1>git remote</h1>
<pre>$ git remote -v
$ git remote add origin &lt;url&gt;
$ git remote rename origin upstream
$ git remote remove upstream</pre>""",
  "commands": [("git remote -v", "List + URLs"),
               ("git remote add <name> <url>", "Add"),
               ("git remote rename <old> <new>", "Rename"),
               ("git remote remove <name>", "Remove")],
  "practice": {"goal": "Add a remote named origin.",
               "steps": ["Run `git remote add origin https://example.com/repo.git`"],
               "hints": ["Any URL works."],
               "setup": _EMPTY, "check": _chk_remote},
  "quiz": [
    {"q": "Conventional main remote name…",
     "options": ["origin", "master", "primary", "source"], "answer": 0,
     "why": "clone uses origin."},
    {"q": "git remote -v shows…",
     "options": ["Remotes + URLs", "Commits", "Branches", "Tags"], "answer": 0,
     "why": "fetch and push URLs."}]},

 {"id": "c_fetch", "cat": "Remotes", "title": "git fetch — download safely",
  "body": """<h1>git fetch</h1>
<pre>$ git fetch
$ git fetch origin
$ git fetch --all
$ git fetch --prune</pre>""",
  "commands": [("git fetch", "Download from default"),
               ("git fetch <remote>", "From a remote"),
               ("git fetch --all", "From all"),
               ("git fetch --prune", "Drop stale refs")],
  "practice": {"goal": "Fetch so origin/main appears locally.",
               "steps": ["A remote 'origin' has a commit", "Run `git fetch origin`"],
               "hints": ["fetch downloads refs without merging."],
               "setup": [("run_in", "origin", "git init -b main"),
                         ("run_in", "origin", 'git config user.name "O"'),
                         ("run_in", "origin", 'git config user.email "o@o"'),
                         ("write_in", "origin", "o.txt", "from origin\n"),
                         ("run_in", "origin", "git add ."),
                         ("run_in", "origin", 'git commit -m "from origin"'),
                         "git remote add origin origin"],
               "check": _chk_fetched},
  "quiz": [
    {"q": "git fetch…",
     "options": ["Downloads without merging", "Uploads", "Deletes", "Commits"], "answer": 0,
     "why": "Updates remote-tracking refs."},
    {"q": "Remote branches appear as…",
     "options": ["origin/<branch>", "local branches", "tags", "stashes"], "answer": 0,
     "why": "Remote-tracking refs."}]},

 {"id": "c_pull", "cat": "Remotes", "title": "git pull — fetch + integrate",
  "body": """<h1>git pull</h1>
<pre>$ git pull
$ git pull origin main
$ git pull --rebase</pre>""",
  "commands": [("git pull", "Fetch + merge"),
               ("git pull <remote> <branch>", "Pull a branch"),
               ("git pull --rebase", "Fetch + rebase")],
  "practice": {"goal": "Pull origin/main into your repo.",
               "steps": ["A remote 'origin' has a commit", "Run `git pull origin main`"],
               "hints": ["Your repo is empty, so pull just brings in main."],
               "setup": [("run_in", "origin", "git init -b main"),
                         ("run_in", "origin", 'git config user.name "O"'),
                         ("run_in", "origin", 'git config user.email "o@o"'),
                         ("write_in", "origin", "o.txt", "from origin\n"),
                         ("run_in", "origin", "git add ."),
                         ("run_in", "origin", 'git commit -m "from origin"'),
                         "git remote add origin origin"],
               "check": _chk_pulled},
  "quiz": [
    {"q": "git pull is roughly…",
     "options": ["fetch + merge", "push + commit", "clone + init", "add + commit"], "answer": 0,
     "why": "Downloads then integrates."},
    {"q": "git pull --rebase…",
     "options": ["Integrates by rebasing", "Pushes", "Tags", "Stashes"], "answer": 0,
     "why": "Replays local commits."}]},

 {"id": "c_push", "cat": "Remotes", "title": "git push — upload commits",
  "body": """<h1>git push</h1>
<pre>$ git push
$ git push -u origin main
$ git push origin --tags
$ git push origin --delete feat</pre>""",
  "commands": [("git push", "Push current to upstream"),
               ("git push -u <remote> <branch>", "Push + set upstream"),
               ("git push --tags", "Push tags"),
               ("git push <remote> --delete <branch>", "Delete remote branch")],
  "practice": {"goal": "Push main to origin.",
               "steps": ["You have a commit + an 'origin' remote", "Run `git push -u origin main`"],
               "hints": ["-u sets upstream."],
               "setup": _ONE + [("run_in", "origin", "git init --bare -b main"),
                                "git remote add origin origin"],
               "check": _chk_push},
  "quiz": [
    {"q": "push -u origin main…",
     "options": ["Pushes + remembers", "Deletes main", "Clones main", "Renames"], "answer": 0,
     "why": "Sets upstream."},
    {"q": "git push --tags…",
     "options": ["Uploads tags", "Deletes tags", "Lists tags", "Creates tags"], "answer": 0,
     "why": "Tags aren't pushed by default."}]},

 {"id": "c_tag", "cat": "Tags & Releases", "title": "git tag — mark releases",
  "body": """<h1>git tag</h1>
<pre>$ git tag
$ git tag v1.0
$ git tag -a v1.0 -m "Release"
$ git push --tags</pre>""",
  "commands": [("git tag", "List"),
               ("git tag <name>", "Lightweight tag"),
               ('git tag -a <name> -m "msg"', "Annotated tag"),
               ("git tag -d <name>", "Delete a tag")],
  "practice": {"goal": "Create annotated tag v1.0.",
               "steps": ['Run `git tag -a v1.0 -m "Release 1.0"`'],
               "hints": ["-a and -m for annotated."],
               "setup": _ONE, "check": _chk_tagged},
  "quiz": [
    {"q": "Annotated tag uses…",
     "options": ["git tag -a", "git tag", "git branch", "git label"], "answer": 0,
     "why": "-a makes a full object."},
    {"q": "Are tags pushed by default?",
     "options": ["No — use git push --tags", "Yes", "Only annotated", "Only on clone"], "answer": 0,
     "why": "Push them explicitly."}]},

 {"id": "c_bisect", "cat": "Debugging", "title": "git bisect — find the bug",
  "body": """<h1>git bisect</h1>
<p>Binary-searches history to find the commit that introduced a bug.</p>
<pre>$ git bisect start
$ git bisect bad
$ git bisect good &lt;sha&gt;
$ git bisect reset</pre>
<div class="tip">💡 N commits take ~log₂(N) steps.</div>""",
  "commands": [("git bisect start", "Begin"),
               ("git bisect bad", "Mark broken"),
               ("git bisect good <sha>", "Mark known-good"),
               ("git bisect reset", "End")],
  "practice": {"goal": "Start a bisect session.",
               "steps": ["Four commits exist", "`git bisect start`", "`git bisect bad`", "`git bisect good <first-sha>`"],
               "hints": ["Find the first commit with `git log`."],
               "setup": [("write", "a.txt", "1\n"), "git add .", 'git commit -m "c1"',
                         ("write", "a.txt", "2\n"), "git add .", 'git commit -m "c2"',
                         ("write", "a.txt", "3\n"), "git add .", 'git commit -m "c3"',
                         ("write", "a.txt", "4\n"), "git add .", 'git commit -m "c4"'],
               "check": _chk_bisecting},
  "quiz": [
    {"q": "bisect uses…",
     "options": ["Binary search", "Linear scan", "git log only", "Tags"], "answer": 0,
     "why": "Halves each step."},
    {"q": "To finish…",
     "options": ["git bisect reset", "git bisect end", "git reset", "git clean"], "answer": 0,
     "why": "reset returns to normal."}]},
]

# ──────────────────────────────────────────────────────────────── MORE COMMAND LESSONS
MORE_COMMAND_LESSONS = [
 {"id": "c_rm", "cat": "Snapshotting", "title": "git rm — remove tracked files",
  "body": """<h1>git rm</h1>
<pre>$ git rm file.txt
$ git rm --cached file.txt   # untrack, keep on disk
$ git rm -r folder</pre>""",
  "commands": [("git rm <file>", "Delete + stage removal"),
               ("git rm --cached <file>", "Untrack only"),
               ("git rm -r <dir>", "Remove a directory")],
  "practice": {"goal": "Remove a.txt from the repo.",
               "steps": ["a.txt is tracked", "Run `git rm a.txt`"],
               "hints": ["git rm deletes and stages."],
               "setup": _ONE, "check": _chk_removed},
  "quiz": [
    {"q": "--cached…",
     "options": ["Untracks, keeps file", "Deletes from disk", "Commits", "Pushes"], "answer": 0,
     "why": "Index only."},
    {"q": "git rm file.txt…",
     "options": ["Deletes + stages removal", "Unstages", "Renames", "Archives"], "answer": 0,
     "why": "Removes and records it."}]},

 {"id": "c_mv", "cat": "Snapshotting", "title": "git mv — rename & move",
  "body": """<h1>git mv</h1>
<pre>$ git mv old.txt new.txt
$ git mv file.txt src/file.txt</pre>""",
  "commands": [("git mv <old> <new>", "Rename"),
               ("git mv <file> <dir>", "Move into a directory"),
               ("git mv -k <old> <new>", "Skip errors")],
  "practice": {"goal": "Rename a.txt to b.txt.",
               "steps": ["Run `git mv a.txt b.txt`"],
               "hints": ["git mv renames + stages."],
               "setup": _ONE, "check": _chk_renamed},
  "quiz": [
    {"q": "git mv…",
     "options": ["Renames + stages", "Only renames on disk", "Commits", "Deletes"], "answer": 0,
     "why": "Move + stage in one step."},
    {"q": "Does Git detect renames without git mv?",
     "options": ["Yes, by similarity", "No", "Only with plugin", "Only on Windows"], "answer": 0,
     "why": "Renames are inferred at diff time."}]},

 {"id": "c_checkout", "cat": "Branching & Merging", "title": "git checkout — the classic switcher",
  "body": """<h1>git checkout</h1>
<pre>$ git checkout dev
$ git checkout -b dev
$ git checkout -- file.txt
$ git checkout &lt;sha&gt;      # detached HEAD</pre>""",
  "commands": [("git checkout <branch>", "Switch"),
               ("git checkout -b <branch>", "Create + switch"),
               ("git checkout -- <file>", "Discard edits"),
               ("git checkout <sha>", "Detach at a commit")],
  "practice": {"goal": "View an old commit (detached HEAD).",
               "steps": ["Two commits exist", "Run `git checkout HEAD~1`"],
               "hints": ["HEAD~1 is the previous commit."],
               "setup": _TWO, "check": _chk_detached},
  "quiz": [
    {"q": "Checking out a SHA gives…",
     "options": ["Detached HEAD", "A new branch", "The stash", "A worktree"], "answer": 0,
     "why": "HEAD points at a commit."},
    {"q": "Modern replacements…",
     "options": ["switch and restore", "add and commit", "fetch and pull", "tag and push"], "answer": 0,
     "why": "switch=branches, restore=files."}]},

 {"id": "c_mergebase", "cat": "Branching & Merging", "title": "git merge-base — common ancestor",
  "body": """<h1>git merge-base</h1>
<pre>$ git merge-base main feature
$ git merge-base --fork-point main feature</pre>""",
  "commands": [("git merge-base <a> <b>", "Common ancestor"),
               ("git merge-base --fork-point <a> <b>", "Account for rebases")],
  "practice": {"goal": "Find where main and feature diverged.",
               "steps": ["main and feature share an ancestor", "Run `git merge-base main feature`", "Write the SHA to base.txt"],
               "hints": ["Copy the SHA."],
               "setup": _ONE + ["git switch -c feature",
                                ("write", "f.txt", "f\n"), "git add .",
                                'git commit -m "feature work"',
                                "git switch main",
                                ("write", "m.txt", "m\n"), "git add .",
                                'git commit -m "main work"'],
               "check": _chk_mergebase},
  "quiz": [
    {"q": "merge-base returns…",
     "options": ["Common ancestor", "Newest commit", "A merge commit", "A tag"], "answer": 0,
     "why": "Where histories diverged."},
    {"q": "Used internally by…",
     "options": ["merge and rebase", "clone", "archive", "bundle"], "answer": 0,
     "why": "Both need the divergence point."}]},

 {"id": "c_grep", "cat": "History & Inspection", "title": "git grep — search the repo",
  "body": """<h1>git grep</h1>
<pre>$ git grep "TODO"
$ git grep -n "func"
$ git grep -i "error"</pre>""",
  "commands": [("git grep <pattern>", "Search tracked files"),
               ("git grep -n <pattern>", "Line numbers"),
               ("git grep -i <pattern>", "Case-insensitive")],
  "practice": {"goal": "Find which file contains 'needle'.",
               "steps": ["Run `git grep needle`", "Write the filename to answer.txt"],
               "hints": ["Output starts with the filename."],
               "setup": [("write", "haystack.txt", "lots of text\nneedle here\nmore\n"),
                         ("write", "other.txt", "nothing to see\n"),
                         "git add .", 'git commit -m "add files"'],
               "check": _chk_grep},
  "quiz": [
    {"q": "git grep searches…",
     "options": ["Tracked files", "The remote", "Only README", "Tags"], "answer": 0,
     "why": "The index/working tree."},
    {"q": "Search an old revision…",
     "options": ["git grep <pat> <rev>", "git grep --old", "git log <pat>", "Not possible"], "answer": 0,
     "why": "Point at any commit."}]},

 {"id": "c_lsfiles", "cat": "History & Inspection", "title": "git ls-files — list tracked files",
  "body": """<h1>git ls-files</h1>
<pre>$ git ls-files
$ git ls-files "*.py"
$ git ls-files --others
$ git ls-files --deleted</pre>""",
  "commands": [("git ls-files", "Tracked files"),
               ("git ls-files --others", "Untracked"),
               ("git ls-files --modified", "Modified"),
               ("git ls-files --stage", "Index metadata")],
  "practice": {"goal": "Count the tracked files.",
               "steps": ["Run `git ls-files`", "Write the count to count.txt"],
               "hints": ["One line per file."],
               "setup": [("write", "one.txt", "1\n"), ("write", "two.txt", "2\n"),
                         ("write", "three.txt", "3\n"), "git add .", 'git commit -m "files"'],
               "check": _chk_lsfiles_count},
  "quiz": [
    {"q": "ls-files lists…",
     "options": ["Tracked files in the index", "Remotes", "Branches", "Tags"], "answer": 0,
     "why": "Reads the index."},
    {"q": "--others shows…",
     "options": ["Untracked", "Deleted", "Staged", "Commits"], "answer": 0,
     "why": "Not in the index."}]},

 {"id": "c_describe", "cat": "History & Inspection", "title": "git describe — human-readable IDs",
  "body": """<h1>git describe</h1>
<pre>$ git describe
$ git describe --always</pre>
<div class="tip">💡 Output = tag-distance-gSHA.</div>""",
  "commands": [("git describe", "Name from nearest tag"),
               ("git describe --always", "Fall back to short SHA"),
               ("git describe --tags", "Include lightweight tags")],
  "practice": {"goal": "Describe the current commit.",
               "steps": ["A tag v1.0 is on HEAD", "Run `git describe`", "Write it to desc.txt"],
               "hints": ["With a tag on HEAD it returns the tag."],
               "setup": _ONE + ["git tag -a v1.0 -m release"],
               "check": _chk_describe},
  "quiz": [
    {"q": "describe bases output on…",
     "options": ["Nearest tag", "Branch name", "Remote", "Stash"], "answer": 0,
     "why": "tag + distance + SHA."},
    {"q": "v1.2-3-gabc1234 means…",
     "options": ["3 commits after v1.2", "3 branches", "3 remotes", "v1.2 x3"], "answer": 0,
     "why": "Distance since the tag."}]},

 {"id": "c_shortlog", "cat": "History & Inspection", "title": "git shortlog — commits by author",
  "body": """<h1>git shortlog</h1>
<pre>$ git shortlog
$ git shortlog -s
$ git shortlog -sne</pre>""",
  "commands": [("git shortlog", "Group by author"),
               ("git shortlog -s", "Counts only"),
               ("git shortlog -sne", "Counts + emails"),
               ("git shortlog -n", "Sort by count")],
  "practice": {"goal": "Count the author's commits.",
               "steps": ["Run `git shortlog -s`", "Write the count to count.txt"],
               "hints": ["All commits are by one author."],
               "setup": [("write", "a.txt", "1\n"), "git add .", 'git commit -m "one"',
                         ("write", "a.txt", "2\n"), "git add .", 'git commit -m "two"',
                         ("write", "a.txt", "3\n"), "git add .", 'git commit -m "three"'],
               "check": _chk_shortlog_count},
  "quiz": [
    {"q": "shortlog -s shows…",
     "options": ["Counts per author", "Diffs", "Tags", "Remotes"], "answer": 0,
     "why": "Just the numbers."},
    {"q": "shortlog summarizes…",
     "options": ["git log", "git status", "git diff", "git fetch"], "answer": 0,
     "why": "Condensed log."}]},

 {"id": "c_notes", "cat": "History & Inspection", "title": "git notes — annotate commits",
  "body": """<h1>git notes</h1>
<pre>$ git notes add -m "reviewed"
$ git notes show &lt;sha&gt;
$ git notes list</pre>""",
  "commands": [("git notes add -m \"msg\"", "Add a note"),
               ("git notes show <sha>", "Show a note"),
               ("git notes list", "List notes"),
               ("git notes remove <sha>", "Delete a note")],
  "practice": {"goal": "Attach a note to HEAD.",
               "steps": ['Run `git notes add -m "review me"`'],
               "hints": ["Include the word 'review'."],
               "setup": _ONE, "check": _chk_note},
  "quiz": [
    {"q": "Adding a note changes the SHA?",
     "options": ["No", "Yes", "Only on main", "Only for tags"], "answer": 0,
     "why": "Stored separately."},
    {"q": "Notes pushed by default?",
     "options": ["No", "Yes", "Only with tags", "Only on clone"], "answer": 0,
     "why": "Push refs/notes/* explicitly."}]},

 {"id": "c_revparse", "cat": "Plumbing & Internals", "title": "git rev-parse — resolve revisions",
  "body": """<h1>git rev-parse</h1>
<pre>$ git rev-parse HEAD
$ git rev-parse --abbrev-ref HEAD
$ git rev-parse --show-toplevel</pre>""",
  "commands": [("git rev-parse HEAD", "Full SHA"),
               ("git rev-parse --abbrev-ref HEAD", "Branch name"),
               ("git rev-parse --show-toplevel", "Repo root"),
               ("git rev-parse --short HEAD", "Short SHA")],
  "practice": {"goal": "Read where HEAD points.",
               "steps": ["Run `git symbolic-ref HEAD`", "Write the output to answer.txt"],
               "hints": ["It prints refs/heads/<branch>."],
               "setup": _ONE, "check": _chk_symbolicref},
  "quiz": [
    {"q": "rev-parse HEAD prints…",
     "options": ["Full SHA", "Branch list", "Log", "Status"], "answer": 0,
     "why": "Resolves to object ID."},
    {"q": "--show-toplevel prints…",
     "options": ["Repo root path", "Latest tag", "HEAD", "Remote URL"], "answer": 0,
     "why": "Top-level directory."}]},

 {"id": "c_apply", "cat": "Packaging & Transfer", "title": "git apply — patch without committing",
  "body": """<h1>git apply</h1>
<pre>$ git apply changes.patch
$ git apply --check changes.patch
$ git apply --reverse changes.patch</pre>""",
  "commands": [("git apply <patch>", "Apply"),
               ("git apply --check <patch>", "Dry run"),
               ("git apply --reverse <patch>", "Un-apply"),
               ("git apply --stat <patch>", "Preview changes")],
  "practice": {"goal": "Apply change.patch to a.txt.",
               "steps": ["change.patch holds a change", "Run `git apply change.patch`"],
               "hints": ["The patch adds a line."],
               "setup": _ONE + [("write", "a.txt", "base\nadded line\n"),
                                "git diff --output=change.patch",
                                "git checkout -- a.txt"],
               "check": _chk_apply},
  "quiz": [
    {"q": "git apply…",
     "options": ["Patches without committing", "Creates a commit", "Pushes", "Tags"], "answer": 0,
     "why": "Working tree only."},
    {"q": "Test without applying…",
     "options": ["git apply -t", "git apply --check", "git apply --test", "git verify"], "answer": 1,
     "why": "--check reports."}]},

 {"id": "c_am", "cat": "Packaging & Transfer", "title": "git am — apply patch emails",
  "body": """<h1>git am</h1>
<pre>$ git am 0001-fix.patch
$ git am *.patch
$ git am --abort</pre>""",
  "commands": [("git am <patch>", "Apply as commit"),
               ("git am --abort", "Abort"),
               ("git am --skip", "Skip current"),
               ("git am -3 <patch>", "3-way fallback")],
  "practice": {"goal": "Re-apply the saved patch as a commit.",
               "steps": ["0001-second.patch exists", "Run `git am 0001-second.patch`"],
               "hints": ["am recreates the commit."],
               "setup": _TWO + ["git format-patch -1 HEAD",
                                "git reset --hard HEAD~1"],
               "check": _chk_am},
  "quiz": [
    {"q": "git am applies…",
     "options": ["Patch emails as commits", "Tags", "Stashes", "Configs"], "answer": 0,
     "why": "format-patch → commits."},
    {"q": "Unlike apply, am preserves…",
     "options": ["Only the diff", "The filename", "Nothing", "Author and message"], "answer": 3,
     "why": "Patch metadata."}]},

 {"id": "c_cherry_cmd", "cat": "Branching & Merging", "title": "git cherry — what's not upstream",
  "body": """<h1>git cherry</h1>
<pre>$ git cherry main feature</pre>
<div class="tip">💡 Matches by patch-id, so rebased commits count as applied.</div>""",
  "commands": [("git cherry <upstream> <head>", "Commits not upstream"),
               ("git cherry -v <upstream> <head>", "With subjects")],
  "practice": {"goal": "Count commits feature has that main lacks.",
               "steps": ["feature is ahead of main", "Run `git cherry main feature`", "Count '+' lines, write to answer.txt"],
               "hints": ["Each '+' is a commit not in main."],
               "setup": _ONE + ["git switch -c feature",
                                ("write", "f1.txt", "f1\n"), "git add .",
                                'git commit -m "feature work"', "git switch main"],
               "check": _chk_cherry},
  "quiz": [
    {"q": "'+' means…",
     "options": ["Not upstream", "Deleted", "Conflict", "Tag"], "answer": 0,
     "why": "Absent from upstream."},
    {"q": "Matches by…",
     "options": ["date", "author", "patch-id", "branch name"], "answer": 2,
     "why": "Ignores SHA changes."}]},

 {"id": "c_difftool", "cat": "History & Inspection", "title": "git difftool — visual diffs",
  "body": """<h1>git difftool</h1>
<pre>$ git difftool
$ git difftool HEAD~1 HEAD
$ git config diff.tool vimdiff</pre>""",
  "commands": [("git difftool", "Diff in a viewer"),
               ("git difftool <a> <b>", "Between commits"),
               ("git config diff.tool <tool>", "Choose a tool")],
  "practice": {"goal": "Configure a diff tool.",
               "steps": ["Run `git config diff.tool vimdiff`"],
               "hints": ["Any tool name works."],
               "setup": _EMPTY, "check": _chk_difftool},
  "quiz": [
    {"q": "Before difftool you must…",
     "options": ["Configure diff.tool", "Push", "Tag", "Stash"], "answer": 0,
     "why": "Needs a viewer."},
    {"q": "difftool shows…",
     "options": ["The log", "Changes in a viewer", "Remotes", "Packs"], "answer": 1,
     "why": "External diff."}]},

 {"id": "c_mergetool", "cat": "Branching & Merging", "title": "git mergetool — resolve conflicts visually",
  "body": """<h1>git mergetool</h1>
<pre>$ git mergetool
$ git config merge.tool vimdiff</pre>""",
  "commands": [("git mergetool", "Resolve conflicts"),
               ("git config merge.tool <tool>", "Choose a tool"),
               ("git mergetool --tool=<tool>", "One-time tool")],
  "practice": {"goal": "Configure a merge tool.",
               "steps": ["Run `git config merge.tool vimdiff`"],
               "hints": ["Any tool name works."],
               "setup": _EMPTY, "check": _chk_mergetool},
  "quiz": [
    {"q": "mergetool helps with…",
     "options": ["Resolving conflicts", "Pushing", "Cloning", "Tagging"], "answer": 0,
     "why": "Visual merge."},
    {"q": "Typically run…",
     "options": ["Before init", "After push", "Only on tags", "During a conflicted merge"], "answer": 3,
     "why": "Resolves merge conflicts."}]},

 {"id": "c_sendemail", "cat": "Packaging & Transfer", "title": "git send-email — email patches",
  "body": """<h1>git send-email</h1>
<pre>$ git format-patch -2 -o patches/
$ git send-email patches/*.patch --to=maintainer@example.com</pre>""",
  "commands": [("git send-email <patches>", "Email patches"),
               ("git send-email --to=<addr> <patches>", "Set recipient"),
               ("git config sendemail.smtpserver <host>", "Configure SMTP")],
  "practice": {"goal": "Know what send-email ships.",
               "steps": ["send-email emails patches", "Which command makes them? Write to answer.txt"],
               "hints": ["It turns commits into .patch files."],
               "setup": _EMPTY, "check": _chk_sendemail},
  "quiz": [
    {"q": "send-email sends…",
     "options": ["Patch files over email", "Packs", "Tags", "Branches"], "answer": 0,
     "why": "format-patch output."},
    {"q": "Patches usually made by…",
     "options": ["git log", "git status", "git format-patch", "git clean"], "answer": 2,
     "why": "format-patch."}]},

 {"id": "c_svn", "cat": "Remotes", "title": "git svn — bridge to Subversion",
  "body": """<h1>git svn</h1>
<pre>$ git svn clone -s &lt;svn-url&gt;
$ git svn rebase
$ git svn dcommit</pre>""",
  "commands": [("git svn clone -s <url>", "Clone SVN repo"),
               ("git svn rebase", "Fetch SVN changes"),
               ("git svn dcommit", "Push to SVN")],
  "practice": {"goal": "Know what git-svn bridges.",
               "steps": ["git-svn connects Git to another VCS", "Which one? Write to answer.txt"],
               "hints": ["It's in the name."],
               "setup": _EMPTY, "check": _chk_svn},
  "quiz": [
    {"q": "git svn bridges…",
     "options": ["Subversion", "Mercurial", "Perforce", "CVS"], "answer": 0,
     "why": "svn = Subversion."},
    {"q": "Push to SVN…",
     "options": ["git push", "git svn dcommit", "git svn send", "git commit"], "answer": 1,
     "why": "dcommit."}]},

 {"id": "c_requestpull", "cat": "Remotes", "title": "git request-pull — ask for a pull",
  "body": """<h1>git request-pull</h1>
<pre>$ git request-pull v1.0 https://example.com/repo.git feature</pre>""",
  "commands": [("git request-pull <start> <url> [<end>]", "Summarize a pull request"),
               ("git request-pull -p <start> <url>", "Include the patch")],
  "practice": {"goal": "Generate a pull-request summary.",
               "steps": ["Run `git request-pull HEAD~1 .`"],
               "hints": ["start=HEAD~1, url=."],
               "setup": _TWO, "check": _chk_requestpull},
  "quiz": [
    {"q": "request-pull generates…",
     "options": ["A pull-request message", "A pack", "A tag", "A merge commit"], "answer": 0,
     "why": "For emailing maintainers."},
    {"q": "Needs a start commit and…",
     "options": ["A tag", "A stash", "A hook", "A URL/repo"], "answer": 3,
     "why": "Where to pull from."}]},

 {"id": "c_credential", "cat": "Remotes", "title": "git credential — remember authentication",
  "body": """<h1>git credential</h1>
<pre>$ git config credential.helper store
$ git config credential.helper cache
$ git config credential.helper osxkeychain</pre>""",
  "commands": [("git config credential.helper store", "Persist to disk"),
               ("git config credential.helper cache", "Cache in memory"),
               ("git credential approve/reject", "Feed the helper")],
  "practice": {"goal": "Configure a credential helper.",
               "steps": ["Run `git config credential.helper store`"],
               "hints": ["'store' keeps credentials on disk."],
               "setup": _EMPTY, "check": _chk_credhelper},
  "quiz": [
    {"q": "credential helpers…",
     "options": ["Store/provide auth", "Create branches", "Pack objects", "List tags"], "answer": 0,
     "why": "Supply tokens for remotes."},
    {"q": "Saves to disk…",
     "options": ["cache", "store", "temp", "ram"], "answer": 1,
     "why": "'store'."}]},
]

# ──────────────────────────────────────────────────────────────── FINAL COMMAND LESSONS
FINAL_COMMAND_LESSONS = [
 {"id": "c_rerere", "cat": "Branching & Merging", "title": "git rerere — reuse conflict fixes",
  "body": """<h1>git rerere</h1>
<p>"Reuse Recorded Resolution" — remembers conflict fixes and re-applies them.</p>
<pre>$ git config rerere.enabled true
$ git rerere status
$ git rerere forget &lt;path&gt;</pre>""",
  "commands": [("git config rerere.enabled true", "Enable"),
               ("git rerere status", "Show recordings"),
               ("git rerere forget <path>", "Un-learn")],
  "practice": {"goal": "Enable rerere.",
               "steps": ["Run `git config rerere.enabled true`"],
               "hints": ["Once enabled, Git records resolutions."],
               "setup": _EMPTY, "check": _chk_rerere},
  "quiz": [
    {"q": "rerere stands for…",
     "options": ["Reuse Recorded Resolution", "Remote Repo", "Reset Refs", "Rapid Rebase"], "answer": 0,
     "why": "Reuses conflict fixes."},
    {"q": "Best for…",
     "options": ["Pushing", "Tagging", "Cloning", "Repeated identical conflicts"], "answer": 3,
     "why": "Auto-applies known fixes."}]},

 {"id": "c_rangediff", "cat": "History & Inspection", "title": "git range-diff — compare revisions of a series",
  "body": """<h1>git range-diff</h1>
<pre>$ git range-diff main…feature@{1} main…feature
$ git range-diff HEAD~3..HEAD HEAD~3..HEAD</pre>""",
  "commands": [("git range-diff <a1>..<b1> <a2>..<b2>", "Compare two ranges"),
               ("git range-diff <base> <old> <new>", "Three-arg form")],
  "practice": {"goal": "Compare a range against itself.",
               "steps": ["Run `git range-diff HEAD~1..HEAD HEAD~1..HEAD`"],
               "hints": ["Shows each commit as identical."],
               "setup": _TWO, "check": _chk_rangediff},
  "quiz": [
    {"q": "range-diff compares…",
     "options": ["Two commit ranges", "Two remotes", "Two stashes", "Two configs"], "answer": 0,
     "why": "Series vs series."},
    {"q": "Handy after…",
     "options": ["Cloning", "Initing", "Revising a patch series", "Stashing"], "answer": 2,
     "why": "v1 vs v2 of a series."}]},

 {"id": "c_replace", "cat": "Plumbing & Internals", "title": "git replace — swap objects",
  "body": """<h1>git replace</h1>
<pre>$ git replace &lt;object&gt; &lt;replacement&gt;
$ git replace -l
$ git replace -d &lt;object&gt;</pre>""",
  "commands": [("git replace <obj> <repl>", "Replace an object"),
               ("git replace -l", "List replacements"),
               ("git replace -d <obj>", "Delete"),
               ("git replace --graft <commit> <parent>", "Rewire parentage")],
  "practice": {"goal": "Create an object replacement.",
               "steps": ["Run `git replace HEAD HEAD~1`", "Verify with `git replace -l`"],
               "hints": ["Treats HEAD as its parent."],
               "setup": _TWO, "check": _chk_replace},
  "quiz": [
    {"q": "git replace lets you…",
     "options": ["Treat one object as another", "Delete refs", "Push tags", "Stash"], "answer": 0,
     "why": "Maps an object to a stand-in."},
    {"q": "Stored under…",
     "options": ["refs/heads/", "refs/replace/", "refs/tags/", "refs/remotes/"], "answer": 1,
     "why": "refs/replace/*."}]},

 {"id": "c_fastexp", "cat": "Packaging & Transfer", "title": "git fast-export / fast-import — portable history",
  "body": """<h1>fast-export / fast-import</h1>
<pre>$ git fast-export --all &gt; repo.dump
$ git fast-import &lt; repo.dump</pre>""",
  "commands": [("git fast-export --all", "Export history"),
               ("git fast-export <branch>", "Export one branch"),
               ("git fast-import", "Rebuild from a dump")],
  "practice": {"goal": "Export the history and count commits.",
               "steps": ["Run `git fast-export --all`", "Count 'commit' lines, write to answer.txt"],
               "hints": ["Each commit becomes a 'commit …' line."],
               "setup": _TWO, "check": _chk_fastexport},
  "quiz": [
    {"q": "fast-export produces…",
     "options": ["A portable history stream", "A pack", "A tag", "A branch"], "answer": 0,
     "why": "A textual dump."},
    {"q": "fast-import…",
     "options": ["Push", "Clean", "Fetch", "Rebuilds a repo from the stream"], "answer": 3,
     "why": "Consumes the dump."}]},

 {"id": "c_submodule", "cat": "Advanced Workflows", "title": "git submodule — nested repositories",
  "body": """<h1>git submodule</h1>
<pre>$ git submodule add &lt;url&gt; libs/lib
$ git submodule update --init
$ git submodule status</pre>""",
  "commands": [("git submodule add <url> <path>", "Add"),
               ("git submodule update --init", "Initialize"),
               ("git submodule update --init --recursive", "Nested too"),
               ("git submodule status", "Pinned commits")],
  "practice": {"goal": "Add the local 'origin' repo as a submodule.",
               "steps": ["A repo exists at ./origin", "Run `git submodule add ./origin libs/mylib`"],
               "hints": ["Clones ./origin into libs/mylib."],
               "setup": _ONE + [("run_in", "origin", "git init -b main"),
                                ("run_in", "origin", 'git config user.name "O"'),
                                ("run_in", "origin", 'git config user.email "o@o"'),
                                ("write_in", "origin", "lib.txt", "library\n"),
                                ("run_in", "origin", "git add ."),
                                ("run_in", "origin", 'git commit -m "lib"')],
               "check": _chk_submodule},
  "quiz": [
    {"q": "A submodule is…",
     "options": ["A repo nested in another", "A branch", "A tag", "A stash"], "answer": 0,
     "why": "Separate repo, pinned commit."},
    {"q": "After cloning a repo with submodules…",
     "options": ["git gc", "git bisect", "git submodule update --init", "git shortlog"], "answer": 2,
     "why": "Populates them."}]},

 {"id": "c_mktree", "cat": "Plumbing & Internals", "title": "git mktree — build a tree from text",
  "body": """<h1>git mktree</h1>
<p>Builds a tree object from a description on stdin.</p>
<pre>$ git mktree &lt; entries.txt</pre>""",
  "commands": [("git mktree", "Read tree description on stdin"),
               ("git mktree --missing", "Allow missing objects")],
  "practice": {"goal": "Know what mktree builds.",
               "steps": ["mktree reads a tree description", "What object type? Write to answer.txt"],
               "hints": ["blob/tree/commit/tag."],
               "setup": _EMPTY, "check": _chk_tree_obj},
  "quiz": [
    {"q": "mktree creates…",
     "options": ["A tree object", "A commit", "A blob", "A remote"], "answer": 0,
     "why": "Textual listing → tree."},
    {"q": "Reads input from…",
     "options": ["a branch", "stdin", "the index", "HEAD"], "answer": 1,
     "why": "Standard input."}]},

 {"id": "c_mktag", "cat": "Plumbing & Internals", "title": "git mktag — build a tag object",
  "body": """<h1>git mktag</h1>
<p>Creates a tag object from a description on stdin.</p>
<pre>$ git mktag &lt; tag-description.txt</pre>""",
  "commands": [("git mktag", "Read tag description on stdin"),
               ("git mktag --strict", "Reject non-conforming input")],
  "practice": {"goal": "Know what mktag builds.",
               "steps": ["mktag reads a tag description", "What object type? Write to answer.txt"],
               "hints": ["blob/tree/commit/tag."],
               "setup": _EMPTY, "check": _chk_tag_obj},
  "quiz": [
    {"q": "mktag creates…",
     "options": ["A tag object", "A tree", "A pack", "A stash"], "answer": 0,
     "why": "Annotated tag object."},
    {"q": "Friendly wrapper…",
     "options": ["git branch", "git fetch", "git tag -a", "git clean"], "answer": 2,
     "why": "tag -a."}]},

 {"id": "c_packobj", "cat": "Plumbing & Internals", "title": "git pack-objects — compress into packs",
  "body": """<h1>git pack-objects</h1>
<pre>$ git rev-list --objects --all | git pack-objects pack-base
$ git repack -a</pre>""",
  "commands": [("git pack-objects <base>", "Pack objects listed on stdin"),
               ("git repack -a", "Pack all reachable"),
               ("git repack -a -d", "Pack + remove redundant")],
  "practice": {"goal": "Pack all objects and count packs.",
               "steps": ["Run `git repack -a`", "Run `git count-objects -v`", "Write 'packs:' number to answer.txt"],
               "hints": ["repack wraps pack-objects."],
               "setup": _TWO, "check": _chk_packs},
  "quiz": [
    {"q": "pack-objects produces…",
     "options": [".pack and .idx", "A branch", "A tag", "A stash"], "answer": 0,
     "why": "Pack + index."},
    {"q": "Friendly wrapper…",
     "options": ["git log", "git status", "git mv", "git repack"], "answer": 3,
     "why": "repack."}]},

 {"id": "c_unpackobj", "cat": "Plumbing & Internals", "title": "git unpack-objects — expand a pack",
  "body": """<h1>git unpack-objects</h1>
<pre>$ git unpack-objects &lt; mypack.pack</pre>""",
  "commands": [("git unpack-objects", "Read pack on stdin"),
               ("git unpack-objects -q", "Quiet"),
               ("git unpack-objects -r", "Keep going past broken")],
  "practice": {"goal": "Know where unpack-objects reads from.",
               "steps": ["It expands a pack into loose objects", "Where does it read? Write to answer.txt"],
               "hints": ["The standard input stream."],
               "setup": _EMPTY, "check": _chk_unpack_stdin},
  "quiz": [
    {"q": "unpack-objects reads…",
     "options": ["stdin", "a branch", "remote config", "a tag"], "answer": 0,
     "why": "Pack data on stdin."},
    {"q": "Turns pack data into…",
     "options": ["Refs", "Loose objects", "Tags", "Remotes"], "answer": 1,
     "why": "Individual loose objects."}]},

 {"id": "c_verifypack", "cat": "Plumbing & Internals", "title": "git verify-pack — validate a pack",
  "body": """<h1>git verify-pack</h1>
<pre>$ git verify-pack -v .git/objects/pack/pack-….idx</pre>""",
  "commands": [("git verify-pack <idx>", "Validate"),
               ("git verify-pack -v <idx>", "List objects"),
               ("git verify-pack -s <idx>", "Summary")],
  "practice": {"goal": "Inspect how many objects are packed.",
               "steps": ["A pack is prepared", "Run `git count-objects -v`", "Write 'in-pack:' number to answer.txt"],
               "hints": ["in-pack counts packed objects."],
               "setup": _TWO + ["git repack -a"], "check": _chk_inpack},
  "quiz": [
    {"q": "verify-pack takes…",
     "options": ["A .idx file", ".gitignore", "A patch", "A bundle"], "answer": 0,
     "why": "The pack index."},
    {"q": "Used to…",
     "options": ["Create a branch", "Send email", "Validate a pack", "Stash"], "answer": 2,
     "why": "Pack integrity."}]},

 {"id": "c_prunepacked", "cat": "Plumbing & Internals", "title": "git prune-packed — drop redundant loose objects",
  "body": """<h1>git prune-packed</h1>
<pre>$ git prune-packed</pre>""",
  "commands": [("git prune-packed", "Remove loose objects in packs"),
               ("git prune-packed -n", "Dry run")],
  "practice": {"goal": "Remove loose objects already packed.",
               "steps": ["A pack is prepared", "Run `git prune-packed`", "Run `git count-objects`, write count to answer.txt"],
               "hints": ["Only removes loose objects present in a pack."],
               "setup": _TWO + ["git repack -a"], "check": _chk_loose},
  "quiz": [
    {"q": "prune-packed removes…",
     "options": ["Loose objects in a pack", "All commits", "Branches", "Remotes"], "answer": 0,
     "why": "Deduplicates."},
    {"q": "Runs automatically in…",
     "options": ["git clone", "git gc", "git pull", "git diff"], "answer": 1,
     "why": "gc housekeeping."}]},
]

# Assemble + categorize
ALL_LESSONS = LESSONS + COMMAND_LESSONS + MORE_COMMAND_LESSONS + FINAL_COMMAND_LESSONS
LESSONS = ALL_LESSONS

CAT_ORDER = ["Concepts", "Getting Started", "Snapshotting", "History & Inspection",
             "Undoing", "Branching & Merging", "Stashing", "Remotes",
             "Tags & Releases", "Debugging", "Packaging & Transfer",
             "Plumbing & Internals", "Advanced Workflows", "Maintenance"]

def build_command_tree(commands):
    tree = QTreeWidget()
    tree.setColumnCount(2)
    tree.setHeaderLabels(["Command", "What it does"])
    tree.setColumnWidth(0, 360)
    tree.setAlternatingRowColors(True)
    tree.setRootIsDecorated(False)
    mono = mono_font(10)
    for cmd, desc in commands:
        it = QTreeWidgetItem([cmd, desc])
        it.setFont(0, mono)
        tree.addTopLevelItem(it)
    return tree

# ──────────────────────────────────────────────────────────────── ACHIEVEMENTS
def _cat_done(d, cat):
    ids = [les["id"] for les in LESSONS if les.get("cat") == cat]
    return bool(ids) and all(i in d.get("completed_lessons", []) for i in ids)

def _all_cats_done(d):
    done = set(d.get("completed_lessons", []))
    cats = {}
    for les in LESSONS:
        cats.setdefault(les.get("cat", "General"), []).append(les["id"])
    return all(any(i in done for i in ids) for ids in cats.values())

ACHIEVEMENTS = [
    ("first_lesson", "🎓", "First Steps", "Complete your first lesson",
     lambda d: len(d.get("completed_lessons", [])) >= 1),
    ("five_lessons", "📚", "Warming Up", "Complete 5 lessons",
     lambda d: len(d.get("completed_lessons", [])) >= 5),
    ("all_lessons", "🏆", "Git Scholar", "Complete every lesson",
     lambda d: len(d.get("completed_lessons", [])) >= len(LESSONS)),
    ("five_practices", "🧪", "Hands On", "Pass 5 practice exercises",
     lambda d: len(d.get("practice_done", [])) >= 5),
    ("all_practices", "🛠", "Practice Master", "Pass every practice exercise",
     lambda d: len(d.get("practice_done", [])) >= len(LESSONS)),
    ("five_quizzes", "🧠", "Quiz Whiz", "Master 5 lesson quizzes (≥75%)",
     lambda d: sum(1 for v in d.get("lesson_quiz_best", {}).values() if v >= 75) >= 5),
    ("all_quizzes", "🎯", "Quiz Legend", "Master every lesson quiz (≥75%)",
     lambda d: sum(1 for v in d.get("lesson_quiz_best", {}).values() if v >= 75) >= len(LESSONS)),
    ("all_cards", "🃏", "Sharp Memory", "Master every flashcard",
     lambda d: sum(1 for v in d.get("card_boxes", {}).values() if v >= 4) >= 16),
    ("plumber", "🔧", "Plumbing Plumber", "Finish all Plumbing & Internals lessons",
     lambda d: _cat_done(d, "Plumbing & Internals")),
    ("merge_master", "🔀", "Merge Master", "Finish a merging lesson",
     lambda d: any(i in d.get("completed_lessons", []) for i in ("l6", "c_merge"))),
    ("perfect_quiz", "💯", "Perfectionist", "Score 100% on the global quiz",
     lambda d: d.get("quiz_best", 0) >= 100),
    ("explorer", "🧭", "Explorer", "Complete a lesson in every category",
     lambda d: _all_cats_done(d)),
    ("conflict_resolver", "🔀", "Conflict Resolver", "Complete the merge-conflict walkthrough",
     lambda d: d.get("conflict_lab_done", False)),
    ("rebase_wrangler", "🪜", "Rebase Wrangler", "Complete the interactive-rebase walkthrough",
     lambda d: d.get("rebase_lab_done", False)),
    ("time_traveler", "⏳", "Time Traveler", "Recover a lost commit with reflog",
     lambda d: d.get("reflog_lab_done", False)),
    ("cherry_picker", "🍒", "Cherry Picker", "Complete the cherry-pick & revert lab",
     lambda d: d.get("pickrevert_lab_done", False)),
    ("bug_hunter", "🔍", "Bug Hunter", "Find the culprit with git bisect",
     lambda d: d.get("bisect_lab_done", False)),
    ("stash_master", "🧳", "Stash Master", "Complete the git stash lab",
     lambda d: d.get("stash_lab_done", False)),
]

# ──────────────────────────────────────────────────────────────── UNDO CHEAT-SHEET
UNDO_SCENARIOS = [
    ("😅", "Wrong commit message", 'git commit --amend -m "new message"',
     "Rewrites the last commit's message (and folds in anything staged)."),
    ("⏪", "Undo last commit — keep changes staged", "git reset --soft HEAD~1",
     "Moves the branch back; your edits stay staged."),
    ("💥", "Undo last commit — discard changes", "git reset --hard HEAD~1",
     "⚠ Destroys the work in that commit. Local/unshared only."),
    ("🔎", "Recover a 'lost' commit", "git reflog\ngit branch rescue <sha>",
     "The reflog lists everywhere HEAD has been; branch the lost SHA back."),
    ("🌿", "Restore a deleted branch", "git reflog\ngit branch <name> <sha>",
     "Find the branch's last tip in the reflog, then recreate it."),
    ("🔀", "Committed on the wrong branch",
     "git reset --soft HEAD~1\ngit stash\ngit switch <right-branch>\ngit stash pop\ngit commit -m \"…\"",
     "Move the changes to the correct branch."),
    ("📤", "Undo an already-pushed commit", "git revert <sha>",
     "Adds an opposite commit — safe for shared history."),
    ("🧩", "Abort a bad merge", "git merge --abort",
     "Returns to the pre-merge state."),
    ("🪜", "Abort a bad rebase", "git rebase --abort\ngit reset --hard ORIG_HEAD",
     "abort restores the pre-rebase state; ORIG_HEAD is your safety marker."),
    ("🕳", "Recover work from detached HEAD", "git reflog\ngit branch <name> <sha>",
     "Detached commits live in the reflog until pruned."),
    ("📄", "Recover a deleted/changed file from history", "git restore --source=<sha> -- <file>",
     "Pulls a file back exactly as it was at <sha>."),
]

# ──────────────────────────────────────────────────────────────── WIDGETS
class HistoryLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._history = []
        self._pos = 0
    def add_history(self, cmd):
        cmd = cmd.strip()
        if cmd and (not self._history or self._history[-1] != cmd):
            self._history.append(cmd)
        self._pos = len(self._history)
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Up:
            if self._history and self._pos > 0:
                self._pos -= 1
                self.setText(self._history[self._pos])
        elif e.key() == Qt.Key_Down:
            if self._pos < len(self._history):
                self._pos += 1
                self.setText(self._history[self._pos] if self._pos < len(self._history) else "")
        else:
            super().keyPressEvent(e)

class GitConsole(QWidget):
    COLORS = {"prompt": "#ff9e6d", "out": "#d8dee9", "err": "#ff8a80",
              "info": "#88c0d0", "dim": "#777e88", "ok": "#a5d6a7"}
    FORBIDDEN = {"-C", "--git-dir", "--work-tree"}
    dirCreated = Signal(str)
    commandFinished = Signal()

    def __init__(self, placeholder="Type any git command… (Enter to run)"):
        super().__init__()
        self._dir = None
        self.git_path = shutil.which("git")
        self.extra_env = {}
        v = QVBoxLayout(self); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(8)
        self.console = QTextEdit()
        self.console.setObjectName("console")
        self.console.setReadOnly(True)
        self.console.setFont(mono_font(10))
        irow = QHBoxLayout()
        prompt = QLabel("$")
        prompt.setStyleSheet("color:#ff9e6d; font-weight:700; font-size:16px;")
        prompt.setFont(mono_font(12))
        self.cmd_edit = HistoryLineEdit()
        self.cmd_edit.setFont(mono_font(11))
        self.cmd_edit.setPlaceholderText(placeholder)
        self.cmd_edit.returnPressed.connect(self._on_enter)
        irow.addWidget(prompt); irow.addWidget(self.cmd_edit, 1)
        v.addWidget(self.console, 1); v.addLayout(irow)

    @property
    def dir(self):
        return self._dir

    def append(self, text, kind="out"):
        self.console.append(
            f'<pre style="margin:0 0 2px 0; color:{self.COLORS[kind]}; '
            f'white-space:pre-wrap;">{html.escape(text)}</pre>')

    def ensure_dir(self):
        if self._dir is None or not self._dir.exists():
            self._dir = Path(tempfile.mkdtemp(prefix="gitdojo_"))
            self.dirCreated.emit(str(self._dir))
        return self._dir

    def _on_enter(self):
        text = self.cmd_edit.text().strip()
        self.cmd_edit.clear()
        if text:
            self.cmd_edit.add_history(text)
            self.run(text)

    def run(self, cmdline, echo=True, cwd=None, notify=True):
        if not self.git_path:
            self.append("git is not installed — cannot run.", "err")
            return None
        try:
            tokens = shlex.split(cmdline)
        except ValueError:
            tokens = cmdline.split()
        if not tokens:
            return None
        if tokens[0].lower() != "git":
            self.append("Only git commands are allowed here 🙂", "err")
            return None
        if any(t in self.FORBIDDEN for t in tokens):
            self.append("That flag is disabled in this sandbox.", "err")
            return None
        d = cwd if cwd is not None else self.ensure_dir()
        env = dict(os.environ, GIT_PAGER="cat", PAGER="cat", GIT_TERMINAL_PROMPT="0")
        env.update(self.extra_env)
        try:
            r = subprocess.run(tokens, cwd=str(d), capture_output=True,
                               text=True, timeout=15, env=env)
        except subprocess.TimeoutExpired:
            self.append("⏱ Command timed out.", "err"); return None
        except Exception as exc:
            self.append(f"Error: {exc}", "err"); return None
        if echo:
            self.append("$ " + cmdline, "prompt")
        if r.stdout.strip():
            self.append(r.stdout.rstrip(), "out")
        if r.stderr.strip():
            self.append(r.stderr.rstrip(), "err" if r.returncode else "info")
        if r.returncode:
            self.append(f"(exit code {r.returncode})", "dim")
        if notify:
            self.commandFinished.emit()
        return r

    def reset_dir(self):
        self.cleanup()
        self._dir = None

    def cleanup(self):
        if self._dir and self._dir.exists():
            shutil.rmtree(self._dir, ignore_errors=True)

class CardWidget(QFrame):
    clicked = Signal()
    def __init__(self):
        super().__init__()
        self.setProperty("card", True)
        self.setMinimumHeight(230)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        v = QVBoxLayout(self)
        v.addStretch()
        self.kind = QLabel(""); self.kind.setObjectName("sub")
        self.kind.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text = QLabel(""); self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text.setWordWrap(True)
        self.text.setStyleSheet("font-size:20px; padding:0 24px;")
        v.addWidget(self.kind); v.addWidget(self.text); v.addStretch()
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(e)

class WorkflowDiagram(QWidget):
    BOXES = [("Working\nDirectory", "#3b82f6"), ("Staging\nArea", "#f59e0b"),
             ("Local\nRepository", "#f05033"), ("Remote\nRepository", "#22c55e")]
    def __init__(self):
        super().__init__()
        self.setFixedHeight(215)
        self.setMinimumWidth(680)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    @staticmethod
    def _arrow(p, x1, x2, y, label, color, dashed=False):
        pen = QPen(color, 2)
        if dashed:
            pen.setStyle(Qt.PenStyle.DashLine)
        p.setPen(pen)
        tip = x2 - (9 if x2 > x1 else -9)
        p.drawLine(QPointF(x1, y), QPointF(tip, y))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(color)
        d = 9 if x2 > x1 else -9
        p.drawPolygon(QPolygonF([QPointF(x2, y), QPointF(x2 - d, y - 5), QPointF(x2 - d, y + 5)]))
        if label:
            p.setPen(color)
            f = QFont(); f.setPointSize(9); f.setItalic(True)
            p.setFont(f)
            p.drawText(QRectF(x1, y - 26, x2 - x1, 18), Qt.AlignmentFlag.AlignCenter, label)
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        n = len(self.BOXES)
        margin, gap, bh, y = 12, 56, 72, 64
        bw = (w - 2 * margin - (n - 1) * gap) / n
        if bw < 70:
            gap = 26
            bw = (w - 2 * margin - (n - 1) * gap) / n
        font = QFont(); font.setBold(True); font.setPointSize(10)
        p.setFont(font)
        rects = []
        for i, (label, c) in enumerate(self.BOXES):
            x = margin + i * (bw + gap)
            r = QRectF(x, y, bw, bh)
            color = QColor(c)
            p.setPen(QPen(color, 2))
            p.setBrush(QBrush(color.darker(145)))
            p.drawRoundedRect(r, 12, 12)
            p.setPen(QColor("#ffffff"))
            p.drawText(r, Qt.AlignmentFlag.AlignCenter, label)
            rects.append(r)
        ay = y + bh / 2
        for i, lab in enumerate(["git add", "git commit", "git push"]):
            self._arrow(p, rects[i].right() + 4, rects[i + 1].left() - 4, ay, lab, QColor("#cbd2dc"))
        y2 = y + bh + 32
        self._arrow(p, rects[3].center().x(), rects[0].center().x(), y2, "", QColor("#9aa0aa"), dashed=True)
        p.setPen(QColor("#9aa0aa"))
        lf = QFont(); lf.setItalic(True); lf.setPointSize(9)
        p.setFont(lf)
        p.drawText(QRectF(rects[0].left(), y2 + 8, rects[3].right() - rects[0].left(), 20),
                   Qt.AlignmentFlag.AlignCenter, "git fetch / git pull")

class CommitGraphWidget(QWidget):
    def __init__(self, console):
        super().__init__()
        self.console = console
        self.nodes = []; self.edges = []; self._max_lane = 0
        self.setMinimumWidth(560)
        self.refresh()
    def refresh(self):
        self._build()
        self.setMinimumHeight(max(120, 36 + len(self.nodes) * 26))
        self.update()
    def _build(self):
        self.nodes = []; self.edges = []; self._max_lane = 0
        if not self.console.git_path:
            return
        r = self.console.run("git log --all --pretty=%H%x1f%P%x1f%d%x1f%s",
                             echo=False, notify=False)
        if not r or r.returncode != 0 or not r.stdout.strip():
            return
        commits = []
        for line in r.stdout.splitlines():
            parts = line.split('\x1f')
            if len(parts) < 4:
                continue
            commits.append({"hash": parts[0], "parents": parts[1].split(),
                            "deco": parts[2], "subject": parts[3]})
        active = []
        for row, c in enumerate(commits):
            h = c["hash"]
            if h in active:
                lane = active.index(h)
            elif None in active:
                lane = active.index(None); active[lane] = h
            else:
                lane = len(active); active.append(h)
            c["lane"] = lane; c["row"] = row
            self.nodes.append(c)
            self._max_lane = max(self._max_lane, lane)
            parents = c["parents"]
            active[lane] = parents[0] if parents else None
            for p in parents[1:]:
                if p not in active:
                    active.append(p)
        row_of = {c["hash"]: c["row"] for c in self.nodes}
        lane_of = {c["hash"]: c["lane"] for c in self.nodes}
        for c in self.nodes:
            for p in c["parents"]:
                if p in row_of:
                    self.edges.append((c["row"], c["lane"], row_of[p], lane_of[p]))
    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor("#101116"))
        if not self.nodes:
            p.setPen(QColor("#8a9099"))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                       "No commits yet — init a repo and commit in the sandbox to see the graph.")
            return
        row_h, lane_w, margin = 26, 22, 18
        palette = [QColor("#f05033"), QColor("#3b82f6"), QColor("#22c55e"), QColor("#f59e0b"),
                   QColor("#a855f7"), QColor("#ec4899"), QColor("#14b8a6"), QColor("#eab308")]
        col = lambda l: palette[l % len(palette)]
        for (r1, l1, r2, l2) in self.edges:
            x1 = margin + l1*lane_w; y1 = margin + r1*row_h
            x2 = margin + l2*lane_w; y2 = margin + r2*row_h
            p.setPen(QPen(col(l1), 2))
            path = QPainterPath(QPointF(x1, y1))
            midy = (y1 + y2) / 2
            path.cubicTo(QPointF(x1, midy), QPointF(x2, midy), QPointF(x2, y2))
            p.drawPath(path)
        label_x = margin + (self._max_lane + 1)*lane_w + 14
        p.setFont(mono_font(9))
        for c in self.nodes:
            x = margin + c["lane"]*lane_w; y = margin + c["row"]*row_h
            p.setPen(QPen(col(c["lane"]).darker(130), 1.5))
            p.setBrush(col(c["lane"]))
            p.drawEllipse(QPointF(x, y), 5, 5)
            deco = c.get("deco", "").strip().strip("()").strip()
            txt = (f"({deco}) " if deco else "") + c["hash"][:7] + "  " + c["subject"]
            p.setPen(QColor("#d8dee9"))
            p.drawText(QPointF(label_x, y + 4), txt)

class MiniQuizWidget(QWidget):
    SS_CORRECT = "QPushButton{background:#1f6f34;border:1px solid #2fa04f;color:white;}"
    SS_WRONG = "QPushButton{background:#8c2f2f;border:1px solid #c04545;color:white;}"
    def __init__(self, questions, on_finish=None, autostart=False):
        super().__init__()
        self.questions = questions
        self.on_finish = on_finish
        self.order, self.idx, self.score = [], 0, 0
        self.stack = QStackedWidget()
        QVBoxLayout(self).addWidget(self.stack)
        self.start_w = QWidget(); sv = QVBoxLayout(self.start_w); sv.addStretch()
        self.best_lbl = QLabel(); self.best_lbl.setObjectName("sub")
        self.best_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        go = make_button("Start ▶", self.start, accent=True)
        sv.addWidget(self.best_lbl)
        hh = QHBoxLayout(); hh.addStretch(); hh.addWidget(go); hh.addStretch()
        sv.addLayout(hh); sv.addStretch()
        self.play_w = QWidget(); pv = QVBoxLayout(self.play_w); pv.setSpacing(12)
        meta_row = QHBoxLayout()
        self.q_meta = QLabel(); self.q_meta.setObjectName("sub")
        self.q_label = QLabel(); self.q_label.setWordWrap(True)
        self.q_label.setStyleSheet("font-size:16px; font-weight:600;")
        self.choices = QVBoxLayout(); self.choice_btns = []
        for i in range(4):
            b = QPushButton(); b.setMinimumHeight(42)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _=False, i=i: self._answer(i))
            self.choices.addWidget(b); self.choice_btns.append(b)
        self.why = QLabel(); self.why.setObjectName("why"); self.why.setWordWrap(True)
        self.why.hide()
        self.next_btn = make_button("Next →", self._next, accent=True)
        self.next_btn.setEnabled(False)
        nrow = QHBoxLayout(); nrow.addStretch(); nrow.addWidget(self.next_btn)
        meta_row.addWidget(self.q_meta); meta_row.addStretch()
        pv.addLayout(meta_row); pv.addWidget(self.q_label)
        pv.addLayout(self.choices); pv.addWidget(self.why)
        pv.addStretch(); pv.addLayout(nrow)
        self.done_w = QWidget(); dv = QVBoxLayout(self.done_w); dv.addStretch()
        self.result_lbl = QLabel(); self.result_lbl.setObjectName("h1")
        self.result_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_msg = QLabel(); self.result_msg.setObjectName("sub")
        self.result_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_msg.setWordWrap(True)
        again = make_button("Play again 🔁", self.start, accent=True)
        dv.addWidget(self.result_lbl); dv.addWidget(self.result_msg); dv.addSpacing(8)
        rr = QHBoxLayout(); rr.addStretch(); rr.addWidget(again); rr.addStretch()
        dv.addLayout(rr); dv.addStretch()
        self.stack.addWidget(self.start_w); self.stack.addWidget(self.play_w); self.stack.addWidget(self.done_w)
        if autostart:
            self.start()
        else:
            self.stack.setCurrentWidget(self.start_w)
    def set_best(self, text):
        self.best_lbl.setText(text)
    def to_start(self):
        self.stack.setCurrentWidget(self.start_w)
    def start(self):
        if not self.questions:
            return
        self.order = random.sample(self.questions, len(self.questions))
        self.idx, self.score = 0, 0
        self.stack.setCurrentWidget(self.play_w)
        self._show_question()
    def _show_question(self):
        q = self.order[self.idx]
        self.q_meta.setText(f"Question {self.idx + 1} of {len(self.order)}    •    Score: {self.score}")
        self.q_label.setText(q["q"])
        for i, b in enumerate(self.choice_btns):
            if i < len(q["options"]):
                b.setText(q["options"][i]); b.show()
            else:
                b.hide()
            b.setStyleSheet(""); b.setEnabled(True)
        self.why.hide()
        last = self.idx == len(self.order) - 1
        self.next_btn.setText("See results 🏁" if last else "Next →")
        self.next_btn.setEnabled(False)
    def _answer(self, chosen):
        q = self.order[self.idx]
        correct = q["answer"]
        for i, b in enumerate(self.choice_btns[: len(q["options"])]):
            b.setEnabled(False)
            if i == correct:
                b.setStyleSheet(self.SS_CORRECT)
            elif i == chosen:
                b.setStyleSheet(self.SS_WRONG)
        if chosen == correct:
            self.score += 1
        self.q_meta.setText(f"Question {self.idx + 1} of {len(self.order)}    •    Score: {self.score}")
        self.why.setText("💡 " + q["why"]); self.why.show()
        self.next_btn.setEnabled(True)
    def _next(self):
        self.idx += 1
        if self.idx >= len(self.order):
            self._finish()
        else:
            self._show_question()
    def _finish(self):
        total = len(self.order)
        pct = round(100 * self.score / total)
        if self.on_finish:
            self.on_finish(self.score, total, pct)
        self.result_lbl.setText(f"{self.score} / {total}   ({pct}%)")
        if pct >= 90: msg = "Outstanding! 🏆"
        elif pct >= 70: msg = "Great job — review the misses and go again."
        elif pct >= 50: msg = "Solid start. A second pass will help."
        else: msg = "Keep practicing — revisit the lesson and retry!"
        self.result_msg.setText(msg)
        self.stack.setCurrentWidget(self.done_w)

class PracticeWidget(QWidget):
    def __init__(self, practice, on_success=None):
        super().__init__()
        self.practice = practice or {}
        self.on_success = on_success
        self.file_n = 0
        self.hint_idx = 0
        v = QVBoxLayout(self); v.setContentsMargins(6, 6, 6, 6); v.setSpacing(10)
        goal = QLabel("🎯 " + self.practice.get("goal", ""))
        goal.setWordWrap(True)
        goal.setStyleSheet("font-size:15px; font-weight:600; color:#ffd166;")
        v.addWidget(goal)
        steps = self.practice.get("steps", [])
        if steps:
            lines = "".join(f"<div>{i+1}. {html.escape(s.replace(chr(96), ''))}</div>"
                            for i, s in enumerate(steps))
            steps_lbl = QLabel(lines)
            steps_lbl.setTextFormat(Qt.TextFormat.RichText)
            steps_lbl.setWordWrap(True)
            steps_lbl.setStyleSheet("color:#cfd2d6;")
            v.addWidget(steps_lbl)
        brow = QHBoxLayout()
        self.start_btn = make_button("▶ Start / Reset exercise", self._prepare, accent=True)
        self.file_btn = make_button("＋ New file", self._new_file)
        self.check_btn = make_button("✓ Check my work", self._check, prop="green")
        self.hint_btn = make_button("💡 Hint", self._hint)
        brow.addWidget(self.start_btn); brow.addWidget(self.file_btn)
        brow.addWidget(self.check_btn); brow.addWidget(self.hint_btn); brow.addStretch()
        v.addLayout(brow)
        wrow = QHBoxLayout()
        self.wf_name = QLineEdit(); self.wf_name.setPlaceholderText("filename.txt")
        self.wf_content = QLineEdit(); self.wf_content.setPlaceholderText("file content")
        self.wf_btn = make_button("✎ Write file", self._write_file)
        wrow.addWidget(QLabel("✎")); wrow.addWidget(self.wf_name)
        wrow.addWidget(self.wf_content, 1); wrow.addWidget(self.wf_btn)
        v.addLayout(wrow)
        self.hint_lbl = QLabel(); self.hint_lbl.setWordWrap(True)
        self.hint_lbl.setStyleSheet("color:#ffd166; background:#232016; border-left:3px solid #ffd166; padding:8px; border-radius:4px;")
        self.hint_lbl.hide()
        v.addWidget(self.hint_lbl)
        self.result_lbl = QLabel(); self.result_lbl.setWordWrap(True)
        self.result_lbl.setStyleSheet("color:#a5d6a7;"); self.result_lbl.hide()
        v.addWidget(self.result_lbl)
        self.console = GitConsole("Run git commands here… (Enter)")
        self.path_lbl = QLabel(""); self.path_lbl.setObjectName("sub")
        self.console.dirCreated.connect(lambda p: self.path_lbl.setText("repo: " + p))
        v.addWidget(self.path_lbl); v.addWidget(self.console, 1)
        if not self.practice.get("hints"):
            self.hint_btn.setEnabled(False)
    def _prepare(self):
        self.hint_idx = 0
        self.hint_btn.setText("💡 Hint")
        self.hint_btn.setEnabled(bool(self.practice.get("hints")))
        self.hint_lbl.hide(); self.result_lbl.hide()
        self.console.reset_dir(); self.console.ensure_dir()
        self.console.run("git init", echo=False, notify=False)
        self.console.run("git symbolic-ref HEAD refs/heads/main", echo=False, notify=False)
        self.console.run('git config user.name "Practice User"', echo=False, notify=False)
        self.console.run('git config user.email "practice@gitdojo.local"', echo=False, notify=False)
        for step in self.practice.get("setup", []):
            self._do_setup_step(step)
        self.console.append("Exercise ready — follow the steps, then 'Check my work'. ✓", "ok")
    def _do_setup_step(self, step):
        if isinstance(step, tuple) and step:
            kind = step[0]
            if kind == "write":
                _, name, content = step
                (self.console.dir / name).write_text(content, encoding="utf-8")
                self.console.append(f"created {name}", "info")
            elif kind == "write_in":
                _, subdir, name, content = step
                sd = self.console.dir / subdir; sd.mkdir(parents=True, exist_ok=True)
                (sd / name).write_text(content, encoding="utf-8")
                self.console.append(f"created {subdir}/{name}", "info")
            elif kind == "run_in":
                _, subdir, cmd = step
                sd = self.console.dir / subdir; sd.mkdir(parents=True, exist_ok=True)
                self.console.run(cmd, echo=False, notify=False, cwd=sd)
            else:
                self.console.run(step, echo=False, notify=False)
        else:
            self.console.run(step, echo=False, notify=False)
    def _new_file(self):
        d = self.console.ensure_dir()
        self.file_n += 1
        name = f"file_{self.file_n}.txt"
        (d / name).write_text(f"content {self.file_n}\n", encoding="utf-8")
        self.console.append(f"created {name} (untracked until you `git add` it)", "info")
    def _write_file(self):
        name = self.wf_name.text().strip()
        if not name:
            return
        d = self.console.ensure_dir()
        (d / name).write_text(self.wf_content.text(), encoding="utf-8")
        self.console.append(f"wrote {name}", "info")
        self.wf_name.clear(); self.wf_content.clear()
    def _hint(self):
        hints = self.practice.get("hints", [])
        if not hints:
            return
        self.result_lbl.setText("💡 " + hints[self.hint_idx])
        self.result_lbl.setStyleSheet("color:#ffd166;")
        self.result_lbl.show()
        self.hint_idx += 1
        if self.hint_idx >= len(hints):
            self.hint_btn.setText("💡 No more hints")
            self.hint_btn.setEnabled(False)
    def _check(self):
        check = self.practice.get("check")
        if not check:
            self._result("No check defined for this exercise.", False); return
        try:
            ok, msg = check(self.console)
        except Exception as exc:
            ok, msg = False, f"Check errored: {exc}"
        self._result(msg, ok)
        if ok and self.on_success:
            self.on_success()
    def _result(self, msg, ok):
        self.result_lbl.setText(("✅ " if ok else "🔁 ") + msg)
        self.result_lbl.setStyleSheet("color:#a5d6a7;" if ok else "color:#ff8a80;")
        self.result_lbl.show()
    def cleanup(self):
        self.console.cleanup()

# ──────────────────────────────────────────────────────────────── WALKTHROUGH ENGINE
TODO_EDITOR = '''import sys, os
d = os.path.dirname(os.path.abspath(__file__))
todo = sys.argv[1]
plan = []
pp = os.path.join(d, "gd_plan.txt")
if os.path.exists(pp):
    with open(pp) as f:
        plan = [l.rstrip("\\n") for l in f if l.strip()]
with open(todo) as f:
    lines = f.readlines()
commits = [l for l in lines if l.startswith("pick ")]
tail = [l for l in lines if not l.startswith("pick ")]
out = []
for i, c in enumerate(commits):
    body = c[5:].rstrip("\\n")
    sha = body.split(" ", 1)[0]
    action, msg = "pick", None
    if i < len(plan):
        p = plan[i].split("|", 1)
        action = p[0]
        if len(p) > 1:
            msg = p[1]
    out.append(f"{action} {sha} {msg}\\n" if msg is not None else f"{action} {body}\\n")
out.extend(tail)
with open(todo, "w") as f:
    f.writelines(out)
'''

MSG_EDITOR = '''import sys, os
d = os.path.dirname(os.path.abspath(__file__))
target = sys.argv[1]
mp = os.path.join(d, "gd_msg.txt")
msg = ""
if os.path.exists(mp):
    with open(mp) as f:
        msg = f.read()
with open(target, "w") as f:
    f.write(msg)
'''

class WalkthroughPage(QWidget):
    page_title = "Walkthrough"
    page_intro = ""
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.step_idx = 0
        self.started = False
        self._define_steps()
        v = QVBoxLayout(self); v.setContentsMargins(24, 20, 24, 20); v.setSpacing(10)
        head = QHBoxLayout()
        t = QLabel(self.page_title); t.setObjectName("h1")
        head.addWidget(t); head.addStretch()
        head.addWidget(make_button("▶ Start / Reset", self._start, accent=True))
        v.addLayout(head)
        sub = QLabel(self.page_intro); sub.setObjectName("sub"); v.addWidget(sub)
        self.prog_lbl = QLabel(); self.prog_lbl.setObjectName("sub")
        self.prog_bar = QProgressBar(); self.prog_bar.setTextVisible(False)
        self.prog_bar.setFixedHeight(8)
        v.addWidget(self.prog_lbl); v.addWidget(self.prog_bar)
        self.step_view = QTextBrowser(); self.step_view.setFixedHeight(170)
        v.addWidget(self.step_view)
        self.console = GitConsole("Run git commands here… (Enter)")
        v.addWidget(self.console, 1)
        crow = QHBoxLayout()
        self.hint_btn = make_button("💡 Hint", self._show_hint)
        self.check_btn = make_button("✓ Check step", self._check, prop="green")
        crow.addWidget(self.hint_btn); crow.addWidget(self.check_btn); crow.addStretch()
        v.addLayout(crow)
        self.feedback = QLabel(); self.feedback.setWordWrap(True); self.feedback.hide()
        v.addWidget(self.feedback)
        self._render()
    def _define_steps(self):
        self.steps = []
    def setup(self):
        pass
    def on_complete(self):
        pass
    def _start(self):
        self.setup()
        self.started = True
        self.step_idx = 0
        self._render()
    def _render(self):
        n = len(self.steps)
        if n == 0:
            return
        idx = min(self.step_idx, n - 1)
        step = self.steps[idx]
        self.prog_lbl.setText(f"Step {idx + 1} of {n} — {step['title']}")
        self.prog_bar.setRange(0, n); self.prog_bar.setValue(idx + 1)
        self.step_view.setHtml(step["body"])
        self.hint_btn.setEnabled(bool(step.get("hint")))
        self.check_btn.setEnabled(step.get("check") is not None)
        self.feedback.hide()
        if step.get("enter"):
            step["enter"]()
    def _check(self):
        if not self.started:
            self._feedback("Click 'Start / Reset' first.", False); return
        step = self.steps[self.step_idx]
        check = step.get("check")
        if not check:
            return
        ok, msg = check(self.console)
        if ok:
            if self.step_idx < len(self.steps) - 1:
                self.step_idx += 1
            if self.step_idx == len(self.steps) - 1:
                self.on_complete()
            self._render()
            self._feedback("✓ " + msg, True)
        else:
            self._feedback("🔁 " + msg, False)
    def _show_hint(self):
        hint = self.steps[self.step_idx].get("hint", "")
        if hint:
            self._feedback("💡 " + hint, True)
    def _feedback(self, msg, ok):
        self.feedback.setText(msg)
        self.feedback.setStyleSheet("color:#a5d6a7;" if ok else "color:#ff8a80;")
        self.feedback.show()
    def refresh(self):
        pass

# ──────────────────────────────────────────────────────────────── LABS
class ConflictLabPage(WalkthroughPage):
    page_title = "🔀 Conflict Lab — guided merge-conflict walkthrough"
    page_intro = "Create, hit, and resolve a real merge conflict — step by step."
    def setup(self):
        c = self.console
        c.reset_dir(); c.ensure_dir()
        c.run("git init", echo=False, notify=False)
        c.run("git symbolic-ref HEAD refs/heads/main", echo=False, notify=False)
        c.run('git config user.name "Walkthrough"', echo=False, notify=False)
        c.run('git config user.email "walk@gitdojo.local"', echo=False, notify=False)
        (c.dir / "greeting.txt").write_text("Hello\n", encoding="utf-8")
        c.run("git add greeting.txt", echo=False, notify=False)
        c.run('git commit -m "initial greeting"', echo=False, notify=False)
        c.run("git switch -c feature", echo=False, notify=False)
        (c.dir / "greeting.txt").write_text("Hello from feature\n", encoding="utf-8")
        c.run("git add greeting.txt", echo=False, notify=False)
        c.run('git commit -m "feature greeting"', echo=False, notify=False)
        c.run("git switch main", echo=False, notify=False)
        (c.dir / "greeting.txt").write_text("Hello from main\n", encoding="utf-8")
        c.run("git add greeting.txt", echo=False, notify=False)
        c.run('git commit -m "main greeting"', echo=False, notify=False)
        self.started = True
        c.append("Scenario ready: main and feature both changed greeting.txt.", "ok")
    def _define_steps(self):
        self.steps = [
            {"title": "The scenario",
             "body": """<p>Two branches <b>edited the same line</b> of <code>greeting.txt</code>:</p>
                        <ul><li><code>main</code>: <i>Hello from main</i></li>
                        <li><code>feature</code>: <i>Hello from feature</i></li></ul>
                        <p>You're on <code>main</code>. Click <b>✓ Check step</b> to confirm.</p>""",
             "hint": "Just click ✓ Check step — the scenario is built.",
             "check": self._chk_scenario},
            {"title": "Attempt the merge",
             "body": """<p>Run the merge:</p><pre>git merge feature</pre>
                        <p>Both branches changed the <i>same line</i>, so Git stops with a <b>conflict</b>.</p>""",
             "hint": "Type `git merge feature` and press Enter.",
             "check": self._chk_conflict},
            {"title": "Read the conflict",
             "body": """<p>Look at <code>greeting.txt</code>. Git marks the disputed region:</p>
                        <pre>&lt;&lt;&lt;&lt;&lt;&lt;&lt; HEAD
Hello from main
=======
Hello from feature
&gt;&gt;&gt;&gt;&gt;&gt;&gt; feature</pre>
                        <p>Run <code>git status</code> too.</p>""",
             "hint": "Run `git status` and read greeting.txt.",
             "check": self._chk_markers},
            {"title": "Resolve it",
             "body": """<p>Decide what the file should say, then rewrite it <b>without</b> the markers
                        using the <b>✎ Write file</b> row (filename <code>greeting.txt</code>).</p>""",
             "hint": "Write greeting.txt with content that has no conflict markers.",
             "check": self._chk_resolved},
            {"title": "Stage the resolution",
             "body": """<p>Mark it resolved:</p><pre>git add greeting.txt</pre>""",
             "hint": "`git add greeting.txt`.",
             "check": self._chk_staged},
            {"title": "Complete the merge",
             "body": """<p>Finalize:</p><pre>git commit --no-edit</pre>
                        <p>This creates a <b>merge commit</b> with two parents.</p>""",
             "hint": "`git commit --no-edit`.",
             "check": self._chk_mergecommit},
            {"title": "Done!",
             "body": """<p>🎉 You resolved a merge conflict like a pro. Run
                        <code>git log --oneline --graph</code>, then <b>Start / Reset</b> to repeat.</p>""",
             "hint": "", "check": None},
        ]
    def _write_file(self, name, content):
        (self.console.dir / name).write_text(content, encoding="utf-8")
    def _chk_scenario(self, c):
        b = c.run("git branch", echo=False, notify=False)
        if b and b.returncode == 0 and "main" in b.stdout and "feature" in b.stdout:
            cur = c.run("git rev-parse --abbrev-ref HEAD", echo=False, notify=False)
            if cur and cur.stdout.strip() == "main":
                return True, "Scenario ready — main and feature diverge."
        return False, "Click 'Start / Reset' to build the scenario."
    def _chk_conflict(self, c):
        r = c.run("git ls-files -u", echo=False, notify=False)
        if r and r.stdout.strip():
            return True, "Merge started — Git hit a conflict."
        return False, "Run `git merge feature`."
    def _chk_markers(self, c):
        txt = _ftext(c, "greeting.txt")
        if "<<<<<<<" in txt and ">>>>>>>" in txt:
            return True, "The conflict markers are visible."
        return False, "The markers should be in greeting.txt."
    def _chk_resolved(self, c):
        txt = _ftext(c, "greeting.txt")
        if txt and "<<<<<<<" not in txt and ">>>>>>>" not in txt:
            return True, "Markers gone — conflict resolved."
        return False, "Rewrite greeting.txt without the markers."
    def _chk_staged(self, c):
        r = c.run("git ls-files -u", echo=False, notify=False)
        if r is not None and not r.stdout.strip():
            return True, "Staged — no unmerged paths remain."
        return False, "Run `git add greeting.txt`."
    def _chk_mergecommit(self, c):
        r = c.run("git rev-list --parents -1 HEAD", echo=False, notify=False)
        if r and r.returncode == 0 and len(r.stdout.split()) >= 3:
            return True, "Merge complete — HEAD is a merge commit."
        return False, "Run `git commit --no-edit`."
    def on_complete(self):
        self.store.data["conflict_lab_done"] = True
        self.store.save()

class RebaseLabPage(WalkthroughPage):
    page_title = "🪜 Rebase Lab — squash & reword"
    page_intro = "Drive a real git rebase -i to squash and reword commits, step by step."
    def _write(self, name, content):
        (self.console.dir / name).write_text(content, encoding="utf-8")
    def setup(self):
        c = self.console
        c.reset_dir(); c.ensure_dir()
        d = c.dir
        c.run("git init", echo=False, notify=False)
        c.run("git symbolic-ref HEAD refs/heads/main", echo=False, notify=False)
        c.run('git config user.name "Rebase Lab"', echo=False, notify=False)
        c.run('git config user.email "rebase@gitdojo.local"', echo=False, notify=False)
        (d / "gd_todo_editor.py").write_text(TODO_EDITOR, encoding="utf-8")
        (d / "gd_msg_editor.py").write_text(MSG_EDITOR, encoding="utf-8")
        exe = Path(sys.executable).as_posix()
        c.extra_env["GIT_SEQUENCE_EDITOR"] = f'"{exe}" "{(d / "gd_todo_editor.py").as_posix()}"'
        c.extra_env["GIT_EDITOR"] = f'"{exe}" "{(d / "gd_msg_editor.py").as_posix()}"'
        (d / "app.py").write_text("def login():\n    pass\n", encoding="utf-8")
        c.run("git add app.py", echo=False, notify=False)
        c.run('git commit -m "Add login form"', echo=False, notify=False)
        (d / "app.py").write_text("def login():\n    return True\n", encoding="utf-8")
        c.run("git add app.py", echo=False, notify=False)
        c.run('git commit -m "fix typo"', echo=False, notify=False)
        (d / "app.py").write_text("def login():\n    return True\ndef logout():\n    pass\n", encoding="utf-8")
        c.run("git add app.py", echo=False, notify=False)
        c.run('git commit -m "Add logout button"', echo=False, notify=False)
        self._write("gd_plan.txt", "")
        c.append("Messy history ready (3 commits). Let's clean it up with rebase -i.", "ok")
    def _define_steps(self):
        self.steps = [
            {"title": "The messy history",
             "body": """<p>Three commits, and 'fix typo' belongs inside 'Add login form':</p>
                        <pre>* Add logout button
* fix typo          ← fold into 'Add login form'
* Add login form</pre>
                        <p>Run <code>git log --oneline</code> to see it.</p>""",
             "hint": "Run `git log --oneline`.",
             "check": self._chk_log},
            {"title": "Meet the rebase todo",
             "body": """<p><code>git rebase -i</code> opens a <b>todo list</b>. You edit the verb:</p>
                        <pre>pick 1aaa111 Add login form
pick 2bbb222 fix typo
pick 3ccc333 Add logout button</pre>
                        <ul><li><code>pick</code> — keep</li><li><code>fixup</code> — fold in, discard message</li>
                        <li><code>squash</code> — fold in, keep message</li><li><code>reword</code> — change message</li>
                        <li><code>edit</code> — pause to amend</li><li><code>drop</code> — delete</li></ul>
                        <p>We've scripted the todo editor, so <code>rebase -i</code> runs non-interactively here.</p>""",
             "hint": "Read it, then click ✓ Check step.",
             "check": self._chk_editor_ready},
            {"title": "Squash 'fix typo'",
             "body": """<p>The todo is pre-set to <b>fixup</b> the typo commit:</p>
                        <pre>pick   … Add login form
fixup  … fix typo
pick   … Add logout button</pre>
                        <p>Run:</p><pre>git rebase -i HEAD~3</pre>""",
             "hint": "Type `git rebase -i HEAD~3` and press Enter.",
             "enter": self._enter_squash,
             "check": self._chk_squashed},
            {"title": "Reword the last commit",
             "body": """<p>Rename the last commit to <i>'Add logout button with icon'</i>. The todo is
                        pre-set to <b>reword</b>:</p><pre>reword … Add logout button</pre>
                        <p>Run:</p><pre>git rebase -i HEAD~1</pre>""",
             "hint": "Type `git rebase -i HEAD~1` and press Enter.",
             "enter": self._enter_reword,
             "check": self._chk_reworded},
            {"title": "Done!",
             "body": """<p>🎉 Spotless history! Run <code>git log --oneline</code>, then
                        <b>Start / Reset</b> to go again.</p>""",
             "hint": "", "check": None},
        ]
    def _enter_squash(self):
        self._write("gd_plan.txt", "pick\nfixup\npick\n")
    def _enter_reword(self):
        self._write("gd_plan.txt", "reword\n")
        self._write("gd_msg.txt", "Add logout button with icon\n")
    def _chk_log(self, c):
        log = c.run("git log --oneline", echo=False, notify=False)
        if log and log.returncode == 0 and len(log.stdout.strip().splitlines()) == 3:
            return True, "Three commits — let's tidy them."
        return False, "Run `git log --oneline` (you should see 3 commits)."
    def _chk_editor_ready(self, c):
        if (c.dir / "gd_todo_editor.py").exists() and c.extra_env.get("GIT_SEQUENCE_EDITOR"):
            return True, "Todo editor is armed."
        return False, "Editor not ready — click Start / Reset."
    def _chk_squashed(self, c):
        log = c.run("git log --oneline", echo=False, notify=False)
        if log and log.returncode == 0:
            lines = log.stdout.strip().splitlines()
            if len(lines) == 2 and not any("fix typo" in l for l in lines):
                return True, "Squashed — 'fix typo' is folded into 'Add login form'."
        return False, "Run `git rebase -i HEAD~3`. If it failed, click Start / Reset and retry."
    def _chk_reworded(self, c):
        if _last_subject(c) == "Add logout button with icon":
            return True, "Reworded — the message is updated."
        return False, "Run `git rebase -i HEAD~1`. If it failed, click Start / Reset and retry."
    def on_complete(self):
        self.store.data["rebase_lab_done"] = True
        self.store.save()

class ReflogLabPage(WalkthroughPage):
    page_title = "⏳ Reflog Lab — detached HEAD & time travel"
    page_intro = "Detach HEAD, strand a commit, then rescue it with git reflog."
    def setup(self):
        c = self.console
        c.reset_dir(); c.ensure_dir()
        c.run("git init", echo=False, notify=False)
        c.run("git symbolic-ref HEAD refs/heads/main", echo=False, notify=False)
        c.run('git config user.name "Time Traveler"', echo=False, notify=False)
        c.run('git config user.email "tt@gitdojo.local"', echo=False, notify=False)
        for i, msg in enumerate(["First commit", "Second commit", "Third commit"]):
            (c.dir / "notes.txt").write_text(f"line {i}\n", encoding="utf-8")
            c.run("git add notes.txt", echo=False, notify=False)
            c.run(f'git commit -m "{msg}"', echo=False, notify=False)
        c.append("Ready: 3 commits on main. Time to travel.", "ok")
    def _define_steps(self):
        self.steps = [
            {"title": "Home base",
             "body": """<p>You're on <code>main</code> with three commits. Run
                        <code>git log --oneline</code> to confirm.</p>""",
             "hint": "Run `git log --oneline`.",
             "check": self._chk_three},
            {"title": "Time travel (detach HEAD)",
             "body": """<p>Check out an older commit directly:</p><pre>git checkout HEAD~1</pre>
                        <p>HEAD now points at a <b>commit</b>, not a branch — <b>detached HEAD</b>.</p>""",
             "hint": "`git checkout HEAD~1`.",
             "check": self._chk_detached2},
            {"title": "Leave a trace",
             "body": """<p>While detached, make a commit:</p>
                        <pre>git commit --allow-empty -m "lost treasure"</pre>""",
             "hint": "`git commit --allow-empty -m \"lost treasure\"`.",
             "check": self._chk_trace},
            {"title": "Back to the present",
             "body": """<p>Return to your branch:</p><pre>git switch main</pre>
                        <p>The 'lost treasure' commit is now <b>orphaned</b>.</p>""",
             "hint": "`git switch main`.",
             "check": self._chk_back},
            {"title": "Rescue it with reflog",
             "body": """<p>Run:</p><pre>git reflog</pre>
                        <p>Find the 'lost treasure' SHA, then:</p><pre>git branch rescue &lt;sha&gt;</pre>""",
             "hint": "Find the SHA in `git reflog`, then `git branch rescue <sha>`.",
             "check": self._chk_rescued},
            {"title": "Done!",
             "body": """<p>🎉 You time-traveled and rescued a 'lost' commit.
                        <code>git log rescue --oneline</code> shows it.</p>""",
             "hint": "", "check": None},
        ]
    def _chk_three(self, c):
        log = c.run("git log --oneline", echo=False, notify=False)
        if log and log.returncode == 0 and len(log.stdout.strip().splitlines()) == 3:
            return True, "Three commits on main."
        return False, "Run `git log --oneline` (you should see 3 commits)."
    def _chk_detached2(self, c):
        if _cbranch(c) == "HEAD":
            return True, "Detached HEAD — you're visiting a commit directly."
        return False, "Detach with `git checkout HEAD~1`."
    def _chk_trace(self, c):
        if _cbranch(c) == "HEAD" and _last_subject(c) == "lost treasure":
            return True, "You committed while detached."
        return False, "While detached: `git commit --allow-empty -m \"lost treasure\"`."
    def _chk_back(self, c):
        if _cbranch(c) == "main":
            return True, "Back on main — the detached commit is orphaned."
        return False, "Return with `git switch main`."
    def _chk_rescued(self, c):
        r = c.run("git log rescue -1 --pretty=%s", echo=False, notify=False)
        if r and r.returncode == 0 and "lost treasure" in r.stdout:
            return True, "Rescued — branch 'rescue' points to the lost commit."
        return False, "Use `git reflog` to find the SHA, then `git branch rescue <sha>`."
    def on_complete(self):
        self.store.data["reflog_lab_done"] = True
        self.store.save()

class PickRevertLabPage(WalkthroughPage):
    page_title = "🍒 Cherry-pick & Revert Lab"
    page_intro = "Copy a fix from another branch with cherry-pick, then safely undo a mistake with revert."
    def setup(self):
        c = self.console
        c.reset_dir(); c.ensure_dir()
        c.run("git init", echo=False, notify=False)
        c.run("git symbolic-ref HEAD refs/heads/main", echo=False, notify=False)
        c.run('git config user.name "Pick Lab"', echo=False, notify=False)
        c.run('git config user.email "pick@gitdojo.local"', echo=False, notify=False)
        (c.dir / "app.py").write_text("print('app')\n", encoding="utf-8")
        c.run("git add app.py", echo=False, notify=False)
        c.run('git commit -m "Base release"', echo=False, notify=False)
        c.run("git switch -c hotfix", echo=False, notify=False)
        (c.dir / "login.py").write_text("def login():\n    return safe_login()\n", encoding="utf-8")
        c.run("git add login.py", echo=False, notify=False)
        c.run('git commit -m "Fix crash on login"', echo=False, notify=False)
        c.run("git switch main", echo=False, notify=False)
        (c.dir / "app.py").write_text("print('app')\nprint('settings')\n", encoding="utf-8")
        c.run("git add app.py", echo=False, notify=False)
        c.run('git commit -m "Add settings page"', echo=False, notify=False)
        c.append("Scenario ready: the login fix only exists on the hotfix branch.", "ok")
    def _define_steps(self):
        self.steps = [
            {"title": "The situation",
             "body": """<p><code>main</code> moved on, but <i>'Fix crash on login'</i> only exists on
                        <code>hotfix</code>. Run <code>git log --oneline --all</code> to see both.</p>""",
             "hint": "Run `git log --oneline --all`.",
             "check": self._chk_see},
            {"title": "Cherry-pick the fix",
             "body": """<p>Copy that commit onto <code>main</code>:</p><pre>git cherry-pick hotfix</pre>""",
             "hint": "On main, run `git cherry-pick hotfix`.",
             "check": self._chk_picked2},
            {"title": "Make a mistake",
             "body": """<p>Create a broken commit:</p>
                        <pre>git commit --allow-empty -m "Add broken banner"</pre>""",
             "hint": "`git commit --allow-empty -m \"Add broken banner\"`.",
             "check": self._chk_bad},
            {"title": "Revert it",
             "body": """<p>Undo it safely:</p><pre>git revert --no-edit HEAD</pre>""",
             "hint": "`git revert --no-edit HEAD`.",
             "check": self._chk_reverted2},
            {"title": "Done!",
             "body": """<p>🎉 You cherry-picked a fix and reverted a mistake. Run
                        <code>git log --oneline</code>, then <b>Start / Reset</b> to repeat.</p>""",
             "hint": "", "check": None},
        ]
    def _chk_see(self, c):
        b = c.run("git branch", echo=False, notify=False)
        if b and b.returncode == 0 and "hotfix" in b.stdout and _cbranch(c) == "main":
            return True, "You can see main and hotfix."
        return False, "Run `git log --oneline --all` (make sure you're on main)."
    def _chk_picked2(self, c):
        log = c.run("git log --oneline", echo=False, notify=False)
        if log and log.returncode == 0 and "Fix crash on login" in log.stdout and _cbranch(c) == "main":
            return True, "Cherry-picked — the fix is now on main."
        return False, "On main, run `git cherry-pick hotfix`."
    def _chk_bad(self, c):
        if _last_subject(c) == "Add broken banner":
            return True, "Uh oh — that commit looks wrong."
        return False, "Create it: `git commit --allow-empty -m \"Add broken banner\"`."
    def _chk_reverted2(self, c):
        if _last_subject(c).startswith("Revert"):
            return True, "Reverted — undone by a new commit, history intact."
        return False, "Run `git revert --no-edit HEAD`."
    def on_complete(self):
        self.store.data["pickrevert_lab_done"] = True
        self.store.save()

class BisectLabPage(WalkthroughPage):
    page_title = "🔍 Bisect Lab — hunt the bug"
    page_intro = "Use git bisect to find exactly which commit introduced a bug."
    SUBJECTS = ["Initial commit", "Add input parsing", "Add validation", "Add tests", "Add docs",
                "Introduce cache bug", "Tweak cache size", "Update README"]
    def setup(self):
        c = self.console
        c.reset_dir(); c.ensure_dir()
        c.run("git init", echo=False, notify=False)
        c.run("git symbolic-ref HEAD refs/heads/main", echo=False, notify=False)
        c.run('git config user.name "Bug Hunter"', echo=False, notify=False)
        c.run('git config user.email "hunt@gitdojo.local"', echo=False, notify=False)
        for i, subj in enumerate(self.SUBJECTS):
            answer = 42 if i < 5 else 0
            (c.dir / "app.py").write_text(f"ANSWER = {answer}\n", encoding="utf-8")
            c.run("git add app.py", echo=False, notify=False)
            c.run(f'git commit -m "{subj}"', echo=False, notify=False)
        root = c.run("git rev-list --max-parents=0 HEAD", echo=False, notify=False).stdout.strip()
        c.run(f"git tag good-start {root}", echo=False, notify=False)
        c.append("8 commits. A bug hides in one. Test: ANSWER=42 good, ANSWER=0 bad.", "ok")
    def _define_steps(self):
        self.steps = [
            {"title": "The bug report",
             "body": """<p>Something broke. There are 8 commits.</p>
                        <p><b>The test:</b> run <code>git show HEAD:app.py</code>.
                        <code>ANSWER = 42</code> = <b>good</b>; <code>ANSWER = 0</code> = <b>bad</b>.</p>
                        <p>The first commit is known-good (tagged <code>good-start</code>); HEAD is bad.</p>""",
             "hint": "Run `git log --oneline` to see the 8 commits.",
             "check": self._chk_setup},
            {"title": "Start the hunt",
             "body": """<p>Tell Git the bounds:</p>
                        <pre>git bisect start
git bisect bad
git bisect good good-start</pre>""",
             "hint": "Run the three commands above.",
             "check": self._chk_started},
            {"title": "Test & narrow down",
             "body": """<p>Repeat until Git names the culprit:</p>
                        <ol><li><code>git show HEAD:app.py</code></li>
                        <li><code>ANSWER = 0</code> → <code>git bisect bad</code></li>
                        <li><code>ANSWER = 42</code> → <code>git bisect good</code></li></ol>
                        <p>When Git prints <i>'… is the first bad commit'</i>, check this step.</p>""",
             "hint": "Keep running `git bisect good`/`bad` based on app.py.",
             "check": self._chk_found},
            {"title": "Wrap up",
             "body": """<p>Leave bisect mode:</p><pre>git bisect reset</pre>""",
             "hint": "`git bisect reset`.",
             "check": self._chk_reset},
            {"title": "Done!",
             "body": """<p>🎉 You found <i>'Introduce cache bug'</i> in ~3 steps.
                        <b>Start / Reset</b> to hunt again.</p>""",
             "hint": "", "check": None},
        ]
    def _chk_setup(self, c):
        log = c.run("git log --oneline", echo=False, notify=False)
        if log and log.returncode == 0 and len(log.stdout.strip().splitlines()) == 8:
            return True, "Eight commits — the hunt can begin."
        return False, "Run `git log --oneline` (you should see 8 commits)."
    def _chk_started(self, c):
        r = c.run("git rev-parse --is-bisecting", echo=False, notify=False)
        if r and "true" in (r.stdout or ""):
            return True, "Bisect is running — Git checked out a midpoint."
        return False, "Run `git bisect start`, `git bisect bad`, `git bisect good good-start`."
    def _chk_found(self, c):
        if _last_subject(c) == "Introduce cache bug":
            r = c.run("git rev-parse --is-bisecting", echo=False, notify=False)
            if r and "true" in (r.stdout or ""):
                return True, "Found it — 'Introduce cache bug' is the culprit."
        return False, "Keep testing app.py and running `git bisect good`/`bad`."
    def _chk_reset(self, c):
        r = c.run("git rev-parse --is-bisecting", echo=False, notify=False)
        if r is None or "true" not in (r.stdout or ""):
            return True, "Bisect complete and reset."
        return False, "Finish with `git bisect reset`."
    def on_complete(self):
        self.store.data["bisect_lab_done"] = True
        self.store.save()

class StashLabPage(WalkthroughPage):
    page_title = "🧳 Stash Lab — shelve & restore"
    page_intro = "Set half-finished work aside with git stash, switch context, then bring it back."
    def setup(self):
        c = self.console
        c.reset_dir(); c.ensure_dir()
        c.run("git init", echo=False, notify=False)
        c.run("git symbolic-ref HEAD refs/heads/main", echo=False, notify=False)
        c.run('git config user.name "Stash Lab"', echo=False, notify=False)
        c.run('git config user.email "stash@gitdojo.local"', echo=False, notify=False)
        (c.dir / "app.py").write_text("def work():\n    return 1\n", encoding="utf-8")
        c.run("git add app.py", echo=False, notify=False)
        c.run('git commit -m "Base"', echo=False, notify=False)
        (c.dir / "app.py").write_text("def work():\n    return 1\n# TODO: half-finished idea\n", encoding="utf-8")
        (c.dir / "scratch.txt").write_text("random notes\n", encoding="utf-8")
        c.append("You have half-finished work: a modified app.py and an untracked scratch.txt.", "ok")
    def _define_steps(self):
        self.steps = [
            {"title": "Your messy desk",
             "body": """<p>You modified <code>app.py</code> and created <code>scratch.txt</code>, but nothing
                        is committed. Run <code>git status</code> to see the mess.</p>""",
             "hint": "Run `git status`.",
             "check": self._chk_dirty},
            {"title": "Stash everything",
             "body": """<p>Shelve it all — including the untracked file:</p>
                        <pre>git stash push -u -m "wip"</pre>""",
             "hint": "`git stash push -u -m \"wip\"`.",
             "check": self._chk_stashed},
            {"title": "Switch context",
             "body": """<p>With a clean tree you can switch freely:</p><pre>git switch -c hotfix</pre>""",
             "hint": "`git switch -c hotfix`.",
             "check": self._chk_on_hotfix},
            {"title": "Come back & restore",
             "body": """<p>Return and bring the work back:</p>
                        <pre>git switch main
git stash pop</pre>
                        <p><code>pop</code> applies and removes. (<code>apply</code> keeps a copy,
                        <code>drop</code> deletes.)</p>""",
             "hint": "`git switch main` then `git stash pop`.",
             "check": self._chk_popped},
            {"title": "Done!",
             "body": """<p>🎉 You shelved work, switched context, and restored it.
                        <b>Start / Reset</b> to run it again.</p>""",
             "hint": "", "check": None},
        ]
    def _chk_dirty(self, c):
        st = c.run("git status --porcelain", echo=False, notify=False)
        if st and st.stdout.strip():
            return True, "Yep — uncommitted changes everywhere."
        return False, "Run `git status` — you should see modified app.py and untracked scratch.txt."
    def _chk_stashed(self, c):
        st = c.run("git status --porcelain", echo=False, notify=False)
        sl = c.run("git stash list", echo=False, notify=False)
        clean = (st is not None and not st.stdout.strip())
        has_stash = (sl is not None and sl.stdout.strip())
        if clean and has_stash:
            return True, "Stashed — working tree clean, work shelved."
        return False, "Run `git stash push -u -m \"wip\"`."
    def _chk_on_hotfix(self, c):
        if _cbranch(c) == "hotfix":
            return True, "On hotfix, and your WIP is safely stashed."
        return False, "Switch with `git switch -c hotfix`."
    def _chk_popped(self, c):
        sl = c.run("git stash list", echo=False, notify=False)
        stash_empty = (sl is not None and not sl.stdout.strip())
        scratch_back = (c.dir / "scratch.txt").exists()
        if stash_empty and scratch_back and _cbranch(c) == "main":
            return True, "Popped — your work is back and the stash is empty."
        return False, "Run `git switch main` then `git stash pop`."
    def on_complete(self):
        self.store.data["stash_lab_done"] = True
        self.store.save()

# ──────────────────────────────────────────────────────────────── PAGES
class HomePage(QWidget):
    def __init__(self, store, goto, continue_cb=None):
        super().__init__()
        self.store, self.goto, self.continue_cb = store, goto, continue_cb
        lay = QVBoxLayout(self); lay.setContentsMargins(26, 22, 26, 22); lay.setSpacing(14)
        h = QLabel("🥋 GitDojo"); h.setObjectName("h1")
        s = QLabel("Master Git with lessons, quizzes, flashcards, labs and a live sandbox — fully offline.")
        s.setObjectName("sub")
        lay.addWidget(h); lay.addWidget(s)
        wf = QFrame(); wf.setProperty("card", True)
        wv = QVBoxLayout(wf); wv.setContentsMargins(16, 12, 16, 16)
        t = QLabel("The Git workflow at a glance"); t.setObjectName("h2")
        wv.addWidget(t); wv.addWidget(WorkflowDiagram())
        lay.addWidget(wf)
        row = QHBoxLayout(); row.setSpacing(12)
        f1, self.lessons_val, self.lessons_bar = self._stat("📖 Lessons completed")
        f2, self.quiz_val, qb = self._stat("🧠 Best quiz score"); qb.hide()
        f3, self.cards_val, self.cards_bar = self._stat("🃏 Flashcards mastered")
        row.addWidget(f1); row.addWidget(f2); row.addWidget(f3)
        lay.addLayout(row)
        bl = QHBoxLayout()
        bl.addWidget(make_button("▶  Continue learning", self._continue, accent=True))
        bl.addWidget(make_button("📖  Browse lessons", lambda: self.goto(1)))
        bl.addWidget(make_button("🧠  Take the quiz", lambda: self.goto(2)))
        bl.addWidget(make_button("🃏  Flashcards", lambda: self.goto(3)))
        bl.addWidget(make_button("🧪  Open sandbox", lambda: self.goto(5)))
        bl.addWidget(make_button("📊  Dashboard", lambda: self.goto(6)))
        bl.addWidget(make_button("⏪  Undo Anything", lambda: self.goto(13)))
        bl.addStretch()
        lay.addLayout(bl); lay.addStretch()
        self.refresh()
    @staticmethod
    def _stat(title):
        f = QFrame(); f.setProperty("card", True)
        v = QVBoxLayout(f); v.setContentsMargins(16, 12, 16, 14); v.setSpacing(6)
        tl = QLabel(title); tl.setObjectName("sub")
        val = QLabel(""); val.setStyleSheet("font-size:22px; font-weight:700;")
        bar = QProgressBar(); bar.setTextVisible(False); bar.setFixedHeight(8); bar.setRange(0, 1)
        v.addWidget(tl); v.addWidget(val); v.addWidget(bar)
        return f, val, bar
    def _first_incomplete(self):
        done = set(self.store.data["completed_lessons"])
        for i, les in enumerate(LESSONS):
            if les["id"] not in done:
                return i
        return None
    def _continue(self):
        if self.continue_cb:
            idx = self._first_incomplete()
            self.continue_cb(0 if idx is None else idx)
    def refresh(self):
        done = len(self.store.data["completed_lessons"])
        self.lessons_val.setText(f"{done} / {len(LESSONS)}")
        self.lessons_bar.setRange(0, len(LESSONS)); self.lessons_bar.setValue(done)
        best = self.store.data.get("quiz_best", 0)
        self.quiz_val.setText(f"{best}%" if best else "—")
        mast = sum(1 for v in self.store.data.get("card_boxes", {}).values() if v >= 4)
        self.cards_val.setText(f"{mast} / 16")
        self.cards_bar.setRange(0, 16); self.cards_bar.setValue(mast)

class LessonsPage(QWidget):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.current = 0
        h = QHBoxLayout(self); h.setContentsMargins(20, 20, 20, 20)
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setFixedWidth(330)
        self.tree.currentItemChanged.connect(self._on_current)
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Search lessons…")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._filter_tree)
        self.only_bm = QCheckBox("⭐ Bookmarks only")
        self.only_bm.toggled.connect(self._filter_tree)
        leftw = QWidget()
        lv = QVBoxLayout(leftw); lv.setContentsMargins(0, 0, 0, 0); lv.setSpacing(6)
        lv.addWidget(self.search); lv.addWidget(self.only_bm); lv.addWidget(self.tree, 1)
        right = QVBoxLayout()
        self.pos_lbl = QLabel(); self.pos_lbl.setObjectName("sub")
        self.title = QLabel(); self.title.setObjectName("h2")
        self.tabs = QTabWidget()
        btns = QHBoxLayout()
        self.prev_btn = make_button("← Previous", lambda: self.step(-1))
        self.next_btn = make_button("Next →", lambda: self.step(1))
        self.bookmark_btn = make_button("☆ Bookmark", self.toggle_bookmark)
        self.mark_btn = make_button("Mark as completed ✓", self.toggle_complete, accent=True)
        btns.addWidget(self.prev_btn); btns.addWidget(self.next_btn)
        btns.addStretch(); btns.addWidget(self.bookmark_btn); btns.addWidget(self.mark_btn)
        right.addWidget(self.pos_lbl); right.addWidget(self.title)
        right.addWidget(self.tabs, 1); right.addLayout(btns)
        h.addWidget(leftw); h.addLayout(right, 1)
        self._fill_list()
    def _badge(self, les):
        lid = les["id"]
        marks = []
        if lid in self.store.data["completed_lessons"]:
            marks.append("✅")
        if lid in self.store.data.get("practice_done", []):
            marks.append("🧪")
        if self.store.data.get("lesson_quiz_best", {}).get(lid, 0) >= 75:
            marks.append("🧠")
        if lid in self.store.data.get("bookmarks", []):
            marks.append("⭐")
        prefix = (" ".join(marks) + "  ") if marks else ""
        return prefix + les["title"]
    def _fill_list(self):
        row = self.tree.currentItem()
        self.tree.blockSignals(True)
        self.tree.clear()
        cats = {}
        for i, les in enumerate(LESSONS):
            cats.setdefault(les.get("cat", "General"), []).append((i, les))
        ordered = [c for c in CAT_ORDER if c in cats] + [c for c in cats if c not in CAT_ORDER]
        bold = QFont(); bold.setBold(True)
        for cat in ordered:
            top = QTreeWidgetItem([cat])
            top.setFont(0, bold)
            top.setFlags(top.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.tree.addTopLevelItem(top)
            for idx, les in cats[cat]:
                child = QTreeWidgetItem([self._badge(les)])
                child.setData(0, Qt.ItemDataRole.UserRole, idx)
                top.addChild(child)
            top.setExpanded(True)
        self.tree.blockSignals(False)
        self.show_lesson(0)
    def _update_list_texts(self):
        self.tree.blockSignals(True)
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            for j in range(top.childCount()):
                ch = top.child(j)
                idx = ch.data(0, Qt.ItemDataRole.UserRole)
                if idx is not None:
                    ch.setText(0, self._badge(LESSONS[idx]))
        self.tree.blockSignals(False)
    def _filter_tree(self, *_):
        t = self.search.text().strip().lower()
        only_bm = self.only_bm.isChecked()
        for i in range(self.tree.topLevelItemCount()):
            cat = self.tree.topLevelItem(i)
            visible = 0
            for j in range(cat.childCount()):
                child = cat.child(j)
                idx = child.data(0, Qt.ItemDataRole.UserRole)
                if idx is None:
                    continue
                les = LESSONS[idx]
                hay = (les["title"] + " " + les.get("cat", "") + " " +
                       " ".join(cmd for cmd, _ in les.get("commands", []))).lower()
                match_text = (not t) or t in hay
                match_bm = (not only_bm) or les["id"] in self.store.data.get("bookmarks", [])
                match = match_text and match_bm
                child.setHidden(not match)
                if match:
                    visible += 1
            cat.setHidden(visible == 0 and (bool(t) or only_bm))
            if t or only_bm:
                cat.setExpanded(True)
    def _on_current(self, item, prev):
        if item is None:
            return
        idx = item.data(0, Qt.ItemDataRole.UserRole)
        if idx is None:
            return
        self.current = idx
        self.show_lesson(idx)
    def _select_index(self, idx):
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            for j in range(top.childCount()):
                ch = top.child(j)
                if ch.data(0, Qt.ItemDataRole.UserRole) == idx:
                    self.tree.setCurrentItem(ch)
                    return
    def step(self, delta):
        r = min(len(LESSONS) - 1, max(0, self.current + delta))
        self._select_index(r)
    def toggle_complete(self):
        lid = LESSONS[self.current]["id"]
        done = self.store.data["completed_lessons"]
        if lid in done:
            done.remove(lid)
        else:
            done.append(lid)
        self.store.save()
        self._update_list_texts()
        completed = lid in done
        self.mark_btn.setText("✅ Completed — click to unmark" if completed else "Mark as completed ✓")
    def toggle_bookmark(self):
        lid = LESSONS[self.current]["id"]
        bm = self.store.data.setdefault("bookmarks", [])
        if lid in bm:
            bm.remove(lid)
        else:
            bm.append(lid)
        self.store.save()
        self._update_bookmark_btn()
        self._update_list_texts()
    def _update_bookmark_btn(self):
        lid = LESSONS[self.current]["id"]
        is_bm = lid in self.store.data.get("bookmarks", [])
        self.bookmark_btn.setText("★ Bookmarked" if is_bm else "☆ Bookmark")
    def _make_notes_tab(self, les):
        w = QWidget()
        v = QVBoxLayout(w); v.setContentsMargins(12, 12, 12, 12); v.setSpacing(8)
        edit = QTextEdit()
        edit.setPlaceholderText("Write your notes for this lesson…")
        lid = les["id"]
        edit.blockSignals(True)
        edit.setPlainText(self.store.data.get("lesson_notes", {}).get(lid, ""))
        edit.blockSignals(False)
        def save():
            self.store.data.setdefault("lesson_notes", {})[lid] = edit.toPlainText()
            self.store.save()
        edit.textChanged.connect(save)
        hint = QLabel("📝 Notes save automatically and are stored with your progress.")
        hint.setObjectName("sub")
        v.addWidget(edit, 1); v.addWidget(hint)
        return w
    def _build_tabs(self, les):
        while self.tabs.count():
            w = self.tabs.widget(0)
            self.tabs.removeTab(0)
            if hasattr(w, "cleanup"):
                w.cleanup()
            w.deleteLater()
        view = QTextBrowser()
        view.setOpenExternalLinks(True)
        view.document().setDefaultStyleSheet(LESSON_CSS)
        view.setHtml(les["body"])
        self.tabs.addTab(view, "📖 Overview")
        self.tabs.addTab(build_command_tree(les.get("commands", [])), "⌨️ Options")
        self.tabs.addTab(PracticeWidget(les.get("practice"),
                                        on_success=self._make_practice_success(les["id"])),
                         "🧪 Practice")
        self.tabs.addTab(MiniQuizWidget(les.get("quiz", []),
                                        on_finish=self._make_quiz_finish(les["id"]),
                                        autostart=True),
                         "🧠 Quiz")
        self.tabs.addTab(self._make_notes_tab(les), "📝 Notes")
    def _make_practice_success(self, lid):
        def cb():
            if lid not in self.store.data["practice_done"]:
                self.store.data["practice_done"].append(lid)
                self.store.save()
            self._update_list_texts()
        return cb
    def _make_quiz_finish(self, lid):
        def on_finish(score, total, pct):
            prev = self.store.data["lesson_quiz_best"].get(lid, 0)
            if pct > prev:
                self.store.data["lesson_quiz_best"][lid] = pct
                self.store.save()
            self._update_list_texts()
        return on_finish
    def show_lesson(self, i):
        if i < 0 or i >= len(LESSONS):
            return
        self.current = i
        les = LESSONS[i]
        self.pos_lbl.setText(les.get("cat", ""))
        self.title.setText(les["title"])
        self.prev_btn.setEnabled(i > 0)
        self.next_btn.setEnabled(i < len(LESSONS) - 1)
        completed = les["id"] in self.store.data["completed_lessons"]
        self.mark_btn.setText("✅ Completed — click to unmark" if completed else "Mark as completed ✓")
        self._update_bookmark_btn()
        self._build_tabs(les)
    def refresh(self):
        self._update_list_texts()

class QuizPage(QWidget):
    def __init__(self, store):
        super().__init__()
        self.store = store
        v = QVBoxLayout(self); v.setContentsMargins(26, 22, 26, 22)
        t = QLabel("🧠 Git Quiz"); t.setObjectName("h2")
        global_quiz = [
            {"q": "Which command creates a new repository?",
             "options": ["git init", "git new", "git create", "git start"], "answer": 0,
             "why": "git init creates the .git directory."},
            {"q": "What does git add do?",
             "options": ["Uploads files", "Copies changes into the staging area", "Saves a snapshot", "Backs up"], "answer": 1,
             "why": "add stages changes."},
            {"q": "Which records staged changes as a snapshot?",
             "options": ["git save", "git push", "git commit", "git snap"], "answer": 2,
             "why": "commit stores staged changes."},
            {"q": "See what changed / staged / which branch…",
             "options": ["git history", "git status", "git inspect", "git state"], "answer": 1,
             "why": "status summarizes state."},
            {"q": "Create branch dev AND switch to it…",
             "options": ["git branch dev", "git switch -c dev", "git new dev", "git dev --switch"], "answer": 1,
             "why": "-c creates + switches."},
            {"q": "List all local branches…",
             "options": ["git branches", "git branch", "git list", "git show --branches"], "answer": 1,
             "why": "git branch lists them."},
            {"q": "On main, integrate branch feature…",
             "options": ["git merge feature", "git merge main", "git attach feature", "git push feature"], "answer": 0,
             "why": "Merge into the current branch."},
            {"q": "When does a conflict happen?",
             "options": ["Two people edit a file", "Both sides changed the same lines", "Repo is big", "Forgot to commit"], "answer": 1,
             "why": "Overlapping edits."},
            {"q": "Copy a remote repository locally…",
             "options": ["git copy", "git clone", "git download", "git fork"], "answer": 1,
             "why": "clone downloads full history."},
            {"q": "git pull is…",
             "options": ["Upload commits", "Download only", "Download + integrate", "Delete a branch"], "answer": 2,
             "why": "fetch + merge."},
            {"q": "HEAD is…",
             "options": ["First commit", "The remote", "Pointer to current position", "The staging area"], "answer": 2,
             "why": "Current checkout."},
            {"q": "Undo last commit, keep changes staged…",
             "options": ["git reset --hard HEAD~1", "git reset --soft HEAD~1", "git undo", "git rm --commit"], "answer": 1,
             "why": "--soft keeps the index."},
            {"q": "Safely undo a pushed commit…",
             "options": ["git revert <commit>", "git reset --hard <commit>", "Delete the repo", "git stash"], "answer": 0,
             "why": "revert adds an undo commit."},
            {"q": "Temporarily shelve uncommitted changes…",
             "options": ["git hold", "git stash", "git park", "git freeze"], "answer": 1,
             "why": "stash shelves work."},
            {"q": "Mark release version 1.0…",
             "options": ["git label v1.0", "git release v1.0", "git tag v1.0", "git mark v1.0"], "answer": 2,
             "why": "tag marks releases."},
            {"q": "Compact one-line-per-commit history…",
             "options": ["git log --oneline", "git history -s", "git show all", "git list"], "answer": 0,
             "why": "--oneline."},
        ]
        self.quiz = MiniQuizWidget(global_quiz, on_finish=self._finished)
        v.addWidget(t); v.addWidget(self.quiz, 1)
    def refresh(self):
        best = self.store.data.get("quiz_best", 0)
        self.quiz.set_best(f"🏆 Best score: {best}%" if best else "No attempts yet — good luck!")
        self.quiz.to_start()
    def _finished(self, score, total, pct):
        self.store.data["quiz_best"] = max(self.store.data.get("quiz_best", 0), pct)
        self.store.save()

class FlashcardsPage(QWidget):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.deck, self.idx, self.flipped, self.finished = [], 0, False, False
        outer = QHBoxLayout(self); outer.addStretch()
        inner = QWidget(); inner.setMaximumWidth(680)
        v = QVBoxLayout(inner); v.setContentsMargins(0, 24, 0, 24); v.setSpacing(10)
        head = QHBoxLayout()
        t = QLabel("🃏 Flashcards — recall the commands"); t.setObjectName("h2")
        self.count_lbl = QLabel(); self.count_lbl.setObjectName("sub")
        head.addWidget(t); head.addStretch(); head.addWidget(self.count_lbl)
        self.bar = QProgressBar(); self.bar.setTextVisible(False); self.bar.setFixedHeight(10)
        self.card = CardWidget(); self.card.clicked.connect(self.flip)
        self.hint = QLabel(""); self.hint.setObjectName("sub")
        self.hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        r1 = QHBoxLayout()
        self.flip_btn = make_button("Flip card 🔁", self.flip)
        r1.addStretch(); r1.addWidget(self.flip_btn); r1.addStretch()
        r2 = QHBoxLayout()
        self.again_btn = make_button("❌ Still learning", self.again)
        self.gotit_btn = make_button("✅ Got it!", self.got_it, prop="green")
        r2.addStretch(); r2.addWidget(self.again_btn); r2.addSpacing(10)
        r2.addWidget(self.gotit_btn); r2.addStretch()
        self.again_btn.hide(); self.gotit_btn.hide()
        self.done_lbl = QLabel(); self.done_lbl.setObjectName("h2")
        self.done_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter); self.done_lbl.hide()
        self.restart_btn = make_button("Shuffle & restart 🔀", self.restart, accent=True)
        rr = QHBoxLayout(); rr.addStretch(); rr.addWidget(self.restart_btn); rr.addStretch()
        self.restart_btn.hide()
        v.addLayout(head); v.addWidget(self.bar); v.addWidget(self.card)
        v.addWidget(self.hint); v.addLayout(r1); v.addLayout(r2)
        v.addWidget(self.done_lbl); v.addLayout(rr); v.addStretch()
        outer.addWidget(inner); outer.addStretch()
        self._new_deck()
    FLASHCARDS = [
        {"id": "f1",  "front": "Start tracking the current folder with Git", "back": "git init"},
        {"id": "f2",  "front": "Stage every changed file in the folder", "back": "git add ."},
        {"id": "f3",  "front": "Commit the staged changes with a message", "back": 'git commit -m "message"'},
        {"id": "f4",  "front": "Show the state of the working tree and staging area", "back": "git status"},
        {"id": "f5",  "front": "Show unstaged differences vs. the last commit", "back": "git diff"},
        {"id": "f6",  "front": "View the commit history", "back": "git log"},
        {"id": "f7",  "front": "Create a branch called 'dev'", "back": "git branch dev"},
        {"id": "f8",  "front": "Create 'dev' and switch to it in one step", "back": "git switch -c dev"},
        {"id": "f9",  "front": "Merge branch 'dev' into the branch I'm on", "back": "git merge dev"},
        {"id": "f10", "front": "Copy a repository from a URL", "back": "git clone <url>"},
        {"id": "f11", "front": "Upload my 'main' commits to the remote 'origin'", "back": "git push origin main"},
        {"id": "f12", "front": "Download remote changes and integrate them", "back": "git pull"},
        {"id": "f13", "front": "Temporarily shelve uncommitted changes", "back": "git stash push"},
        {"id": "f14", "front": "Undo the last commit but keep the changes staged", "back": "git reset --soft HEAD~1"},
        {"id": "f15", "front": "Undo an old commit without rewriting history", "back": "git revert <commit>"},
        {"id": "f16", "front": "See who last modified each line of a file", "back": "git blame <file>"},
    ]
    def _box(self, cid):
        return self.store.data.get("card_boxes", {}).get(cid, 1)
    def _set_box(self, cid, box):
        self.store.data.setdefault("card_boxes", {})[cid] = max(1, min(5, box))
        self.store.save()
    def _mastered_count(self):
        return sum(1 for v in self.store.data.get("card_boxes", {}).values() if v >= 4)
    def refresh(self):
        if not self.deck:
            self._new_deck()
    def _new_deck(self):
        self.deck = self.FLASHCARDS.copy()
        random.shuffle(self.deck)
        self.deck.sort(key=lambda c: self._box(c["id"]))
        self.idx, self.flipped, self.finished = 0, False, False
        self._show()
    def _show(self):
        card = self.deck[self.idx]
        self.flipped = False
        box = self._box(card["id"])
        self.card.kind.setText(f"BOX {box}/5   ·   SCENARIO — which command?")
        self.card.text.setText(card["front"])
        self.card.text.setStyleSheet("font-size:20px; padding:0 24px;")
        self.bar.setRange(0, len(self.deck)); self.bar.setValue(self.idx + 1)
        mast = self._mastered_count()
        self.count_lbl.setText(
            f"Card {self.idx + 1} / {len(self.deck)}    •    Mastered: {mast} / {len(self.FLASHCARDS)}")
        self.flip_btn.show(); self.again_btn.hide(); self.gotit_btn.hide()
        self.hint.setText("Click the card (or press Flip) to reveal the answer")
    def flip(self):
        if self.finished or self.flipped:
            return
        self.flipped = True
        card = self.deck[self.idx]
        box = self._box(card["id"])
        self.card.kind.setText(f"BOX {box}/5   ·   ANSWER")
        self.card.text.setText(card["back"])
        self.card.text.setStyleSheet(
            "font-family:Consolas,'Courier New',monospace; font-size:24px; color:#a5d6ff;")
        self.flip_btn.hide(); self.again_btn.show(); self.gotit_btn.show()
        self.hint.setText("How did you do?")
    def got_it(self):
        cid = self.deck[self.idx]["id"]
        self._set_box(cid, self._box(cid) + 1)
        if cid not in self.store.data["mastered_cards"]:
            self.store.data["mastered_cards"].append(cid)
        self.store.save()
        self._advance()
    def again(self):
        cid = self.deck[self.idx]["id"]
        self._set_box(cid, 1)
        self._advance()
    def _advance(self):
        if self.finished:
            return
        self.idx += 1
        if self.idx >= len(self.deck):
            self._session_done()
        else:
            self._show()
    def _session_done(self):
        self.finished = True
        self.card.hide(); self.hint.hide()
        self.flip_btn.hide(); self.again_btn.hide(); self.gotit_btn.hide()
        mast = self._mastered_count()
        self.done_lbl.setText(f"🎉 Deck complete!\nMastered overall: {mast} / {len(self.FLASHCARDS)}")
        self.done_lbl.show(); self.restart_btn.show()
    def restart(self):
        self.finished = False
        self.card.show(); self.hint.show()
        self.done_lbl.hide(); self.restart_btn.hide()
        self._new_deck()

class ReferencePage(QWidget):
    def __init__(self):
        super().__init__()
        v = QVBoxLayout(self); v.setContentsMargins(24, 22, 24, 22)
        t = QLabel("📚 Command reference"); t.setObjectName("h2")
        self.search = QLineEdit()
        self.search.setPlaceholderText("Filter commands…  (e.g. merge, stash, log)")
        self.tree = build_command_tree([])
        self.tree.clear()
        mono = mono_font(10); bold = QFont(); bold.setBold(True)
        REFERENCE = {
         "Setup & Config": [("git --version", "Check that git is installed"),
                            ('git config --global user.name "Your Name"', "Who you are"),
                            ('git config --global user.email "you@example.com"', "Contact on commits"),
                            ("git init", "Turn the current folder into a repository"),
                            ("git clone <url>", "Download a repository with full history")],
         "Snapshotting": [("git status", "What changed? What is staged? Which branch?"),
                          ("git add <file>", "Stage a single file"),
                          ("git add .", "Stage all changes"),
                          ('git commit -m "msg"', "Save staged changes as a commit"),
                          ("git commit --amend", "Fold changes into the last commit"),
                          ("git diff", "Unstaged changes vs last commit"),
                          ("git diff --staged", "Staged changes vs last commit")],
         "Branching & Merging": [("git branch", "List branches"),
                                 ("git branch <name>", "Create a branch"),
                                 ("git switch <name>", "Switch branches"),
                                 ("git switch -c <name>", "Create and switch"),
                                 ("git branch -d <name>", "Delete a merged branch"),
                                 ("git merge <name>", "Integrate <name> into current branch"),
                                 ("git merge --abort", "Cancel a conflicted merge safely")],
         "Remotes": [("git remote -v", "List configured remotes"),
                     ("git remote add origin <url>", "Register a remote named origin"),
                     ("git push -u origin <branch>", "Upload a branch and remember it"),
                     ("git push", "Push to the remembered upstream"),
                     ("git fetch", "Download remote changes without merging"),
                     ("git pull", "Fetch + integrate into current branch")],
         "Inspection": [("git log", "Commit history"),
                        ("git log --oneline --graph --all", "Compact visual history"),
                        ("git show <commit>", "Details of one commit"),
                        ("git blame <file>", "Who last touched each line"),
                        ("git reflog", "History of HEAD moves")],
         "Undoing": [("git restore <file>", "Discard working-tree changes (⚠)"),
                     ("git restore --staged <file>", "Unstage a file, keep the edits"),
                     ("git reset --soft HEAD~1", "Undo commit, keep changes staged"),
                     ("git reset HEAD~1", "Undo commit and unstage"),
                     ("git reset --hard HEAD~1", "Undo commit AND discard changes (⚠)"),
                     ("git revert <commit>", "Undo a commit with a new commit")],
         "Stash & Tags": [('git stash push -m "wip"', "Shelve uncommitted work"),
                          ("git stash list", "List stashes"),
                          ("git stash pop", "Apply + remove the latest stash"),
                          ("git clean -n / -f", "Preview / delete untracked files"),
                          ("git tag", "List tags"),
                          ('git tag -a v1.0 -m "Release"', "Create an annotated tag"),
                          ("git push --tags", "Upload tags")],
        }
        for cat, items in REFERENCE.items():
            top = QTreeWidgetItem([cat, f"{len(items)} commands"])
            top.setFont(0, bold)
            for cmd, desc in items:
                ch = QTreeWidgetItem([cmd, desc]); ch.setFont(0, mono)
                top.addChild(ch)
            self.tree.addTopLevelItem(top)
        self.tree.expandAll()
        self.search.textChanged.connect(self._filter)
        v.addWidget(t); v.addWidget(self.search); v.addWidget(self.tree, 1)
    def _filter(self, text):
        t = text.strip().lower()
        for i in range(self.tree.topLevelItemCount()):
            cat = self.tree.topLevelItem(i)
            visible = 0
            for j in range(cat.childCount()):
                ch = cat.child(j)
                match = (not t) or t in ch.text(0).lower() or t in ch.text(1).lower()
                ch.setHidden(not match)
                visible += match
            cat.setHidden(visible == 0 and bool(t))

class SandboxPage(QWidget):
    def __init__(self):
        super().__init__()
        self.file_n = self.commit_n = self.branch_n = 0
        v = QVBoxLayout(self); v.setContentsMargins(24, 20, 24, 20); v.setSpacing(10)
        head = QHBoxLayout()
        t = QLabel("🧪 Sandbox — a throw-away repository"); t.setObjectName("h2")
        self.reset_btn = make_button("🗑 New sandbox", self.reset)
        head.addWidget(t); head.addStretch(); head.addWidget(self.reset_btn)
        prow = QHBoxLayout()
        pl = QLabel("Repo:"); pl.setObjectName("sub")
        self.path_lbl = QLabel("no sandbox yet"); self.path_lbl.setObjectName("sub")
        self.path_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        prow.addWidget(pl); prow.addWidget(self.path_lbl, 1)
        self.console = GitConsole("Type any git command, e.g. git log --oneline  (Enter to run)")
        self.console.dirCreated.connect(lambda p: self.path_lbl.setText(p))
        q1 = QHBoxLayout(); q2 = QHBoxLayout()
        for label, slot in [("Init repo", self.act_init), ("＋ New file", self.act_file),
                            ("Stage all", lambda: self.console.run("git add .")),
                            ("Commit", self.act_commit),
                            ("Status", lambda: self.console.run("git status"))]:
            q1.addWidget(make_button(label, slot))
        q1.addStretch()
        for label, slot in [("Log graph", lambda: self.console.run("git log --oneline --graph --all --decorate")),
                            ("Branches", lambda: self.console.run("git branch -a")),
                            ("＋ Branch", self.act_branch), ("Back to main", self.act_main)]:
            q2.addWidget(make_button(label, slot))
        q2.addStretch()
        self.graph = CommitGraphWidget(self.console)
        glabel = QLabel("🌿 Commit graph"); glabel.setObjectName("h2")
        gscroll = QScrollArea(); gscroll.setWidgetResizable(True); gscroll.setWidget(self.graph)
        gscroll.setFixedHeight(200)
        self.console.commandFinished.connect(self.graph.refresh)
        v.addLayout(head); v.addLayout(prow)
        v.addWidget(self.console, 1)
        v.addLayout(q1); v.addLayout(q2)
        v.addWidget(glabel); v.addWidget(gscroll)
        self.console.append("Welcome to the Git sandbox 🧪", "info")
        self.console.append("1. Click 'Init repo'   2. Add files   3. Stage & commit   4. Explore!", "info")
        if not self.console.git_path:
            self.console.append("⚠ git was not found on PATH — the sandbox needs git installed.", "err")
    def act_init(self):
        self.console.ensure_dir()
        r = self.console.run("git init -b main")
        if r is None:
            return
        if r.returncode != 0:
            r = self.console.run("git init")
            if r is None or r.returncode != 0:
                return
        self.console.run('git config user.name "Sandbox User"', echo=False)
        self.console.run('git config user.email "sandbox@gitdojo.local"', echo=False)
        self.console.append("✔ Repo ready. Create a file, stage it, then commit!", "ok")
    def act_file(self):
        d = self.console.ensure_dir()
        self.file_n += 1
        name = f"notes_{self.file_n}.txt"
        (d / name).write_text(f"Hello from GitDojo! File #{self.file_n}\n", encoding="utf-8")
        self.console.append(f"Created {name} (untracked until you `git add` it)", "info")
    def act_commit(self):
        self.commit_n += 1
        self.console.run(f'git commit -m "Sandbox commit #{self.commit_n}"')
    def act_branch(self):
        self.branch_n += 1
        r = self.console.run(f"git switch -c feature-{self.branch_n}")
        if r and r.returncode != 0:
            self.console.run(f"git checkout -b feature-{self.branch_n}")
    def act_main(self):
        r = self.console.run("git switch main")
        if r and r.returncode != 0:
            self.console.run("git checkout main")
    def reset(self):
        self.console.reset_dir()
        self.file_n = self.commit_n = self.branch_n = 0
        d = self.console.ensure_dir()
        self.console.append(f"New sandbox created at {d}", "ok")
    def refresh(self):
        self.graph.refresh()
    def cleanup(self):
        self.console.cleanup()

class DashboardPage(QWidget):
    def __init__(self, store, goto, open_lesson):
        super().__init__()
        self.store, self.goto, self.open_lesson = store, goto, open_lesson
        self._cont_idx = None
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); scroll.setWidget(content); outer.addWidget(scroll)
        lay = QVBoxLayout(content); lay.setContentsMargins(26, 22, 26, 22); lay.setSpacing(14)
        head = QHBoxLayout()
        h = QLabel("📊 Mastery Dashboard"); h.setObjectName("h1")
        head.addWidget(h); head.addStretch()
        head.addWidget(make_button("🗑 Reset progress", self._reset_progress))
        lay.addLayout(head)
        sub = QLabel("Your progress across lessons, practice, quizzes, and flashcards.")
        sub.setObjectName("sub"); lay.addWidget(sub)
        srow = QHBoxLayout()
        srow.addWidget(QLabel("⚙ Settings:"))
        srow.addWidget(make_button("🌗 Theme", self._toggle_theme))
        srow.addWidget(make_button("A−", lambda: self._change_size(-1)))
        srow.addWidget(make_button("A+", lambda: self._change_size(1)))
        srow.addStretch()
        lay.addLayout(srow)
        self.stats_row = QHBoxLayout(); self.stats_row.setSpacing(12)
        lay.addLayout(self.stats_row)
        self.ach_title = QLabel("Achievements"); self.ach_title.setObjectName("h2")
        lay.addWidget(self.ach_title)
        self.ach_widget = QWidget()
        self.ach_layout = QGridLayout(self.ach_widget)
        self.ach_layout.setContentsMargins(0, 0, 0, 0); self.ach_layout.setSpacing(8)
        lay.addWidget(self.ach_widget)
        lay.addWidget(QLabel("Progress by category"))
        self.cat_widget = QWidget()
        self.cat_layout = QVBoxLayout(self.cat_widget)
        self.cat_layout.setContentsMargins(0, 0, 0, 0); self.cat_layout.setSpacing(8)
        lay.addWidget(self.cat_widget)
        self.cont_frame = QFrame(); self.cont_frame.setProperty("card", True)
        cv = QHBoxLayout(self.cont_frame); cv.setContentsMargins(16, 12, 16, 12)
        self.cont_lbl = QLabel(); self.cont_lbl.setObjectName("h2")
        self.cont_btn = make_button("Continue ▶", self._continue, accent=True)
        cv.addWidget(self.cont_lbl, 1); cv.addWidget(self.cont_btn)
        lay.addWidget(self.cont_frame)
        trow = QHBoxLayout()
        trow.addWidget(make_button("💾 Export progress", self._export_progress))
        trow.addWidget(make_button("📂 Import progress", self._import_progress))
        trow.addWidget(make_button("🖨 Cheat-sheet (HTML)", self._cheatsheet))
        trow.addStretch()
        lay.addLayout(trow)
        lay.addStretch()
        self.refresh()
    def _settings(self):
        return self.store.data.setdefault("settings", {"theme": "dark", "size": 14})
    def _mastered_cards(self):
        return sum(1 for v in self.store.data.get("card_boxes", {}).values() if v >= 4)
    def _stat_card(self, title, value, frac=None):
        f = QFrame(); f.setProperty("card", True)
        v = QVBoxLayout(f); v.setContentsMargins(16, 12, 16, 14); v.setSpacing(6)
        tl = QLabel(title); tl.setObjectName("sub")
        val = QLabel(value); val.setStyleSheet("font-size:22px; font-weight:700;")
        v.addWidget(tl); v.addWidget(val)
        if frac is not None:
            bar = QProgressBar(); bar.setTextVisible(False); bar.setFixedHeight(8)
            bar.setRange(0, max(1, frac[1])); bar.setValue(frac[0])
            v.addWidget(bar)
        return f
    def _clear(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear(item.layout())
                item.layout().deleteLater()
    def refresh(self):
        self._clear(self.stats_row); self._clear(self.ach_layout); self._clear(self.cat_layout)
        data = self.store.data
        total = len(LESSONS)
        done = len(data["completed_lessons"])
        prac = len(data.get("practice_done", []))
        qmast = sum(1 for v in data.get("lesson_quiz_best", {}).values() if v >= 75)
        cmast = self._mastered_cards()
        best = data.get("quiz_best", 0)
        self.stats_row.addWidget(self._stat_card("📖 Lessons done", f"{done} / {total}", (done, total)))
        self.stats_row.addWidget(self._stat_card("🧪 Practices passed", f"{prac} / {total}", (prac, total)))
        self.stats_row.addWidget(self._stat_card("🧠 Quizzes mastered", f"{qmast} / {total}", (qmast, total)))
        self.stats_row.addWidget(self._stat_card("🃏 Cards mastered", f"{cmast} / 16", (cmast, 16)))
        self.stats_row.addWidget(self._stat_card("🏆 Best global quiz", f"{best}%"))
        unlocked = 0; col = 0; row = 0
        for aid, icon, title, desc, cond in ACHIEVEMENTS:
            try:
                ok = bool(cond(data))
            except Exception:
                ok = False
            unlocked += ok
            card = QFrame(); card.setProperty("card", True)
            ch = QHBoxLayout(card); ch.setContentsMargins(10, 8, 10, 8); ch.setSpacing(8)
            ic = QLabel(icon if ok else "🔒"); ic.setStyleSheet("font-size:22px;")
            txv = QVBoxLayout(); txv.setSpacing(2)
            tl = QLabel(title); tl.setStyleSheet("font-weight:700;" + ("" if ok else "color:#8a9099;"))
            dl = QLabel(desc); dl.setObjectName("sub"); dl.setWordWrap(True)
            txv.addWidget(tl); txv.addWidget(dl)
            ch.addWidget(ic); ch.addLayout(txv, 1)
            self.ach_layout.addWidget(card, row, col)
            col += 1
            if col >= 3:
                col = 0; row += 1
        self.ach_title.setText(f"Achievements — {unlocked}/{len(ACHIEVEMENTS)} unlocked")
        cats = {}
        for les in LESSONS:
            cats.setdefault(les.get("cat", "General"), []).append(les["id"])
        done_set = set(data["completed_lessons"])
        for cat in CAT_ORDER:
            if cat not in cats:
                continue
            ids = cats[cat]
            n = sum(1 for i in ids if i in done_set)
            rowl = QHBoxLayout()
            lbl = QLabel(cat); lbl.setMinimumWidth(210)
            bar = QProgressBar(); bar.setTextVisible(False); bar.setFixedHeight(10)
            bar.setRange(0, len(ids)); bar.setValue(n)
            cnt = QLabel(f"{n}/{len(ids)}"); cnt.setObjectName("sub")
            rowl.addWidget(lbl); rowl.addWidget(bar, 1); rowl.addWidget(cnt)
            self.cat_layout.addLayout(rowl)
        idx = self._first_incomplete()
        if idx is not None:
            self.cont_lbl.setText("Up next: " + LESSONS[idx]["title"])
            self._cont_idx = idx; self.cont_btn.setEnabled(True)
        else:
            self.cont_lbl.setText("🎉 All lessons completed — amazing!")
            self._cont_idx = None; self.cont_btn.setEnabled(False)
    def _first_incomplete(self):
        done = set(self.store.data["completed_lessons"])
        for i, les in enumerate(LESSONS):
            if les["id"] not in done:
                return i
        return None
    def _continue(self):
        if self._cont_idx is not None and self.open_lesson:
            self.open_lesson(self._cont_idx)
    def _toggle_theme(self):
        s = self._settings()
        s["theme"] = "light" if s.get("theme", "dark") == "dark" else "dark"
        self.store.save(); self._apply_theme()
    def _change_size(self, delta):
        s = self._settings()
        s["size"] = max(11, min(20, s.get("size", 14) + delta))
        self.store.save(); self._apply_theme()
    def _apply_theme(self):
        s = self.store.data.get("settings", {})
        QApplication.instance().setStyleSheet(
            make_stylesheet(s.get("theme", "dark"), s.get("size", 14)))
    def _reset_progress(self):
        reply = QMessageBox.question(
            self, "Reset progress",
            "This will erase all lesson, practice, quiz, and flashcard progress.\nAre you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.store.reset(); self.refresh()
    def _export_progress(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export progress",
                                              "gitdojo_progress.json", "JSON (*.json)")
        if not path:
            return
        try:
            Path(path).write_text(json.dumps(self.store.data, indent=2), encoding="utf-8")
            QMessageBox.information(self, "Exported", f"Progress saved to:\n{path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
    def _import_progress(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import progress", "", "JSON (*.json)")
        if not path:
            return
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            for k in self.store.DEFAULTS:
                if k in data:
                    self.store.data[k] = data[k]
            self.store.save(); self.refresh()
            QMessageBox.information(self, "Imported", "Progress imported successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
    def _cheatsheet(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save cheat-sheet",
                                              "git_cheatsheet.html", "HTML (*.html)")
        if not path:
            return
        try:
            Path(path).write_text(self._build_cheatsheet_html(), encoding="utf-8")
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
    def _build_cheatsheet_html(self):
        REFERENCE = {
         "Setup & Config": [("git --version", "Check install"), ('git config --global user.name "Name"', "Identity"),
                            ("git init", "New repo"), ("git clone <url>", "Copy a repo")],
         "Snapshotting": [("git status", "State summary"), ("git add .", "Stage all"),
                          ('git commit -m "msg"', "Commit"), ("git diff", "Unstaged diff"),
                          ("git diff --staged", "Staged diff")],
         "Branching & Merging": [("git branch", "List"), ("git switch -c <name>", "Create+switch"),
                                 ("git merge <name>", "Merge"), ("git merge --abort", "Abort conflict")],
         "Remotes": [("git remote -v", "List remotes"), ("git push -u origin <branch>", "Push+upstream"),
                     ("git fetch", "Download"), ("git pull", "Fetch+integrate")],
         "Undoing": [("git restore <file>", "Discard edits"), ("git reset --soft HEAD~1", "Undo commit, keep staged"),
                     ("git revert <commit>", "Safe undo"), ("git reflog", "Find lost commits")],
        }
        rows = ["<!doctype html><html><head><meta charset='utf-8'>",
                "<title>GitDojo Cheat Sheet</title><style>",
                "body{font-family:Segoe UI,Arial,sans-serif;margin:28px;color:#222;}",
                "h1{color:#f05033;} h2{border-bottom:2px solid #f05033;padding-bottom:4px;margin-top:22px;}",
                "table{border-collapse:collapse;width:100%;margin-top:6px;}",
                "td,th{border:1px solid #ccc;padding:5px 8px;text-align:left;font-size:13px;}",
                "th{background:#f4f4f4;} code{background:#f4f4f4;padding:1px 5px;border-radius:3px;font-family:Consolas,monospace;}",
                "@media print{h2{page-break-after:avoid;}}",
                "</style></head><body>",
                "<h1>🥋 GitDojo — Git Cheat Sheet</h1>",
                "<p><em>Generated by GitDojo.</em></p>"]
        for cat, items in REFERENCE.items():
            rows.append(f"<h2>{html.escape(cat)}</h2>")
            rows.append("<table><tr><th style='width:45%'>Command</th><th>What it does</th></tr>")
            for cmd, desc in items:
                rows.append(f"<tr><td><code>{html.escape(cmd)}</code></td>"
                            f"<td>{html.escape(desc)}</td></tr>")
            rows.append("</table>")
        rows.append("</body></html>")
        return "\n".join(rows)

class UndoCheatSheetPage(QWidget):
    def __init__(self, store):
        super().__init__()
        self.store = store
        v = QVBoxLayout(self); v.setContentsMargins(24, 20, 24, 20); v.setSpacing(12)
        head = QHBoxLayout()
        t = QLabel("⏪ Undo Anything"); t.setObjectName("h1")
        head.addWidget(t); head.addStretch()
        v.addLayout(head)
        sub = QLabel("When it all goes wrong, reach for these — powered by git reflog and friends.")
        sub.setObjectName("sub"); v.addWidget(sub)
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Search undo scenarios…")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._filter)
        v.addWidget(self.search)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.list_layout = QVBoxLayout(self.container)
        self.list_layout.setContentsMargins(4, 4, 4, 4); self.list_layout.setSpacing(10)
        self.cards = []
        for emoji, title, cmd, desc in UNDO_SCENARIOS:
            card = self._make_card(emoji, title, cmd, desc)
            self.cards.append((card, (title + " " + desc + " " + cmd).lower()))
            self.list_layout.addWidget(card)
        self.list_layout.addStretch()
        scroll.setWidget(self.container)
        v.addWidget(scroll, 1)
    def _make_card(self, emoji, title, cmd, desc):
        card = QFrame(); card.setProperty("card", True)
        lay = QVBoxLayout(card); lay.setContentsMargins(14, 12, 14, 12); lay.setSpacing(6)
        top = QHBoxLayout()
        ic = QLabel(emoji); ic.setStyleSheet("font-size:20px;")
        tl = QLabel(title); tl.setStyleSheet("font-weight:700; font-size:15px;")
        top.addWidget(ic); top.addWidget(tl); top.addStretch()
        lay.addLayout(top)
        cmdbox = QTextEdit(); cmdbox.setReadOnly(True); cmdbox.setFont(mono_font(10))
        cmdbox.setPlainText(cmd)
        cmdbox.setFixedHeight(24 + 20 * (cmd.count("\n") + 1))
        cmdbox.setStyleSheet("background:#101116; color:#a5d6ff; border:1px solid #2c2f36; border-radius:6px;")
        lay.addWidget(cmdbox)
        d = QLabel(desc); d.setObjectName("sub"); d.setWordWrap(True)
        lay.addWidget(d)
        return card
    def _filter(self, *_):
        t = self.search.text().strip().lower()
        for card, hay in self.cards:
            card.setVisible((not t) or t in hay)
    def refresh(self):
        pass

# ──────────────────────────────────────────────────────────────── MAIN WINDOW
NAV = [("🏠", "Home"), ("📖", "Lessons"), ("🧠", "Quiz"),
       ("🃏", "Flashcards"), ("📚", "Reference"), ("🧪", "Sandbox"),
       ("📊", "Dashboard"), ("🔀", "Conflict Lab"), ("🪜", "Rebase Lab"),
       ("⏳", "Reflog Lab"), ("🍒", "Cherry-pick & Revert Lab"), ("🔍", "Bisect Lab"),
       ("🧳", "Stash Lab"), ("⏪", "Undo Anything")]

class MainWindow(QMainWindow):
    def __init__(self, store):
        super().__init__()
        self.setWindowTitle("GitDojo — Learn Git")
        self.resize(1280, 940)
        self.setMinimumSize(1000, 680)
        self.store = store
        self.sandbox = SandboxPage()
        self.lessons = LessonsPage(self.store)
        self.quiz = QuizPage(self.store)
        self.cards = FlashcardsPage(self.store)
        self.ref = ReferencePage()
        self.home = HomePage(self.store, self.goto, self._open_lesson)
        self.dashboard = DashboardPage(self.store, self.goto, self._open_lesson)
        self.conflict_lab = ConflictLabPage(self.store)
        self.rebase_lab = RebaseLabPage(self.store)
        self.reflog_lab = ReflogLabPage(self.store)
        self.pickrevert_lab = PickRevertLabPage(self.store)
        self.bisect_lab = BisectLabPage(self.store)
        self.stash_lab = StashLabPage(self.store)
        self.undo_page = UndoCheatSheetPage(self.store)
        pages = [self.home, self.lessons, self.quiz, self.cards, self.ref,
                 self.sandbox, self.dashboard, self.conflict_lab,
                 self.rebase_lab, self.reflog_lab, self.pickrevert_lab,
                 self.bisect_lab, self.stash_lab, self.undo_page]
        self.stack = QStackedWidget()
        for p in pages:
            self.stack.addWidget(p)
        side = QWidget()
        sv = QVBoxLayout(side); sv.setContentsMargins(0, 0, 0, 0); sv.setSpacing(0)
        brand = QLabel("🥋 GitDojo"); brand.setObjectName("brand")
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar"); self.sidebar.setFixedWidth(210)
        for icon, name in NAV:
            self.sidebar.addItem(QListWidgetItem(f"{icon}  {name}"))
        self.sidebar.currentRowChanged.connect(self._switch)
        sv.addWidget(brand); sv.addWidget(self.sidebar, 1)
        central = QWidget()
        hb = QHBoxLayout(central); hb.setContentsMargins(0, 0, 0, 0); hb.setSpacing(0)
        hb.addWidget(side); hb.addWidget(self.stack, 1)
        self.setCentralWidget(central)
        self.sidebar.setCurrentRow(0)
    def goto(self, i):
        self.sidebar.setCurrentRow(i)
    def _open_lesson(self, idx):
        self.sidebar.setCurrentRow(1)
        self.lessons._select_index(idx)
    def _switch(self, i):
        self.stack.setCurrentIndex(i)
        page = self.stack.widget(i)
        if hasattr(page, "refresh"):
            page.refresh()
    def closeEvent(self, e):
        self.sandbox.cleanup()
        super().closeEvent(e)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("GitDojo")
    app.setStyle("Fusion")
    store = ProgressStore()
    s = store.data.get("settings", {})
    app.setStyleSheet(make_stylesheet(s.get("theme", "dark"), s.get("size", 14)))
    win = MainWindow(store)
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()