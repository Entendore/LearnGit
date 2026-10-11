#!/usr/bin/env python3
"""
GitLearn — learn Git interactively.
pip install PySide6  →  python gitlearn.py
"""
import base64, datetime, difflib, fnmatch, hashlib, html as html_mod, json, random, re, shlex, sys, time
from pathlib import Path
from PySide6.QtCore import (Qt, QPointF, Signal, QTimer, QSettings, QEvent)
from PySide6.QtGui import (QBrush, QColor, QFont, QFontDatabase, QKeySequence,
                           QPainter, QPainterPath, QPen, QShortcut, QTextCursor)
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout,
                               QLabel, QLineEdit, QListWidget, QListWidgetItem,
                               QMainWindow, QMessageBox, QProgressBar,
                               QPushButton, QRadioButton, QScrollArea,
                               QSplitter, QStackedWidget, QTextBrowser,
                               QVBoxLayout, QWidget)

APP_BG, PANEL, PANEL2 = "#1a1b26", "#24283b", "#16161e"
BORDER, FG, MUTED = "#2f334d", "#c0caf5", "#565f89"
ACCENT, GREEN, RED = "#7aa2f7", "#9ece6a", "#f7768e"
YELLOW, CYAN, ORANGE, PURPLE = "#e0af68", "#7dcfff", "#ff9e64", "#bb9af7"
BRANCH_PALETTE = ["#7aa2f7", "#bb9af7", "#9ece6a", "#e0af68", "#f7768e",
                  "#7dcfff", "#ff9e64", "#73daca"]
KIND_COLORS = {"out": FG, "err": RED, "ok": GREEN, "warn": YELLOW,
               "info": CYAN, "add": GREEN, "del": RED}
PROGRESS_FILE = Path.home() / ".gitlearn_progress.json"
MONO = None
def _mono_family():
    global MONO
    if MONO is None:
        MONO = QFontDatabase.systemFont(QFontDatabase.FixedFont).family()
    return MONO

def _span(color, text, mono=True):
    fam = "font-family:'" + _mono_family() + "'; " if mono else ""
    return '<span style="' + fam + 'color:' + color + ';">' + text + '</span>'
def _ws(escaped):
    escaped = re.sub(r'  +', lambda m: '&nbsp;' * len(m.group(0)), escaped)
    return escaped if escaped else '&nbsp;'
def _ic(t):
    return ('<span style="font-family:\'' + _mono_family() + '\'; color:' +
            ORANGE + ';">&nbsp;' + html_mod.escape(t) + '&nbsp;</span>')
def _code(*lines):
    rows = "<br>".join(_span(GREEN, html_mod.escape(l).replace(" ", "&nbsp;"))
                       for l in lines)
    return ('<div style="background-color:' + PANEL2 + '; border:1px solid ' +
            BORDER + '; margin:8px 0px; padding:6px 8px;">' + rows + '</div>')
def _h3(t): return "<h3 style='color:" + ACCENT + "; margin-top:16px;'>" + t + "</h3>"
def _p(t): return "<p style='line-height:155%;'>" + t + "</p>"
def _ul(*items):
    return "<ul>" + "".join("<li style='margin:4px 0; line-height:145%;'>" + i +
                            "</li>" for i in items) + "</ul>"
def _callout(title, body, color=YELLOW):
    return ('<div style="background-color:' + PANEL + '; border-left:3px solid ' +
            color + '; margin:10px 0; padding:6px;"><b style="color:' + color +
            ';">' + title + '</b><br>' + body + '</div>')
WRAP_OPEN = "<div style='color:" + FG + "; font-size:14px;'>"
WRAP_CLOSE = "</div>"
def _practice(*cmds):
    return (_callout("🛠 Try it yourself", "Open the <b>Sandbox</b> tab and run:" +
                     _code(*cmds) + "Tip: type <b>help</b> in the sandbox to see "
                     "every command.", color=GREEN))

# =============================================================== LESSONS =====
LESSONS = [
{"title": "What is Git, and why should you care?",
 "body": _h3("The problem it solves") +
  _p("Have you ever saved files like <i>report_final_v2_REALLY_FINAL.py</i>? Git replaces that chaos with a clean, complete history of your project.") +
  _h3("What Git actually is") +
  _ul("A <b>distributed version control system</b> — every clone contains the full history.",
      "It stores <b>snapshots</b> of your files, not confusing diffs.",
      "It lets you <b>experiment safely</b> with branches and undo almost anything.",
      "It is the standard tool for team collaboration.") +
  _h3("Git vs GitHub") +
  _p("Git is the tool on your machine. GitHub/GitLab/Bitbucket are websites that <i>host</i> Git repos. You can use Git perfectly well without any website.") +
  _callout("Key idea", "A <b>commit</b> is a named snapshot of your project. The whole game: make changes, snapshot them, move between snapshots.")),
{"title": "Installing & configuring Git",
 "body": _h3("Install") +
  _p("Download from <a href='https://git-scm.com' style='color:" + ACCENT + ";'>git-scm.com</a> or use your package manager. Check: " + _ic("git --version") + ".") +
  _h3("One-time setup") +
  _code("$ git config --global user.name \"Ada Lovelace\"",
        "$ git config --global user.email \"ada@example.com\"",
        "$ git config --global init.defaultBranch main") +
  _callout("Sandbox note", "This app's sandbox pretends your identity is already configured.", color=CYAN)),
{"title": "Your first repository",
 "body": _h3("git init") +
  _p("A repository is a folder Git watches. " + _ic("git init") + " creates a hidden " + _ic(".git") + " sub-folder — that's the entire database: history, branches, everything.") +
  _code("$ mkdir my-project && cd my-project",
        "$ git init",
        "Initialized empty Git repository in .../my-project/.git/") +
  _p("Delete .git and you're back to a plain folder.") +
  _practice("git init", "touch readme.md", "git status", "git log")),
{"title": "The three areas",
 "body": _h3("Where your files live") +
  _code("  Working Directory   →   Staging Area   →   Repository",
        "  (you edit here)        (git add)        (git commit)") +
  _p(_ic("git add") + " places files into the <b>staging area</b> — a preview of the next snapshot. " + _ic("git commit") + " records it permanently.") +
  _h3("Why a staging area?") +
  _p("To craft clean, focused commits: stage two related files, commit, then the rest.") +
  _ul(_ic("git add file.py") + " — stage one file", _ic("git add .") + " — stage everything",
      _ic("git commit -m \"message\"") + " — snapshot", _ic("git commit -a -m") + " — stage tracked & commit") +
  _practice("touch app.py utils.py", "git add app.py", "git status",
            "git commit -m \"Add app skeleton\"", "git status")),
{"title": "Inspecting your work",
 "body": _h3("status · log · diff") +
  _p(_ic("git status") + " — what changed, staged, untracked. Run it constantly.") +
  _p(_ic("git log") + " — history, newest first. Try " + _ic("--oneline") + " and " + _ic("--graph --all --oneline") + ".") +
  _p(_ic("git diff") + " — unstaged changes; " + _ic("git diff --staged") + " — what you're about to commit.") +
  _practice("touch a.txt", "echo \"hello\" > a.txt", "git diff",
            "git add a.txt", "git diff --staged", "git log --oneline")),
{"title": "Branching",
 "body": _h3("A branch is just a sticky note") +
  _p("A branch is a movable pointer to a commit — 41 bytes on disk. <b>HEAD</b> says “you are here”.") +
  _code("main:    A---B---C",
        "                \\",
        "feature:          D---E      (HEAD -> feature)") +
  _h3("Commands") +
  _code("$ git branch feature        # create pointer",
        "$ git switch feature        # move HEAD",
        "$ git switch -c feature     # create + switch (modern)",
        "$ git checkout -b feature   # create + switch (classic)",
        "$ git branch -d feature     # delete") +
  _callout("Golden rule", "Keep <b>main</b> stable. Do work on branches.", color=PURPLE) +
  _practice("git switch -c feature", "touch feature.txt", "git add .",
            "git commit -m \"work\"", "git switch main", "ls",
            "git switch feature", "ls")),
{"title": "Merging & conflicts",
 "body": _h3("Two kinds of merge") +
  _ul("<b>Fast-forward</b> — main hasn't moved; the pointer slides forward.",
      "<b>Three-way merge</b> — both advanced; a merge commit with two parents is created.") +
  _code("$ git switch main", "$ git merge feature") +
  _h3("When both of you edit the same lines") +
  _code("<<<<<<< HEAD", "print(\"hello\")", "=======",
        "print(\"bonjour\")", ">>>>>>> greeting") +
  _p("Edit to what it should be, stage, commit. Sandbox shortcut: " + _ic("resolve") + ".") +
  _practice("git switch main", "git merge feature", "git merge --abort")),
{"title": "Working with remotes",
 "body": _h3("Clone, push, pull") +
  _p("A remote is a copy on a server (usually <b>origin</b>). This sandbox <i>simulates one</i> — push/fetch/pull really work.") +
  _code("$ git remote add origin <url>",
        "$ git push -u origin main",
        "$ git pull", "$ git fetch") +
  _h3("The daily rhythm") +
  _code("git pull  →  branch  →  code  →  commit  →  push  →  pull request") +
  _practice("git remote add origin https://github.com/you/r.git",
            "git push -u origin main", "teammate \"server edit\"", "git pull")),
{"title": "Undoing things",
 "body": _h3("Match the tool to the mistake") +
  _ul(_ic("git restore file") + " — discard unstaged edits",
      _ic("git restore --staged file") + " — unstage",
      _ic("git commit --amend") + " — fix the last commit",
      _ic("git revert <hash>") + " — undo with a NEW commit (safe)",
      _ic("git reset --soft HEAD~1") + " — uncommit, keep staged",
      _ic("git reset --hard HEAD~1") + " — uncommit and delete ⚠") +
  _callout("⚠ Danger zone", "Avoid " + _ic("reset --hard") + " / " + _ic("push --force") +
           " on shared branches.", color=RED) +
  _practice("touch secret.txt", "git add secret.txt",
            "git restore --staged secret.txt", "git log --oneline")),
{"title": "A real-world workflow",
 "body": _h3("One loop to remember") +
  _code("git switch main && git pull",
        "git switch -c add-dark-mode",
        "git status && git add . && git commit -m \"Add dark mode\"",
        "git push -u origin add-dark-mode") +
  _h3("Commit messages that don't suck") +
  _ul("Imperative mood: “Add dark mode”.", "First line ≤ 50 chars.",
      "One logical change per commit.") +
  _p("You've finished the core course — the appendices go deep. Happy committing! 🚀") +
  _practice("git init", "touch main.py", "git switch -c add-tests",
            "git add .", "git commit -m \"Add tests\"")),
{"title": "Appendix A — Command-line survival kit",
 "body": _h3("Getting around") +
  _ul(_ic("pwd") + " — where am I", _ic("ls / ls -la") + " — list",
      _ic("cd dir · cd .. · cd") + " — move", _ic("mkdir -p a/b") + " — nested dirs",
      _ic("touch f") + " — empty file", _ic("cp -r src dst") + " — copy",
      _ic("mv old new") + " — move/rename", _ic("rm -r dir") + " — delete") +
  _callout("⚠ rm has no undo", _ic("rm -rf") + " deletes recursively and silently.", color=RED) +
  _h3("Reading files & searching") +
  _ul(_ic("cat f") + " · " + _ic("less f") + " · " + _ic("head -n 5 f") + " · " + _ic("tail -n 20 f"),
      _ic("grep -rn \"TODO\" .") + " — search text", _ic("find . -name \"*.py\"") + " — find files") +
  _h3("Terminal superpowers") +
  _ul("<b>Tab</b> completes · <b>↑↓</b> history · <b>Ctrl+R</b> searches it · <b>man git-log</b> full manual.") +
  _practice("touch notes.txt", "echo \"hi\" > notes.txt", "cat notes.txt", "ls", "rm notes.txt")),
{"title": "git log — reading history like a pro",
 "body": _h3("One command, a dozen lenses") +
  _ul(_ic("git log --oneline") + " · " + _ic("--graph --all") + " · " + _ic("-n 5") +
      " · " + _ic("--author=\"Ada\"") + " · " + _ic("--grep=\"fix\"") + " · " + _ic("--since=\"2.days.ago\""),
      _ic("git log -p app.py") + " — full patch · " + _ic("--stat") + " — files touched",
      _ic("git log -S \"darkmode\"") + " — pickaxe: commits adding/removing a string",
      _ic("git log --format=\"%h %an %s\"") + " — custom output",
      _ic("git log main..feature") + " — commits main doesn't have") +
  _practice("touch x.txt", "git add .", "git commit -m \"fix the widget\"",
            "git log --oneline", "git log --stat", "git log --grep=\"fix\"",
            "git log -S \"widget\"", "git log --graph --all --oneline")),
{"title": "show, diff & blame — CSI for your code",
 "body": _h3("git show — one commit, in full") +
  _p(_ic("git show") + " · " + _ic("git show v1.0") + " · " + _ic("git show HEAD~2")) +
  _h3("git diff — every comparison") +
  _ul(_ic("git diff") + " · " + _ic("--staged") + " · " + _ic("git diff HEAD") +
      " · " + _ic("git diff main feature") + " · " + _ic("git diff v1.0 v1.1") +
      " · " + _ic("--stat") + " · " + _ic("-w") + " (ignore whitespace)") +
  _h3("git blame") +
  _p(_ic("git blame app.py") + " — who wrote each line and when. For understanding, not blaming. Mostly.") +
  _practice("touch app.py", "echo \"print('hi')\" > app.py", "git add .",
            "git commit -m \"add app\"", "git show", "git show --stat", "git blame app.py")),
{"title": "git stash — the pause button",
 "body": _h3("“I need to switch, but I'm mid-change!”") +
  _code("$ git stash                       # shelve tracked changes",
        "$ git stash push -m \"wip: login\"  # labelled",
        "$ git stash -u                    # include untracked",
        "$ git stash list / pop / apply / drop / clear") +
  _ul("<b>pop</b> removes the entry after applying; <b>apply</b> keeps it.",
      "Stashes are a stack (stash@{0} newest) and never pushed to remotes.") +
  _callout("Better habit?", "Coherent work → WIP commit on a branch. Stash is for short interruptions.", color=CYAN) +
  _practice("touch a.txt", "echo \"half-done\" > a.txt", "git stash",
            "git status", "git stash list", "git stash pop", "cat a.txt")),
{"title": "git tag — naming the milestones",
 "body": _h3("Marks that don't move") +
  _code("$ git tag v1.0                          # lightweight",
        "$ git tag -a v1.0 -m \"first stable\"    # annotated (recommended)",
        "$ git tag / -l \"v1.*\" / -d v1.0",
        "$ git show v1.0") +
  _ul("SemVer: MAJOR.MINOR.PATCH.", "Tags aren't pushed by default: " + _ic("git push origin v1.0") + ".") +
  _practice("git tag v0.1", "git tag -a v0.2 -m \"demo\"", "git tag",
            "git show v0.2", "git log --oneline")),
{"title": "The complete undo toolbox",
 "body": _h3("Mistake → cure") +
  _ul("Hate unstaged edits → " + _ic("git restore f"),
      "Staged by accident → " + _ic("git restore --staged f"),
      "Typo in message → " + _ic("git commit --amend -m \"fixed\""),
      "Uncommit keep work → " + _ic("git reset --soft HEAD~1"),
      "Uncommit+unstage → " + _ic("git reset --mixed HEAD~1"),
      "Uncommit+discard → " + _ic("git reset --hard HEAD~1") + " ⚠",
      "Already pushed → " + _ic("git revert <hash>")) +
  _h3("The three reset modes") +
  _code("            HEAD     Staging    Working dir",
        "--soft      moves    kept       kept",
        "--mixed     moves    reset      kept",
        "--hard      moves    reset      reset  ⚠") +
  _callout("Amend is a rewrite", "New hash! Fine private; never on pushed commits.", color=RED) +
  _practice("touch f.txt", "git add .", "git commit -m \"bad mesage\"",
            "git commit --amend -m \"good message\"", "git reset --soft HEAD~1",
            "git status", "git commit -m \"good message\"", "git log --oneline")),
{"title": "git rebase — replay your work elsewhere",
 "body": _h3("What it does") +
  _p("Lifts your commits off their base and replays them on another commit — same changes, brand-new hashes.") +
  _code("before:   A---B---C (main)",
        "               \\",
        "                D---E (feature)",
        "after 'git rebase main' on feature:  D'--E' ← rewritten!") +
  _h3("Merge vs rebase") +
  _ul("<b>Merge</b> — history as it happened; adds a merge commit.",
      "<b>Rebase</b> — manufactured linear history. Clean, a polite fiction.") +
  _callout("🚨 Golden rule", "Never rebase commits others may already have.", color=RED) +
  _practice("git switch -c feature", "touch a.txt", "git add .",
            "git commit -m \"feat A\"", "git switch main", "touch m.txt",
            "git add .", "git commit -m \"main moves on\"", "git switch feature",
            "git rebase main", "git log --oneline")),
{"title": "Interactive rebase — rewriting history neatly",
 "body": _h3("The todo list") +
  _p(_ic("git rebase -i HEAD~3") + " lists the last 3 commits. Change <i>pick</i> to:") +
  _code("# reword — edit message · squash — fold into the one ABOVE",
        "# fixup  — fold in, discard message · drop — delete") +
  _h3("Sandbox edition") +
  _code("$ git rebase -i HEAD~3",
        "$ drop 3      $ squash 2      $ reword 1 tidy message",
        "$ git rebase --continue   # or --abort") +
  _callout("Same golden rule", "Interactive rebase = strongest history rewriting.", color=RED) +
  _practice("touch a.txt", "git add .", "git commit -m \"add feature\"",
            "touch b.txt", "git add .", "git commit -m \"wip\"",
            "git rebase -i HEAD~2", "squash 2", "git rebase --continue",
            "git log --oneline")),
{"title": "git cherry-pick — copy one commit",
 "body": _h3("Surgical transplant") +
  _p("Applies one commit on top of your branch as a <b>new commit</b> — new hash, same message/author.") +
  _ul("Hotfix from main needed on a release branch now.",
      "Committed to the wrong branch.",
      "Harvesting one good commit from an abandoned PR.") +
  _code("$ git cherry-pick 3f2c1a9     # or -x to record origin") +
  _callout("It's a copy, not a move", "Later merges recognise identical changes.", color=CYAN) +
  _practice("git switch -c side", "touch s.txt", "git add .",
            "git commit -m \"important fix\"", "git switch main",
            "git cherry-pick -x side", "git log --oneline")),
{"title": "git reflog — nothing is ever lost",
 "body": _h3("Git secretly keeps a diary") +
  _p("Every HEAD move (commit, switch, reset, rebase, merge) is recorded, kept ~90 days.") +
  _code("$ git reflog",
        "a1b2c3d HEAD@{0}: reset: moving to HEAD~1",
        "e4f5g6h HEAD@{1}: commit: precious work",
        "$ git reset --hard HEAD@{1}      # time-travel back!") +
  _callout("The one exception", "Reflog only protects <b>committed</b> work. Commit early, commit often.", color=RED) +
  _practice("touch precious.txt", "git add .", "git commit -m \"precious\"",
            "git reset --hard HEAD~1", "git reflog",
            "git reset --hard HEAD@{1}", "git log --oneline")),
{"title": "git clean & .gitignore — taming untracked files",
 "body": _h3("The clutter problem") +
  _code("# .gitignore — one pattern per line",
        "*.log          # any .log file, anywhere",
        "node_modules/  # whole directory",
        "/secret.txt    # repo root only",
        "!keep.tmp      # exception (real git)") +
  _h3("git clean") +
  _ul(_ic("git clean -n") + " — <b>dry run</b> (always start here)",
      _ic("-f") + " delete files · " + _ic("-fd") + " dirs · " + _ic("-fx") + " also ignored") +
  _callout("No undo", "Cleaned files never entered Git.", color=RED) +
  _practice("echo \"*.log\" > .gitignore", "touch debug.log keep.txt",
            "git status", "git clean -n", "git clean -f", "ls")),
{"title": "git bisect — hunting the bug commit",
 "body": _h3("200 commits. One broke the build.") +
  _p("Bisect binary-searches: mark current <b>bad</b> and an older commit <b>good</b>; Git jumps to the middle. 200 commits ≈ 8 steps.") +
  _code("$ git bisect start HEAD v1.0",
        "$ git bisect good      # or bad — repeat",
        "abc1234 is the first bad commit!",
        "$ git bisect reset") +
  _ul("Bisect uses <b>detached HEAD</b> — normal and safe.",
      "Automate: " + _ic("git bisect run python test.py") + ".") +
  _practice("touch a.txt", "git add .", "git commit -m \"v1\"", "touch b.txt",
            "git add .", "git commit -m \"v2\"", "touch c.txt", "git add .",
            "git commit -m \"v3 (buggy)\"", "git bisect start", "git bisect bad",
            "git bisect good HEAD~2", "git bisect bad", "git bisect reset")),
{"title": "git config & aliases — set it and forget it",
 "body": _h3("Essentials") +
  _code("$ git config --global user.name \"Ada\"   $ git config --list") +
  _h3("Aliases") +
  _code("$ git config --global alias.st status",
        "$ git config --global alias.hist \"log --oneline --graph --all\"",
        "$ git st          # works exactly like git status") +
  _practice("git config alias.st status", "git config user.name \"Ada Lovelace\"",
            "git config user.name", "git config --list", "git st")),
{"title": "Small tools, big wins: grep · shortlog · describe · gc",
 "body": _h3("Search & summarize") +
  _ul(_ic("git grep \"TODO\"") + " — search tracked files (" + _ic("-i") + " case-insensitive)",
      _ic("git shortlog") + " — commits per author",
      _ic("git describe") + " — v1.2-3-g1a2b3c4 style names") +
  _h3("Housekeeping & export") +
  _ul(_ic("git gc") + " · " + _ic("git fsck") + " · " + _ic("git archive -o release.zip HEAD")) +
  _callout("Why describe matters", "CI stamps builds with describe output — every artifact traceable.", color=CYAN) +
  _practice("touch a.txt", "echo \"# TODO\" > a.txt", "git add .",
            "git commit -m \"todo\"", "git grep TODO", "git shortlog",
            "git tag -a v0.1 -m \"first\"", "git describe", "git gc")),
{"title": "Remotes deep-dive: fetch, pull, push & PRs",
 "body": _h3("origin, tracking, origin/main") +
  _ul(_ic("git remote -v") + " / add / rename / remove",
      _ic("git push -u origin main") + " links branches; afterwards plain push/pull work",
      "<b>origin/main</b> is your cached view — it moves when you <i>fetch</i>.") +
  _h3("fetch vs pull") +
  _code("git fetch                   # download, touch nothing",
        "git diff main origin/main   # inspect safely",
        "git pull                    # fetch + merge") +
  _h3("When push is rejected") +
  _p(_ic("git pull --rebase") + ", then push. Never blind " + _ic("--force") + "; prefer " + _ic("--force-with-lease") + ".") +
  _h3("Pull requests") +
  _p("A PR is a website feature: “please pull my branch” — wrapping the merge in review + CI.") +
  _practice("git push", "git pull", "teammate \"nit\"", "git fetch",
            "git log origin/main --oneline")),
{"title": "Appendix B — pipes, redirection & text tools",
 "body": _h3("Small tools, connected") +
  _p(_ic("|") + " wires the left command's stdout to the right command's stdin.") +
  _code("$ history | grep commit",
        "$ git log --oneline | head -n 3",
        "$ grep -rn TODO . | wc -l",
        "$ cat words.txt | sort | uniq -c | sort -rn | head -n 3") +
  _h3("Redirection") +
  _ul(_ic("git log > changelog.txt") + " — overwrite", _ic("echo note >> notes.txt") + " — append") +
  _h3("Text tools") +
  _ul(_ic("sort [-rn] [-u]") + " · " + _ic("uniq -c") + " (sort first!) · " +
      _ic("cut -d, -f2") + " · " + _ic("sed s/old/new/g") + " (" + _ic("-i") + " in-place) · " +
      _ic("wc -l") + " · " + _ic("nl") + " · " + _ic("tac")) +
  _callout("Real-world combo", _ic("git log --format=\"%an\" | sort | uniq -c | sort -rn") +
           " → commits per author.", color=CYAN) +
  _practice("touch fruits.txt", "echo banana > fruits.txt", "echo apple >> fruits.txt",
            "sort fruits.txt | uniq -c", "git log --oneline | head -n 3",
            "git log --oneline > log.txt", "cat log.txt")),
{"title": "Appendix C — plumbing & the object model",
 "body": _h3("What a commit is really made of") +
  _p("Git stores content-addressed objects: <b>blobs</b>, <b>trees</b>, <b>commits</b>, <b>tags</b>. Same content → same SHA-1, everywhere, forever.") +
  _code("$ git hash-object app.py       # real sha1 of 'blob <size>\\0<content>'",
        "$ git cat-file -t HEAD         # what kind?",
        "$ git cat-file -p HEAD~1:app.py # a file as it was") +
  _h3("The plumbing toolbox") +
  _ul(_ic("git rev-parse HEAD") + " / " + _ic("--abbrev-ref HEAD"),
      _ic("git show HEAD~1:file") + " — time-travel read",
      _ic("git merge-base main feature") + " — divergence point",
      _ic("git for-each-ref") + " · " + _ic("git symbolic-ref HEAD") + " · " + _ic("git branch hotfix <hash>")) +
  _h3("Shell superpowers") +
  _ul(_ic("export VAR=x") + " then " + _ic("echo $VAR") + " · " + _ic("$?") + " exit status · " +
      _ic("time git log") + " · " + _ic("tee") + " splits a pipeline · " + _ic("xargs") + " → arguments · " +
      _ic("awk -F, '{print $2}'")) +
  _callout("Why plumbing matters", "GUIs are plumbing in a costume. Read refs and hashes directly and nothing confuses you for long.", color=PURPLE) +
  _practice("touch app.py", "git add .", "git commit -m \"seed\"",
            "git hash-object app.py", "git rev-parse --abbrev-ref HEAD",
            "git cat-file -t HEAD", "echo \"2+2\" | bc", "export N=ada", "echo hi $N")),
{"title": "Appendix D — chaining, scripts & patches by email",
 "body": _h3("Gluing commands") +
  _ul(_ic("a && b") + " — b only if a succeeded · " + _ic("a || b") + " — on failure · " + _ic("a ; b") + " — always",
      _ic("echo \"$(git branch --show-current)\"") + " — command substitution",
      _ic("echo $?") + " — status (0=ok) · " + _ic("!!") + " repeat last · " + _ic("!$") + " its last arg") +
  _h3("Shell scripts") +
  _code("$ echo 'git status -sb' > daily.sh",
        "$ echo 'git log --oneline -5' >> daily.sh",
        "$ sh daily.sh            # runs each line; $1 $2 = args") +
  _h3("Patches by email — git's original workflow") +
  _code("$ git format-patch -1                 # commit → 0001-x.patch",
        "$ git format-patch main..feature",
        "$ git apply --check 0001-x.patch      # dry run",
        "$ git am 0001-x.patch                 # apply AS a commit",
        "$ git apply 0001-x.patch              # worktree only") +
  _callout("Why it still matters", "A patch is a commit minus a home. --fixup + --autosquash, cherry-pick A..B and rebase --onto are the same move: relocating commits.", color=PURPLE) +
  _practice("git switch -c patch-demo", "echo hello > feat.txt", "git add .",
            "git commit -m \"a lovely feature\"", "git format-patch -1", "ls",
            "git switch main", "git am 0001-a-lovely-feature.patch",
            "git log --oneline")),
{"title": "Deep dive — inside the .git directory",
 "body": _h3("One folder runs the show") +
  _ul("<b>HEAD</b> — text file: " + _ic("ref: refs/heads/main"),
      "<b>refs/</b> — one 41-byte file per branch/tag",
      "<b>objects/</b> — blobs/trees/commits by SHA-1 (packed over time)",
      "<b>index</b> — the staging area · <b>config</b> · <b>hooks/</b> · <b>packed-refs</b>") +
  _h3("Prove it") +
  _ul(_ic("git rev-parse --show-toplevel") + " · " + _ic("git cat-file -p HEAD") +
      " · " + _ic("git hash-object f") + " · " + _ic("git for-each-ref")) +
  _callout("The big idea", "Nothing is a copy. Everything is content-addressed objects plus tiny pointers — that's why branching is instant.", color=PURPLE) +
  _practice("echo hi > obj.txt", "git add .", "git commit -m \"anatomy\"",
            "git rev-parse --git-dir", "git cat-file -t HEAD",
            "git hash-object obj.txt", "git for-each-ref")),
{"title": "Signing commits & tags",
 "body": _h3("Who <i>really</i> wrote this?") +
  _p("Author fields are just text. A GPG/SSH signature proves key control.") +
  _code("$ git commit -S -m \"signed\"",
        "$ git log --show-signature -1",
        "$ git tag -s v2.0 -m \"signed release\"   $ git tag -v v2.0",
        "$ git verify-commit HEAD") +
  _ul("Real setup: " + _ic("gpg --full-generate-key") + " → " + _ic("user.signingkey") +
      " → " + _ic("commit.gpgsign true") + " → upload public key for the Verified badge.") +
  _callout("Signed ≠ trusted", "It proves key control, not good intent.", color=CYAN) +
  _practice("git add .", "git commit -S -m \"signed\"", "git log --show-signature -1",
            "git tag -s v2.0 -m \"rel\"", "git tag -v v2.0", "git verify-commit HEAD")),
{"title": "Never commit your secrets",
 "body": _h3("The rite of passage") +
  _p("Bots find leaked " + _ic("API_KEY=sk-live-…") + " in minutes. Prevention is cheap.") +
  _ul("Secrets in .env / vaults — never tracked.",
      "Ignore them on day one; a pre-commit hook greps for patterns.",
      "Use " + _ic("YOUR_API_KEY") + " placeholders in examples.") +
  _h3("If you already did") +
  _code("1. ROTATE THE KEY. History rewriting is hygiene, not safety.",
        "2. git rm --cached .env && echo .env >> .gitignore",
        "3. git filter-repo to rewrite, then a coordinated force-push.") +
  _callout("Force-push etiquette", "Rewriting shared history is a team event.", color=RED) +
  _practice("echo \"API_KEY=x\" > .env", "echo \".env\" > .gitignore",
            "git status -s", "git add .", "git commit -m \"config\"")),
{"title": "git hooks — robots that guard your history",
 "body": _h3("Code that runs on git events") +
  _p("Client-side: " + _ic("pre-commit") + ", " + _ic("commit-msg") + ", " + _ic("pre-push") +
     ". Server-side: " + _ic("pre-receive") + " — the trick behind protected branches.") +
  _h3("Sandbox edition") +
  _p("Put commands in " + _ic(".githooks/pre-commit") + "; any failure blocks the commit.") +
  _code("$ mkdir .githooks",
        "$ echo 'test -f CHANGELOG.md' > .githooks/pre-commit",
        "$ git commit -m \"no changelog\"      # ✖ blocked!",
        "$ touch CHANGELOG.md && git commit -m \"passes\"",
        "$ git commit --no-verify -m \"emergency\"") +
  _ul("Recipes: lint staged files, block sk-live secrets, enforce Conventional Commits.",
      "Shared hooks: commit .githooks/ + " + _ic("git config core.hooksPath .githooks") + ".") +
  _practice("mkdir .githooks",
            "echo 'test -f CHANGELOG.md' > .githooks/pre-commit",
            "git commit --allow-empty -m \"blocked?\"", "touch CHANGELOG.md",
            "git commit --allow-empty -m \"passes\"",
            "git commit --allow-empty -m \"bypass\" --no-verify")),
{"title": "git rerere — remember your conflict resolutions",
 "body": _h3("The same conflict, twice? Never again") +
  _p("<b>re</b>use <b>re</b>corded <b>re</b>solution: resolving a conflict teaches Git; identical future conflicts auto-resolve. Enable: " +
     _ic("rerere.enabled true") + " — always on here.") +
  _h3("Toolbox") +
  _ul(_ic("git rerere status") + " · " + _ic("git rerere diff") + " · " + _ic("git rerere clear")) +
  _callout("Why teams love it", "feature↔main ping-pong means the same conflict repeatedly; rerere turns repeats into one keystroke.", color=GREEN) +
  _practice("git switch -c r1", "echo alpha > share.txt", "git add .",
            "git commit -m \"r1\"", "git switch main", "echo beta > share.txt",
            "git add .", "git commit -m \"beta\"", "git merge r1",
            "resolve share.txt ours", "git add .", "git commit -m \"merge r1\"",
            "git reset --hard HEAD~2", "git branch -D r1", "git switch -c r2",
            "echo alpha > share.txt", "git add .", "git commit -m \"r2\"",
            "git switch main", "echo beta2 > share.txt", "git add .",
            "git commit -m \"beta2\"", "git merge r2", "git commit -m \"merge\"",
            "git rerere status")),
{"title": "Submodules & vendoring",
 "body": _h3("A repo inside your repo") +
  _p("A submodule pins another repository to one exact commit in a subfolder: path + URL (.gitmodules) + pinned hash.") +
  _code("$ git submodule add https://github.com/you/lib libs/lib",
        "$ git submodule status",
        "$ git clone --recurse-submodules <url>   # or folders look empty!") +
  _ul("Update = pull inside, commit new pin in parent — two commits, two repos.",
      "Alternatives: subtree (merges INTO your history), package managers, vendoring.") +
  _callout("Rule of thumb", "Submodule only when you control both repos and need a hard pin.", color=YELLOW) +
  _practice("git submodule add https://github.com/you/lib libs/lib",
            "cat .gitmodules", "git submodule status", "ls libs/lib",
            "git add .", "git commit -m \"pin lib\"")),
{"title": "Team workflows: GitHub Flow · Git Flow · trunk-based",
 "body": _h3("Three ways to organize") +
  _ul("<b>GitHub Flow</b> — main always deployable; short branch + PR + merge.",
      "<b>Git Flow</b> — main + develop with feature/release/hotfix branches; versioned releases.",
      "<b>Trunk-based</b> — hours-long branches (or direct to main) behind feature flags.") +
  _ul("Whatever you pick: <b>protect main</b>, require reviews + green CI.") +
  _code("git switch -c feature/ui && git push -u origin feature/ui",
        "teammate \"review nits\" && git pull --rebase",
        "git switch main && git merge --no-ff feature/ui") +
  _callout("Truth", "Small PRs, fast reviews and green CI beat any branching religion.", color=PURPLE) +
  _practice("git remote add origin https://github.com/you/demo.git",
            "git switch -c feature/ui", "touch ui.txt", "git add .",
            "git commit -m \"ui\"", "git push -u origin feature/ui",
            "teammate \"review nits\"", "git pull --rebase", "git switch main",
            "git merge --no-ff feature/ui", "git push")),
{"title": "Squash, rebase or merge? A maintainer's guide",
 "body": _h3("Three ways a PR lands") +
  _ul("<b>Merge commit</b> — truthful history: " + _ic("git merge --no-ff"),
      "<b>Squash & merge</b> — whole PR becomes ONE commit on main: " + _ic("git merge --squash && git commit"),
      "<b>Rebase & merge</b> — every PR commit replayed linearly: " + _ic("git rebase main")) +
  _code("merge            squash           rebase",
        "history   truthful         one-commit/PR    linear",
        "bisection muddy            clean            clean") +
  _ul("Messy PR → squash. Meaningful commits → rebase. Integration points matter → merge.") +
  _callout("Squash rewrites identity", "One NEW hash; delete the branch after.", color=CYAN) +
  _practice("git switch -c work", "touch w.txt", "git add .", "git commit -m \"wip 1\"",
            "echo x >> w.txt", "git add .", "git commit -m \"wip 2\"",
            "git switch main", "git merge --squash work",
            "git commit -m \"Add widget (squashed)\"", "git branch -D work")),
{"title": "Code review & conventional commits",
 "body": _h3("The PR is a conversation") +
  _ul("<b>Small beats thorough</b> — ~200-line diffs get real reviews.",
      "Review intent → design → nits. Label nits vs blockers.",
      "Praise good things out loud.") +
  _h3("Conventional Commits") +
  _code("feat: add dark mode toggle",
        "fix(auth): correct token refresh race",
        "refactor!: drop Python 3.8      # ! = breaking") +
  _code("$ git log --format=\"%s\" | cut -d: -f1 | sort | uniq -c") +
  _callout("Reviewer superpower", _ic("git log --author=you --since=1.week.ago --oneline") + " before standup.", color=GREEN) +
  _practice("touch feature.py", "git add .", "git commit -m \"feat: dark mode\"",
            "git log --format=\"%s\" | cut -d: -f1 | sort | uniq -c")),
{"title": "Big repos: depth, LFS & performance",
 "body": _h3("When cloning takes forever") +
  _ul(_ic("git clone --depth 1") + " — shallow (CI favorite); undo: " + _ic("fetch --unshallow"),
      _ic("git clone --filter=blob:none") + " — partial clone",
      _ic("git sparse-checkout set docs/src") + " — few of 40,000 paths",
      "<b>Git LFS</b> — binaries become pointers: " + _ic("git lfs track \"*.psd\"")) +
  _ul(_ic("git gc") + " · " + _ic("git count-objects -v") + " · " + _ic("git fsck") +
      " · fetch with " + _ic("--prune") + ".") +
  _callout("Monorepo or polyrepo?", "Atomic cross-project changes vs access control; big monorepos lean on partial clone + sparse checkout.", color=PURPLE) +
  _practice("git count-objects -v", "git gc", "git fsck",
            "git archive -o snapshot.zip HEAD")),
{"title": "The “Oh no!” recovery playbook",
 "body": _h3("Symptom → cure") +
  _ul("Wrong branch → " + _ic("switch correct && cherry-pick <hash>") + " then " + _ic("reset --hard HEAD~1"),
      "Deleted branch → " + _ic("git reflog") + " → " + _ic("git switch -c name <hash>"),
      "Diverged from origin → " + _ic("git pull --rebase"),
      "reset --hard ate work → " + _ic("reflog") + " → " + _ic("reset --hard HEAD@{n}"),
      "Push rejected → fetch, look, " + _ic("pull --rebase") + ", push",
      "Detached HEAD commits → " + _ic("git switch -c rescue") + " <i>before</i> leaving") +
  _callout("The one rule", "Stop. git status. git reflog. Panic commands cause more damage than the mistake.", color=RED) +
  _practice("git switch -c precious", "echo gold > gold.txt", "git add .",
            "git commit -m \"gold\"", "git switch main", "git branch -D precious",
            "git reflog", "git switch -c precious HEAD@{1}", "cat gold.txt")),
{"title": "Decoder ring — reading Git's error messages",
 "body": _h3("Errors are documentation") +
  _ul("<b>“not a git repository”</b> → outside a repo — init or cd up.",
      "<b>“changes would be overwritten”</b> → commit, stash, or restore first.",
      "<b>“! [rejected] (fetch first)”</b> → fetch, pull --rebase, push.",
      "<b>“refusing to merge unrelated histories”</b> → two roots; " + _ic("--allow-unrelated-histories") + " if intentional.",
      "<b>“detached HEAD”</b> → " + _ic("switch -c <name>") + " to keep new commits.",
      "<b>fatal vs warning</b> → didn't run vs ran-with-caveat.") +
  _h3("Universal first response") +
  _code("$ git status && git log --oneline -5 --all --graph && git reflog") +
  _callout("Exit codes count", "0 = success — that's what makes && and CI work.", color=CYAN) +
  _practice("git checkout no-such-branch", "git merge also-missing",
            "git commit --allow-empty -m \"one\" 2>/dev/null; git log --oneline")),
{"title": "Diffs, hunks & context",
 "body": _h3("How to read a hunk") +
  _code("@@ -2,7 +2,8 @@     ← old: line 2, 7 lines · new: line 2, 8",
        " line two           ← context (unchanged)",
        "-line three         ← removed",
        "+LINE THREE!        ← added") +
  _ul("Context lines let patches apply despite shifted line numbers.",
      _ic("git diff -U0") + " minimal · " + _ic("-U10") + " more context · " +
      _ic("--word-diff") + " inline [-old-] [+new+].") +
  _callout("Review trick", "Read diffs bottom-up — regressions sit near the newest change.", color=GREEN) +
  _practice("echo one > poem.txt", "echo two >> poem.txt", "git add .",
            "git commit -m \"v1\"", "echo ONE > poem.txt", "git diff -U0",
            "git diff -U10", "git diff --word-diff", "git diff --stat")),
{"title": "The art of the atomic commit",
 "body": _h3("One commit, one idea") +
  _p("An atomic commit does one logical thing and passes tests alone. Makes revert, bisect, review and changelogs easy.") +
  _h3("git add -p — stage by the hunk") +
  _code("$ git add -p poem.txt",
        "Stage this hunk?  y = yes · n = no · a = all · q = quit",
        "$ git diff --staged    # verify",
        "$ git commit -m \"fix: uppercase\"",
        "$ git add poem.txt && git commit -m \"add line four\"") +
  _callout("Message = the why", "The diff shows the what.", color=PURPLE) +
  _practice("echo one > poem.txt", "echo two >> poem.txt", "git add .",
            "git commit -m \"v1\"", "echo ONE > poem.txt", "echo four >> poem.txt",
            "git add -p poem.txt", "y", "q", "git diff --staged",
            "git commit -m \"uppercase ONE\"", "git add .",
            "git commit -m \"add four\"", "git log --oneline")),
{"title": "Line endings & .gitattributes",
 "body": _h3("The ^M mystery") +
  _p("Windows CRLF vs Unix LF. Fix by declaring intent in a committed <b>.gitattributes</b>:") +
  _code("* text=auto            # normalize to LF in the repo",
        "*.bat text eol=crlf   # Windows scripts need CRLF",
        "*.png binary") +
  _ul("Re-normalize: " + _ic("git add --renormalize .") + " then commit once.",
      "Also: " + _ic("config.yml merge=ours") + " keeps OUR version; GitHub language stats use it too.") +
  _callout("Rule", "Per-machine → .gitconfig. Per-repo team rules → committed .gitattributes.", color=CYAN) +
  _practice("echo hello > cfg.txt", "unix2dos cfg.txt", "git diff --stat",
            "echo \"*.txt text eol=lf\" > .gitattributes", "git add cfg.txt",
            "git status -s", "git add .gitattributes",
            "git commit -m \"normalize line endings\"")),
{"title": "Ignore patterns — the full picture",
 "body": _h3("Syntax") +
  _code("*.log            # everywhere",
        "/build           # root only",
        "node_modules/    # directories only",
        "doc/**/*.pdf     # any depth",
        "!important.log  # un-ignore") +
  _h3("Debugging") +
  _ul(_ic("git check-ignore -v debug.log") + " — file:line:pattern of the match",
      _ic("git status --ignored") + " · " + _ic("git clean -nX/-fX")) +
  _h3("Already tracked?") +
  _code("$ git rm --cached config.local && git commit") +
  _ul("Silence a tracked file: " + _ic("git update-index --skip-worktree f") +
      " (check with " + _ic("git ls-files -v") + ").") +
  _practice("echo \"*.log\" > .gitignore", "touch debug.log", "git check-ignore -v debug.log",
            "git status -s", "git add .", "git commit -m \"ignore logs\"")),
{"title": "git worktree — two branches, two folders",
 "body": _h3("The interrupt problem") +
  _p("Deep in a feature when a prod bug lands? Check the hotfix out in a <b>second folder</b> — one shared .git, zero duplication.") +
  _code("$ git worktree add ../hotfix        $ git worktree list",
        "$ git -C ../hotfix status           # run git inside it",
        "$ git -C hotfix commit -am \"hotfix\"",
        "$ git merge hotfix && git worktree remove hotfix") +
  _ul("Git refuses the same branch in two places — that error makes sense now.") +
  _callout("Why not clone twice?", "A clone re-downloads and needs its own sync; worktrees share objects.", color=GREEN) +
  _practice("git worktree add hotfix-wt", "git worktree list",
            "git -C hotfix-wt status -s", "git -C hotfix-wt log --oneline -2",
            "git merge hotfix-wt", "git worktree remove hotfix-wt")),
{"title": "Bare repos & bundles — git without a server",
 "body": _h3("What 'bare' means") +
  _p("A bare repo has no working tree — just the database. That's why servers hold bare repos: pushes can't clobber a checkout.") +
  _code("$ git init --bare shared.git",
        "$ git remote add shared shared.git && git push -u shared main") +
  _h3("Bundles — history on a USB stick") +
  _code("$ git bundle create feature.bundle main",
        "$ git bundle verify feature.bundle",
        "$ git bundle unbundle feature.bundle   # other side") +
  _practice("git init --bare shared.git", "git remote add shared shared.git",
            "git push -u shared main", "git ls-remote shared",
            "git bundle create all.bundle main", "git bundle verify all.bundle")),
{"title": "Forks, upstreams & contributing to open source",
 "body": _h3("You can't push — good") +
  _p("Fork (your server copy), clone it, add the original as <b>upstream</b>:") +
  _code("git clone https://github.com/you/project.git",
        "git remote add upstream https://github.com/them/project.git",
        "git fetch upstream && git switch -c fix-typo upstream/main",
        "git push -u origin fix-typo     # → open the PR") +
  _h3("Etiquette") +
  _ul("Read CONTRIBUTING.md. Small focused PRs explaining <b>why</b>.",
      "Update PRs with " + _ic("rebase upstream/main") + " (your branch — safe).",
      "After merge: delete branch, sync main with " + _ic("merge --ff-only upstream/main") + ".") +
  _callout("upstream vs origin", "origin = you push here. upstream = fetch-only. Mixing them up is the classic fork mistake.", color=CYAN) +
  _practice("git remote add upstream https://github.com/them/lib.git",
            "git remote -v", "git fetch upstream", "git switch -c fix-typo",
            "touch fix.txt", "git add .", "git commit -m \"docs: fix typo\"",
            "git remote add origin https://github.com/you/lib.git",
            "git push -u origin fix-typo")),
{"title": "Releases, tags & changelogs",
 "body": _h3("Shipping is a naming problem") +
  _p("<b>MAJOR.MINOR.PATCH</b> — breaking.feature.fix. Conventional Commits let tools infer it.") +
  _code("$ git tag -a v2.4.0 -m \"dark mode ships\"",
        "$ git describe / git describe --abbrev=0",
        "$ git log v2.3.0..HEAD --format=\"- %s\"   # your changelog",
        "$ git archive -o release-2.4.0.zip HEAD") +
  _callout("Tag the commit you tested", "Retagging a published release is not free.", color=RED) +
  _practice("git tag -a v1.0.0 -m \"first\"", "echo x > feat.txt", "git add .",
            "git commit -m \"feat: add feat.txt\"", "git describe",
            "git describe --abbrev=0", "git log v1.0.0..HEAD --format=\"- %s\"",
            "git tag -a v1.1.0 -m \"feat\"", "git tag")),
{"title": "Git in CI/CD pipelines",
 "body": _h3("CI is a robot running git") +
  _ul(_ic("clone --depth 1") + " — fast; breaks describe/blame until " + _ic("fetch --unshallow"),
      "Tags trigger deploys — that's why tags should be meaningful.",
      _ic("git describe --tags --always") + " — traceable artifact names",
      "Protected branches = a server-side pre-receive hook.",
      "Merge queues test main+your-PR <i>combined</i> before merging.") +
  _ul("Commits must pass tests alone. No secrets in history (logs are public).") +
  _callout("Reproduce CI locally", "Most “works in CI” bugs: test on " + _ic("git clean -fdx") + "-clean state first.", color=PURPLE) +
  _practice("git fetch --prune", "git describe --tags --always",
            "git archive -o build.zip HEAD", "ls")),
{"title": "Putting it together — a day in the life",
 "body": _h3("Everything, in one loop") +
  _code("git switch main && git pull --ff-only",
        "git switch -c feat/search",
        "git status -s && git add -p && git commit -m \"feat(search): filter\"",
        "git fetch upstream 2>/dev/null; git rebase upstream/main",
        "git push -u origin feat/search        # PR → squash → tag → deploy",
        "git tag -a v3.1.0 -m \"search ships\" && git push --tags") +
  _ul("Small commits → easy reviews → stable main. Read errors. reflog when lost.") +
  _p("You've seen Git from " + _ic("touch") + " to plumbing. Keep breaking the sandbox. 🚀") +
  _practice("git log --oneline --graph --all", "git worktree list", "git tag",
            "git reflog | head -n 5")),
{"title": "Undoing a shipped merge — revert -m",
 "body": _h3("The merge is out. It's bad. Now what?") +
  _p(_ic("git revert -m 1 <merge>") + " — merges have two parents; <b>-m 1</b> keeps parent #1's line (the branch you merged INTO).") +
  _h3("The famous trap") +
  _p("Re-merging the feature later brings <b>nothing</b> — those commits are already in main's history. Only new commits arrive.") +
  _h3("The cure: revert the revert") +
  _code("$ git revert -m 1 a1b2c3d      # undo the merge",
        "# ...fix the feature...",
        "$ git revert e5f6a7b           # undo the undo — path clear",
        "$ git merge feature            # lands normally") +
  _practice("git switch -c feature", "echo shiny > feat.txt", "git add .",
            "git commit -m \"feature\"", "git switch main",
            "git merge --no-ff feature", "git revert -m 1 HEAD", "ls",
            "git revert HEAD", "ls")),
{"title": "Force-pushes done right",
 "body": _h3("When rewriting is legal") +
  _ul("Your own unshared branch — normal.", "Shared branch — dangerous.", "main — coordinated team events only.") +
  _h3("--force vs --force-with-lease") +
  _ul(_ic("--force") + " — server loses whatever it had.",
      _ic("--force-with-lease") + " — overwrites ONLY if the remote is where your last fetch saw it. Otherwise: rejected.") +
  _code("$ git fetch && git push --force-with-lease origin feature",
        "! [rejected] (lease failed — remote moved)",
        "$ git pull --rebase            # fold in their work, retry") +
  _callout("Reflex", _ic("--force-with-lease") + " costs nothing and turns the worst accident into a polite rejection.", color=RED) +
  _practice("git remote add origin https://github.com/you/x.git",
            "git push -u origin main", "git commit --allow-empty -m \"local\"",
            "teammate \"server change\"",
            "git push --force-with-lease origin main",
            "git fetch && git push --force-with-lease origin main")),
{"title": "Guardrails — pre-push hooks & branch protection",
 "body": _h3("Stop bad pushes at the door") +
  _p(_ic(".githooks/pre-push") + " runs before every push; failure blocks it.") +
  _code("$ echo 'test -f VERSION' > .githooks/pre-push",
        "$ git push          # ✖ blocked   → touch VERSION → ✔") +
  _h3("What servers enforce") +
  _ul("<b>Protected branches</b> — no direct pushes; everything via PR.",
      "<b>Required checks</b> — CI must be green to merge.",
      "<b>CODEOWNERS</b> — path→reviewer mapping, auto-requested.",
      "<b>Required signatures</b> — unsigned commits rejected.") +
  _callout("Why local hooks aren't enough", "Anyone can --no-verify. Local hooks protect <i>you</i>; server rules protect the <i>project</i>.", color=CYAN) +
  _practice("echo 'test -f VERSION' > .githooks/pre-push", "git push",
            "echo 1.0.0 > VERSION", "git push", "echo '*  @alice' > CODEOWNERS",
            "git add .", "git commit -m \"docs: ownership\"")),
{"title": "git notes — metadata without rewriting",
 "body": _h3("Annotations that don't change a single hash") +
  _p("Attach facts (ticket IDs, review verdicts) <b>beside</b> a commit — stored in refs/notes/commits:") +
  _code("$ git notes add -m \"Reviewed-by: Ada · JIRA-42\" a1b2c3d",
        "$ git show a1b2c3d        # Notes: section appears",
        "$ git notes list / append -m \"…\" / remove <ref>") +
  _ul("The commit itself untouched — no force-push. Sync notes: " +
      _ic("fetch origin 'refs/notes/*:refs/notes/*'") + ".") +
  _practice("echo hi > f.txt", "git add .", "git commit -m \"one\"",
            "git notes add -m \"JIRA-42\"", "git show", "git notes list",
            "git notes append -m \"more\"", "git show", "git notes remove")),
{"title": "History surgery at scale — filter-repo & BFG",
 "body": _h3("The big red button") +
  _p("Rewrites <i>every</i> commit — scrub leaked secrets, delete a 2 GB folder, rename paths. Every touched commit gets a new hash.") +
  _code("$ git filter-repo --path .env --invert-paths   # delete from all history",
        "$ git filter-repo --path services/api          # keep only this",
        "$ git reflog                                    # old commits linger") +
  _h3("Checklist") +
  _ul("1. Rotate secrets first. 2. Freeze. 3. Rewrite on a fresh clone. 4. " +
      _ic("push --force --all --tags") + ". 5. Everyone re-clones. 6. " + _ic("git gc") + ".") +
  _callout("This sandbox really rewrites the DAG", "Watch hashes change and reflog keep the old world.", color=YELLOW) +
  _practice("echo x > .env", "git add .", "git commit -m \"oops\"",
            "git log --oneline", "git filter-repo --path .env --invert-paths",
            "git log --oneline", "ls", "git reflog | head -n 3")),
{"title": "Git LFS — binaries without the bloat",
 "body": _h3("Why git hates big binaries") +
  _p("Every version of every file forever. 100 MB asset × 50 changes = 5 GB per clone.") +
  _h3("The pointer trick") +
  _code("$ git lfs install && git lfs track \"*.psd\"   # commits .gitattributes",
        "$ git add design.psd && git commit -m \"art\"",
        "$ git show HEAD:design.psd",
        "version https://git-lfs.github.com/spec/v1",
        "oid sha256:...      ← 130 bytes in git; bytes live in LFS",
        "$ git lfs ls-files · git lfs status · git lfs pointer --file f") +
  _ul("Commit the .gitattributes change FIRST. Clones need " + _ic("git lfs install") + ".",
      "Binaries can't merge — use " + _ic("git lfs lock") + " in real life.") +
  _practice("git lfs install", "git lfs track \"*.psd\"", "cat .gitattributes",
            "echo pretend > art.psd", "git add art.psd", "git commit -m \"art\"",
            "git show HEAD:art.psd", "git lfs ls-files")),
{"title": "Stacked PRs — reviewing big features in slices",
 "body": _h3("The 2000-line PR nobody reads") +
  _p("Chain small branches, each on top of the last, each its own PR:") +
  _code("$ git switch -c pr1-schema main      # slice 1",
        "$ git switch -c pr2-api pr1-schema   # slice 2 ON TOP of 1",
        "$ git switch -c pr3-ui pr2-api") +
  _h3("Restacking after review feedback") +
  _code("$ git switch pr1-schema && git commit --amend",
        "$ git switch pr2-api && git rebase pr1-schema",
        "$ git push --force-with-lease origin pr2-api") +
  _ul("Merge bottom-up; when pr1 lands, rebase pr2 onto main — the stack shrinks.",
      "Independent slices? Parallel branches. Dependent slices? Stack.") +
  _callout("The payoff", "Small PRs get reviewed in hours — and bugs surface in the slice that caused them.", color=GREEN) +
  _practice("git switch -c pr1 main", "echo a > s1.txt", "git add .",
            "git commit -m \"slice 1\"", "git switch -c pr2 pr1", "echo b > s2.txt",
            "git add .", "git commit -m \"slice 2\"", "git switch pr1",
            "echo fix >> s1.txt", "git add .", "git commit --amend --no-edit",
            "git switch pr2", "git rebase pr1", "git log --oneline --graph -4")),
{"title": "Pairing on one branch — the multi-party flow",
 "body": _h3("Two people, one feature branch") +
  _code("$ git fetch && git switch -t origin/feature-alice   # join",
        "# ...work, commit...",
        "$ git pull --rebase    # replay onto theirs — stays linear",
        "$ git push") +
  _ul("Teammate pushed? " + _ic("pull --rebase") + ". Rewriting shared history? " +
      _ic("--force-with-lease") + " — and tell them first.",
      "Agree up front: rebase-to-shared (linear) or merge-to-shared (bubbly).") +
  _callout("One owner of truth", "Branch contention is a signal to split the feature — stacked PRs beat tug-of-war.", color=PURPLE) +
  _practice("git remote add origin https://github.com/you/demo.git",
            "git push -u origin main",
            "teammate -b feature-alice \"kicked off\"", "git fetch",
            "git switch -t origin/feature-alice", "echo mine > mine.txt",
            "git add .", "git commit -m \"my part\"",
            "teammate \"more work\"", "git pull --rebase", "git push")),
{"title": "Git archaeology — finding when it broke",
 "body": _h3("You are a detective with excellent tools") +
  _ul(_ic("git log -S \"oldName\" --oneline") + " — follow a rename across time",
      _ic("git blame -L 40,55 f") + " — who owns these lines; list giant reformats in " +
      _ic(".git-blame-ignore-revs") + " or pass " + _ic("--ignore-rev <hash>"),
      _ic("git reflog") + " — what did I <i>do</i>? · " + _ic("git fsck --lost-found") + " — dangling commits",
      _ic("git show 'main@{2.weeks.ago}':file.py") + " — read the past · " + _ic("git bisect") + " — robot binary search") +
  _callout("Write for your future detective", "Atomic commits + why-messages are archaeology tools.", color=PURPLE) +
  _practice("echo \"old()\" > lib.py", "git add .", "git commit -m \"lib v1\"",
            "echo \"new()\" > lib.py", "git add .",
            "git commit -m \"refactor: rename old to new\"",
            "git log -S \"old\" --oneline", "git blame lib.py",
            "git blame --ignore-rev HEAD lib.py")),
{"title": "Git ergonomics — a setup you'll actually keep",
 "body": _h3("Configure once") +
  _code("git config --global pull.rebase true       # linear shared branches",
        "git config --global rerere.enabled true",
        "git config --global push.autoSetupRemote true",
        "git config --global alias.hist \"log --oneline --graph --all\"",
        "git config --global alias.undo \"reset --soft HEAD~1\"",
        "git config --global alias.wip \"!git add -A && git commit -m WIP\"") +
  _h3("Housekeeping cadence") +
  _ul("<b>Never manually</b>: gc, prune. <b>Weekly</b>: fetch --prune, delete merged branches.",
      "<b>Per context</b>: " + _ic("includeIf \"gitdir:~/work/.\"") + " for split identities.",
      "Prompt showing branch + dirty state prevents half of all mistakes.") +
  _callout("The daily 20%", "status · switch -c · add -p · commit · pull --rebase · push · hist · reflog.", color=GREEN) +
  _practice("git config alias.undo \"reset --soft HEAD~1\"",
            "echo x > t.txt", "git add .", "git commit -m \"wip\"",
            "git undo", "git status -s")),
]

# ================================================================= QUIZ ======
QUIZ = [
{"q": "What is Git?", "o": ["A programming language", "A distributed version control system", "A code editor", "A hosting website"], "a": 1,
 "e": "Git is the local version-control tool; GitHub is a hosting service for Git repos."},
{"q": "After  git add app.py , where is app.py?", "o": ["In the repository", "In the staging area (index)", "On the remote", "Nowhere special"], "a": 1,
 "e": "git add copies current content into the staging area, ready to commit."},
{"q": "Which records a snapshot of staged changes?", "o": ["git save -m", "git push", "git commit -m \"msg\"", "git snapshot"], "a": 2,
 "e": "git commit stores the staged content permanently in history."},
{"q": "What does git status tell you?", "o": ["Your Git version", "Branch + staged/modified/untracked", "The remote's state", "Who committed last"], "a": 1,
 "e": "status compares HEAD, the staging area and the working directory."},
{"q": "git branch login  does what?", "o": ["Switches to login", "Creates + switches", "Creates the pointer but stays put", "Merges login"], "a": 2,
 "e": "Then git switch login (or git switch -c login for both)."},
{"q": "Create AND switch in one command?", "o": ["git branch -n", "git switch -c name", "git commit -b name", "git checkout name"], "a": 1,
 "e": "git switch -c name (classic: git checkout -b name)."},
{"q": "What is HEAD?", "o": ["The first commit", "A pointer to your current checkout", "The remote's newest commit", "A conflict marker"], "a": 1,
 "e": "HEAD is “you are here” — usually your current branch."},
{"q": "When does a merge conflict happen?", "o": ["Every merge", "Same lines changed differently on the two branches", "Branch deleted", "Forgot to pull"], "a": 1,
 "e": "Git refuses to guess when both sides edited the same lines."},
{"q": "What does git push do?", "o": ["Downloads commits", "Uploads local commits to the remote", "Creates a branch", "Undoes the last commit"], "a": 1,
 "e": "push uploads; pull downloads and integrates."},
{"q": "Pushed commit needs undoing — safest?", "o": ["git reset --hard HEAD~1", "Delete and re-clone", "git revert <hash>", "git push --force"], "a": 2,
 "e": "revert adds a new undoing commit — history stays intact for everyone."},
{"q": "What does  git stash  do?", "o": ["Deletes untracked files", "Shelves uncommitted changes, cleans the tree", "Commits everything", "Backs up remotely"], "a": 1,
 "e": "stash saves uncommitted work; git stash pop brings it back."},
{"q": "stash pop vs stash apply?", "o": ["None", "pop also deletes the entry after applying", "apply is faster", "pop also pushes"], "a": 1,
 "e": "apply keeps the stash for re-applying elsewhere; pop removes it."},
{"q": "Which creates an annotated tag?", "o": ["git tag -a v1.0 -m \"msg\"", "git tag v1.0 --sign", "git annotate v1.0", "git tag --message"], "a": 0,
 "e": "-a creates a full tag object; plain git tag is lightweight."},
{"q": "The golden rule of rebase?", "o": ["Rebase before every commit", "Never rebase commits others may have", "Only rebase main", "Rebase instead of every merge"], "a": 1,
 "e": "Rebasing rewrites hashes — shared history would break everyone's clones."},
{"q": "git cherry-pick <hash> does what?", "o": ["Moves (deletes) the commit", "Copies it as a new commit onto your branch", "Picks the biggest commit", "Merges branches"], "a": 1,
 "e": "Applies that single commit's change on top of HEAD (new hash)."},
{"q": "You ran git reset --hard HEAD~1 by mistake. First move?", "o": ["git push --force", "git reflog → reset back", "Delete the repo", "git revert --all"], "a": 1,
 "e": "The reflog remembers where HEAD was — recovery for ~90 days."},
{"q": "What does git bisect do?", "o": ["Splits branches", "Binary-searches commits to find a bug's origin", "Checks out everything", "Finds large files"], "a": 1,
 "e": "Mark good/bad; each mark halves the search space."},
{"q": "What does  git clean -n  do?", "o": ["Deletes untracked files", "Dry run — lists what would go", "Cleans the reflog", "Nothing"], "a": 1,
 "e": "-n previews; -f deletes; -x includes ignored files."},
{"q": "Create the alias  git st  for status?", "o": ["git alias st status", "git config --global alias.st status", "git shortcut st=status", "git config alias.st = status"], "a": 1,
 "e": "Aliases live in config."},
{"q": "git fetch vs git pull?", "o": ["Identical", "fetch downloads only; pull = fetch + merge into your branch", "pull downloads only", "fetch pushes first"], "a": 1,
 "e": "fetch is look-don't-touch; pull integrates immediately."},
{"q": "Which log flag finds commits changing a string's occurrences?", "o": ["--grep", "-S (pickaxe)", "--find", "-s"], "a": 1,
 "e": "git log -S \"name\" — the pickaxe."},
{"q": "git commit --amend …", "o": ["Adds a fixup commit", "Replaces the last commit (new hash!)", "Only fixes messages", "Edits any commit"], "a": 1,
 "e": "amend rewrites the last commit — fine unpushed, forbidden shared."},
{"q": "What does the pipe | do?", "o": ["Parallel execution", "Left command's stdout → right command's stdin", "Comments the line", "Saves to a file"], "a": 1,
 "e": "Pipes chain tools: each stage transforms the previous output."},
{"q": "git log --oneline | head -n 3 shows…", "o": ["3 oldest", "3 newest (log prints newest first)", "3 repos", "An error"], "a": 1,
 "e": "log lists newest-first; head keeps the first 3 lines."},
{"q": "sort f | uniq -c outputs…", "o": ["Sorted lines + duplicate counts", "Only duplicates", "Reversed lines", "A checksum"], "a": 0,
 "e": "uniq merges only ADJACENT duplicates — sort groups them first."},
{"q": "git commit -am differs from -m because -a also…", "o": ["Pushes", "Stages modifications of tracked files", "Adds untracked files", "Amends"], "a": 1,
 "e": "-a stages tracked-file edits/deletions; new files still need git add."},
{"q": "git rev-parse HEAD prints…", "o": ["The branch name", "The commit hash HEAD points to", "The last diff", "The remote URL"], "a": 1,
 "e": "rev-parse translates any ref to the raw hash."},
{"q": "git merge-base A B finds…", "o": ["The newest commit", "The best common ancestor — divergence point", "The merge commit", "A conflict"], "a": 1,
 "e": "Three-way merges compute from this point."},
{"q": "In a shell, $? holds…", "o": ["The cwd", "The last command's exit status (0=ok)", "Job count", "The shell PID"], "a": 1,
 "e": "Scripts branch on it constantly."},
{"q": "cat list.txt | xargs rm does…", "o": ["Prints then deletes list.txt", "Runs rm with each word from list.txt as an argument", "Removes blank lines", "Nothing"], "a": 1,
 "e": "xargs converts stdin into command-line arguments."},
{"q": "git add . && git commit — if git add fails?", "o": ["Commits anyway", "Skips the commit — && continues only on success", "Retries", "Asks"], "a": 1,
 "e": "&& short-circuits on failure."},
{"q": "echo \"on $(git branch --show-current)\" will…", "o": ["Print literally", "Substitute the command's output into the string", "Fail", "Create a file"], "a": 1,
 "e": "$( ) is command substitution."},
{"q": "git am vs git apply?", "o": ["None", "am creates commits preserving author/message; apply only edits files", "apply is for remotes", "am is for binaries"], "a": 1,
 "e": "am = apply + commit (the mailbox workflow)."},
{"q": "Why --fixup=<ref> before rebase -i --autosquash?", "o": ["Faster to type", "The fixup auto-moves next to <ref> and folds in during the rebase", "It signs", "Auto-fixes bugs"], "a": 1,
 "e": "--autosquash reorders the todo and squashes into the target."},
{"q": "Signing a commit with GPG proves…", "o": ["It compiles", "The holder of the private key made it", "The code is safe", "The email exists"], "a": 1,
 "e": "Key control — authorship and integrity, not quality."},
{"q": "Skip hooks for one commit?", "o": ["git commit --skip", "git commit --no-verify", "git commit -f", "Impossible"], "a": 1,
 "e": "--no-verify (-n) skips pre-commit/commit-msg once."},
{"q": "What does git rerere do?", "o": ["Auto-reverts merges", "Records conflict resolutions and re-applies them to identical conflicts", "Reruns tests", "Refreshes refs"], "a": 1,
 "e": "Reuse recorded resolution — a time-saver on long-lived branches."},
{"q": "A parent repo stores about a submodule…", "o": ["Full history copy", "Path, URL and one pinned commit", "Latest branch name", "Only the URL"], "a": 1,
 "e": "That's why submodules are called 'pinned'."},
{"q": "“Squash and merge” on a 10-commit PR yields…", "o": ["10 commits as-is", "One new commit; originals discarded", "A 11-parent merge", "A tag"], "a": 1,
 "e": "ONE new commit summarizing the PR — great for messy branches."},
{"q": "In  @@ -12,7 +12,9 @@  the 7 means…", "o": ["7 added lines", "Old hunk covers 7 lines starting at line 12", "7 conflicts", "Line 7"], "a": 1,
 "e": "Format: -oldStart,oldCount +newStart,newCount."},
{"q": "Git refuses a branch checked out in two worktrees because…", "o": ["Worktrees are read-only", "Two checkouts moving one pointer could lose commits", "Branches live in the main tree", "It's just a warning"], "a": 1,
 "e": "One branch = one movable pointer; real git refuses."},
{"q": "git merge --allow-unrelated-histories is for…", "o": ["Every merge", "Histories sharing no common ancestor", "Only conflicts", "Never"], "a": 1,
 "e": "Like merging an orphan gh-pages branch."},
{"q": "In git add -p, answering  n …", "o": ["Deletes the hunk", "Leaves it unstaged in the working tree", "Commits the others", "Reverts the file"], "a": 1,
 "e": "Staging is selective; skipped hunks remain for later."},
{"q": "Why do servers store bare repos?", "o": ["Smaller", "No working tree → pushes can't clobber a checkout", "Better compression", "Marketing"], "a": 1,
 "e": "Just the object database — nothing to corrupt."},
{"q": "git revert -m 1 <merge> means…", "o": ["Revert the repo's first commit", "Undo the merge keeping parent #1's line", "Keep parent #2", "Re-merge"], "a": 1,
 "e": "-m picks which parent's side is kept — usually the branch you merged into."},
{"q": "After reverting a merge, re-merging the branch…", "o": ["Brings everything back", "Brings only NEW commits until you revert the revert", "Fails", "Deletes the branch"], "a": 1,
 "e": "Old commits are already in history — revert the revert to re-land."},
{"q": "--force-with-lease differs from --force: it…", "o": ["Is faster", "Refuses if the remote moved since your last fetch", "Also pushes tags", "Backs up"], "a": 1,
 "e": "It checks your fetched view against the real remote."},
{"q": "An LFS repo stores for a tracked video…", "o": ["The compressed video", "A small text pointer (version, sha256, size)", "Zip of frames", "Nothing"], "a": 1,
 "e": "Repo stays tiny; bytes download from LFS storage."},
{"q": "After filter-repo rewrites history, the OLD commits…", "o": ["Vanish instantly", "Linger until gc — reflog can restore them", "Move to origin", "Become tags"], "a": 1,
 "e": "Refs repointed; unreferenced objects wait for gc — your undo window."},
]

# ============================================================ CHEAT SHEET ====
CHEAT_SECTIONS = [
("Setup", [("git config --global user.name \"Name\"", "set your name"),
           ("git config --global user.email me@mail.com", "set your email"),
           ("git config --list", "show settings")]),
("Start", [("git init", "create a repo here"),
           ("git clone <url>", "copy a remote repo")]),
("Stage & commit", [("git status [-s]", "what changed?"),
                    ("git add <f> | . | -p", "stage (interactive with -p)"),
                    ("git commit -m \"msg\" | -am | --amend", "snapshot"),
                    ("git rm [--cached] f / git mv a b", "remove / move tracked")]),
("Inspect", [("git log --oneline --graph --all", "compact history"),
             ("git log -S \"str\" / --grep= / -n 5", "pickaxe & filters"),
             ("git diff [--staged] [-w] [--word-diff] [-U<n>]", "compare"),
             ("git show <ref>[:file] / git blame -L a,b f", "details")]),
("Branch & merge", [("git switch -c name / - / -t origin/b", "move"),
                    ("git merge <b> [--no-ff|--squash|--ff-only]", "merge"),
                    ("git rebase <b> | -i HEAD~n | --onto", "replay"),
                    ("git branch -d name / -m new / -vv", "manage")]),
("Undo", [("git restore [--staged] <f>", "discard / unstage"),
          ("git reset --soft|--mixed|--hard HEAD~1", "uncommit"),
          ("git revert <hash> / -m 1 <merge>", "safe undo"),
          ("git reflog", "the safety net"),
          ("git clean -n/-f/-x", "purge untracked")]),
("Remote", [("git remote add/-v/rename/remove", "manage"),
            ("git push -u origin b / --tags / --force-with-lease", "upload"),
            ("git fetch [--prune] / git pull [--rebase]", "download"),
            ("git ls-remote / git remote show origin", "inspect")]),
("Shelve & tag", [("git stash [-u] [pop|apply|list|branch]", "shelve work"),
                  ("git tag -a v1.0 -m \"rel\" / -l / -d / --contains", "tag")]),
("History surgery", [("git cherry-pick [-x] <h> | A..B", "copy commits"),
                     ("git commit --fixup=<ref> + rebase -i --autosquash", "tidy later"),
                     ("git filter-repo --path f --invert-paths", "scrub history ⚠"),
                     ("git notes add -m \"x\" <ref>", "attach metadata"),
                     ("git blame --ignore-rev <h> · .git-blame-ignore-revs", "blame hygiene")]),
("Plumbing", [("git rev-parse HEAD | --abbrev-ref HEAD", "resolve refs"),
              ("git cat-file -p|-t <ref>:<f>", "read objects"),
              ("git hash-object f", "real sha1"),
              ("git merge-base A B / for-each-ref / ls-tree", "more plumbing"),
              ("git format-patch -1 · apply --check · am f.patch", "email flow")]),
("Automation & big files", [(".githooks/pre-commit · pre-push", "gates (exit≠0 blocks)"),
                            ("git rerere [status|clear]", "conflict memory"),
                            ("git lfs track \"*.psd\" · ls-files", "big files"),
                            ("git worktree add <path> · git -C <path> …", "two checkouts"),
                            ("git init --bare x.git · git bundle create f <ref>", "server-less")]),
("Terminal", [("cd · pwd · mkdir -p · cp -r · mv · tree · ls -la", "filesystem"),
              ("cat · head · tail · wc · less · grep -rn · find -name", "read & search"),
              ("a && b · a || b · a ; b · $(cmd) · cmd > f · cmd | f", "compose"),
              ("export V=x · echo $? · !! · sh script.sh", "shell"),
              ("sort | uniq -c | cut -d, -f2 | sed s/a/b/g | tr a-z A-Z", "text tools"),
              ("Tab · ↑↓ · Ctrl+R · Ctrl+L · man git-x", "this terminal")]),
]

def _cheat_html():
    parts = [WRAP_OPEN, "<h2 style='color:" + ACCENT + ";'>Git Cheat Sheet</h2>"]
    for title, rows in CHEAT_SECTIONS:
        parts.append("<h3 style='color:" + PURPLE + ";'>" + title + "</h3>")
        parts.append("<table width='100%' cellspacing='0' cellpadding='4'>")
        for cmd, desc in rows:
            parts.append("<tr><td width='48%'>" + _ic(cmd) +
                         "</td><td style='color:" + MUTED + ";'>" + desc + "</td></tr>")
        parts.append("</table>")
    parts.append(WRAP_CLOSE)
    return "".join(parts)

# ====================================================== the simulated git ====
class Commit:
    _seq = 0
    def __init__(self, message, parents, tree, branch):
        self.message, self.parents = message, list(parents)
        self.tree, self.branch = dict(tree), branch
        Commit._seq += 1
        self.seq = Commit._seq
        self.hash = "".join(random.choice("0123456789abcdef") for _ in range(7))
        self.date = time.time()
        self.author = "You"

class SimRepo:
    GIT_FORTUNES = ["commit early, commit often", "a branch is a sticky note",
                    "HEAD is you; origin/main is everyone else",
                    "when lost: git reflog", "rebase your own work, merge theirs"]

    def __init__(self):
        self.reset()

    def reset(self):
        self.initialized = False
        self.working, self.index = {}, {}
        self.commits, self.branches = {}, {}
        self.current, self.head = None, None
        self.detached = False
        self.merge_state = None
        self.stash, self.tags = [], {}
        self.reflog, self.rebase_state, self.bisect = [], None, None
        self.aliases, self.shell_aliases = {}, {}
        self.user_name, self.user_email = "You", "you@example.com"
        self.cwd, self.dirs = [], set()
        self.history, self._stdin = [], None
        self.prev_branch = None
        self.squash_pending = None
        self.remotes = {}
        self.remote_branches, self.remote_tags = {}, {}
        self.rt, self.tracking = {}, {}
        self.env = {"HOME": "~/project", "SHELL": "/bin/gitlearn",
                    "USER": "sandbox-user", "EDITOR": "none", "PATH": "/usr/bin:/bin"}
        self.last_status = 0
        self._status_forced = None
        self.orig_head = self.fetch_head = None
        self.dirstack = []
        self._sh_depth = 0
        self._in_script = False
        self.rerere = {}
        self.submodules = {}
        self.hooks_path = ".githooks"
        self.worktrees = {}
        self._addp_state = None
        self.au_files, self.sw_files = set(), set()
        self._main_current = self._wt_context = None
        self.notes = {}
        self.lfs_patterns = set()

    # ---------------- small helpers ----------------
    def _guard(self):
        if not self.initialized:
            return [("fatal: not a git repository (run 'git init' first)", "err")]
        return None
    def _new_commit(self, message, parents, tree, author=None):
        c = Commit(message, parents, tree, self.current)
        c.author = author or self.user_name
        while c.hash in self.commits:
            c.hash = "".join(random.choice("0123456789abcdef") for _ in range(7))
        self.commits[c.hash] = c
        self._reflog(c.hash, "commit", c.message.splitlines()[0])
        return c
    def _reflog(self, h, op, s=""):
        self.reflog.append((h, op, s))
    def head_tree(self):
        return dict(self.commits[self.head].tree) if self.head else {}
    def _ancestors(self, h):
        seen, stack = set(), [h]
        while stack:
            x = stack.pop()
            if x in seen: continue
            seen.add(x)
            stack.extend(self.commits[x].parents)
        return seen
    def _merge_base(self, a, b):
        common = self._ancestors(a) & self._ancestors(b)
        return max(common, key=lambda h: self.commits[h].seq) if common else None
    def _clean_for_switch(self):
        head = self.head_tree()
        if self.index != head: return False
        for f, w in self.working.items():
            if f in self.sw_files: continue
            if f not in self.index and f not in head: continue
            if w != self.index.get(f): return False
        return all(f in self.working for f in self.index)
    def _resolve_ref(self, token):
        if token is None: return None
        t = str(token).strip()
        if t == "@": t = "HEAD"
        m = re.match(r'^(.*)@\{(\d+)\}$', t)
        if m:
            n = int(m.group(2))
            if m.group(1) in ("", "HEAD") and n < len(self.reflog):
                return self.reflog[-1 - n][0]
            return None
        base, steps = t, 0
        m = re.match(r'^(.+?)(~|\^)(\d+)$', t)
        if m: base, steps = m.group(1), int(m.group(3))
        elif t.endswith(("~", "^")): base, steps = t[:-1], 1
        if base == "HEAD": h = self.head
        elif base == "ORIG_HEAD": h = self.orig_head
        elif base == "FETCH_HEAD": h = self.fetch_head
        elif base == "MERGE_HEAD": h = self.merge_state["head"] if self.merge_state else None
        elif base in self.branches: h = self.branches[base]
        elif base in self.rt: return self.rt[base]
        elif base in self.tags: h = self.tags[base][0]
        else:
            hits = [c for c in self.commits if c.startswith(base)] if base else []
            if len(hits) == 1: h = hits[0]
            elif len(hits) > 1: return "ambiguous"
            else: return None
        for _ in range(steps):
            c = self.commits.get(h)
            if not c or not c.parents: return None
            h = c.parents[0]
        return h
    @staticmethod
    def _parse_since(s):
        m = re.match(r'^(\d+)\.(\w+)\.ago$', s.strip())
        if not m: return None
        mult = {"second": 1, "seconds": 1, "minute": 60, "minutes": 60, "hour": 3600,
                "hours": 3600, "day": 86400, "days": 86400, "week": 604800,
                "weeks": 604800, "month": 2592000, "months": 2592000}
        u = m.group(2).lower()
        return time.time() - int(m.group(1)) * mult[u] if u in mult else None
    @staticmethod
    def _ago(ts):
        d = int(time.time() - ts)
        if d < 5: return "just now"
        if d < 60: return str(d) + " seconds ago"
        if d < 3600: return str(d // 60) + " minutes ago"
        if d < 86400: return str(d // 3600) + " hours ago"
        return str(d // 86400) + " days ago"
    # ------------- filesystem / ignore / attrs / lfs -------------
    def _pwd_str(self):
        return "~/project" + (("/" + "/".join(self.cwd)) if self.cwd else "")
    def _resolve_path(self, arg):
        parts = [] if str(arg).startswith("/") else list(self.cwd)
        for seg in str(arg).replace("\\", "/").split("/"):
            if seg in ("", "."): continue
            if seg == "..":
                if parts: parts.pop()
                continue
            parts.append(seg)
        return "/".join(parts)
    def _ensure_parent(self, key):
        parts = key.split("/")[:-1]
        for i in range(len(parts)):
            self.dirs.add("/".join(parts[:i + 1]))
    def _is_dir(self, key):
        return key == "" or key in self.dirs or \
               any(f.startswith(key + "/") for f in self.working)
    def _ignore_patterns(self):
        pats = []
        for line in self.working.get(".gitignore", "").splitlines():
            line = line.strip()
            if line and not line.startswith(("#", "!")):
                pats.append(line.rstrip("/"))
        return pats
    def _is_ignored(self, name):
        return any(fnmatch.fnmatch(name, p) or name.startswith(p + "/")
                   for p in self._ignore_patterns())
    def _attrs(self):
        rules = []
        for raw in self.working.get(".gitattributes", "").splitlines():
            line = raw.split("#")[0].strip()
            if not line: continue
            parts = line.split()
            attrs = {}
            for a in parts[1:]:
                if "=" in a:
                    k, v = a.split("=", 1); attrs[k] = v
                elif a.startswith("-"): attrs[a[1:]] = False
                else: attrs[a] = True
            rules.append((parts[0], attrs))
        return rules
    def _attr_for(self, path, name):
        base = path.rsplit("/", 1)[-1]
        for pat, attrs in self._attrs():
            if fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(base, pat):
                if name in attrs: return attrs[name]
        return None
    def _needs_norm(self, f):
        if "\r" not in self.working.get(f, ""): return False
        t = self._attr_for(f, "text")
        return t is True or t == "auto" or self._attr_for(f, "eol") == "lf"
    def _lfs_match(self, f):
        base = f.rsplit("/", 1)[-1]
        return any(fnmatch.fnmatch(f, p) or fnmatch.fnmatch(base, p)
                   for p in self.lfs_patterns)
    def _lfs_pointer(self, data):
        b = data.encode()
        return ("version https://git-lfs.github.com/spec/v1\noid sha256:" +
                hashlib.sha256(b).hexdigest() + "\nsize " + str(len(b)) + "\n")
    def _blob_sha(self, data):
        return hashlib.sha1(b"blob " + str(len(data.encode())).encode() +
                            b"\x00" + data.encode()).hexdigest()
    # ------------- diff machinery -------------
    def _diff_lines(self, old_map, new_map, stat=False, patch=True, ws=True, prefix=""):
        files = ins = dele = 0
        lines = []
        def norm(s): return re.sub(r"\s+", " ", (s or "")).strip()
        for f in sorted(set(old_map) | set(new_map)):
            old, new = old_map.get(f), new_map.get(f)
            if old == new or (not ws and norm(old) == norm(new)): continue
            files += 1
            d = list(difflib.unified_diff((old or "").splitlines(),
                                          (new or "").splitlines(), lineterm=""))
            adds = sum(1 for l in d if l.startswith("+") and not l.startswith("+++"))
            dels = sum(1 for l in d if l.startswith("-") and not l.startswith("---"))
            ins += adds; dele += dels
            lines.append((prefix + "diff --git a/" + f + " b/" + f, "info"))
            if stat:
                lines.append((prefix + " " + f + " | " + str(adds + dels) + " " +
                              "+" * adds + "-" * dels, "out")); continue
            if patch:
                for l in d:
                    if l.startswith(("---", "+++")): continue
                    kind = ("info" if l.startswith("@@") else
                            "add" if l.startswith("+") else
                            "del" if l.startswith("-") else "out")
                    lines.append((prefix + l, kind))
        if files:
            lines.append((prefix + " " + str(files) + " file(s) changed, " +
                          str(ins) + " insertion(s), " + str(dele) + " deletion(s)", "ok"))
        return lines
    def _hunks_for(self, old, new, n=3):
        a = (old or "").splitlines(); b = (new or "").splitlines()
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        ops = [o for o in sm.get_opcodes() if o[0] != "equal"]
        if not ops: return []
        groups = []
        for op in ops:
            if groups and op[1] - groups[-1][-1][2] <= 2 * n: groups[-1].append(op)
            else: groups.append([op])
        out = []
        for g in groups:
            i1 = max(g[0][1] - n, 0); i2 = min(g[-1][2] + n, len(a))
            j1 = max(g[0][3] - n, 0)
            lines, ai = [], i1
            for (tag, x1, x2, y1, y2) in g:
                while ai < x1:
                    lines.append((" ", a[ai])); ai += 1
                for l in a[x1:x2]: lines.append(("-", l))
                for l in b[y1:y2]: lines.append(("+", l))
                ai = x2
            while ai < i2:
                lines.append((" ", a[ai])); ai += 1
            adds = len([1 for t, _l in lines if t == "+"])
            out.append({"header": "@@ -" + str(i1 + 1) + "," + str(i2 - i1) +
                        " +" + str(j1 + 1) + "," + str(i2 - i1 + adds) + " @@",
                        "lines": lines})
        return out
    def _wordify(self, lines):
        dels = [l for t, l in lines if t == "-"]
        adds = [l for t, l in lines if t == "+"]
        sm = difflib.SequenceMatcher(None, dels, adds)
        out = []
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "equal": out.append(dels[i1])
            else:
                if i1 < i2: out.append("[-" + " ".join(dels[i1:i2]) + "-]")
                if j1 < j2: out.append("[+" + " ".join(adds[j1:j2]) + "+]")
        return " ".join(x for x in out if x)
    def _render_graph(self, picked, refmap):
        lanes, out = [], []
        for h in picked:
            c = self.commits[h]
            if h not in lanes: lanes.append(h)
            col = lanes.index(h)
            row = ["|"] * len(lanes)
            row[col] = "*"
            if c.parents:
                p0 = c.parents[0]
                if p0 in lanes and lanes.index(p0) != col: del lanes[col]
                else: lanes[col] = p0
                for p in c.parents[1:]:
                    if p not in lanes:
                        lanes.append(p); row.append("\\")
            else: del lanes[col]
            refs = refmap.get(h, "")
            out.append("".join(row) + ((" " + refs) if refs else "") + " " +
                       c.hash[:7] + " " + c.message.splitlines()[0])
        return [(l, "out") for l in out]
    # ------------- hooks / rerere -------------
    def _hook_path(self, name):
        return (self.hooks_path or ".githooks").rstrip("/") + "/" + name
    def _run_hook(self, name):
        key = self._hook_path(name)
        if key not in self.working: return True, []
        out = [("🪝 running " + name + " hook…", "info")]
        for raw in self.working[key].splitlines():
            line = raw.strip()
            if not line or line.startswith("#"): continue
            self._exec_segment(line)
            if self.last_status != 0: return False, out
        return True, out
    @staticmethod
    def _rerere_sig(text):
        norm = []
        for l in text.splitlines():
            if l.startswith("<<<<<<<"): norm.append("<<<")
            elif l.startswith(">>>>>>>"): norm.append(">>>")
            else: norm.append(l)
        return "\n".join(norm)
    def _rerere_autostep(self):
        applied = []
        ms = self.merge_state
        if ms:
            for f in list(ms.get("conflicts", [])):
                cur = self.working.get(f, "")
                sig = self._rerere_sig(cur)
                if "<<<<<<<" in cur and sig in self.rerere:
                    res = self.rerere[sig]
                    self.working[f] = res; self.index[f] = res
                    ms["conflicts"].remove(f)
                    applied.append(f)
        return applied
    # ------------- stash/todo utils -------------
    def _stash_index(self, tok):
        m = re.match(r'stash@\{(\d+)\}$', str(tok))
        if m: return int(m.group(1))
        return int(tok) if str(tok).isdigit() else None
    def _print_todo(self):
        out = [("todo:", "info")]
        for i, (action, h, msg) in enumerate(self.rebase_state["todo"], 1):
            out.append((str(i) + ". " + action.ljust(7) + h[:7] + " " +
                        (msg.splitlines()[0] if msg else ""), "out"))
        return out
    def _todo_edit(self, tokens):
        st = self.rebase_state
        if not st:
            return [("'" + tokens[0] + "' only works during an interactive rebase", "warn"),
                    ("start one with: git rebase -i HEAD~2", "out")]
        action = tokens[0]
        try: n = int(tokens[1])
        except (IndexError, ValueError):
            return [("usage: " + action + " <n>" +
                     (" <new message>" if action == "reword" else ""), "err")]
        if not 1 <= n <= len(st["todo"]):
            return [("no commit number " + str(n), "err")]
        entry = st["todo"][n - 1]
        if action in ("squash", "fixup") and n == 1:
            return [("can't fold commit 1 — it has nothing above it", "err")]
        if action == "reword":
            if len(tokens) < 3: return [("usage: reword <n> <new message>", "err")]
            entry[0], entry[2] = "reword", " ".join(tokens[2:])
        else: entry[0] = action
        return [("todo updated ✔", "ok")] + self._print_todo()
    def _resolve(self, args):
        pre = None
        f = args[0] if args else None
        if f and f in self.working and "<<<<<<<" in self.working[f]:
            pre = self._rerere_sig(self.working[f])
        out = self._resolve_impl(args)
        if pre is not None and self.merge_state and \
                f in self.merge_state.get("conflicts", []) and \
                not any(k == "err" for _t, k in out):
            self.rerere[pre] = self.index.get(f, self.working.get(f, ""))
            out.append(("📝 rerere recorded this resolution — identical future "
                        "conflicts auto-resolve", "info"))
        return out
    def _resolve_impl(self, args):
        if not self.merge_state:
            return [("nothing to resolve — no merge in progress", "warn")]
        if len(args) < 2 or args[1] not in ("ours", "theirs"):
            return [("usage: resolve <file> ours|theirs", "err")]
        f, side = args[0], args[1]
        if f not in self.merge_state["conflicts"]:
            return [("'" + f + "' is not conflicted", "warn")]
        content = (self.index.get(f, "") if side == "ours"
                   else self.merge_state["theirs"].get(f, ""))
        self.working[f] = self.index[f] = content
        return [("resolved '" + f + "' using " + side + " (staged ✔)", "ok"),
                ("finish with: git commit", "out")]
    # ------------- pipeline / shell engine -------------
    @staticmethod
    def _split_unquoted(line, sep):
        parts, cur, q = [], "", None
        for ch in line:
            if q:
                cur += ch
                if ch == q: q = None
            elif ch in "\"'": q = ch; cur += ch
            elif ch == sep: parts.append(cur); cur = ""
            else: cur += ch
        parts.append(cur)
        return parts
    @staticmethod
    def _find_redirect(line):
        q = None
        for i, ch in enumerate(line):
            if q:
                if ch == q: q = None
            elif ch in "\"'": q = ch
            elif ch == ">":
                op = ">>" if line[i:i + 2] == ">>" else ">"
                rest = line[i + len(op):].strip().split()
                return line[:i].rstrip(), op, (rest[0] if rest else "")
        return line, None, None
    def _input_lines(self, args):
        files = [a for a in args if not a.startswith("-")]
        if files:
            key = self._resolve_path(files[0])
            if key not in self.working: return None
            return self.working[key].splitlines() or [""]
        return list(self._stdin) if self._stdin is not None else None
    @staticmethod
    def _history_expand_impl(line, history):
        if "!" not in line: return line, []
        warns, out, i, q = [], [], 0, None
        n = len(line)
        while i < n:
            ch = line[i]
            if q:
                out.append(ch)
                if ch == q: q = None
                i += 1; continue
            if ch in "\"'":
                q = ch; out.append(ch); i += 1; continue
            if ch == "!" and i + 1 < n and line[i + 1] in "!$":
                prev = history[-1] if history else ""
                if not prev:
                    warns.append(("bash: !: no previous command yet", "warn")); i += 2; continue
                if line[i + 1] == "!": out.append(prev)
                else:
                    toks = prev.split()
                    out.append(toks[-1] if toks else "")
                i += 2; continue
            out.append(ch); i += 1
        return "".join(out), warns
    def _cmd_subst(self, line):
        for _ in range(10):
            pos, q, i = None, None, 0
            while i < len(line) - 1:
                ch = line[i]
                if q:
                    if ch == q: q = None
                    i += 1; continue
                if ch == "'": q = ch; i += 1; continue
                if ch == "$" and line[i + 1] == "(": pos = i; break
                i += 1
            if pos is None: return line
            depth, end = 0, None
            for k in range(pos + 1, len(line)):
                if line[k] == "(": depth += 1
                elif line[k] == ")":
                    depth -= 1
                    if depth == 0: end = k; break
            if end is None: return line
            inner = line[pos + 2:end]
            _all, last = self._chained_run(inner)
            text = " ".join(t for t, k in last
                            if k in ("out", "info", "ok", "add", "del"))
            line = line[:pos] + text.strip() + line[end + 1:]
        return line
    def _expand_vars(self, line):
        env = dict(self.env)
        env["?"] = str(self.last_status); env["$"] = "1337"
        env["PWD"] = self._pwd_str()
        out, i, q = [], 0, None
        while i < len(line):
            ch = line[i]
            if q == "'":
                out.append(ch)
                if ch == "'": q = None
                i += 1; continue
            if ch in "\"'":
                if q is None: q = ch
                elif q == ch: q = None
                out.append(ch); i += 1; continue
            if ch == "$":
                m = re.match(r'\$\{(\w+)\}', line[i:]) or \
                    re.match(r'\$([A-Za-z_]\w*|\?|\$|\d)', line[i:])
                if m:
                    out.append(env.get(m.group(1), "")); i += len(m.group(0)); continue
            out.append(ch); i += 1
        return "".join(out)
    @staticmethod
    def _split_chained(line):
        segs, cur, q, i = [], "", None, 0
        n = len(line)
        while i < n:
            ch = line[i]
            if q:
                cur += ch
                if ch == q: q = None
                i += 1; continue
            if ch in "\"'":
                q = ch; cur += ch; i += 1; continue
            if ch == "$" and i + 1 < n and line[i + 1] == "(":
                depth, j = 0, i + 1
                while j < n:
                    if line[j] == "(": depth += 1
                    elif line[j] == ")":
                        depth -= 1
                        if depth == 0: break
                    j += 1
                cur += line[i:j + 1]; i = j + 1; continue
            if line[i:i + 2] == "&&":
                segs.append((cur.strip(), "&&")); cur = ""; i += 2; continue
            if line[i:i + 2] == "||":
                segs.append((cur.strip(), "||")); cur = ""; i += 2; continue
            if ch == ";":
                segs.append((cur.strip(), ";")); cur = ""; i += 1; continue
            if ch == "&":
                segs.append((cur.strip(), "syntax")); cur = ""; i += 1; continue
            cur += ch; i += 1
        segs.append((cur.strip(), None))
        return segs
    def _exec_segment(self, seg):
        self._status_forced = None
        timed = False
        if seg.startswith("time "):
            timed = True; seg = seg[5:].strip()
        body, op, target = self._find_redirect(seg)
        if op:
            target = target.strip().strip('"').strip("'")
            if not target: return [("syntax error near unexpected redirect", "err")]
        try: out = self._pipeline(body.strip())
        except Exception as exc: out = [("sandbox error: " + str(exc), "err")]
        self.last_status = self._status_forced if self._status_forced is not None \
            else (1 if (out and out[-1][1] == "err") else 0)
        if op:
            if target == "/dev/null": return []
            key = self._resolve_path(target)
            self._ensure_parent(key)
            text = "\n".join(t for t, _k in out) + "\n"
            self.working[key] = (self.working.get(key, "") + text) if op == ">>" else text
            return []
        if timed:
            out = out + [("", "out"), ("real    0m0.0" + str(random.randint(1, 9)) +
                          "s   (sandbox time flies ⏱)", "warn")]
        return out
    def _chained_run(self, line):
        segs = self._split_chained(line)
        all_out, last, pending = [], [], None
        for seg, op in segs:
            if pending == "&&" and self.last_status != 0: pass
            elif pending == "||" and self.last_status == 0: pass
            else:
                last = self._exec_segment(seg); all_out += last
            pending = op
        return all_out, last
    def run(self, line):
        line = line.strip()
        if not line: return []
        line, warns = self._history_expand_impl(line, self.history)
        if not self._in_script: self.history.append(line)
        line = self._cmd_subst(line)
        line = self._expand_vars(line)
        segs = self._split_chained(line)
        if any(op == "syntax" for _s, op in segs):
            return warns + [("syntax: stray '&' — background jobs aren't supported", "err")]
        if any(not s for s, _op in segs[:-1]):
            return warns + [("syntax error near '&&' or ';'", "err")]
        out, pending = list(warns), None
        for seg, op in segs:
            if pending == "&&" and self.last_status != 0: pass
            elif pending == "||" and self.last_status == 0: pass
            else: out += self._exec_segment(seg)
            pending = op
        return out
    def _pipeline(self, body):
        stages = [s.strip() for s in self._split_unquoted(body, "|")]
        results, stdin = [], None
        try:
            for s in stages:
                if not s: return [("syntax error near '|'", "err")]
                self._stdin = stdin
                try: tokens = shlex.split(s)
                except ValueError: tokens = s.split()
                hops = 0
                while tokens and tokens[0] in self.shell_aliases and hops < 5:
                    try: exp = shlex.split(self.shell_aliases[tokens[0]])
                    except ValueError: exp = self.shell_aliases[tokens[0]].split()
                    tokens = exp + tokens[1:]; hops += 1
                cmd = tokens[0]
                if getattr(self, "_addp_state", None) and cmd in ("y", "n", "a", "q", "s"):
                    results = self._addp_answer(cmd)
                elif cmd == "git":
                    args = tokens[1:]; gh = 0
                    while args and args[0] in self.aliases and gh < 5:
                        try: inner = shlex.split(self.aliases[args[0]])
                        except ValueError: inner = self.aliases[args[0]].split()
                        args = inner + args[1:]; gh += 1
                    results = self._git(args)
                elif cmd in ("pick", "drop", "squash", "fixup", "reword"):
                    results = self._todo_edit(tokens)
                else:
                    h = self._simple_map().get(cmd)
                    results = h(tokens[1:]) if h else \
                        [(cmd + ": command not found (try 'help')", "err")]
                stdin = [t for t, k in results if k in ("out", "info", "ok", "add", "del")]
        finally:
            self._stdin = None
        return results
    def _simple_map(self):
        m = {
            "touch": self._touch, "echo": lambda a: self._echo("echo " + " ".join(
                x for i, x in enumerate(a) if not (i == 0 and x == "-n"))),
            "rm": self._rm, "ls": self._ls, "cat": self._cat,
            "resolve": self._resolve, "help": self._help,
            "pwd": self._pwd, "cd": self._cd, "mkdir": self._mkdir,
            "cp": self._cp, "mv": self._mv,
            "head": lambda a: self._head_tail(a, False),
            "tail": lambda a: self._head_tail(a, True),
            "wc": self._wc, "less": self._less, "more": self._less,
            "grep": self._sh_grep, "find": self._sh_find, "tree": self._tree,
            "history": self._history, "man": self._man, "date": self._date,
            "whoami": self._whoami, "which": self._which,
            "nano": self._editor, "vim": self._editor, "vi": self._editor,
            "emacs": self._editor, "code": self._editor,
            "curl": lambda a: self._offline("curl"),
            "ping": lambda a: self._offline("ping"),
            "ssh": lambda a: self._offline("ssh"),
            "python": lambda a: self._nolang("python"),
            "python3": lambda a: self._nolang("python3"),
            "node": lambda a: self._nolang("node"),
            "npm": lambda a: self._nolang("npm"),
            "teammate": self._teammate,
            "sort": self._sort, "uniq": self._uniq, "cut": self._cut,
            "sed": self._sed, "nl": self._nl, "rev": self._rev, "tac": self._tac,
            "cmp": self._cmp, "diff": self._f_diff,
            "basename": self._basename, "dirname": self._dirname,
            "seq": self._seq, "stat": self._stat,
            "alias": self._alias, "unalias": self._unalias,
            "sudo": self._sudo, "uname": self._uname, "hostname": self._hostname,
            "uptime": self._uptime, "exit": self._exit, "logout": self._exit,
            "chmod": self._chmod, "chown": self._chmod, "df": self._df_du,
            "du": self._df_du, "gitk": self._gitk, "gui": self._gitk,
            "export": self._export, "unset": self._unset, "env": self._env_cmd,
            "tee": self._tee, "xargs": self._xargs, "awk": self._awk,
            "tr": self._tr, "bc": self._bc, "expr": self._expr,
            "printf": self._printf, "comm": self._comm, "paste": self._paste,
            "column": self._column, "fold": self._fold, "shuf": self._shuf,
            "md5sum": lambda a: self._hashsum("md5", a),
            "sha1sum": lambda a: self._hashsum("sha1", a),
            "sha256sum": lambda a: self._hashsum("sha256", a),
            "base64": self._b64, "strings": self._strings, "file": self._file,
            "mktemp": self._mktemp, "dos2unix": self._dos2unix,
            "unix2dos": self._unix2dos, "ln": self._ln, "type": self._type,
            "tldr": self._man, "apropos": self._man,
            "id": lambda a: [("uid=1000(sandbox-user) gid=1000(learners)", "out")],
            "groups": lambda a: [("learners git-fans", "out")],
            "tty": lambda a: [("/dev/pts/0", "out")],
            "sleep": lambda a: [("⏱ time passes instantly in the sandbox", "warn")],
            "yes": self._yes, "ps": self._ps, "top": self._top, "htop": self._top,
            "kill": self._kill,
            "open": lambda a: [("GUI windows aren't available here", "warn")],
            "xdg-open": lambda a: [("GUI windows aren't available here", "warn")],
            "watch": lambda a: [("watch: sandbox time doesn't flow", "warn")],
            "cmatrix": lambda a: [("📦 reality not installed — no green rain", "warn")],
            "fortune": self._fortune, "cowsay": self._cowsay, "sl": self._sl,
            "sh": self._sh_script, "bash": self._sh_script, "zsh": self._sh_script,
            "source": self._sh_script, ".": self._sh_script,
            "read": self._read, "test": self._test, "[": self._test,
            "true": self._true, "false": self._false,
            "pushd": self._pushd, "popd": self._popd, "dirs": self._dirs_cmd,
            "rmdir": self._rmdir,
            "jobs": lambda a: [("[1]+  Running    learning git &", "warn")],
            "fg": lambda a: [("fg: no job control in the sandbox", "warn")],
            "bg": lambda a: [("bg: no job control in the sandbox", "warn")],
            "umask": lambda a: [("0022", "out")],
            "clear": lambda a: [("clear works at the prompt", "warn")],
        }
        return m
    # ------------- shell: files -------------
    def _pwd(self, args=None): return [(self._pwd_str(), "out")]
    def _cd(self, args):
        if not args or args[0] in ("~", "/"):
            self.cwd = []; return [("→ " + self._pwd_str(), "ok")]
        if args[0] == "-":
            return [("cd - isn't simulated — use 'cd ~' or 'cd ..'", "warn")]
        tgt = self._resolve_path(args[0])
        if self._is_dir(tgt):
            self.cwd = [p for p in tgt.split("/") if p]
            return [("→ " + self._pwd_str(), "ok")]
        return [("cd: no such directory: " + args[0], "err")]
    def _mkdir(self, args):
        rec = "-p" in args
        pos = [a for a in args if not a.startswith("-")]
        if not pos: return [("usage: mkdir [-p] <dir>", "err")]
        out = []
        for a in pos:
            t = self._resolve_path(a)
            if not t: continue
            if t in self.dirs or t in self.working:
                out.append(("mkdir: '" + a + "': already exists", "err")); continue
            parts = t.split("/")
            if len(parts) > 1 and "/".join(parts[:-1]) not in self.dirs and not rec:
                out.append(("mkdir: '" + a + "': No such directory (use -p)", "err")); continue
            self._ensure_parent(t + "/x")
            out.append(("created directory '" + t + "/'", "ok"))
        out.append(("note: git ignores empty directories", "warn"))
        return out
    def _cp(self, args):
        rec = any(f.startswith("-") and "r" in f for f in args)
        pos = [a for a in args if not a.startswith("-")]
        if len(pos) != 2: return [("usage: cp [-r] <src> <dst>", "err")]
        src, dst = self._resolve_path(pos[0]), self._resolve_path(pos[1])
        if src in self.working:
            d = dst + ("/" + src.rsplit("/", 1)[-1] if self._is_dir(dst) else "")
            self._ensure_parent(d); self.working[d] = self.working[src]
            return [("copied '" + src + "' → '" + d + "'", "ok")]
        if self._is_dir(src):
            if not rec: return [("cp: " + pos[0] + " is a directory (use cp -r)", "err")]
            pre = (src + "/") if src else ""
            keys = [f for f in self.working if f.startswith(pre)]
            for f in keys:
                d = dst + "/" + f[len(pre):]
                self._ensure_parent(d); self.working[d] = self.working[f]
            return [("copied " + str(len(keys)) + " file(s)", "ok")] if keys else \
                [("cp: '" + pos[0] + "' is empty", "warn")]
        return [("cp: cannot stat '" + pos[0] + "'", "err")]
    def _mv(self, args):
        pos = [a for a in args if not a.startswith("-")]
        if len(pos) != 2: return [("usage: mv <src> <dst>", "err")]
        src, dst = self._resolve_path(pos[0]), self._resolve_path(pos[1])
        if src in self.working:
            d = dst + ("/" + src.rsplit("/", 1)[-1] if self._is_dir(dst) else "")
            self._ensure_parent(d); self.working[d] = self.working.pop(src)
            return [("renamed '" + src + "' → '" + d + "'", "ok")]
        if self._is_dir(src):
            pre = (src + "/") if src else ""
            keys = [f for f in self.working if f.startswith(pre)]
            for f in keys:
                d = dst + "/" + f[len(pre):]
                self._ensure_parent(d); self.working[d] = self.working.pop(f)
            if keys: return [("moved " + str(len(keys)) + " file(s)", "ok")]
        return [("mv: cannot stat '" + pos[0] + "'", "err")]
    def _ls(self, args):
        rec = "-R" in args or any(a.startswith("-") and "R" in a for a in args)
        flags = "".join(a for a in args if a.startswith("-"))
        pos = [a for a in args if not a.startswith("-")]
        if rec:
            base = self._resolve_path(pos[0]) if pos else "/".join(self.cwd)
            out = []
            def walk(d, label):
                pre = (d + "/") if d else ""
                here = sorted(f[len(pre):] for f in self.working
                              if f.startswith(pre) and "/" not in f[len(pre):])
                out.append((label + ":", "info"))
                if here: out.append(("  ".join(here), "out"))
                out.append(("", "out"))
                subs = sorted({f[len(pre):].split("/", 1)[0] for f in self.working
                               if f.startswith(pre) and "/" in f[len(pre):]})
                for sd in subs: walk(pre + sd, (label + "/" + sd) if label != "." else sd)
            walk(base, base if base else ".")
            return out
        show_all, long = "a" in flags, "l" in flags
        target = self._resolve_path(pos[0]) if pos else "/".join(self.cwd)
        if not self._is_dir(target):
            if target in self.working: return [(target, "out")]
            return [("ls: cannot access '" + pos[0] + "'", "err")]
        pre = (target + "/") if target else ""
        files = sorted(f[len(pre):] for f in self.working
                       if f.startswith(pre) and "/" not in f[len(pre):])
        dsrc = set(self.dirs) | {f.rsplit("/", 1)[0] for f in self.working if "/" in f}
        dirs = sorted({d[len(pre):] for d in dsrc
                       if d.startswith(pre) and "/" not in d[len(pre):] and d[len(pre):]})
        if not show_all:
            files = [f for f in files if not f.startswith(".")]
            dirs = [d for d in dirs if not d.startswith(".")]
        if long:
            out = [("drwxr-xr-x       - " + d + "/", "info") for d in dirs]
            out += [("-rw-r--r-- " + str(len(self.working[pre + f].encode())).rjust(6) +
                     " " + f, "out") for f in files]
            return out or [("(empty)", "warn")]
        names = [d + "/" for d in dirs] + files
        return [("  ".join(names), "out")] if names else [("(empty)", "warn")]
    def _touch(self, args):
        out = []
        for a in [x for x in (args or []) if not x.startswith("-")]:
            key = self._resolve_path(a)
            if not key: continue
            new = key not in self.working
            self._ensure_parent(key)
            self.working[key] = self.working.get(key, "")
            out.append((("created '" if new else "touched '") + key + "'", "ok"))
        return out or [("usage: touch <file>", "err")]
    def _echo(self, line):
        m = re.match(r'echo\s+(.*?)\s*(>>|>)\s*(\S+)\s*$', line)
        if m:
            text = m.group(1).strip().strip('"').strip("'")
            key = self._resolve_path(m.group(3))
            self._ensure_parent(key)
            self.working[key] = (self.working.get(key, "") + text + "\n") \
                if m.group(2) == ">>" else (text + "\n")
            return [("wrote to '" + key + "'", "ok")]
        text = re.sub(r'^echo\s+', '', line).strip().strip('"').strip("'")
        return [(text, "out")]
    def _rm(self, args):
        rec = any(f.startswith("-") and "r" in f for f in args)
        pos = [a for a in args if not a.startswith("-")]
        if not pos: return [("usage: rm [-r] <file>", "err")]
        out = []
        for a in pos:
            key = self._resolve_path(a)
            if key in self.working:
                del self.working[key]; out.append(("deleted '" + key + "'", "out"))
            elif self._is_dir(key):
                if not rec:
                    out.append(("rm: '" + a + "': is a directory (use rm -r)", "err")); continue
                n = 0
                for f in [f for f in self.working if f.startswith(key + "/")]:
                    del self.working[f]; n += 1
                out.append(("deleted " + str(n) + " file(s) under '" + key + "/'", "out"))
            else:
                out.append(("rm: cannot remove '" + a + "'", "err"))
        return out
    def _cat(self, args):
        files = [a for a in args if not a.startswith("-")]
        if not files:
            if self._stdin is not None: return [(l, "out") for l in self._stdin]
            return [("usage: cat <file>…  (or pipe something in)", "err")]
        out = []
        for a in files:
            key = self._resolve_path(a)
            if key not in self.working:
                out.append(("cat: " + a + ": No such file", "err")); continue
            for l in (self.working[key].splitlines() or [""]):
                out.append((l, "err" if l.startswith(("<<<<<<<", "=======",
                                                      ">>>>>>>")) else "out"))
        return out
    def _head_tail(self, args, from_end):
        n, toks, i = 10, list(args), 0
        while i < len(toks):
            if toks[i] == "-n" and i + 1 < len(toks):
                n = int(toks[i + 1]); del toks[i:i + 2]
            elif toks[i].startswith("-") and toks[i][1:].isdigit():
                n = int(toks[i][1:]); del toks[i]
            else: i += 1
        lines = self._input_lines(toks)
        if lines is None:
            return [("usage: " + ("tail" if from_end else "head") +
                     " [-n N] <file>  (or pipe in)", "err")]
        return [(l, "out") for l in (lines[-n:] if from_end else lines[:n])]
    def _wc(self, args):
        mode = next((f[1:] for f in args
                     if f.startswith("-") and f[1:] in ("l", "w", "c")), None)
        lines = self._input_lines(args)
        if lines is None: return [("usage: wc [-l|-w|-c] <file>  (or pipe in)", "err")]
        l = len(lines); w = sum(len(x.split()) for x in lines)
        b = len(("\n".join(lines) + "\n").encode()) if lines else 0
        body = str({"l": l, "w": w, "c": b}[mode]) if mode else \
            (str(l).rjust(4) + str(w).rjust(5) + str(b).rjust(6))
        files = [a for a in args if not a.startswith("-")]
        return [(body + ((" " + self._resolve_path(files[0])) if files else ""), "out")]
    def _less(self, args):
        files = [a for a in args if not a.startswith("-")]
        if not files: return [("usage: less <file>", "err")]
        key = self._resolve_path(files[0])
        if key not in self.working: return [("no such file: " + files[0], "err")]
        return [(l, "out") for l in (self.working[key].splitlines() or [""])] + \
            [("(no pager in the sandbox — that's the whole file 🙂)", "warn")]
    def _sh_grep(self, args):
        icase, n_flag = "-i" in args, "-n" in args
        names_only, invert, count = "-l" in args, "-v" in args, "-c" in args
        rec = bool({"-r", "-R"} & set(args))
        pos = [a for a in args if not a.startswith("-")]
        if not pos: return [("usage: grep [-r] [-i] [-n] [-l] [-v] [-c] <pat> [path]", "err")]
        try: rx = re.compile(pos[0], re.IGNORECASE if icase else 0)
        except re.error: return [("grep: invalid pattern", "err")]
        if len(pos) == 1 and self._stdin is not None:
            hits = [(n, l) for n, l in enumerate(self._stdin, 1)
                    if bool(rx.search(l)) != invert]
            if count: return [(str(len(hits)), "out")]
            out = [((str(n) + ":" if n_flag else "") + l, "out") for n, l in hits]
            return out or [("no matches for '" + pos[0] + "'", "warn")]
        scope = pos[1] if len(pos) > 1 else "."
        base = self._resolve_path(scope) if scope not in (".", "./") else ""
        if base and not self._is_dir(base):
            if base not in self.working:
                return [("grep: " + scope + ": No such file", "err")]
            files = [base]
        else:
            if base and not rec:
                return [("grep: " + scope + ": Is a directory (use -r)", "err")]
            pre = (base + "/") if base else ""
            files = [f for f in sorted(self.working) if f.startswith(pre)]
        matched, out, total = [], [], 0
        for f in files:
            if self._is_ignored(f): continue
            hits = [(n, l) for n, l in enumerate(self.working[f].splitlines(), 1)
                    if bool(rx.search(l)) != invert]
            if not hits: continue
            total += len(hits); matched.append(f)
            if count and len(files) > 1: out.append((f + ":" + str(len(hits)), "out"))
            elif not count and not names_only:
                out += [(f + ":" + (str(n) + ":" if n_flag else "") + l, "out")
                        for n, l in hits]
        if count: return out + ([(str(total), "out")] if len(files) <= 1 else [])
        if names_only:
            return [(f, "out") for f in matched] or [("no matches", "warn")]
        return out or [("no matches for '" + pos[0] + "'", "warn")]
    def _sh_find(self, args):
        path, name, ftype = ".", None, None
        toks, i = list(args), 0
        while i < len(toks):
            if toks[i] == "-name" and i + 1 < len(toks):
                name = toks[i + 1].strip('"'); i += 2
            elif toks[i] == "-type" and i + 1 < len(toks):
                ftype = toks[i + 1]; i += 2
            elif not toks[i].startswith("-"): path = toks[i]; i += 1
            else: i += 1
        base = self._resolve_path(path) if path not in (".", "./") else ""
        res = []
        if ftype in (None, "f"):
            for f in sorted(self.working):
                if base and not (f == base or f.startswith(base + "/")): continue
                if name and not fnmatch.fnmatch(f.rsplit("/", 1)[-1], name): continue
                res.append(("./" + f, "out"))
        if ftype in (None, "d"):
            dirs = set(self.dirs) | {f.rsplit("/", 1)[0] for f in self.working if "/" in f}
            for d in sorted(dirs):
                if base and not (d == base or d.startswith(base + "/")): continue
                if name and not fnmatch.fnmatch(d.rsplit("/", 1)[-1], name): continue
                res.append(("./" + d + "/", "info"))
        return res or [("no matches", "warn")]
    def _tree(self, args=None):
        dirs = set(self.dirs)
        for f in self.working:
            parts = f.split("/")
            for i in range(1, len(parts)): dirs.add("/".join(parts[:i]))
        root = {}
        for d in sorted(dirs):
            node = root
            for p in d.split("/"): node = node.setdefault(p, {})
        for f in self.working:
            node = root; parts = f.split("/")
            for p in parts[:-1]: node = node.setdefault(p, {})
            node[parts[-1]] = None
        def walk(node, indent, path):
            items = sorted(node.items(), key=lambda kv: (kv[1] is None, kv[0]))
            lines = []
            for i, (name, sub) in enumerate(items):
                last = i == len(items) - 1
                full = (path + "/" + name) if path else name
                branch = "└── " if last else "├── "
                if sub is None:
                    lines.append((indent + branch + name,
                                  "warn" if self._is_ignored(full) else "out"))
                else:
                    lines.append((indent + branch + name + "/", "info"))
                    lines += walk(sub, indent + ("    " if last else "│   "), full)
            return lines
        if not root: return [("(empty directory)", "warn")]
        return [("~/project", "info")] + walk(root, "", "")
    def _history(self, args=None):
        if not self.history: return [("history is empty", "warn")]
        return [(str(i + 1).rjust(4) + "  " + c, "out")
                for i, c in enumerate(self.history)]
    def _man(self, args):
        q = " ".join(args).strip()
        if not q: return [("What manual page do you want?  (try: man git-log)", "err")]
        if q.startswith("git-"): q = "git " + q[4:]
        base = q[4:] if q.startswith("git ") else q
        rows = [t.strip() for t, _ in self._help()[1:] if t.strip()]
        hits = []
        for t in rows:
            words = t.split()
            cand = words[1] if words[0] == "git" and len(words) > 1 else words[0]
            if cand == base or cand.split("<")[0] == base or t.startswith(q):
                hits.append(t)
        out = [(h, "out") for h in hits] if hits else \
            [("No manual entry for " + q, "err")]
        n = _lesson_refs(q)
        if n is not None:
            out.append(("📘 lesson " + str(n + 1) + " covers this: " +
                        LESSONS[n]["title"], "info"))
        elif not hits and base:
            out.append(("full docs: https://git-scm.com/docs/git-" + base, "out"))
        return out
    def _date(self, args=None): return [(time.strftime("%a %b %d %H:%M:%S %Y"), "out")]
    def _whoami(self, args=None): return [("sandbox-user", "out")]
    def _which(self, args):
        if not args: return [("usage: which <command>", "err")]
        return [("/usr/bin/" + args[0] + "   (simulated)", "out")]
    def _editor(self, args):
        hint = [("🖥 No text editor here — change files with:", "warn"),
                ('  echo "replacement" > file    # overwrite', "out"),
                ('  echo "extra" >> file        # append', "out")]
        if args:
            key = self._resolve_path(args[0])
            if key in self.working and "<<<<<<<" in self.working[key]:
                hint.append(("psst: '" + key + "' has conflict markers — try:  resolve " +
                             key + " ours|theirs", "ok"))
        return hint
    def _offline(self, cmd):
        return [("🌐 '" + cmd + "' needs the internet — this sandbox is offline.", "warn")]
    def _nolang(self, cmd):
        return [(cmd + " isn't available here — this sandbox teaches git & shell.", "warn")]
    # ------------- shell: text tools -------------
    def _sort(self, args):
        lines = self._input_lines(args)
        if lines is None: return [("usage: sort [-r] [-n] [-u] [file]  (or pipe in)", "err")]
        rev, num, uniq = "-r" in args, "-n" in args, "-u" in args
        def nkey(l):
            m = re.match(r'\s*-?\d+(\.\d+)?', l)
            return float(m.group()) if m else float("-inf")
        lines = sorted(lines, key=nkey if num else None, reverse=rev)
        if uniq:
            seen, out = set(), []
            for l in lines:
                if l not in seen: seen.add(l); out.append(l)
            lines = out
        return [(l, "out") for l in lines]
    def _uniq(self, args):
        lines = self._input_lines(args)
        if lines is None:
            return [("usage: uniq [-c] [file]  (sort first — adjacent only!)", "err")]
        groups = []
        for l in lines:
            if groups and groups[-1][1] == l: groups[-1][0] += 1
            else: groups.append([1, l])
        return [((str(n).rjust(7) + " " if "-c" in args else "") + l, "out")
                for n, l in groups]
    def _cut(self, args):
        delim, fspec, toks, i = "\t", None, list(args), 0
        while i < len(toks):
            if toks[i] == "-d" and i + 1 < len(toks): delim = toks[i + 1]; i += 2
            elif toks[i].startswith("-d") and len(toks[i]) > 2: delim = toks[i][2:]; i += 1
            elif toks[i] == "-f" and i + 1 < len(toks): fspec = toks[i + 1]; i += 2
            elif toks[i].startswith("-f") and len(toks[i]) > 2: fspec = toks[i][2:]; i += 1
            else: i += 1
        if fspec is None: return [("usage: cut -d <delim> -f <n[,m]> [file]", "err")]
        fields = []
        for part in fspec.split(","):
            if "-" in part:
                a, b = part.split("-", 1)
                fields += list(range(int(a or 1), int(b or 99999) + 1))
            else: fields.append(int(part))
        lines = self._input_lines([a for a in toks if not a.startswith("-")])
        if lines is None: return [("cut: no input", "err")]
        out = []
        for l in lines:
            parts = l.split(delim)
            out.append(delim.join(parts[f - 1] for f in sorted(set(fields))
                                  if f <= len(parts)))
        return [(l, "out") for l in out]
    def _sed(self, args):
        inplace = "-i" in args
        exprs = [a for a in args if not a.startswith("-")]
        if not exprs: return [("usage: sed [-i] s/old/new/[g] [file]", "err")]
        m = re.match(r's(.)(.*?)(?<!\\)\1(.*?)(?<!\\)\1([gi]*)$', exprs[0])
        if not m: return [("usage: sed [-i] s/old/new/[g] [file]  (only s///)", "err")]
        old, new, flags = m.group(2), m.group(3), m.group(4)
        try: rx = re.compile(old, re.IGNORECASE if "i" in flags else 0)
        except re.error: return [("sed: invalid pattern", "err")]
        count = 0 if "g" in flags else 1
        target = exprs[1] if len(exprs) > 1 else None
        lines = self._input_lines([target] if target else [])
        if lines is None: return [("sed: no input file", "err")]
        new_lines = [rx.sub(new, l, count=count) for l in lines]
        if inplace:
            if not target: return [("sed -i needs a file argument", "err")]
            key = self._resolve_path(target)
            self._ensure_parent(key); self.working[key] = "\n".join(new_lines) + "\n"
            return [("wrote '" + key + "' (in place ✔)", "ok")]
        return [(l, "out") for l in new_lines]
    def _nl(self, args):
        lines = self._input_lines(args)
        if lines is None: return [("usage: nl [file]", "err")]
        return [(str(n).rjust(6) + "  " + l, "out") for n, l in enumerate(lines, 1)]
    def _rev(self, args):
        lines = self._input_lines(args)
        if lines is None: return [("usage: rev [file]", "err")]
        return [(l[::-1], "out") for l in lines]
    def _tac(self, args):
        lines = self._input_lines(args)
        if lines is None: return [("usage: tac [file]", "err")]
        return [(l, "out") for l in reversed(lines)]
    def _cmp(self, args):
        pos = [a for a in args if not a.startswith("-")]
        if len(pos) != 2: return [("usage: cmp <file1> <file2>", "err")]
        k1, k2 = self._resolve_path(pos[0]), self._resolve_path(pos[1])
        if k1 not in self.working or k2 not in self.working:
            return [("cmp: no such file", "err")]
        l1, l2 = self.working[k1].splitlines(), self.working[k2].splitlines()
        for i, (a, b) in enumerate(zip(l1, l2), 1):
            if a != b: return [(pos[0] + " " + pos[1] + " differ: line " + str(i), "err")]
        if len(l1) != len(l2):
            return [("files differ in length", "err")]
        return [("files are identical", "ok")]
    def _f_diff(self, args):
        pos = [a for a in args if not a.startswith("-")]
        if len(pos) != 2:
            return [("usage: diff <file1> <file2>   (git diff compares git things)", "err")]
        k1, k2 = self._resolve_path(pos[0]), self._resolve_path(pos[1])
        for k, n in ((k1, pos[0]), (k2, pos[1])):
            if k not in self.working: return [("diff: " + n + ": No such file", "err")]
        a, b = self.working[k1].splitlines(), self.working[k2].splitlines()
        if a == b: return [("files are identical", "ok")]
        out = [("diff " + k1 + " " + k2, "info")]
        for l in difflib.unified_diff(a, b, lineterm=""):
            if l.startswith(("---", "+++")): continue
            kind = ("info" if l.startswith("@@") else
                    "add" if l.startswith("+") else "del" if l.startswith("-") else "out")
            out.append((l, kind))
        return out
    def _basename(self, args):
        if not args: return [("usage: basename <path>", "err")]
        return [(self._resolve_path(args[0]).rsplit("/", 1)[-1] or "/", "out")]
    def _dirname(self, args):
        if not args: return [("usage: dirname <path>", "err")]
        d = self._resolve_path(args[0]).rsplit("/", 1)[0]
        return [(d if d else ".", "out")]
    def _seq(self, args):
        nums = [int(a) for a in args if a.lstrip("-").isdigit()]
        if len(nums) == 1: a, b = 1, nums[0]
        elif len(nums) == 2: a, b = nums
        else: return [("usage: seq [start] <end>", "err")]
        return [(str(n), "out") for n in range(a, b + 1)]
    def _stat(self, args):
        if not args: return [("usage: stat <file>", "err")]
        key = self._resolve_path(args[0])
        if key not in self.working: return [("stat: cannot stat '" + args[0] + "'", "err")]
        c = self.working[key]
        tracked = "tracked" if key in self.index or key in self.head_tree() else "untracked"
        return [("  File: " + key, "out"),
                ("  Size: " + str(len(c.encode())) + " bytes    Lines: " +
                 str(len(c.splitlines()) or (1 if c else 0)), "out"),
                ("  Git:  " + tracked, "info")]
    # ------------- shell: env / glue / misc -------------
    def _export(self, args):
        if not args: return self._env_cmd()
        out = []
        for t in args:
            n, sep, v = t.partition("=")
            if not sep:
                out.append((t + "=" + self.env.get(t, "(unset)"), "out")); continue
            if not re.fullmatch(r'[A-Za-z_]\w*', n):
                return [("export: invalid name: " + t, "err")]
            self.env[n] = v
            out.append((n + "=" + v + "   (use as $" + n + ")", "ok"))
        return out
    def _unset(self, args):
        out = []
        for n in args:
            if n in self.env: del self.env[n]; out.append(("unset " + n, "ok"))
            else: out.append((n + ": not set", "warn"))
        return out or [("usage: unset <NAME>", "err")]
    def _env_cmd(self, args=None):
        rows = [k + "=" + v for k, v in sorted(self.env.items())]
        rows.append("PWD=" + self._pwd_str())
        return [(r, "out") for r in rows]
    def _tee(self, args):
        append = "-a" in args
        files = [a for a in args if not a.startswith("-")]
        lines = self._stdin if self._stdin is not None else []
        text = "\n".join(lines) + ("\n" if lines else "")
        for f in files:
            key = self._resolve_path(f)
            self._ensure_parent(key)
            self.working[key] = (self.working.get(key, "") + text) if append else text
        out = [(l, "out") for l in lines]
        if files: out.append(("(tee " + ("appended to" if append else "wrote") +
                              " " + ", ".join(files) + ")", "info"))
        return out or [("(tee: nothing on stdin)", "warn")]
    def _xargs(self, args):
        if self._stdin is None:
            return [("xargs: no input — pipe something in", "err")]
        base = [a for a in args if a not in ("-n", "-n1", "1", "-0")]
        one = "-n1" in args or ("-n" in args and "1" in args)
        items = " ".join(self._stdin).split()
        groups = [[it] for it in items] if one else ([items] if items else [])
        if not base: base = ["echo"]
        out = []
        for g in groups: out += self._pipeline(shlex.join(base + g))
        return out or [("(xargs: nothing to run)", "warn")]
    def _awk(self, args):
        sep, prog, files = None, None, []
        toks, i = list(args), 0
        while i < len(toks):
            if toks[i] == "-F" and i + 1 < len(toks): sep = toks[i + 1]; i += 2
            elif toks[i].startswith("-F") and len(toks[i]) > 2: sep = toks[i][2:]; i += 1
            elif prog is None and toks[i].startswith(("{", "/")): prog = toks[i]; i += 1
            else: files.append(toks[i]); i += 1
        if not prog: return [("usage: awk [-F c] '/pat/ {print $1}' [file]", "err")]
        m = re.match(r'^(?P<p>/(?:[^/\\]|\\.)*/)?\s*(?P<a>\{.*\})?\s*$', prog)
        if not m or not (m.group("p") or m.group("a")):
            return [("awk: only '/pat/' and '{print …}' simulated", "err")]
        pat = re.compile(m.group("p")[1:-1]) if m.group("p") else None
        act = m.group("a")
        lines = self._input_lines(files)
        if lines is None: return [("awk: no input", "err")]
        out = []
        for nr, line in enumerate(lines, 1):
            if pat and not pat.search(line): continue
            fields = line.split(sep) if sep else line.split()
            def field(tok):
                if tok == "$0": return line
                m2 = re.fullmatch(r'\$(\d+|NF)', tok)
                if m2:
                    if m2.group(1) == "NF": return fields[-1] if fields else ""
                    idx = int(m2.group(1))
                    return fields[idx - 1] if idx <= len(fields) else ""
                if tok == "NF": return str(len(fields))
                if tok == "NR": return str(nr)
                return tok
            if not act: out.append((line, "out")); continue
            body = act.strip("{}").strip()
            if body in ("print", "print $0"): out.append((line, "out")); continue
            mp = re.match(r'^print\s+(.*)$', body)
            if not mp: return [("awk: only 'print' actions simulated", "err")]
            rendered = []
            for p in [x.strip() for x in mp.group(1).split(",") if x.strip()]:
                mm = re.match(r'^"(.*)"$', p)
                rendered.append(mm.group(1) if mm else field(p))
            out.append((" ".join(rendered), "out"))
        return out
    @staticmethod
    def _tr_set(s):
        res, i = [], 0
        while i < len(s):
            if i + 2 < len(s) and s[i + 1] == "-":
                res.extend(chr(c) for c in range(ord(s[i]), ord(s[i + 2]) + 1)); i += 3
            else: res.append(s[i]); i += 1
        return "".join(res)
    def _tr(self, args):
        sets = [a for a in args if not a.startswith("-")]
        dele, squeeze = "-d" in args, "-s" in args
        if self._stdin is None: return [("tr: reads stdin — try: cat f | tr a-z A-Z", "err")]
        if not sets and not dele: return [("usage: tr [-d] [-s] SET1 [SET2]", "err")]
        s1 = self._tr_set(sets[0]) if sets else ""
        s2 = self._tr_set(sets[1]) if len(sets) > 1 else ""
        res = []
        for line in self._stdin:
            if dele: line = "".join(c for c in line if c not in s1)
            else: line = line.translate({ord(a): b for a, b in zip(s1, s2)})
            if squeeze:
                sq = s2 or s1
                line = re.sub(r'(.)\1+', lambda mm: mm.group(1)
                              if mm.group(1) in sq else mm.group(0), line)
            res.append(line)
        return [(l, "out") for l in res]
    def _bc(self, args):
        exprs = list(self._stdin) if self._stdin is not None else \
            ([" ".join(args)] if args else None)
        if exprs is None: return [("usage: echo \"2+2\" | bc", "err")]
        out = []
        for e in exprs:
            e = e.strip()
            if not e or e.lower().startswith(("scale", "quit")): continue
            if not re.fullmatch(r'[\d\s.+\-*/%()]+', e):
                return [("bc: only plain arithmetic: " + e, "err")]
            try: v = eval(e, {"__builtins__": {}}, {})
            except Exception: return [("bc: syntax error: " + e, "err")]
            out.append((str(int(v)) if float(v).is_integer() else str(round(v, 6)), "out"))
        return out or [("(nothing to compute)", "warn")]
    def _expr(self, args):
        e = " ".join(args)
        if not re.fullmatch(r'[\d\s.+\-*/%()]+', e):
            return [("expr: only arithmetic (e.g. expr 2 + 2)", "err")]
        try: v = eval(e, {"__builtins__": {}}, {})
        except Exception: return [("expr: syntax error", "err")]
        return [(str(int(v)) if float(v).is_integer() else str(v), "out")]
    def _printf(self, args):
        if not args: return [("usage: printf \"fmt\" [args…]", "err")]
        fmt = args[0].strip('"').strip("'")
        rest, res, ri, i = args[1:], "", 0, 0
        while i < len(fmt):
            c = fmt[i]
            if c == "%" and i + 1 < len(fmt):
                spec = fmt[i + 1]
                if spec == "%": res += "%"
                elif spec == "s":
                    res += rest[ri] if ri < len(rest) else ""; ri += 1
                elif spec in "dif":
                    try:
                        res += str(int(float(rest[ri]))) if spec != "f" \
                            else str(float(rest[ri])); ri += 1
                    except (IndexError, ValueError): res += "?" + spec
                else: res += "%" + spec
                i += 2; continue
            if c == "\\" and i + 1 < len(fmt):
                res += {"n": "\n", "t": "\t", "\\": "\\"}.get(fmt[i + 1],
                                                              "\\" + fmt[i + 1])
                i += 2; continue
            res += c; i += 1
        lines = res.split("\n")
        if lines and lines[-1] == "": lines = lines[:-1]
        return [(l, "out") for l in lines]
    def _comm(self, args):
        sup = set(f for a in args if a.startswith("-") for f in a[1:] if f in "123")
        pos = [a for a in args if not a.startswith("-")]
        if len(pos) != 2: return [("usage: comm [-1|-2|-3] file1 file2", "err")]
        k1, k2 = self._resolve_path(pos[0]), self._resolve_path(pos[1])
        if k1 not in self.working or k2 not in self.working:
            return [("comm: no such file", "err")]
        A, B = self.working[k1].splitlines(), self.working[k2].splitlines()
        out, i, j = [], 0, 0
        while i < len(A) or j < len(B):
            if j >= len(B) or (i < len(A) and A[i] < B[j]):
                if "1" not in sup: out.append((A[i], "out"))
                i += 1
            elif i >= len(A) or B[j] < A[i]:
                if "2" not in sup: out.append((B[j], "out"))
                j += 1
            else:
                if "3" not in sup: out.append(("        " + A[i], "out"))
                i += 1; j += 1
        return out or [("(files identical)", "ok")]
    def _paste(self, args):
        pos = [a for a in args if not a.startswith("-")]
        if len(pos) != 2: return [("usage: paste file1 file2", "err")]
        k1, k2 = self._resolve_path(pos[0]), self._resolve_path(pos[1])
        if k1 not in self.working or k2 not in self.working:
            return [("paste: no such file", "err")]
        A, B = self.working[k1].splitlines(), self.working[k2].splitlines()
        n = max(len(A), len(B))
        return [((A[i] if i < len(A) else "") + "\t" + (B[i] if i < len(B) else ""),
                 "out") for i in range(n)]
    def _column(self, args):
        lines = self._input_lines([a for a in args if not a.startswith("-")])
        if lines is None: return [("usage: column -t [file]  (or pipe in)", "err")]
        rows = [l.split() for l in lines if l.split()]
        if not rows: return [("(empty)", "warn")]
        w = [max(len(r[c]) for r in rows if c < len(r))
             for c in range(max(map(len, rows)))]
        return [("  ".join(cell.ljust(w[i]) for i, cell in enumerate(r)).rstrip(),
                 "out") for r in rows]
    def _fold(self, args):
        w, toks, i = 80, list(args), 0
        while i < len(toks):
            if toks[i] == "-w" and i + 1 < len(toks): w = int(toks[i + 1]); del toks[i:i + 2]
            else: i += 1
        lines = self._input_lines(toks)
        if lines is None: return [("usage: fold -w N [file]", "err")]
        out = []
        for l in lines:
            out += [l[k:k + w] for k in range(0, len(l), w)] or [""]
        return [(x, "out") for x in out]
    def _shuf(self, args):
        n = None
        if "-n" in args:
            i = args.index("-n")
            if i + 1 < len(args): n = int(args[i + 1])
        lines = self._input_lines([a for a in args if not a.startswith("-")])
        if lines is None: return [("usage: shuf [-n N] [file]", "err")]
        pool = list(lines); random.shuffle(pool)
        return [(l, "out") for l in (pool[:n] if n is not None else pool)]
    def _hashsum(self, algo, args):
        files = [a for a in args if not a.startswith("-")]
        if files:
            key = self._resolve_path(files[0])
            if key not in self.working: return [("no such file: " + files[0], "err")]
            data, name = self.working[key], key
        elif self._stdin is not None:
            data, name = "\n".join(self._stdin) + "\n", "-"
        else: return [("usage: " + algo + "sum <file>  (or pipe in)", "err")]
        return [(getattr(hashlib, algo)(data.encode()).hexdigest() + "  " + name, "out")]
    def _b64(self, args):
        dec = "-d" in args
        lines = self._input_lines([a for a in args if not a.startswith("-")])
        if lines is None: return [("usage: base64 [-d] [file]  (or pipe in)", "err")]
        blob = "\n".join(lines)
        try:
            if dec:
                txt = base64.b64decode(blob + "=" * (-len(blob) % 4)).decode()
                return [(l, "out") for l in (txt.splitlines() or [""])]
            return [(base64.b64encode(blob.encode()).decode(), "out")]
        except Exception: return [("base64: invalid input", "err")]
    def _strings(self, args):
        files = [a for a in args if not a.startswith("-")]
        if files:
            key = self._resolve_path(files[0])
            if key not in self.working: return [("no such file: " + files[0], "err")]
            text = self.working[key]
        elif self._stdin is not None: text = "\n".join(self._stdin)
        else: return [("usage: strings <file>", "err")]
        res = [l for l in text.splitlines()
               if len("".join(ch for ch in l if ch.isprintable())) >= 4]
        return [(l, "out") for l in res] or [("(no printable strings ≥4 chars)", "warn")]
    def _file(self, args):
        out = []
        for a in args:
            key = self._resolve_path(a)
            if self._is_dir(key): out.append((a + ": directory", "out"))
            elif key in self.working:
                c = self.working[key]
                out.append((a + ": ASCII text" +
                            (", with CRLF line terminators" if "\r\n" in c else ""), "out"))
            else: out.append((a + ": cannot open", "err"))
        return out
    def _mktemp(self, args):
        name = ".tmp" + "".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789")
                                for _ in range(6))
        key = self._resolve_path(name)
        self._ensure_parent(key); self.working[key] = ""
        return [(key, "out")]
    def _dos2unix(self, args): return self._line_ending(args, False)
    def _unix2dos(self, args): return self._line_ending(args, True)
    def _line_ending(self, args, to_crlf):
        files = [a for a in args if not a.startswith("-")]
        if not files:
            return [("usage: " + ("unix2dos" if to_crlf else "dos2unix") +
                     " <file>", "err")]
        key = self._resolve_path(files[0])
        if key not in self.working: return [("no such file: " + files[0], "err")]
        c = self.working[key]
        if to_crlf: new = c.replace("\r\n", "\n").replace("\n", "\r\n")
        else: new = c.replace("\r\n", "\n").replace("\r", "\n")
        self.working[key] = new
        return [("converted " + key + " (" + ("LF → CRLF" if to_crlf else "CRLF → LF") + ")", "ok")]
    def _type(self, args):
        if not args: return [("usage: type <command>", "err")]
        c = args[0]
        if c in self.shell_aliases:
            return [(c + " is aliased to '" + self.shell_aliases[c] + "'", "out")]
        if c in self._simple_map(): return [(c + " is a sandbox command", "out")]
        if c in ("pick", "drop", "squash", "fixup", "reword"):
            return [(c + " is a rebase-todo command", "out")]
        if c == "git": return [("git is /usr/bin/git (simulated, quite well 🙂)", "out")]
        return [(c + ": not found", "err")]
    def _ln(self, args): return [("symlinks aren't modeled — use cp", "warn")]
    def _yes(self, args=None):
        w = args[0] if args else "y"
        return [(w, "out")] * 5 + [("…stopped before infinity", "warn")]
    def _ps(self, args=None):
        return [("  PID TTY          TIME CMD", "out"),
                ("    1 ?        00:00:01 gitlearn", "out"),
                ("   42 pts/0    00:00:00 git-sim", "out")]
    def _top(self, args=None): return [("load: 100% learning · 0% idle 🚀", "out")]
    def _kill(self, args=None): return [("nothing to kill — peaceful 🕊", "warn")]
    def _fortune(self, args=None):
        return [("❝ " + random.choice(self.GIT_FORTUNES) + " ❞", "info")]
    def _cowsay(self, args=None):
        msg = " ".join(args) if args else "moo"
        w = len(msg)
        return [(" " + "_" * (w + 2), "out"), 
                ("< " + msg + " >", "out"),
                (" " + "-" * (w + 2), "out"), 
                (r"^__^", "out"),
                (r"(oo)_______", "out"),
                (r"(__)", "out"),
                (r"||----w |", "out"), 
                (r"||     ||", "out")]
    def _sl(self, args=None):
        return [("      🚂 what a ride — you typed 'sl'", "info"),
                ("(next time that's 'ls' 😉)", "warn")]
    # ------------- shell: scripts / conditions / dirs -------------
    def _sh_script(self, args):
        if not args: return [("usage: sh <script> [args]", "err")]
        key = self._resolve_path(args[0])
        if key not in self.working: return [("sh: " + args[0] + ": No such file", "err")]
        if self._sh_depth >= 8: return [("too many nested scripts", "err")]
        self._sh_depth += 1
        was, saved_env = self._in_script, dict(self.env)
        self._in_script = True
        for i, v in enumerate(args[1:], 1): self.env[str(i)] = v
        out = []
        try:
            for ln in self.working[key].splitlines():
                ln = ln.strip()
                if not ln or ln.startswith("#"): continue
                out += self.run(ln)
        finally:
            self._sh_depth -= 1; self._in_script = was; self.env = saved_env
        return out + [("── end of " + args[0] + " ──", "info")]
    def _test(self, args):
        args = [a for a in args if a != "]"]
        ok = False
        try:
            if args and args[0] in ("-f", "-d", "-e"):
                key = self._resolve_path(args[1])
                ok = self._is_dir(key) if args[0] == "-d" else \
                    (key in self.working if args[0] == "-f" else
                     key in self.working or self._is_dir(key))
            elif args and args[0] in ("-z", "-n") and len(args) > 1:
                v = self._expand_vars(args[1])
                ok = (v == "") if args[0] == "-z" else (v != "")
            elif len(args) >= 3:
                a, b = self._expand_vars(args[0]), self._expand_vars(args[2])
                op = args[1]
                if op in ("=", "=="): ok = a == b
                elif op == "!=": ok = a != b
                elif op in ("-eq", "-ne", "-lt", "-le", "-gt", "-ge"):
                    x, y = int(a), int(b)
                    ok = {"-eq": x == y, "-ne": x != y, "-lt": x < y,
                          "-le": x <= y, "-gt": x > y, "-ge": x >= y}[op]
        except (IndexError, ValueError): ok = False
        self._status_forced = 0 if ok else 1
        return []
    def _read(self, args):
        if not args: return [("usage: read VARNAME", "err")]
        val = self._stdin[0] if self._stdin else ""
        self.env[args[0]] = val
        self._status_forced = 0
        return [("read: " + args[0] + "=\"" + val + "\"", "ok")]
    def _true(self, args=None):
        self._status_forced = 0; return []
    def _false(self, args=None):
        self._status_forced = 1; return []
    def _dirs_cmd(self, args=None):
        items = ["~"] + ["/".join(d) if d else "~" for d in self.dirstack]
        return [(" ".join(items), "out")]
    def _pushd(self, args):
        old = list(self.cwd)
        res = self._cd(args)
        if any(k == "err" for _t, k in res): return res
        self.dirstack.insert(0, old)
        return res + [("stack: " + " ".join(["~"] +
                    ["/".join(d) if d else "~" for d in self.dirstack]), "info")]
    def _popd(self, args=None):
        if not self.dirstack: return [("popd: directory stack empty", "err")]
        self.cwd = list(self.dirstack.pop(0))
        return [("→ " + self._pwd_str(), "ok")]
    def _rmdir(self, args):
        out = []
        for a in args:
            t = self._resolve_path(a)
            if t not in self.dirs and not self._is_dir(t):
                out.append(("rmdir: '" + a + "': No such directory", "err"))
            elif any(f.startswith(t + "/") for f in self.working) if t else False:
                out.append(("rmdir: '" + a + "': Directory not empty", "err"))
            else:
                self.dirs.discard(t)
                out.append(("removed directory '" + (t or ".") + "'", "ok"))
        return out
    # ------------- shell: aliases / fun -------------
    def _alias(self, args):
        if not args:
            if not self.shell_aliases:
                return [("(no shell aliases — try: alias gs=\"git status -s\")", "warn")]
            return [("alias " + k + "='" + v + "'", "ok")
                    for k, v in sorted(self.shell_aliases.items())]
        for t in args:
            if "=" in t:
                name, _, val = t.partition("=")
                val = val.strip().strip('"').strip("'")
                if not name or not val: return [("usage: alias <name>='<command>'", "err")]
                self.shell_aliases[name] = val
                return [("alias added: " + name + "  →  " + val, "ok")]
            if t in self.shell_aliases:
                return [("alias " + t + "='" + self.shell_aliases[t] + "'", "out")]
            return [(": not an alias", "err")]
        return []
    def _unalias(self, args):
        if "-a" in args:
            self.shell_aliases = {}; return [("all shell aliases removed", "ok")]
        if not args: return [("usage: unalias <name> | unalias -a", "err")]
        if args[0] in self.shell_aliases:
            del self.shell_aliases[args[0]]; return [("removed alias " + args[0], "ok")]
        return [("unalias: no such alias: " + args[0], "err")]
    def _sudo(self, args):
        return [("sandbox-user is not in the sudoers file.", "err"),
                ("This incident will be reported. 😄", "warn")]
    def _uname(self, args):
        return [("GitLearnSandbox 1.0-git-sim x86_64 GNU/Linux", "out")]
    def _hostname(self, args=None): return [("sandbox", "out")]
    def _uptime(self, args=None):
        return [(" up 42 min,  1 user (you),  load average: 0.10 0.05 0.01", "out")]
    def _exit(self, args=None):
        return [("There's no escape from the learning sandbox 😄", "warn")]
    def _chmod(self, args):
        return [("permissions aren't simulated — everything is rwx here 🙂", "warn")]
    def _df_du(self, args):
        return [("disk space is imaginary — commit freely 🧻", "out")]
    def _gitk(self, args=None):
        return [("You already have a graphical git view open 🙂", "out"),
                ("→ the commit graph panel right beside this terminal", "info"),
                ("(gitk / git gui are real desktop tools worth trying)", "warn")]
    # ------------- teammate -------------
    def _teammate(self, args):
        remote = "origin" if "origin" in self.remotes else \
            (self.tracking.get(self.current, (None, ""))[0]
             if not self.detached and self.current in self.tracking else "")
        if args and args[0] == "-b":
            if len(args) < 3 or not remote or remote not in self.remotes:
                return [("usage: teammate -b <branch> <message> [file]   (needs a remote)", "err")]
            branch, msg, rest = args[1], args[2], args[3:]
            rkey = remote + "/" + branch
            base = self.remote_branches.get(rkey) or \
                self.remote_branches.get(remote + "/main") or self.head
            if base is None:
                return [("nothing on the remote to branch from — push something first", "err")]
            tree = dict(self.commits[base].tree)
            if rest:
                f = self._resolve_path(rest[0])
                tree[f] = "edited by a teammate on '" + branch + "'\n(" + msg + ")\n"
            else:
                f = "team_" + branch + ".txt"
                tree[f] = "work by a teammate on branch '" + branch + "'\n(" + msg + ")\n"
            c = Commit(msg, [base], tree, branch)
            while c.hash in self.commits:
                c.hash = "".join(random.choice("0123456789abcdef") for _ in range(7))
            c.date = time.time(); c.author = "Teammate (" + branch + ")"
            self.commits[c.hash] = c
            self.remote_branches[rkey] = c.hash
            return [("🤝 Teammate pushed to " + rkey + ":", "info"),
                    ("   " + c.hash + "  " + msg, "out"),
                    ("git fetch   →   git switch -t origin/" + branch, "warn")]
        if not args:
            return [("usage: teammate <message> [file]   |   teammate -b <branch> <msg>", "err")]
        if not remote or remote not in self.remotes:
            return [("no remote yet — git remote add origin <url>, push, then teammate", "err")]
        msg = args[0]
        explicit = len(args) > 1
        fname = self._resolve_path(args[1]) if explicit else "team_notes.txt"
        rkey = remote + "/" + str(self.current)
        base = self.remote_branches.get(rkey)
        if base is None:
            return [("the remote has no '" + str(self.current) + "' branch — git push first", "err")]
        tree = dict(self.commits[base].tree)
        note = "edited by a teammate on the server\n(message was: " + msg + ")\n"
        tree[fname] = tree.get(fname, "") + note if not explicit else note
        c = Commit(msg, [base], tree, self.current)
        while c.hash in self.commits:
            c.hash = "".join(random.choice("0123456789abcdef") for _ in range(7))
        c.date = time.time(); c.author = "Teammate"
        self.commits[c.hash] = c
        self.remote_branches[rkey] = c.hash
        return [("🤝 Teammate pushed to " + rkey + ":", "info"),
                ("   " + c.hash + "  " + msg, "out"),
                ("your local branch doesn't have it yet — git fetch", "warn")]
    # ================= git commands =================
    def cmd_init(self, args=None):
        args = args or []
        if "--bare" in args:
            pos = [a for a in args if not a.startswith("-")]
            path = (pos[0] if pos else "repo.git").rstrip("/")
            if not path.endswith(".git"): path += ".git"
            self.remotes[path] = "~/project/" + path
            return [("Initialized empty Git repository in ~/project/" + path +
                     "  (BARE — no working tree)", "ok"),
                    ("bare repos are safe push targets — that's what servers hold", "info"),
                    ("now:  git remote add shared " + path + "  →  git push -u shared " +
                     str(self.current), "out")]
        name = "main"
        if "-b" in args and args.index("-b") + 1 < len(args):
            name = args[args.index("-b") + 1]
        else:
            for a in args:
                if a.startswith("--initial-branch="): name = a.split("=", 1)[1]
        if self.initialized:
            return [("Reinitialized existing Git repository in ~/project/.git/", "warn")]
        self.initialized = True
        self.branches = {name: None}
        self.current, self.head = name, None
        return [("Initialized empty Git repository in ~/project/.git/ [default branch: " +
                 name + "]", "ok"),
                ("hint: touch a file, git add it, then git commit -m \"...\"", "out")]
    def cmd_status(self, args=None):
        args = args or []
        short = bool({"-s", "--short", "--porcelain"} & set(args))
        if short:
            out = []
            if self.detached:
                out.append(("## HEAD (detached at " +
                            (self.head[:7] if self.head else "?") + ")", "info"))
            else:
                line = "## " + str(self.current)
                tr = self.tracking.get(self.current)
                if tr:
                    rkey = tr[0] + "/" + tr[1]
                    rh = self.rt.get(rkey)
                    if rh and self.head:
                        ahead = len(self._ancestors(self.head) - self._ancestors(rh))
                        behind = len(self._ancestors(rh) - self._ancestors(self.head))
                        bits = (["ahead " + str(ahead)] if ahead else []) + (["behind " + str(behind)] if behind else [])
                        line += "..." + rkey + ((" [" + ", ".join(bits) + "]") if bits else "")
                out.append((line, "info"))
            head = self.head_tree()
            if self.merge_state:
                for f in self.merge_state["conflicts"]:
                    if "<<<<<<<" in self.index.get(f, ""): out.append(("UU " + f, "err"))
            for f in sorted(set(self.index) | set(head)):
                i, h = self.index.get(f), head.get(f)
                if i != h:
                    out.append((("A" if h is None else ("D" if i is None else "M")) +
                                "  " + f, "ok"))
            for f in sorted(set(self.working) | set(self.index)):
                if f not in self.working and f in self.index: out.append((" D " + f, "err"))
                elif f in self.working and f in self.index and \
                        self.working[f] != self.index[f] and f not in self.sw_files:
                    out.append((" M " + f, "err"))
            for f in sorted(self.working):
                if f not in self.index and f not in head and not self._is_ignored(f):
                    out.append(("?? " + f, "err"))
            return out
        out = []
        if self.detached:
            out.append(("HEAD detached at " + (self.head[:7] if self.head else "?"), "warn"))
        else:
            out.append(("On branch " + str(self.current), "info"))
        tr = self.tracking.get(self.current) if not self.detached else None
        if tr:
            rkey = tr[0] + "/" + tr[1]
            rh = self.rt.get(rkey)
            if rh and self.head:
                ahead = len(self._ancestors(self.head) - self._ancestors(rh))
                behind = len(self._ancestors(rh) - self._ancestors(self.head))
                if ahead and behind:
                    out.append(("Your branch and '" + rkey + "' have diverged, " +
                                str(ahead) + " vs " + str(behind) + ".  (git pull)", "warn"))
                elif ahead:
                    out.append(("Your branch is ahead of '" + rkey + "' by " +
                                str(ahead) + " commit(s).  (git push)", "warn"))
                elif behind:
                    out.append(("Your branch is behind '" + rkey + "' by " +
                                str(behind) + " commit(s).  (git pull)", "warn"))
        if self.rebase_state:
            out.append(("interactive rebase in progress — continue/--abort", "warn"))
        if self.bisect:
            out.append(("bisect in progress — git bisect good|bad", "warn"))
        if self.merge_state:
            out.append(("You have unmerged paths — fix conflicts, then git commit.", "warn"))
            for f in self.merge_state["conflicts"]:
                if "<<<<<<<" in self.index.get(f, ""):
                    out.append(("        both modified:  " + f, "err"))
            return out
        if self.head is None: out.append(("No commits yet", "out"))
        head = self.head_tree()
        staged = []
        for f in sorted(set(self.index) | set(head)):
            i, h = self.index.get(f), head.get(f)
            if i != h:
                staged.append("\tnew file:   " + f if h is None else
                              ("\tdeleted:    " + f if i is None else "\tmodified:   " + f))
        if staged:
            out.append(("Changes to be committed:", "out"))
            out += [(s, "ok") for s in staged]
        unstaged = []
        for f in sorted(set(self.working) | set(self.index)):
            if f in self.sw_files: continue
            if f not in self.working and f in self.index: unstaged.append("\tdeleted:    " + f)
            elif f in self.working and f in self.index and self.working[f] != self.index[f]:
                unstaged.append("\tmodified:   " + f)
        if unstaged:
            out.append(("Changes not staged for commit:", "out"))
            out += [(s, "err") for s in unstaged]
        untracked = [f for f in sorted(self.working)
                     if f not in self.index and f not in head and not self._is_ignored(f)]
        if untracked:
            out.append(("Untracked files:", "out"))
            out += [("\t" + f, "err") for f in untracked]
            if not staged:
                out.append(('nothing added to commit (use "git add")', "out"))
        ignored = [f for f in sorted(self.working)
                   if f not in self.index and f not in head and self._is_ignored(f)]
        if ignored:
            out.append(("Ignored (via .gitignore): " + ", ".join(ignored), "out"))
        if not (staged or unstaged or untracked):
            out.append(("nothing to commit, working tree clean", "ok"))
        return out
    def cmd_add(self, args):
        if not args: return [("Nothing specified — maybe: git add .", "warn")]
        if any(a in ("-p", "--patch") for a in args):
            files = [f for f in sorted(self.index)
                     if f in self.working and self.working[f] != self.index[f]]
            rest = [a for a in args if not a.startswith("-") and a not in ("-p", "--patch")]
            if rest:
                want = {self._resolve_path(a) for a in rest}
                files = [f for f in files if f in want]
            if not files:
                return [("No hunks to stage — add -p works on modified tracked files", "warn")]
            q = []
            for f in files:
                q += [{"file": f, "header": h["header"], "lines": h["lines"]}
                      for h in self._hunks_for(self.index[f], self.working[f], 3)]
            if not q: return [("No changes to stage", "warn")]
            self._addp_state = {"queue": q, "staged": 0}
            return [("interactive staging — answer each hunk", "info")] + self._addp_show()
        if any(a in ("-p", "--patch", "-i", "--interactive") for a in args):
            return [("interactive patch staging isn't simulated", "warn")]
        touched = [f for f in self.working if self._needs_norm(f)]
        for f in touched:
            self.working[f] = self.working[f].replace("\r\n", "\n").replace("\r", "\n")
        pending_lfs = {f for f in self.working
                       if self._lfs_match(f) and self.working[f] != self.index.get(f)}
        out = self._add_core(args)
        if touched:
            out.append(("🧹 .gitattributes: converted CRLF → LF in " +
                        ", ".join(sorted(touched)) + " (before staging)", "info"))
        swapped = []
        for f in pending_lfs:
            if f in self.index and not self.index[f].startswith("version https://git-lfs"):
                self.index[f] = self._lfs_pointer(self.working.get(f, ""))
                swapped.append(f)
        if swapped:
            out.append(("🔧 LFS: " + str(len(swapped)) +
                        " file(s) staged as pointer(s) — real bytes live outside git", "info"))
        return out
    def _add_core(self, args):
        if args[0] in (".", "-A", "--all"):
            targets = {f: v for f, v in self.working.items() if not self._is_ignored(f)}
            if self.index == targets: return [("(nothing to stage)", "warn")]
            self.index = targets
            return [("staged all changes ✔ (respects .gitignore)", "ok")]
        if args[0] in ("-u", "--update"):
            for f in list(self.index):
                if f in self.working: self.index[f] = self.working[f]
                else: del self.index[f]
            return [("updated tracked files", "ok")]
        out = []
        for a in args:
            key = self._resolve_path(a)
            if key not in self.working:
                out.append(("fatal: pathspec '" + a + "' did not match any files", "err"))
            else:
                self.index[key] = self.working[key]
                out.append(("staged '" + key + "'", "ok"))
        return out
    def _addp_show(self):
        st = self._addp_state
        e = st["queue"][0]
        out = [("hunk in '" + e["file"] + "'   " + e["header"], "info")]
        for tag, l in e["lines"]:
            out.append((l, "out" if tag == " " else "del" if tag == "-" else "add"))
        out.append(("Stage this hunk?   y = yes · n = no · a = all remaining · q = quit", "warn"))
        return out
    def _stage_hunk(self, e):
        base = self.index.get(e["file"], "")
        new = self._hunk_apply(base, [{"lines": e["lines"]}])
        if new is None: return False
        self.index[e["file"]] = new
        self._addp_state["staged"] += 1
        return True
    def _addp_answer(self, c):
        st = self._addp_state
        if not st or not st["queue"]:
            return [("no 'git add -p' session in progress", "warn")]
        out = []
        if c == "y":
            e = st["queue"].pop(0)
            if not self._stage_hunk(e): out.append(("couldn't apply that hunk — skipped", "err"))
        elif c == "n": st["queue"].pop(0)
        elif c == "a":
            while st["queue"]: self._stage_hunk(st["queue"].pop(0))
        elif c == "q": st["queue"] = []
        elif c == "s":
            return [("s (split) isn't supported — hunks are already small", "warn")]
        else: return [("answer with y, n, a, or q", "warn")]
        if st["queue"]: return out + self._addp_show()
        out.append(("staged " + str(st["staged"]) + " hunk(s) ✔ — review with git diff --staged, then commit", "ok"))
        self._addp_state = None
        return out
    def cmd_commit(self, args):
        signed = any(a in ("-S", "--gpg-sign") or a.startswith("--gpg-sign=") for a in args)
        clean = [a for a in args if a not in ("-S", "--gpg-sign") and
                 not a.startswith("--gpg-sign=")]
        no_verify = bool({"--no-verify", "-n"} & set(clean))
        clean = [a for a in clean if a not in ("--no-verify", "-n")]
        hook_out = []
        if not no_verify:
            ok, hook_out = self._run_hook("pre-commit")
            if not ok:
                return hook_out + [("✖ pre-commit hook failed — commit blocked", "err"),
                                   ("bypass once with: git commit --no-verify (use sparingly!)", "warn")]
        out = list(hook_out)
        if signed: out.append(("🔒 GPG signature attached ✔ (simulated)", "info"))
        for pref, verb in (("--fixup=", "fixup"), ("--squash=", "squash")):
            hit = next((a for a in clean if a.startswith(pref)), None)
            if hit:
                target = self._resolve_ref(hit[len(pref):])
                if target in (None, "ambiguous"):
                    return [("fatal: bad revision '" + hit[len(pref):] + "'", "err")]
                msg = verb + "! " + self.commits[target].message.splitlines()[0]
                clean = [a for a in clean if a != hit]
                clean += ["-m", msg]
                break
        if "--dry-run" in clean:
            return [("dry-run — nothing will be committed. Status:", "info")] + \
                self.cmd_status(["-s"])
        return out + self._commit_core(clean)
    def _commit_core(self, args):
        message = None
        if "-m" in args:
            i = args.index("-m")
            if i + 1 < len(args): message = args[i + 1]
            else: return [("error: switch 'm' requires a value", "err")]
        if "-F" in args:
            i = args.index("-F")
            if i + 1 < len(args):
                key = self._resolve_path(args[i + 1])
                if key in self.working and self.working[key].strip():
                    message = self.working[key].strip().splitlines()[0]
        if any(t.startswith("-") and not t.startswith("--") and "a" in t[1:]
               for t in args) or "--all" in args:
            head_t = self.head_tree()
            for f in list(self.index):
                if f in self.working: self.index[f] = self.working[f]
                else: del self.index[f]
            for f, v in self.working.items():
                if f in self.index or f in head_t: self.index[f] = v
        allow_empty = "--allow-empty" in args
        if self.merge_state:
            is_sq = bool(self.merge_state.get("squash"))
            for f in self.merge_state["conflicts"]:
                if "<<<<<<<" in self.index.get(f, ""):
                    return [("error: unresolved conflict in '" + f + "'", "err"),
                            ("fix with: resolve " + f + " ours|theirs  →  git add " + f, "warn")]
            if is_sq:
                msg = message or ("Squash merge branch '" + self.merge_state["branch"] +
                                  "' into " + str(self.current))
                c = self._new_commit(msg, [self.head], self.index)
                self.squash_pending = None
            else:
                msg = message or ("Merge branch '" + self.merge_state["branch"] +
                                  "' into " + str(self.current))
                c = self._new_commit(msg, [self.head, self.merge_state["head"]], self.index)
            self.branches[self.current] = c.hash
            self.head, self.merge_state = c.hash, None
            self.working = dict(self.index)
            return [("[" + str(self.current) + " " + c.hash + "] " + msg, "ok")]
        if self.squash_pending and message is None:
            message = ("Squash merge branch '" + self.squash_pending["branch"] +
                       "' into " + str(self.current))
        if "--amend" in args:
            if self.head is None:
                return [("error: nothing to amend — no commits yet", "err")]
            prev = self.commits[self.head]
            if self.index == prev.tree and message is None:
                return [("nothing to amend — stage changes or add -m \"message\"", "warn")]
            msg = message or prev.message
            nc = self._new_commit(msg, list(prev.parents), dict(self.index),
                                  author=prev.author)
            self.branches[self.current] = nc.hash
            self.head = nc.hash
            self.working = dict(self.index)
            return [("[" + str(self.current) + " " + nc.hash + "] " + msg + "  (amended)", "ok"),
                    ("note: the old commit was replaced — its hash changed!", "warn")]
        head = self.head_tree()
        if self.index == head and not allow_empty:
            if self.working != self.index:
                return [("nothing added to commit (unstaged/untracked changes present)", "warn"),
                        ('stage them with "git add" — or use commit -am for tracked files', "out")]
            return [("nothing to commit, working tree clean (use --allow-empty anyway)", "warn")]
        msg = message or "(no message)"
        c = self._new_commit(msg, [self.head] if self.head else [], self.index)
        if not self.detached: self.branches[self.current] = c.hash
        self.head = c.hash
        self.working = dict(self.index)
        out = [("[" + ("detached HEAD" if self.detached else str(self.current)) +
                " " + c.hash + "] " + msg, "ok")]
        if self.squash_pending:
            self.squash_pending = None
            out.append(("(squash-merge completed — one tidy commit, no merge bubble)", "info"))
        if self.detached:
            out.append(("⚠ this commit belongs to no branch — keep it: git switch -c my-branch", "warn"))
        return out
    def cmd_log(self, args):
        if "-g" in args or "--walk-reflogs" in args: return self.cmd_reflog([])
        if "--show-signature" in args:
            res = self._log_core([a for a in args if a != "--show-signature"])
            return [("gpg: Good signature from \"" + self.user_name + "\" 🔒 (simulated)", "ok")] + res
        if "--notes" in args:
            res = self._log_core([a for a in args if a != "--notes"])
            if self.notes:
                res += [("notes exist — git show <hash> displays them", "warn")]
            return res
        if "--merges" in args or "--no-merges" in args:
            base = [a for a in args if a not in ("--merges", "--no-merges")]
            return [("log: --merges/--no-merges filtering isn't simulated —", "warn"),
                    ("hint: merge commits show two parents in --graph", "out")] + self._log_core(base)
        if "--follow" in args:
            out = self._log_core([a for a in args if a != "--follow"])
            return out + [("note: --follow (rename tracking) is a no-op here", "warn")]
        strip = [a for a in args if a in ("--decorate", "--decorate=short",
                 "--decorate=full") or a.startswith("--date=") or a.startswith("--color")]
        res = self._log_core([a for a in args if a not in strip])
        if any("%x09" in a for a in args):
            res = [(t.replace("%x09", "\t"), k) for t, k in res]
        return res
    def _log_core(self, args):
        oneline = "--oneline" in args
        graph = "--graph" in args
        all_refs = "--all" in args
        stat = "--stat" in args
        patch = "-p" in args or "--patch" in args
        rev_flag = "--reverse" in args
        name_mode = next((t for t in args if t in ("--name-only", "--name-status")), None)
        fmt = limit = author = grep = since = until = pickaxe = pathspec = None
        excl = None
        toks = list(args); i = 0
        while i < len(toks):
            t = toks[i]
            if t == "-n" and i + 1 < len(toks): limit = int(toks[i + 1]); del toks[i:i + 2]
            elif re.fullmatch(r'-\d+', t): limit = int(t[1:]); del toks[i]
            elif t.startswith("-n") and len(t) > 2 and t[2:].isdigit():
                limit = int(t[2:]); del toks[i]
            elif t.startswith("--author="): author = t[9:].strip('"'); del toks[i]
            elif t.startswith("--grep="): grep = t[7:].strip('"'); del toks[i]
            elif t.startswith("--since="): since = self._parse_since(t[8:]); del toks[i]
            elif t.startswith("--until="): until = self._parse_since(t[8:]); del toks[i]
            elif t.startswith("--format="): fmt = t[9:].strip('"'); del toks[i]
            elif t.startswith("--pretty="): fmt = t[9:].strip('"'); del toks[i]
            elif t == "-S" and i + 1 < len(toks): pickaxe = toks[i + 1]; del toks[i:i + 2]
            elif t.startswith("-S") and len(t) > 2: pickaxe = t[2:]; del toks[i]
            elif t == "--":
                if i + 1 < len(toks): pathspec = toks[i + 1]
                del toks[i:]
            else: i += 1
        unknown = [t for t in toks if t.startswith("-")]
        if unknown:
            return [("log: flag(s) not simulated: " + " ".join(unknown), "warn"),
                    ("supported: --oneline --graph --all --stat -p -n/-<n> --author= "
                     "--grep= --since= --until= -S --format= --name-only "
                     "--name-status --reverse A..B", "out")]
        pos = list(toks); starts = []
        if pos and ".." in pos[0]:
            a, b = pos[0].split("..", 1)
            ha = self.head if a == "" else self._resolve_ref(a)
            hb = self.head if b == "" else self._resolve_ref(b)
            if None in (ha, hb) or "ambiguous" in (ha, hb):
                return [("fatal: bad revision range '" + pos[0] + "'", "err")]
            starts, excl = [hb], self._ancestors(ha)
            pos = pos[1:]
        elif pos and self.head is not None and pos[0] in self.head_tree():
            pathspec = pos[0]; pos = pos[1:]
        elif pos:
            h = self._resolve_ref(pos[0])
            if h is None or h == "ambiguous":
                return [("fatal: bad revision '" + pos[0] + "'", "err")]
            starts = [h]; pos = pos[1:]
        if pos: return [("unexpected argument: " + pos[0], "err")]
        if all_refs:
            starts = [h for h in self.branches.values() if h]
            for tname, (th, _m) in self.tags.items():
                if th and th not in starts: starts.append(th)
            if self.head and self.head not in starts: starts.append(self.head)
        if not starts:
            return [("fatal: your current branch has no commits yet", "err")]
        seen, stack = set(), list(starts)
        while stack:
            h = stack.pop()
            if h in seen: continue
            seen.add(h)
            stack.extend(self.commits[h].parents)
        ordered = sorted(seen, key=lambda h: self.commits[h].seq, reverse=True)
        def keep(h):
            c = self.commits[h]
            if author and author.lower() not in c.author.lower(): return False
            if grep and grep.lower() not in c.message.lower(): return False
            if since is not None and c.date < since: return False
            if until is not None and c.date > until: return False
            if excl is not None and h in excl: return False
            if pathspec is not None:
                if not any((self.commits[p].tree if p else {}).get(pathspec) !=
                           c.tree.get(pathspec) for p in (c.parents or [None])):
                    return False
            if pickaxe is not None:
                total = lambda tree: sum(v.count(pickaxe) for v in tree.values())
                if not any(total(self.commits[p].tree if p else {}) != total(c.tree)
                           for p in (c.parents or [None])):
                    return False
            return True
        picked = [h for h in ordered if keep(h)]
        if not picked: return [("no commits matched your filters", "warn")]
        if limit: picked = picked[:limit]
        if name_mode:
            out = []
            for h in picked:
                c = self.commits[h]
                pt = self.commits[c.parents[0]].tree if c.parents else {}
                out.append(("commit " + h, "info"))
                for f in sorted(set(pt) | set(c.tree)):
                    if pt.get(f) == c.tree.get(f): continue
                    st = "A" if f not in pt else ("D" if f not in c.tree else "M")
                    out.append(((st + " " if name_mode == "--name-status" else "") + f, "out"))
            return out
        if rev_flag: picked = list(reversed(picked))
        refmap = {}
        for h in picked:
            labs = [b for b, bh in self.branches.items() if bh == h]
            labs += ["tag: " + t for t, (th, _m) in self.tags.items() if th == h]
            if h == self.head:
                if self.detached: labs.insert(0, "HEAD (detached)")
                else:
                    if self.current in labs: labs.remove(self.current)
                    labs.insert(0, "HEAD -> " + str(self.current))
            if labs: refmap[h] = "(" + ", ".join(labs) + ")"
        if graph: return self._render_graph(picked, refmap)
        out = []
        for h in picked:
            c = self.commits[h]
            refs = refmap.get(h, "")
            if fmt:
                out.append((fmt.replace("%h", c.hash[:7]).replace("%H", c.hash)
                             .replace("%an", c.author)
                             .replace("%s", c.message.splitlines()[0])
                             .replace("%ad", self._ago(c.date)), "out"))
                continue
            if oneline:
                out.append((c.hash + (" " + refs if refs else "") + " " +
                            c.message.splitlines()[0], "out"))
                continue
            out.append(("commit " + c.hash + ((" " + refs) if refs else ""), "info"))
            out.append(("Author: " + c.author + " <" + self.user_email + ">", "out"))
            out.append(("Date:   " + self._ago(c.date), "out"))
            out.append(("", "out"))
            for ln in c.message.splitlines(): out.append(("    " + ln, "out"))
            if stat or patch:
                if len(c.parents) > 1:
                    out.append(("    (merge commit — diff hidden)", "warn"))
                else:
                    pt = self.commits[c.parents[0]].tree if c.parents else {}
                    out += self._diff_lines(pt, c.tree, stat=stat, patch=patch, prefix="    ")
            out.append(("", "out"))
        return out
    def cmd_diff(self, args):
        ud = next((a for a in args if re.fullmatch(r'-U\d+', a)), None)
        word = any(a.startswith("--word-diff") for a in args)
        if ud or word:
            nctx = int(ud[2:]) if ud else 3
            clean = [a for a in args if a != ud and not a.startswith("--word-diff")]
            if "--" in clean:
                i = clean.index("--")
                paths = [self._resolve_path(p) for p in clean[i + 1:]]
                clean = clean[:i]
            else: paths = []
            staged = bool({"--staged", "--cached"} & set(clean))
            refs = [a for a in clean if not a.startswith("-")]
            trees = []
            skip = False
            for r in refs[:2]:
                if ".." in r:
                    x, y = r.split("..", 1)
                    hx = self.head if x == "" else self._resolve_ref(x)
                    hy = self.head if y == "" else self._resolve_ref(y)
                    if any(v in (None, "ambiguous") for v in (hx, hy)):
                        return [("fatal: bad range", "err")]
                    trees = [self.commits[hx].tree, self.commits[hy].tree]
                    skip = True; break
                h = self._resolve_ref(r)
                if h in (None, "ambiguous"): return [("fatal: bad revision '" + r + "'", "err")]
                trees.append(self.commits[h].tree)
            if not skip:
                if staged:
                    old = trees[0] if trees else self.head_tree(); new = self.index
                elif len(trees) == 2: old, new = trees
                elif len(trees) == 1: old, new = trees[0], self.working
                else: old, new = self.index, self.working
            else:
                old, new = trees[0], trees[1]
            out, ins, dele, nfiles = [], 0, 0, 0
            for f in sorted(set(old) | set(new)):
                o, w = old.get(f), new.get(f)
                if o == w: continue
                if paths and not any(f == p or f.startswith(p + "/") for p in paths): continue
                nfiles += 1
                out.append(("diff --git a/" + f + " b/" + f, "info"))
                if self._attr_for(f, "binary"):
                    out.append(("Binary files a/" + f + " and b/" + f + " differ", "warn")); continue
                d = difflib.unified_diff((o or "").splitlines(), (w or "").splitlines(), lineterm="")
                ins += sum(1 for l in d if l.startswith("+") and not l.startswith("+++"))
                dele += sum(1 for l in d if l.startswith("-") and not l.startswith("---"))
                for h in self._hunks_for(o, w, nctx):
                    out.append((h["header"], "info"))
                    if word:
                        i2 = 0
                        while i2 < len(h["lines"]):
                            if h["lines"][i2][0] in ("-", "+"):
                                grp = []
                                while i2 < len(h["lines"]) and h["lines"][i2][0] in ("-", "+"):
                                    grp.append(h["lines"][i2]); i2 += 1
                                out.append((self._wordify(grp), "warn"))
                            else:
                                out.append((h["lines"][i2][1], "out")); i2 += 1
                    else:
                        for tag, l in h["lines"]:
                            out.append((l, "out" if tag == " " else
                                        "add" if tag == "+" else "del"))
            if nfiles:
                out.append((" " + str(nfiles) + " file(s) changed, " + str(ins) +
                            " insertion(s), " + str(dele) + " deletion(s)", "ok"))
            return out or [("no changes", "warn")]
        return self._diff_core(args)
    def _diff_core(self, args):
        if "--" in args:
            i = args.index("--")
            before, extra_paths = args[:i], args[i + 1:]
        else: before, extra_paths = list(args), []
        staged = bool({"--staged", "--cached"} & set(before))
        do_stat = "--stat" in before
        name_only = "--name-only" in before or "--name-status" in before
        ws = not ("-w" in before or "--ignore-all-space" in before)
        refs, paths = [], [self._resolve_path(p) for p in extra_paths]
        for a in before:
            if a.startswith("-"): continue
            if ".." in a:
                x, y = a.split("..", 1)
                refs += [x or "HEAD", y or "HEAD"]
            else:
                h = self._resolve_ref(a)
                if h and h != "ambiguous": refs.append(a)
                elif self._resolve_path(a) in self.working or \
                        self._resolve_path(a) in self.index or \
                        self._resolve_path(a) in self.head_tree():
                    paths.append(self._resolve_path(a))
                else: return [("fatal: bad revision '" + a + "'", "err")]
        if len(refs) > 2:
            return [("usage: git diff [--staged] [--stat] [-w] [<ref> [<ref>]] [-- <path>]", "err")]
        trees = []
        for r in refs:
            h = self._resolve_ref(r)
            if h is None or h == "ambiguous":
                return [("fatal: bad revision '" + r + "'", "err")]
            trees.append(self.commits[h].tree)
        if staged: old = trees[0] if trees else self.head_tree(); new = self.index
        elif len(trees) == 2: old, new = trees
        elif len(trees) == 1: old, new = trees[0], self.working
        else: old, new = self.index, self.working
        if name_only:
            files = sorted(f for f in set(old) | set(new) if old.get(f) != new.get(f))
            if paths:
                files = [f for f in files
                         if any(f == p or f.startswith(p + "/") for p in paths)]
            return [(f, "out") for f in files] or [("no changes", "warn")]
        result = self._diff_lines(old, new, stat=do_stat, patch=not do_stat, ws=ws)
        if paths:
            flines, cur = [], False
            for t, k in result:
                if t.startswith("diff --git a/"):
                    f = t.split(" b/")[-1]
                    cur = any(f == p or f.startswith(p + "/") for p in paths)
                if cur: flines.append((t, k))
            result = flines
        return result or [("no changes " + ("staged" if staged else "to show"), "warn")]
    def cmd_branch(self, args):
        flags = [a for a in args if a.startswith("-")]
        pos = [a for a in args if not a.startswith("-")]
        if "--show-current" in args:
            return [("" if self.detached else str(self.current), "out")]
        if "-m" in flags or "-M" in flags:
            force = "-M" in flags
            if not pos: return [("usage: git branch -m [<old>] <new-name>", "err")]
            old = pos[0] if len(pos) > 1 else self.current
            new = pos[-1]
            if old not in self.branches: return [("error: branch '" + str(old) + "' not found", "err")]
            if new in self.branches and not force:
                return [("fatal: a branch named '" + new + "' already exists", "err")]
            self.branches[new] = self.branches.pop(old)
            if self.current == old: self.current = new
            if self.prev_branch == old: self.prev_branch = new
            if old in self.tracking: self.tracking[new] = self.tracking.pop(old)
            return [("Renamed branch '" + str(old) + "' → '" + new + "'", "ok")]
        if "-d" in flags or "-D" in flags:
            if not pos: return [("fatal: branch name required", "err")]
            out = []
            for name in pos:
                if name not in self.branches:
                    out.append(("error: branch '" + name + "' not found", "err"))
                elif name == self.current:
                    out.append(("error: cannot delete the branch you are on", "err"))
                else:
                    was = self.branches.pop(name)
                    suffix = (" (was " + was[:7] + ")") if was else ""
                    out.append(("Deleted branch " + name + suffix + ".", "ok"))
            return out
        if "--contains" in args:
            i = args.index("--contains")
            ref = args[i + 1] if i + 1 < len(args) else "HEAD"
            h = self._resolve_ref(ref)
            if not h or h == "ambiguous": return [("fatal: bad revision '" + ref + "'", "err")]
            anc = self._ancestors(h)
            rows = [(("* " if b == self.current else "  ") + b,
                     "ok" if b == self.current else "out")
                    for b in sorted(self.branches)
                    if self.branches[b] and self.branches[b] in anc]
            return rows or [("(no branches contain " + ref + ")", "warn")]
        mflag = next((f for f in ("--merged", "--no-merged") if f in args), None)
        if mflag:
            i = args.index(mflag)
            ref = "HEAD"
            if i + 1 < len(args) and not args[i + 1].startswith("-"): ref = args[i + 1]
            h = self._resolve_ref(ref)
            if not h or h == "ambiguous": return [("fatal: bad revision", "err")]
            head_anc = self._ancestors(self.head) if self.head else set()
            want_in = (mflag == "--merged")
            rows = [(("* " if b == self.current else "  ") + b,
                     "ok" if b == self.current else "out")
                    for b in sorted(self.branches)
                    if self.branches[b] and ((self.branches[b] in head_anc) == want_in)]
            return rows or [("(no branches match)", "warn")]
        list_all, list_rem = "-a" in flags, "-r" in flags
        verbose = "-v" in flags or "-vv" in flags
        if not pos or list_all or list_rem:
            out = []
            if not list_rem:
                if verbose:
                    for b in sorted(self.branches):
                        h = self.branches[b]
                        if h is None:
                            out.append((("* " if b == self.current else "  ") + b +
                                        "  (no commits yet)",
                                        "ok" if b == self.current else "out"))
                            continue
                        tr = self.tracking.get(b)
                        s = ""
                        if tr and (tr[0] + "/" + tr[1]) in self.rt:
                            rh = self.rt[tr[0] + "/" + tr[1]]
                            a = len(self._ancestors(h) - self._ancestors(rh))
                            d = len(self._ancestors(rh) - self._ancestors(h))
                            parts = (["ahead " + str(a)] if a else []) + (["behind " + str(d)] if d else [])
                            s = (" [" + tr[0] + "/" + tr[1] +
                                 (": " + ", ".join(parts) if parts else "") + "]")
                        out.append((("* " if b == self.current else "  ") + b.ljust(12) +
                                    h[:7] + " " +
                                    self.commits[h].message.splitlines()[0][:34] + s,
                                    "ok" if b == self.current else "out"))
                else:
                    out += [(("* " if b == self.current else "  ") + b,
                             "ok" if b == self.current else "out")
                            for b in sorted(self.branches)]
            if (list_all or list_rem) and self.rt:
                out += [("  " + k, "info") for k in sorted(self.rt)]
            return out or [("no branches yet — make a commit first", "warn")]
        if len(pos) >= 2:
            name, start = pos[0], pos[1]
            if name in self.branches:
                return [("fatal: a branch named '" + name + "' already exists", "err")]
            h = self._resolve_ref(start)
            if not h or h == "ambiguous": return [("fatal: bad revision '" + start + "'", "err")]
            self.branches[name] = h
            return [("created branch '" + name + "' at " + h[:7], "ok")]
        name = pos[0]
        if name in self.branches:
            return [("fatal: a branch named '" + name + "' already exists", "err")]
        if self.head is None:
            return [("fatal: not a valid object name: 'HEAD' — commit before branching", "err")]
        self.branches[name] = self.head
        return [("created branch '" + name + "'", "ok")]
    def _checkout_files(self, files, branch=None):
        tree = self.commits[self.branches[branch]].tree if branch else self.index
        src_name = branch or "HEAD (index)"
        out = []
        for f in files:
            key = self._resolve_path(f)
            if key not in tree:
                out.append(("error: pathspec '" + f + "' did not match any file in " + src_name, "err"))
                continue
            self.working[key] = tree[key]
            if branch: self.index[key] = tree[key]
            out.append(("restored '" + key + "' from " + src_name, "ok"))
        return out
    def cmd_checkout(self, args, verb):
        args = ["--detach" if a == "-d" else a for a in args]
        if "--orphan" in args:
            name = next((a for a in args if not a.startswith("-")), None)
            if not name: return [("usage: git " + verb + " --orphan <new-branch>", "err")]
            keep = {f: v for f, v in self.working.items()
                    if f not in self.index and f not in self.head_tree()}
            self.current, self.head, self.detached = name, None, False
            self.branches[name] = None
            self.working, self.index = dict(keep), {}
            return [("Switched to a new orphan branch '" + name + "'", "ok"),
                    ("History is empty — the first commit starts from scratch", "info"),
                    ("(classic use: a fresh gh-pages branch)", "out")]
        if "-t" in args or "--track" in args:
            name = next((a for a in args if not a.startswith("-") and "/" in a), None)
            if not name or "/" not in name:
                return [("usage: git " + verb + " -t origin/<branch>", "err")]
            remote, rb = name.split("/", 1)
            rkey = remote + "/" + rb
            if rkey not in self.rt:
                return [("fatal: '" + name + "' is not a remote branch — git fetch first", "err")]
            if rb in self.branches:
                return [("fatal: a branch named '" + rb + "' already exists", "err")]
            self.branches[rb] = self.rt[rkey]
            self.tracking[rb] = (remote, rb)
            return [("branch '" + rb + "' set up to track '" + rkey + "' ✔", "ok")] + \
                self._checkout_core([rb], verb)
        if not args:
            return [("usage: git " + verb + " <branch> | -b <new> | --detach <c> | - | [--] <file>", "err")]
        if args[0] == "-":
            if not self.prev_branch:
                return [("fatal: no previous branch to jump back to", "err")]
            args = [self.prev_branch]
        if args[0] in ("-b", "-c"):
            if len(args) < 2: return [("fatal: missing branch name", "err")]
            name = args[1]
            if name in self.branches:
                return [("fatal: a branch named '" + name + "' already exists", "err")]
            if self.head is None:
                return [("fatal: make your first commit before creating branches", "err")]
            self.branches[name] = self.head
            args = [name]
        if "--" in args:
            i = args.index("--")
            branch = next((a for a in args[:i] if not a.startswith("-")), None)
            if branch and branch not in self.branches:
                return [("fatal: invalid reference: " + branch, "err")]
            return self._checkout_files(args[i + 1:], branch)
        detach = "--detach" in args
        name = next((a for a in args if not a.startswith("-")), None)
        if name is None: return [("fatal: missing branch or commit", "err")]
        ctx = self._wt_context
        if name in self.branches and not detach:
            occupied = ({self._main_current or self.current} if ctx is None else set()) | \
                       {w["branch"] for p, w in self.worktrees.items() if p != ctx}
            if not (ctx is None and name == self.current and not self.detached) \
                    and name in occupied and name != self.current:
                return [("fatal: '" + name + "' is already checked out in another worktree", "err"),
                        ("work on it there:  git -C <path> <cmd>   or remove:  git worktree remove <path>", "out")]
        key = self._resolve_path(name)
        if not detach and name not in self.branches and \
                (key in self.index or key in self.working):
            return self._checkout_files([name])
        return self._checkout_core(args, verb)
    def _checkout_core(self, args, verb):
        if args and args[0] in ("-b", "-c") and len(args) > 1:
            name = args[1]
            if name not in self.branches:
                if self.head is None:
                    return [("fatal: make your first commit first", "err")]
                self.branches[name] = self.head
            args = [name]
        if not args: return [("usage: git " + verb + " <branch> | -b <new> | --detach <c>", "err")]
        detach = "--detach" in args
        name = next((a for a in args if not a.startswith("-")), None)
        if name is None: return [("fatal: missing branch or commit", "err")]
        if not detach and not self.detached and name in self.branches and name == self.current:
            return [("Already on '" + name + "'", "warn")]
        if not self._clean_for_switch():
            return [("error: your local changes would be overwritten by switching", "err"),
                    ("commit first (git add → git commit) — or git stash", "warn")]
        untracked = {f: c for f, c in self.working.items()
                     if f not in self.index and f not in self.head_tree()}
        old = None if self.detached else self.current
        if name in self.branches:
            self.current, self.head, self.detached = name, self.branches[name], False
            where = "branch '" + name + "'"
        else:
            h = self._resolve_ref(name)
            if h is None or h == "ambiguous":
                return [("fatal: invalid reference: " + name, "err")]
            self.head, self.detached = h, True
            where = "detached HEAD at " + h[:7]
        tree = self.head_tree()
        self.working, self.index = dict(tree), dict(tree)
        self.working.update(untracked)
        self._reflog(self.head, "checkout", "moving from " + str(old) + " to " + name)
        if old and old != name: self.prev_branch = old
        if self.detached:
            return [("Note: switching to '" + name + "' — 'detached HEAD' state.", "warn"),
                    ("New commits belong to no branch (git switch -c <name> keeps them).", "out"),
                    ("Switched to " + where, "ok")]
        return [("Switched to " + where, "ok")]
    def cmd_restore(self, args):
        staged_flag = "--staged" in args
        src = None
        if "--source" in args:
            i = args.index("--source")
            if i + 1 < len(args): src = args[i + 1]
        files = [a for a in args if not a.startswith("-") and a != src]
        if not files:
            return [("usage: git restore [--staged] [--source <ref>] <file>", "err")]
        src_tree = None
        if src:
            h = self._resolve_ref(src)
            if h is None or h == "ambiguous": return [("fatal: bad revision '" + src + "'", "err")]
            src_tree = self.commits[h].tree
        out = []
        for f in files:
            key = self._resolve_path(f)
            if staged_flag:
                base = src_tree if src_tree is not None else self.head_tree()
                if key in self.index:
                    if key in base: self.index[key] = base[key]
                    else: del self.index[key]
                    out.append(("unstaged '" + key + "'", "ok"))
                else: out.append(("'" + key + "' is not staged", "warn"))
            elif src_tree is not None:
                if key not in src_tree:
                    out.append(("error: pathspec '" + f + "' not in " + src, "err"))
                else:
                    self.working[key] = src_tree[key]
                    out.append(("restored '" + key + "' from " + src, "ok"))
            elif key in self.index:
                self.working[key] = self.index[key]
                out.append(("restored '" + key + "' from the staging area", "ok"))
            elif key in self.head_tree():
                self.working[key] = self.head_tree()[key]
                out.append(("restored '" + key + "' from HEAD", "ok"))
            else:
                out.append(("fatal: pathspec '" + f + "' did not match any files", "err"))
        return out
    def cmd_reset(self, args):
        pos = [a for a in args if not a.startswith("-")]
        if pos:
            resolved = [self._resolve_ref(p) for p in pos]
            if all(r in (None, "ambiguous") for r in resolved) and \
                    all(self._resolve_path(p) in self.index or
                        self._resolve_path(p) in self.head_tree() for p in pos):
                head_t = self.head_tree()
                for f in pos:
                    key = self._resolve_path(f)
                    if key in self.index:
                        if key in head_t: self.index[key] = head_t[key]
                        else: del self.index[key]
                out = [("Unstaged changes after reset:", "out")]
                for f in sorted(self.index):
                    if f in self.working and self.working[f] != self.index[f]:
                        out.append(("\tmodified:   " + f, "err"))
                return out
        mode = "--mixed"
        for m in ("--soft", "--mixed", "--hard"):
            if m in args: mode = m; break
        ref = pos[0] if pos else "HEAD"
        h = self._resolve_ref(ref)
        if h is None or h == "ambiguous":
            return [("fatal: bad revision '" + ref + "'", "err")]
        before = self.head
        tree = self.commits[h].tree
        if not self.detached: self.branches[self.current] = h
        self.head = h
        if mode == "--mixed": self.index = dict(tree)
        elif mode == "--hard":
            keep = {f: v for f, v in self.working.items()
                    if f not in self.index and f not in tree}
            self.working = dict(tree); self.working.update(keep)
            self.index = dict(tree)
        self._reflog(h, "reset", "moving to " + h)
        if before: self.orig_head = before
        out = [("HEAD is now at " + h[:7] + " " + self.commits[h].message.splitlines()[0], "ok")]
        if mode == "--soft": out.append(("changes stay staged — re-commit whenever", "out"))
        elif mode == "--hard":
            out.append(("⚠ tracked changes after that point were discarded", "warn"))
        return out
    def cmd_merge(self, args):
        if args and args[0] == "--abort":
            tree = self.head_tree()
            self.working, self.index, self.merge_state = dict(tree), dict(tree), None
            return [("Merge aborted; working tree restored.", "ok")]
        if args and args[0] == "--continue":
            if self.merge_state or self.squash_pending: return self.cmd_commit([])
            return [("fatal: There is no merge to continue (MERGE_HEAD missing).", "err")]
        if self.merge_state:
            return [("error: conclude the current merge first (commit, or --abort)", "err")]
        if not args:
            return [("usage: git merge [--no-ff|--squash|--ff-only|-s ours|-X ours|theirs] <branch>", "err")]
        strategy = None
        if "-s" in args and args.index("-s") + 1 < len(args):
            strategy = args[args.index("-s") + 1]
        xopt = None
        for flag in ("-X", "--strategy-option"):
            if flag in args and args.index(flag) + 1 < len(args):
                xopt = args[args.index(flag) + 1]
        msg = None
        if "-m" in args and args.index("-m") + 1 < len(args):
            msg = args[args.index("-m") + 1]
        noff = "--no-ff" in args
        squash = "--squash" in args
        ffonly = "--ff-only" in args
        name = next((a for a in args if not a.startswith("-") and
                     a not in (strategy, xopt)), None)
        if name is None: return [("fatal: merge needs a branch name", "err")]
        if name == self.current and not self.detached:
            return [("fatal: cannot merge a branch into itself", "err")]
        if name not in self.branches:
            return [("merge: " + name + " - not something we can merge", "err")]
        other = self.branches[name]
        if other is None or other == self.head: return [("Already up to date.", "ok")]
        if self.head is not None and self._merge_base(self.head, other) is None \
                and "--allow-unrelated-histories" not in args and strategy != "ours":
            return [("fatal: refusing to merge unrelated histories", "err"),
                    ("these two lines of history share no common ancestor —", "warn"),
                    ("if you really mean it:  git merge --allow-unrelated-histories " + name, "out")]
        if self.head is None or self.head in self._ancestors(other):
            if squash:
                tree = self.commits[other].tree
                self.working, self.index = dict(tree), dict(tree)
                self.squash_pending = {"branch": name}
                return [("Squash commit -- not updating HEAD", "warn"),
                        ("finish with:  git commit  (one tidy commit)", "out")]
            if noff:
                m = msg or ("Merge branch '" + name + "' into " + str(self.current))
                c = self._new_commit(m, [self.head, other], self.commits[other].tree)
                self.branches[self.current] = c.hash; self.head = c.hash
                self.working, self.index = dict(c.tree), dict(c.tree)
                return [("Merge made by explicit --no-ff.", "ok"),
                        ("[" + str(self.current) + " " + c.hash + "] " + m, "ok")]
            old, self.head = self.head, other
            self.branches[self.current] = other
            tree = self.head_tree()
            self.working, self.index = dict(tree), dict(tree)
            return [("Updating " + (old or "") + ".." + other, "out"), ("Fast-forward ⏩", "ok")]
        if ffonly: return [("fatal: Not possible to fast-forward, aborting.", "err")]
        if other in self._ancestors(self.head): return [("Already up to date.", "ok")]
        base = self._merge_base(self.head, other)
        base_t = self.commits[base].tree if base else {}
        ours = self.commits[self.head].tree
        theirs = self.commits[other].tree
        merged, conflicts, taken = dict(ours), [], 0
        for f in sorted(set(ours) | set(theirs) | set(base_t)):
            b, o, t = base_t.get(f), ours.get(f), theirs.get(f)
            if o == t: continue
            if b == o:
                if strategy == "ours": taken += 1; continue
                if t is None: merged.pop(f, None)
                else: merged[f] = t
            elif b != t:
                if strategy == "ours" or xopt == "ours": taken += 1; continue
                if xopt == "theirs":
                    taken += 1
                    if t is None: merged.pop(f, None)
                    else: merged[f] = t
                else: conflicts.append(f)
        if conflicts:
            for f in conflicts:
                self.working[f] = ("<<<<<<< HEAD\n" + (ours.get(f) or "") +
                                   "\n=======\n" + (theirs.get(f) or "") +
                                   "\n>>>>>>> " + name)
            self.index = dict(merged)
            kept = []
            for f in conflicts:
                if self._attr_for(f, "merge") == "ours":
                    self.working[f] = ours.get(f, ""); self.index[f] = ours.get(f, "")
                    continue
                self.index[f] = ours.get(f) or ""
                kept.append(f)
            self.merge_state = {"branch": name, "head": other,
                                "conflicts": kept, "theirs": dict(theirs), "squash": squash}
            out = [("Auto-merging…", "out")]
            out += [("CONFLICT (content): Merge conflict in " + f, "err") for f in kept]
            out += [("Automatic merge failed; fix conflicts and commit the result.", "err"),
                    ("1) cat <file>  2) resolve <file> ours|theirs  3) git add <file>  4) git commit", "warn")]
            return out
        if squash:
            self.working, self.index = dict(merged), dict(merged)
            self.squash_pending = {"branch": name}
            return [("Squash commit -- not updating HEAD", "warn"),
                    ("finish with:  git commit", "out")]
        note = ("merge -s ours: kept OUR tree; ignored " + str(taken) +
                " change(s) from '" + name + "'" if strategy == "ours" else
                ("-X " + str(xopt) + ": auto-resolved " + str(taken) +
                 " conflict(s) via the " + str(xopt) + " side") if xopt else None)
        m = msg or ("Merge branch '" + name + "' into " + str(self.current))
        c = self._new_commit(m, [self.head, other], merged)
        self.branches[self.current] = c.hash; self.head = c.hash
        self.working, self.index = dict(merged), dict(merged)
        out = []
        if note: out.append((note, "info"))
        out += [("Merge made by the 'ort' strategy.", "ok"),
                ("[" + str(self.current) + " " + c.hash + "] " + m, "ok")]
        applied = self._rerere_autostep()
        return out
    def cmd_rebase(self, args):
        if not args or args[0] in ("--abort", "--continue", "--edit-todo"):
            if not args or args[0] == "--abort":
                if not self.rebase_state: return [("no rebase in progress", "warn")]
                cur, head = self.rebase_state["saved"]
                self.current, self.head = cur, head
                tree = self.head_tree()
                self.working, self.index = dict(tree), dict(tree)
                self.rebase_state = None
                return [("Rebase aborted — back on '" + str(cur) + "', everything intact.", "ok")]
            if args and args[0] == "--edit-todo":
                if not self.rebase_state: return [("no interactive rebase in progress", "warn")]
                return self._print_todo()
            if not self.rebase_state: return [("no rebase in progress", "warn")]
            return self._rebase_exec()
        if "--root" in args:
            return [("git rebase --root isn't simulated — rebase onto a branch instead", "warn")]
        if "--onto" in args:
            rest = [a for a in args if not a.startswith("-")]
            if len(rest) < 2:
                return [("usage: git rebase --onto <newbase> <upstream> [<branch>]", "err")]
            onto_name, up_name = rest[0], rest[1]
            branch_name = rest[2] if len(rest) > 2 else None
            if branch_name:
                if branch_name not in self.branches:
                    return [("fatal: invalid branch: " + branch_name, "err")]
                if branch_name != self.current or self.detached:
                    sw = self.cmd_checkout([branch_name], "switch")
                    if any(k == "err" for _t, k in sw): return sw
            onto = self._resolve_ref(onto_name); up = self._resolve_ref(up_name)
            if any(x in (None, "ambiguous") for x in (onto, up)):
                return [("fatal: bad revision", "err")]
            up_anc = self._ancestors(up)
            if self.head in up_anc: return [("Current branch is up to date.", "ok")]
            todo, h = [], self.head
            while h is not None and h not in up_anc:
                todo.append(h); c = self.commits[h]
                h = c.parents[0] if c.parents else None
            todo.reverse()
            if not self._clean_for_switch():
                return [("error: commit or stash your changes before rebasing", "err")]
            self.rebase_state = {"todo": [["pick", x, self.commits[x].message] for x in todo],
                                 "onto": onto, "saved": (self.current, self.head)}
            return [("Rebasing " + up_name + ".." + str(self.current) + " onto " + onto_name + "…", "info")] + \
                self._rebase_exec()
        if "--autosquash" in args:
            refs = [a for a in args if not a.startswith("-")]
            if not refs: return [("usage: git rebase -i --autosquash <base>", "err")]
            up = self._resolve_ref(refs[0])
            if up in (None, "ambiguous"): return [("fatal: bad revision", "err")]
            up_anc, todo, h = self._ancestors(up), [], self.head
            while h is not None and h not in up_anc:
                todo.append(["pick", h, self.commits[h].message])
                c = self.commits[h]; h = c.parents[0] if c.parents else None
            todo.reverse()
            plan = []
            for item in todo:
                m0 = re.match(r'^(fixup|squash)! (.+)$', item[2].splitlines()[0])
                if not m0: plan.append(item); continue
                idx = next((k for k, e in enumerate(plan)
                            if e[2].splitlines()[0] == m0.group(2)), None)
                if idx is None: plan.append(item)
                else: plan.insert(idx + 1, [m0.group(1), item[1], item[2]])
            if not self._clean_for_switch():
                return [("error: commit or stash your changes before rebasing", "err")]
            self.rebase_state = {"todo": plan, "onto": up, "saved": (self.current, self.head)}
            out = [("autosquash plan:", "info")]
            return out + self._print_todo() + self._rebase_exec()
        junk = ("--keep-empty", "--force-rebase", "--no-ff", "-f", "--fork-point",
                "--no-fork-point", "--ignore-date")
        clean = [a for a in args if a not in junk and
                 not a.startswith("--committer") and not a.startswith("--rebase-merges")]
        return self._rebase_core(clean)
    def _rebase_core(self, args):
        if not args: return [("usage: git rebase <branch> | -i HEAD~<n>", "err")]
        interactive = "-i" in args or "--interactive" in args
        refs = [a for a in args if not a.startswith("-")]
        if not refs: return [("fatal: rebase needs an upstream — e.g. git rebase main", "err")]
        onto = self._resolve_ref(refs[0])
        if onto is None or onto == "ambiguous":
            return [("fatal: invalid upstream '" + refs[0] + "'", "err")]
        if self.head is None: return [("fatal: no commits on this branch yet", "err")]
        if onto == self.head or onto in self._ancestors(self.head):
            return [("Current branch " + str(self.current) + " is up to date.", "ok")]
        if self.head in self._ancestors(onto):
            self.head = onto
            if not self.detached: self.branches[self.current] = onto
            tree = self.commits[onto].tree
            self.working, self.index = dict(tree), dict(tree)
            self._reflog(onto, "rebase", "(fast-forward)")
            return [("Fast-forwarded " + str(self.current) + " to " + refs[0] + " ⏩", "ok")]
        anc_onto = self._ancestors(onto)
        todo, h = [], self.head
        while h is not None and h not in anc_onto:
            todo.append(h); c = self.commits[h]
            h = c.parents[0] if c.parents else None
        if h is None: return [("fatal: no common ancestor — cannot rebase", "err")]
        todo.reverse()
        if not self._clean_for_switch():
            return [("error: commit or stash your changes before rebasing", "err")]
        self.rebase_state = {"todo": [["pick", x, self.commits[x].message] for x in todo],
                             "onto": onto, "saved": (self.current, self.head)}
        if interactive:
            return [("Interactive rebase started (sandbox edition) ✏️", "info"),
                    ("Real git opens your $EDITOR with this todo list:", "out")] + \
                self._print_todo() + \
                [("Edit it with:   pick | drop | squash | fixup | reword <n> [message]", "warn"),
                 ("  e.g.   drop 2        squash 2        reword 1 a clearer message", "out"),
                 ("Then:   git rebase --continue     (or --abort to bail)", "warn")]
        return self._rebase_exec()
    def _rebase_exec(self):
        st = self.rebase_state
        new_head, last_new = st["onto"], None
        for action, h, msg in st["todo"]:
            c = self.commits[h]
            ptree = self.commits[c.parents[0]].tree if c.parents else {}
            cur_tree = self.commits[new_head].tree
            changed = {f for f in set(ptree) | set(c.tree)
                       if ptree.get(f) != c.tree.get(f)}
            conflicts = [f for f in sorted(changed)
                         if f in cur_tree and cur_tree[f] != ptree.get(f)
                         and cur_tree[f] != c.tree.get(f)]
            if action == "drop": continue
            if conflicts:
                cur, head = st["saved"]
                self.current, self.head = cur, head
                tree = self.head_tree()
                self.working, self.index = dict(tree), dict(tree)
                self.rebase_state = None
                return [("error: could not apply " + h[:7] + "… " +
                         c.message.splitlines()[0], "err"),
                        ("conflict in: " + ", ".join(conflicts), "err"),
                        ("hint: git rebase --abort restores everything", "warn")]
            tree = dict(cur_tree)
            for f in changed:
                if f in c.tree: tree[f] = c.tree[f]
                else: tree.pop(f, None)
            if action in ("squash", "fixup") and last_new is not None:
                last_new.tree = tree
                if action == "squash" and msg:
                    last_new.message = last_new.message + " + " + msg.splitlines()[0]
            else:
                use_msg = msg if action == "reword" and msg else c.message
                nc = self._new_commit(use_msg, [new_head], tree, author=c.author)
                nc.branch = self.current
                new_head, last_new = nc.hash, nc
        cur, _ = st["saved"]
        self.current = cur
        self.branches[cur] = new_head
        self.head = new_head
        tree = self.commits[new_head].tree
        self.working, self.index = dict(tree), dict(tree)
        self._reflog(new_head, "rebase", "finished onto " + st["onto"][:7])
        self.rebase_state = None
        return [("Successfully rebased and updated refs/heads/" + str(cur) + ".", "ok")]
    def cmd_cherry_pick(self, args):
        no_commit = bool({"-n", "--no-commit"} & set(args))
        note = "-x" in args
        refs = [a for a in args if not a.startswith("-")]
        if not refs:
            return [("usage: git cherry-pick [-n] [-x] <commit> | <a>..<b>", "err")]
        if self.index != self.head_tree():
            return [("error: your index has uncommitted changes — commit or git reset first", "err")]
        want = []
        for r in refs:
            if ".." in r:
                a, b = r.split("..", 1)
                ha = self.head if a == "" else self._resolve_ref(a)
                hb = self.head if b == "" else self._resolve_ref(b)
                if any(x in (None, "ambiguous") for x in (ha, hb)):
                    return [("fatal: bad revision range '" + r + "'", "err")]
                excl, chain, h = self._ancestors(ha), [], hb
                while h and h not in excl:
                    chain.append(h); c = self.commits[h]
                    h = c.parents[0] if c.parents else None
                want += reversed(chain)
            else:
                h = self._resolve_ref(r)
                if h in (None, "ambiguous"): return [("fatal: bad revision '" + r + "'", "err")]
                want.append(h)
        want = [h for h in want if h != self.head]
        if not want: return [("Nothing to pick — range is empty", "warn")]
        cur_tree, last_new, out = dict(self.head_tree()), self.head, []
        for h in want:
            c = self.commits[h]
            ptree = self.commits[c.parents[0]].tree if c.parents else {}
            changed = {f for f in set(ptree) | set(c.tree)
                       if ptree.get(f) != c.tree.get(f)}
            conflicts = [f for f in sorted(changed)
                         if f in cur_tree and cur_tree[f] != ptree.get(f)
                         and cur_tree[f] != c.tree.get(f)]
            if conflicts:
                return out + [("error: could not apply " + h[:7] + "… " +
                               c.message.splitlines()[0], "err"),
                              ("conflict in: " + ", ".join(conflicts), "err"),
                              ("undo partial picks: git reset --hard " + last_new[:7], "warn")]
            tree = dict(cur_tree)
            for f in changed:
                if f in c.tree: tree[f] = c.tree[f]
                else: tree.pop(f, None)
            cur_tree = tree
            msg = c.message.splitlines()[0] if c.message else "(picked)"
            if no_commit:
                out.append(("applied " + h[:7] + " " + msg + "  (staged, not committed)", "ok"))
                continue
            nc = self._new_commit(msg, [last_new], tree, author=c.author)
            nc.branch = self.current
            last_new = nc.hash
            out.append(("[" + str(self.current) + " " + nc.hash + "] " + msg, "ok"))
            if note: out.append(("(cherry picked from commit " + h + ")", "out"))
        if no_commit:
            self.working, self.index = dict(cur_tree), dict(cur_tree)
            out.append(("-n: changes are staged; finish with git commit", "warn"))
        else:
            self.branches[self.current] = last_new
            self.head = last_new
            self.working, self.index = dict(cur_tree), dict(cur_tree)
            out.append(("picked " + str(len(want)) + " commit(s) ✔", "info"))
        return out
    def cmd_stash(self, args):
        if args and args[0] == "branch":
            rest = [a for a in args[1:] if not a.startswith("-")]
            if not rest: return [("usage: git stash branch <name> [<stash>]", "err")]
            name = rest[0]
            n = self._stash_index(rest[1]) if len(rest) > 1 else 0
            if n is None or n >= len(self.stash): return [("no such stash entry", "err")]
            e = self.stash[n]
            if name in self.branches:
                return [("fatal: a branch named '" + name + "' already exists", "err")]
            if not self._clean_for_switch():
                return [("error: commit or stash your current changes first", "err")]
            base = e["base"]
            self.branches[name] = base
            self.current, self.head, self.detached = name, base, False
            tree = self.head_tree()
            self.working, self.index = dict(tree), dict(tree)
            for f, v in e["working"].items(): self.working[f] = v
            for f, v in e["index"].items(): self.index[f] = v
            self.stash.pop(n)
            return [("Switched to a new branch '" + name + "' at " + base[:7], "ok"),
                    ("applied the stash here ✔ — commit when ready", "ok")]
        known = {"push", "save", "list", "show", "pop", "apply", "drop", "clear"}
        rest = [a for a in args if not a.startswith("-")]
        if rest and rest[0] in known: sub, tail = rest[0], rest[1:]
        else: sub, tail = "push", rest
        if sub in ("push", "save"):
            msg = args[args.index("-m") + 1] if "-m" in args and \
                args.index("-m") + 1 < len(args) else None
            incl_u = "-u" in args or "--include-untracked" in args
            head = self.head_tree()
            untracked = {f: v for f, v in self.working.items()
                         if f not in self.index and f not in head}
            dirty = (self.index != head) or any(
                f in self.index and self.working.get(f) != self.index.get(f)
                for f in self.index if f not in self.sw_files)
            if not dirty and not (incl_u and untracked):
                return [("No local changes to save", "warn")]
            label = ("On " + str(self.current) + ": " +
                     (msg or ("WIP on " + str(self.current) +
                              (": " + self.head[:7] if self.head else ""))))
            self.stash.insert(0, {"index": dict(self.index), "working": dict(self.working),
                                  "base": self.head, "msg": label})
            keep = {} if incl_u else untracked
            self.working = dict(head); self.working.update(keep)
            self.index = dict(head)
            return [("Saved working directory and index state " + label, "ok")]
        if sub == "list":
            if not self.stash: return [("No stash entries.", "warn")]
            return [("stash@{" + str(i) + "}: " + e["msg"], "out")
                    for i, e in enumerate(self.stash)]
        if sub == "show":
            n = self._stash_index(tail[0]) if tail else 0
            if n is None or n >= len(self.stash): return [("no such stash entry", "err")]
            e = self.stash[n]
            base = self.commits[e["base"]].tree if e["base"] else {}
            if "-p" in args or "--patch" in args:
                out = self._diff_lines(base, e["working"], stat=False, patch=True)
                return out or [("stash is identical to its base", "warn")]
            out = self._diff_lines(base, e["working"], stat=True, patch=False)
            return out or [("stash is identical to its base", "warn")]
        if sub in ("pop", "apply"):
            if not self.stash: return [("No stash entries found.", "err")]
            n = 0
            if tail:
                n = self._stash_index(tail[0])
                if n is None or n >= len(self.stash):
                    return [("no such stash entry: " + tail[0], "err")]
            e = self.stash[n]
            for f, v in e["working"].items(): self.working[f] = v
            for f, v in e["index"].items(): self.index[f] = v
            out = [("applied stash@{" + str(n) + "}", "ok")]
            if sub == "pop":
                self.stash.pop(n)
                out.append(("Dropped refs/stash@{" + str(n) + "}", "out"))
            return out
        if sub == "drop":
            if not self.stash: return [("No stash entries found.", "err")]
            n = self._stash_index(tail[0]) if tail else 0
            if n is None or n >= len(self.stash): return [("no such stash entry", "err")]
            self.stash.pop(n)
            return [("Dropped refs/stash@{" + str(n) + "}", "ok")]
        if sub == "clear":
            self.stash = []; return [("Cleared all stash entries.", "ok")]
        return [("usage: git stash [push [-m msg] [-u]] | list | show [-p] | pop | apply | drop | branch | clear", "err")]
    def cmd_tag(self, args):
        if "-v" in args or "--verify" in args:
            name = next((a for a in args if not a.startswith("-")), None)
            if name not in self.tags: return [("error: tag '" + str(name) + "' not found.", "err")]
            h, msg = self.tags[name]
            out = [("object " + h, "out"), ("type commit", "out"), ("tag " + name, "out"),
                   ("tagger " + self.user_name + " <" + self.user_email + ">", "out")]
            if msg: out.append(("", "out")); out += [(l, "out") for l in msg.splitlines()]
            out += [("gpg: Good signature from \"" + self.user_name + "\" 🔒", "ok"),
                    ("(signatures are simulated in the sandbox)", "warn")]
            return out
        if "--contains" in args:
            i = args.index("--contains")
            ref = args[i + 1] if i + 1 < len(args) and not args[i + 1].startswith("-") else "HEAD"
            h = self._resolve_ref(ref)
            if h in (None, "ambiguous"): return [("fatal: bad revision '" + ref + "'", "err")]
            anc = self._ancestors(h)
            names = sorted(t for t, (th, _m) in self.tags.items() if th in anc)
            return [(t, "out") for t in names] or [("(no tags contain " + ref + ")", "warn")]
        if "-f" in args or "--force" in args:
            msg = args[args.index("-m") + 1] if "-m" in args and \
                args.index("-m") + 1 < len(args) else None
            pos = [a for a in args if not a.startswith("-") and a != msg]
            if pos and pos[0] in self.tags:
                del self.tags[pos[0]]
                return [("replacing tag '" + pos[0] + "'", "warn")] + \
                    self._tag_core([a for a in args if a not in ("-f", "--force")])
        if "-s" in args or "--sign" in args:
            args = [("-a" if a == "-s" else a) for a in args if a != "--sign"]
            return [("🔒 tag will be signed ✔ (simulated)", "info")] + self._tag_core(args)
        return self._tag_core(args)
    def _tag_core(self, args):
        flags = [a for a in args if a.startswith("-")]
        pos = [a for a in args if not a.startswith("-")]
        msg = None
        if "-m" in args and args.index("-m") + 1 < len(args):
            msg = args[args.index("-m") + 1]
        pos = [a for a in pos if a != msg]
        if "-l" in flags or "--list" in flags or not pos:
            pat = pos[0] if pos else "*"
            names = sorted(t for t in self.tags if fnmatch.fnmatch(t, pat))
            if not names:
                return [("no tags yet — try: git tag -a v1.0 -m \"first release\"", "warn")]
            return [(t + ("   " + self.tags[t][1].splitlines()[0]
                          if self.tags[t][1] else ""), "out") for t in names]
        if "-d" in flags or "--delete" in flags:
            if pos[0] not in self.tags: return [("error: tag '" + pos[0] + "' not found.", "err")]
            del self.tags[pos[0]]
            return [("Deleted tag '" + pos[0] + "'", "ok")]
        name = pos[0]
        ref = pos[1] if len(pos) > 1 else "HEAD"
        h = self._resolve_ref(ref)
        if h is None or h == "ambiguous": return [("fatal: bad revision '" + ref + "'", "err")]
        if name in self.tags: return [("fatal: tag '" + name + "' already exists", "err")]
        annotated = bool({"-a", "--annotate"} & set(flags))
        self.tags[name] = (h, msg if annotated else None)
        return [("created " + ("annotated" if annotated else "lightweight") +
                 " tag '" + name + "' at " + h[:7], "ok")]
    def cmd_show(self, args):
        ref = next((a for a in args if not a.startswith("-")), None)
        if ref and ":" in ref:
            r, p = ref.split(":", 1)
            if p[:1].isdigit() and ":" in p: p = p.split(":", 1)[1]
            if r == "": tree, src = self.index, "the index"
            else:
                h = self._resolve_ref(r)
                if not h or h == "ambiguous": return [("fatal: bad revision '" + r + "'", "err")]
                tree, src = self.commits[h].tree, r
            if p not in tree: return [("fatal: path '" + p + "' does not exist in " + src, "err")]
            return [(src + ":" + p, "info")] + \
                [(l, "out") for l in (tree[p].splitlines() or [""])]
        stat = "--stat" in args
        ref = ref or "HEAD"
        out = []
        if ref in self.tags and self.tags[ref][1]:
            out += [("tag " + ref, "info"), ("    " + self.tags[ref][1], "out"), ("", "out")]
        h = self._resolve_ref(ref)
        if h is None or h == "ambiguous": return [("fatal: bad revision '" + ref + "'", "err")]
        c = self.commits[h]
        refs = [b for b, bh in self.branches.items() if bh == h]
        refs += ["tag: " + t for t, (th, _m) in self.tags.items() if th == h]
        out.append(("commit " + h + ((" (" + ", ".join(refs) + ")") if refs else ""), "info"))
        out.append(("Author: " + c.author, "out"))
        out.append(("Date:   " + self._ago(c.date), "out"))
        out.append(("", "out"))
        for ln in c.message.splitlines(): out.append(("    " + ln, "out"))
        out.append(("", "out"))
        if len(c.parents) > 1:
            out.append(("    (merge commit — showing diff vs first parent)", "warn"))
        pt = self.commits[c.parents[0]].tree if c.parents else {}
        out += self._diff_lines(pt, c.tree, stat=stat, patch=not stat, prefix="    ")
        if h in self.notes:
            out += [("Notes:", "info")] + [("    " + l, "out") for l in self.notes[h].splitlines()]
        return out
    def cmd_blame(self, args):
        ign, rest, i = set(), [], 0
        sugar = {"-w", "-M", "-C", "-l", "-e", "--show-email", "--show-name", "--show-number"}
        rng = None
        while i < len(args):
            a = args[i]
            if a == "-L" and i + 1 < len(args):
                m = re.fullmatch(r'(\d+)(?:,(\d+))?', args[i + 1])
                if m: rng = (int(m.group(1)), int(m.group(2)) if m.group(2) else None)
                i += 2; continue
            if a == "--ignore-rev" and i + 1 < len(args):
                h = self._resolve_ref(args[i + 1])
                if h and h != "ambiguous": ign.add(h)
                i += 2; continue
            if a.startswith("--ignore-rev="):
                h = self._resolve_ref(a.split("=", 1)[1])
                if h and h != "ambiguous": ign.add(h)
                i += 1; continue
            if a not in sugar: rest.append(a)
            i += 1
        for l in self.working.get(".git-blame-ignore-revs", "").splitlines():
            l = l.strip()
            if l and not l.startswith("#"):
                h = self._resolve_ref(l[:12])
                if h and h != "ambiguous": ign.add(h)
        out = self._blame_core(rest)
        if rng and out and out[0][1] == "out":
            a, b = rng
            out = out[a - 1:(b if b else len(out))]
        if not ign: return out
        fixed = []
        for t, k in out:
            head, sep, tail = t.partition(") ")
            if sep:
                hh, _, meta = head.partition(" (")
                if hh in ign and self.commits.get(hh) and self.commits[hh].parents:
                    pc = self.commits[self.commits[hh].parents[0]]
                    ln = meta.rsplit(" ", 1)[-1]
                    t = (self.commits[hh].parents[0] + " (" + pc.author + " " +
                         self._ago(pc.date) + " " + ln + ") " + tail)
            fixed.append((t, k))
        return fixed + [("attribution via --ignore-rev — " + str(len(ign)) +
                         " revision(s) hidden", "info")]
    def _blame_core(self, args):
        f = next((a for a in args if not a.startswith("-")), None)
        if not f: return [("usage: git blame <file>", "err")]
        key = self._resolve_path(f)
        if key not in self.working: return [("fatal: no such path '" + f + "'", "err")]
        chain, h = [], self.head
        while h and key in self.commits[h].tree:
            chain.append((h, self.commits[h].tree[key]))
            c = self.commits[h]
            h = c.parents[0] if c.parents else None
        chain.reverse()
        prev_lines, prev_attr = [], []
        for ch, content in chain:
            cur = content.splitlines() or [""]
            free = list(range(len(prev_lines)))
            attr = []
            for ln in cur:
                idx = next((i for i in free if prev_lines[i] == ln), None)
                if idx is not None:
                    free.remove(idx); attr.append(prev_attr[idx])
                else: attr.append(ch)
            prev_lines, prev_attr = cur, attr
        cur = (self.working.get(key) or "").splitlines() or [""]
        free = list(range(len(prev_lines)))
        rows = []
        for n, ln in enumerate(cur, 1):
            idx = next((i for i in free if prev_lines[i] == ln), None)
            if idx is not None:
                hc = prev_attr[idx]
                who = self.commits[hc].author + " " + self._ago(self.commits[hc].date)
            else: hc, who = "0000000", "Not Committed Yet"
            rows.append(hc + " (" + who + " " + str(n) + ") " + ln)
        return [(r, "out") for r in rows]
    def cmd_grep(self, args):
        icase = "-i" in args
        pat = next((a for a in args if not a.startswith("-")), None)
        if not pat: return [("usage: git grep [-i] <pattern>", "err")]
        try: rx = re.compile(pat, re.IGNORECASE if icase else 0)
        except re.error: return [("invalid pattern", "err")]
        out = []
        for f in sorted(self.working):
            if self._is_ignored(f): continue
            for n, line in enumerate(self.working[f].splitlines(), 1):
                if rx.search(line): out.append((f + ":" + str(n) + ": " + line, "out"))
        return out or [("no matches for '" + pat + "'", "warn")]
    def cmd_reflog(self, args):
        clean = [a for a in args if a != "show" and not a.startswith("-") and not a.isdigit()]
        if not self.reflog: return [("reflog is empty", "warn")]
        n = len(self.reflog)
        out = [(self.reflog[i][0] + " HEAD@{" + str(n - 1 - i) + "}: " +
                self.reflog[i][1] + ": " + self.reflog[i][2], "out")
               for i in range(n - 1, -1, -1)]
        if clean:
            out += [("note: per-ref reflogs aren't kept here — '" + clean[0] +
                     "' shares HEAD's journal", "info")]
        return out
    def cmd_revert(self, args):
        mainline = None
        for pref in ("-m", "--mainline"):
            if pref in args:
                i = args.index(pref)
                if i + 1 < len(args):
                    try: mainline = int(args[i + 1])
                    except ValueError: return [("error: -m expects a number (1 or 2)", "err")]
                args = args[:i] + args[i + 2:]
                break
        if mainline is not None:
            no_commit = bool({"-n", "--no-commit"} & set(args))
            pos = [a for a in args if not a.startswith("-")]
            if not pos:
                return [("usage: git revert [-n] -m <1|2> <merge-commit>", "err")]
            h = self._resolve_ref(pos[0])
            if h in (None, "ambiguous"): return [("fatal: bad revision '" + pos[0] + "'", "err")]
            c = self.commits[h]
            if len(c.parents) < 2:
                return [("error: commit " + h[:7] + " is not a merge but option -m given", "err")]
            if mainline not in (1, 2):
                return [("error: commit " + h[:7] + " does not have parent number " + str(mainline), "err")]
            if self.index != self.head_tree():
                return [("error: commit or stash your changes first", "err")]
            ptree = self.commits[c.parents[mainline - 1]].tree
            tree = dict(self.head_tree())
            for f in set(ptree) | set(c.tree):
                if ptree.get(f) != c.tree.get(f):
                    if f in ptree: tree[f] = ptree[f]
                    else: tree.pop(f, None)
            first = 'Revert "' + c.message.splitlines()[0] + '"'
            if no_commit:
                self.working, self.index = dict(tree), dict(tree)
                return [("reverted merge " + h[:7] + " relative to parent #" +
                         str(mainline) + " (staged, -n)", "warn")]
            nc = self._new_commit(first + "\n\nThis reverts merge " + h +
                                  " (keeping parent #" + str(mainline) + ").",
                                  [self.head], tree)
            self.branches[self.current] = nc.hash; self.head = nc.hash
            self.working, self.index = dict(tree), dict(tree)
            return [("[" + str(self.current) + " " + nc.hash + "] " + first, "ok"),
                    ("This reverts merge " + h + ".", "out"),
                    ("re-landing later: git revert " + nc.hash + "  (revert the revert)", "info")]
        no_commit = bool({"-n", "--no-commit"} & set(args))
        pos = [a for a in args if not a.startswith("-")]
        if not no_commit:
            if len(pos) <= 1: return self._revert_core(args)
            out = []
            for r in pos: out += self._revert_core([r])
            return out
        if not pos: return [("usage: git revert -n <commit>...", "err")]
        if self.index != self.head_tree():
            return [("error: commit or stash your changes first", "err")]
        tree, out = dict(self.head_tree()), []
        for r in pos:
            h = self._resolve_ref(r)
            if h in (None, "ambiguous"):
                return out + [("fatal: bad revision '" + r + "'", "err")]
            c = self.commits[h]
            ptree = self.commits[c.parents[0]].tree if c.parents else {}
            for f in set(ptree) | set(c.tree):
                if ptree.get(f) != c.tree.get(f):
                    if f in ptree: tree[f] = ptree[f]
                    else: tree.pop(f, None)
            out.append(("reverted " + h[:7] + " — " + c.message.splitlines()[0], "ok"))
        self.working, self.index = dict(tree), dict(tree)
        out.append(("-n: reversal is staged — git commit when ready", "warn"))
        return out
    def _revert_core(self, args):
        if not args: return [("usage: git revert <commit>", "err")]
        if self.index != self.head_tree():
            return [("error: commit or stash your changes first", "err")]
        h = self._resolve_ref(args[0])
        if h is None or h == "ambiguous": return [("fatal: bad revision '" + args[0] + "'", "err")]
        c = self.commits[h]
        ptree = self.commits[c.parents[0]].tree if c.parents else {}
        tree = dict(self.head_tree())
        for f in set(ptree) | set(c.tree):
            if ptree.get(f) != c.tree.get(f):
                if f in ptree: tree[f] = ptree[f]
                else: tree.pop(f, None)
        msg = "Revert \"" + c.message.splitlines()[0] + "\""
        nc = self._new_commit(msg, [self.head], tree)
        self.branches[self.current] = nc.hash; self.head = nc.hash
        self.working, self.index = dict(tree), dict(tree)
        return [("[" + str(self.current) + " " + nc.hash + "] " + msg, "ok"),
                ("This reverts commit " + h + ".", "out")]
    def cmd_clean(self, args):
        if "-X" in args:
            dry, force = "-n" in args, "-f" in args
            head = self.head_tree()
            targets = [f for f in sorted(self.working)
                       if f not in self.index and f not in head and self._is_ignored(f)]
            if not targets: return [("no ignored files to clean 🧹", "ok")]
            if not dry and not force:
                return [("fatal: clean requires -f (preview with -n)", "err")]
            if not dry:
                for f in targets: del self.working[f]
            verb = "Would remove" if dry else "Removing"
            return [(verb + " " + f + "  (ignored)", "warn" if dry else "out") for f in targets]
        dry = "-n" in args or "--dry-run" in args
        force = "-f" in args
        inc_ignored = "-x" in args
        head = self.head_tree()
        targets = [f for f in sorted(self.working)
                   if f not in self.index and f not in head
                   and (inc_ignored or not self._is_ignored(f))]
        if not targets: return [("Nothing to clean — no untracked files 🧹", "ok")]
        if not dry and not force:
            return [("fatal: clean requires -f (refusing to delete without it)", "err"),
                    ("tip: preview first with  git clean -n", "warn")]
        verb = "Would remove" if dry else "Removing"
        if not dry:
            for f in targets: del self.working[f]
        return [(verb + " " + f, "warn" if dry else "out") for f in targets]
    def cmd_config(self, args):
        flat = [a for a in args if not a.startswith("-")]
        args = [a for a in args if a not in ("--global", "--local", "--system")]
        if flat and flat[0] == "core.hooksPath" and len(args) > 1:
            self.hooks_path = args[-1].strip('"').rstrip("/")
            return [("hooks path → " + self.hooks_path + " (pre-commit will run from there)", "ok")]
        if flat and flat[0].startswith("rerere."):
            return [("rerere is always-on in this sandbox ✔ (real git: rerere.enabled true)", "ok")]
        if "--unset" in args:
            key = next((a for a in args if not a.startswith("-")), "")
            if key.startswith("alias."):
                name = key[6:]
                if name in self.aliases:
                    del self.aliases[name]; return [("alias '" + name + "' removed", "ok")]
                return [("error: no such alias '" + name + "'", "err")]
            if key == "user.name": self.user_name = "You"; return [("user.name reset", "ok")]
            if key == "user.email":
                self.user_email = "you@example.com"; return [("user.email reset", "ok")]
            return [("'" + key + "' is not set", "warn")]
        if not args or args[0] in ("--list", "--get"):
            key = next((a for a in args if not a.startswith("-")), None)
            if key:
                val = {"user.name": self.user_name, "user.email": self.user_email}.get(key)
                if val: return [(val, "out")]
                if key.startswith("alias.") and key[6:] in self.aliases:
                    return [(self.aliases[key[6:]], "out")]
                return [("'" + key + "' is not set", "warn")]
            rows = [("user.name=" + self.user_name, "out"),
                    ("user.email=" + self.user_email, "out")]
            rows += [("alias." + k + "=" + v, "ok") for k, v in sorted(self.aliases.items())]
            return [("sandbox config:", "info")] + rows
        key = args[0]
        if key.startswith("alias."):
            name = key[6:]
            if len(args) > 1:
                self.aliases[name] = " ".join(args[1:])
                return [("set alias: git " + name + "  →  git " + self.aliases[name], "ok")]
            if name in self.aliases: return [("git " + name + " = " + self.aliases[name], "out")]
            return [("error: no alias named '" + name + "'", "err")]
        if len(args) > 1:
            val = " ".join(args[1:])
            if key == "user.name": self.user_name = val
            elif key == "user.email": self.user_email = val
            return [("(" + key + " = " + val + ")", "ok")]
        val = {"user.name": self.user_name, "user.email": self.user_email}.get(key)
        return [(val, "out")] if val else [("'" + key + "' is not set", "warn")]
    def cmd_shortlog(self, args=None):
        args = args or []
        counts_only = "-s" in args
        all_refs = "--all" in args
        starts = ([h for h in self.branches.values() if h] if all_refs
                  else ([self.head] if self.head else []))
        if not starts: return [("fatal: no commits yet", "err")]
        seen, stack = set(), list(starts)
        while stack:
            h = stack.pop()
            if h in seen: continue
            seen.add(h); stack.extend(self.commits[h].parents)
        groups = {}
        for h in seen:
            c = self.commits[h]
            groups.setdefault(c.author, []).append(
                "      " + c.message.splitlines()[0] + " (" + h[:7] + ")")
        order = sorted(groups, key=lambda a: -len(groups[a]))
        if counts_only:
            return [(str(len(groups[a])).rjust(5) + "  " + a, "out") for a in order]
        out = []
        for a in order:
            out.append((a + " (" + str(len(groups[a])) + "):", "info"))
            out += [(l, "out") for l in sorted(groups[a])]
        return out
    def cmd_describe(self, args):
        rest = [a for a in args if not (a.startswith("--abbrev=") or
                a.startswith("--candidates") or a in ("--tags", "--all", "--long", "--dirty"))]
        if not self.tags: return [("fatal: no tags — describe needs at least one tag", "err")]
        if self.head is None: return [("fatal: no commits yet", "err")]
        anc = self._ancestors(self.head)
        best = None
        for name, (h, _m) in self.tags.items():
            if h in anc:
                seq = self.commits[h].seq
                if best is None or seq > best[1]: best = (name, seq, h)
        if best is None: return [("fatal: no tag in this branch's history", "err")]
        name, _, th = best
        if th == self.head: return [(name, "ok")]
        extra = len(anc - self._ancestors(th))
        res = name + "-" + str(extra) + "-g" + self.head[:7]
        if "--abbrev=0" in args: res = name
        return [(res, "ok")]
    def cmd_gc(self, args=None):
        return [("Enumerating objects: " + str(len(self.commits) * 4) + ", done.", "out"),
                ("Nothing to collect — this sandbox keeps every commit 🧹", "ok"),
                ("(real gc prunes unreachable objects once reflog entries expire)", "info")]
    def cmd_fsck(self, args=None):
        return [("Checking objects: 100% done.", "out"),
                ("No dangling commits found (reflog protects them anyway).", "ok")]
    def cmd_archive(self, args):
        ref = next((a for a in args if not a.startswith("-")), "HEAD")
        h = self._resolve_ref(ref)
        tree = self.commits[h].tree if h and h != "ambiguous" else {}
        return [("simulated: wrote project-" + (h[:7] if h else "tree") +
                 ".tar.gz with " + str(len(tree)) + " files", "ok"),
                ("(real: git archive -o proj.zip HEAD — export without history)", "info")]
    def cmd_bisect(self, args):
        sub = args[0] if args else ""
        if sub == "start":
            bad = self._resolve_ref(args[1]) if len(args) > 1 else self.head
            good = self._resolve_ref(args[2]) if len(args) > 2 else None
            if bad is None or bad == "ambiguous": return [("fatal: bad revision", "err")]
            self.bisect = {"bad": bad, "good": {good} if good else set()}
            if not good:
                return [("status: waiting for a good commit — run: git bisect good <older-ref>", "warn")]
            return self._bisect_step()
        if sub in ("good", "bad"):
            if not self.bisect: return [("run 'git bisect start' first", "err")]
            h = self._resolve_ref(args[1]) if len(args) > 1 else self.head
            if h is None or h == "ambiguous": return [("fatal: bad revision", "err")]
            if sub == "good":
                if h == self.bisect["bad"]:
                    return [("that commit is marked bad — contradiction 🤨", "err")]
                self.bisect["good"].add(h)
            else: self.bisect["bad"] = h
            return self._bisect_step()
        if sub == "reset":
            self.bisect = None
            if self.detached and self.current in self.branches:
                self.detached = False
                self.head = self.branches[self.current]
                tree = self.head_tree()
                self.working, self.index = dict(tree), dict(tree)
            return [("bisect reset — back on '" + str(self.current) + "'", "ok")]
        if sub == "log":
            if not self.bisect: return [("no bisect in progress", "warn")]
            out = [("git bisect start", "out"), ("git bisect bad " + self.bisect["bad"], "out")]
            out += [("git bisect good " + g, "out") for g in sorted(self.bisect["good"])]
            return out
        return [("usage: git bisect start [<bad>] [<good>] | good|bad [<ref>] | reset | log", "err")]
    def _bisect_step(self):
        st = self.bisect
        bad_anc = self._ancestors(st["bad"])
        good_anc = set()
        for g in st["good"]: good_anc |= self._ancestors(g)
        if st["bad"] in good_anc:
            return [("contradiction: a 'good' commit contains the 'bad' one", "err")]
        unknown = bad_anc - good_anc
        if len(unknown) <= 1:
            h = next(iter(unknown)) if unknown else st["bad"]
            return [("🏆 first bad commit found: " + h, "ok"),
                    ("    " + self.commits[h].message.splitlines()[0], "out"),
                    ("run 'git bisect reset' when done", "warn")]
        ordered = sorted(unknown, key=lambda x: self.commits[x].seq)
        cand = ordered[(len(ordered) - 1) // 2]
        if not self._clean_for_switch():
            return [("error: commit or stash your changes before bisecting", "err")]
        self.detached = True
        self.head = cand
        tree = self.commits[cand].tree
        self.working, self.index = dict(tree), dict(tree)
        return [("Bisecting: " + str(len(unknown) - 1) + " revisions left to test", "info"),
                ("[detached at " + cand[:7] + "] " + self.commits[cand].message.splitlines()[0], "out"),
                ("test it, then:  git bisect good    or    git bisect bad", "warn")]
    def cmd_rm(self, args):
        cached = "--cached" in args
        files = [a for a in args if not a.startswith("-")]
        if not files: return [("usage: git rm [--cached] <file>", "err")]
        out = []
        for a in files:
            key = self._resolve_path(a)
            if key not in self.working and key not in self.index:
                out.append(("fatal: pathspec '" + a + "' did not match any files", "err")); continue
            if not cached: self.working.pop(key, None)
            if key in self.index: del self.index[key]
            out.append(("untracked '" + key + "' (file kept on disk — add to .gitignore?)"
                        if cached else "removed '" + key + "'", "ok"))
        return out
    def cmd_mv(self, args):
        pos = [a for a in args if not a.startswith("-")]
        if len(pos) != 2: return [("usage: git mv <source> <destination>", "err")]
        src, dst = self._resolve_path(pos[0]), self._resolve_path(pos[1])
        if src not in self.working:
            return [("fatal: bad source, '" + pos[0] + "' does not exist", "err")]
        d = dst + ("/" + src.rsplit("/", 1)[-1] if self._is_dir(dst) else "")
        self._ensure_parent(d)
        self.working[d] = self.working.pop(src)
        if src in self.index: del self.index[src]
        self.index[d] = self.working[d]
        return [("renamed '" + src + "' → '" + d + "'  (change staged ✔)", "ok")]
    # ---------------- remotes ----------------
    def cmd_remote(self, args):
        sub = args[0] if args else ""
        dflt = "origin" if "origin" in self.remotes else (next(iter(self.remotes), ""))
        if sub in ("", "-v", "--verbose"):
            if not self.remotes:
                return [("(no remotes — add one:  git remote add origin <url>)", "warn")]
            out = []
            for n, u in sorted(self.remotes.items()):
                out += [(n + "  " + u + " (fetch)", "out"), (n + "  " + u + " (push)", "out")]
            return out
        if sub == "add":
            if len(args) < 3: return [("usage: git remote add <name> <url>", "err")]
            name, url = args[1], args[2]
            if name in self.remotes: return [("error: remote " + name + " already exists.", "err")]
            self.remotes[name] = url
            return [("remote '" + name + "' added — simulated server ready ✔", "ok"),
                    ("next:  git push -u " + name + " " + str(self.current), "out")]
        if sub in ("remove", "rm"):
            name = args[1] if len(args) > 1 else ""
            if name not in self.remotes: return [("error: No such remote: '" + name + "'", "err")]
            del self.remotes[name]
            for k in [k for k in self.rt if k.startswith(name + "/")]: del self.rt[k]
            for k in [k for k in self.remote_branches if k.startswith(name + "/")]:
                del self.remote_branches[k]
            self.tracking = {b: t for b, t in self.tracking.items() if t[0] != name}
            return [("Removed remote '" + name + "'.", "ok")]
        if sub == "rename":
            if len(args) < 3: return [("usage: git remote rename <old> <new>", "err")]
            old, new = args[1], args[2]
            if old not in self.remotes: return [("error: No such remote: '" + old + "'", "err")]
            self.remotes[new] = self.remotes.pop(old)
            for k in [k for k in self.rt if k.startswith(old + "/")]:
                self.rt[new + k[len(old):]] = self.rt.pop(k)
            for k in [k for k in self.remote_branches if k.startswith(old + "/")]:
                self.remote_branches[new + k[len(old):]] = self.remote_branches.pop(k)
            self.tracking = {b: ((new, rb) if r == old else (r, rb))
                             for b, (r, rb) in self.tracking.items()}
            return [("Renamed remote '" + old + "' → '" + new + "'", "ok")]
        if sub == "prune":
            remote = args[1] if len(args) > 1 else dflt
            if remote not in self.remotes: return [("fatal: no such remote: " + remote, "err")]
            pre = remote + "/"
            gone = [k for k in self.rt if k.startswith(pre) and k not in self.remote_branches]
            for k in gone: del self.rt[k]
            out = [("Pruning " + remote, "info")]
            out += [(" - [deleted]         (none) -> " + k, "warn") for k in gone]
            return out or [("everything up to date (nothing to prune)", "ok")]
        if sub == "show":
            remote = args[1] if len(args) > 1 else dflt
            if remote not in self.remotes: return [("fatal: no such remote: " + remote, "err")]
            out = [("* remote " + remote, "info"),
                   ("  Fetch URL: " + self.remotes[remote], "out"),
                   ("  Push  URL: " + self.remotes[remote], "out"),
                   ("  Remote branches:", "out")]
            any_b = False
            for k in sorted(self.remote_branches):
                if k.startswith(remote + "/"):
                    any_b = True
                    b = k[len(remote) + 1:]
                    tracked = (not self.detached and self.current in self.tracking and
                               self.tracking[self.current] == (remote, b))
                    out.append(("    " + b + ("   (tracked by '" + str(self.current) + "')"
                                if tracked else ""), "out"))
            if not any_b:
                out.append(("    (the remote has no branches yet — push!)", "warn"))
            return out
        if sub == "get-url" and len(args) > 1:
            return [(self.remotes.get(args[1], "error: No such remote"), "out")]
        if sub == "set-url" and len(args) > 2:
            if args[1] not in self.remotes: return [("error: No such remote: '" + args[1] + "'", "err")]
            self.remotes[args[1]] = args[2]
            return [("(URL updated)", "ok")]
        return [("usage: git remote [-v | add | rename | remove | prune | show | get-url | set-url]", "err")]
    def cmd_push(self, args):
        ok, hook_out = self._run_hook("pre-push")
        if not ok:
            return hook_out + [("✖ pre-push hook failed — push blocked", "err"),
                               ("fix the problem (pushes have no --no-verify)", "warn")]
        lease = "--force-with-lease" in args
        rest = [a for a in args if a != "--force-with-lease"]
        if lease:
            pos0 = [a for a in rest if not a.startswith("-")]
            remote = pos0[0] if (pos0 and pos0[0] in self.remotes) else \
                ("origin" if "origin" in self.remotes else "")
            rb = None
            if len(pos0) > 1 and pos0[1] not in self.tags: rb = pos0[1].split(":")[-1]
            elif not self.detached: rb = self.current
            if not remote or rb is None:
                return [("fatal: --force-with-lease needs an explicit branch: git push --force-with-lease <remote> <branch>", "err")]
            rkey = remote + "/" + rb
            known = self.rt.get(rkey)
            if known is None:
                return [("To " + self.remotes[remote], "out"),
                        (" ! [rejected]        " + rb + " (stale lease — no fetched view of " + rkey + ")", "err"),
                        ("hint: git fetch first, confirm it's safe, retry", "out")]
            actual = self.remote_branches.get(rkey)
            if actual != known:
                return [("To " + self.remotes[remote], "out"),
                        (" ! [rejected]        " + rb + " (lease failed — remote moved past " +
                         known[:7] + " since your last fetch)", "err"),
                        ("error: someone pushed meanwhile — fetch & rebase, don't stomp their work", "err")]
            rest = [a for a in rest if a not in ("-f", "--force")]
            rest = ["--force"] + rest
        return self._push_core(rest)
    def _push_core(self, args):
        force = "--force" in args or "-f" in args
        set_up = "-u" in args or "--set-upstream" in args
        push_tags = "--tags" in args
        pos = [a for a in args if not a.startswith("-") and
               not (a.startswith(":") and len(a) > 1)]
        dele = None
        if "--delete" in args or "-d" in args:
            dele = pos[-1] if pos else None
            pos = pos[:-1]
        elif any(a.startswith(":") and len(a) > 1 and ":" not in a[1:] for a in args):
            dele = next(a[1:] for a in args if a.startswith(":") and ":" not in a[1:])
        dremote = "origin"
        if not self.detached and self.current in self.tracking:
            dremote = self.tracking[self.current][0]
        remote = pos[0] if pos else dremote
        if remote not in self.remotes:
            return [("fatal: '" + remote + "' does not appear to be a git repository", "err"),
                    ("create one first:  git remote add " + remote + " <url>", "out")]
        url = self.remotes[remote]
        if dele:
            rkey = remote + "/" + dele
            if rkey in self.remote_branches:
                del self.remote_branches[rkey]; self.rt.pop(rkey, None)
                self.tracking.pop(dele, None)
                return [("To " + url, "out"), (" - [deleted]         " + dele, "ok")]
            return [("error: remote branch not found: " + dele, "err")]
        if push_tags:
            out = [("To " + url, "out")]; moved = False
            for t in sorted(self.tags):
                h = self.tags[t][0]
                if self.remote_tags.get(t) != h:
                    moved = True; was = self.remote_tags.get(t)
                    self.remote_tags[t] = h
                    out.append(("* [new tag]         " + t + " -> " + t, "ok") if was is None
                               else ("   " + was[:9] + ".." + h[:9] + "  " + t + " -> " + t, "ok"))
            return out if moved else [("Everything up-to-date", "warn")]
        refspec = pos[1] if len(pos) > 1 else (None if self.detached else self.current)
        if refspec is None:
            return [("fatal: detached HEAD — name a branch: git push <remote> <branch>", "err")]
        if refspec in self.tags:
            h = self.tags[refspec][0]
            if self.remote_tags.get(refspec) == h: return [("Everything up-to-date", "warn")]
            self.remote_tags[refspec] = h
            return [("To " + url, "out"), ("* [new tag]         " + refspec + " -> " + refspec, "ok")]
        lb, rb = (refspec.split(":", 1) + [refspec])[:2] if ":" in refspec else (refspec, refspec)
        if lb not in self.branches or self.branches[lb] is None:
            return [("error: src refspec " + lb + " does not match any", "err")]
        lhash = self.branches[lb]
        rkey = remote + "/" + rb
        rhash = self.remote_branches.get(rkey)
        if rhash == lhash: return [("Everything up-to-date", "warn")]
        fast = rhash is None or rhash in self._ancestors(lhash)
        if not fast and not force:
            return [("To " + url, "out"),
                    (" ! [rejected]        " + lb + " -> " + rb + " (fetch first)", "err"),
                    ("error: failed to push some refs to '" + url + "'", "err"),
                    ("hint: the remote contains work you don't have —", "warn"),
                    ("hint:   git pull     (integrate, then push again)", "out"),
                    ("hint:   git push --force-with-lease   (only if you really mean it ⚠)", "out")]
        sent = len(self._ancestors(lhash) - (self._ancestors(rhash) if rhash else set()))
        self.remote_branches[rkey] = lhash
        self.rt[rkey] = lhash
        if set_up: self.tracking[lb] = (remote, rb)
        out = [("Enumerating objects: " + str(max(sent * 3, 2)) + ", done.", "out"),
               ("To " + url, "info")]
        if rhash is None: out.append(("* [new branch]      " + lb + " -> " + rb, "ok"))
        elif force:
            out.append((" + " + rhash[:9] + "..." + lhash[:9] + "  " + lb + " -> " + rb +
                        "  (forced update ⚠)", "warn"))
        else: out.append(("   " + rhash[:9] + ".." + lhash[:9] + "  " + lb + " -> " + rb, "ok"))
        if set_up: out.append(("branch '" + lb + "' set up to track '" + rkey + "' ✔", "ok"))
        return out
    def _fetch(self, remote, want_tags=False):
        out = [("From " + self.remotes[remote], "out")]
        pre = remote + "/"
        changed = False
        for rkey in sorted(self.remote_branches):
            if not rkey.startswith(pre): continue
            h = self.remote_branches[rkey]
            b = rkey[len(pre):]
            old = self.rt.get(rkey)
            if old == h: continue
            changed = True
            self.rt[rkey] = h
            if old is None:
                out.append((" * [new branch]      " + b + "     -> " + rkey, "ok"))
            else:
                out.append(("   " + old[:9] + ".." + h[:9] + "  " + b + "     -> " + rkey, "out"))
        if want_tags:
            for t, h in sorted(self.remote_tags.items()):
                if t not in self.tags:
                    self.tags[t] = (h, None)
                    out.append((" * [new tag]         " + t + "     -> " + t, "ok"))
        if changed:
            ck = remote + "/" + (self.current if not self.detached else "")
            self.fetch_head = self.rt.get(ck) or self.rt[[k for k in self.rt
                                                          if k.startswith(pre)][0]]
        else:
            out.append(("(everything up to date)", "warn"))
        return out
    def cmd_fetch(self, args):
        want_tags = "--tags" in args
        prune = "--prune" in args or "-p" in args
        pos = [a for a in args if not a.startswith("-")]
        dremote = "origin"
        if not self.detached and self.current in self.tracking:
            dremote = self.tracking[self.current][0]
        if "--all" in args:
            if not self.remotes: return [("no remotes configured", "warn")]
            out = []
            for r in sorted(self.remotes): out += self._fetch(r, want_tags)
            return out
        remote = pos[0] if pos else dremote
        if remote not in self.remotes:
            return [("fatal: '" + remote + "' does not appear to be a git repository", "err")]
        out = self._fetch(remote, want_tags)
        if prune:
            pre = remote + "/"
            for k in [k for k in self.rt if k.startswith(pre) and k not in self.remote_branches]:
                del self.rt[k]
                out.append((" - [deleted]         (none) -> " + k, "warn"))
        if len(pos) > 1:
            want = pos[1]
            kept = [(t, k) for t, k in out
                    if t.startswith("From") or want in t or "up to date" in t]
            if len(kept) <= 1: kept.append(("(no updates for '" + want + "')", "warn"))
            out = kept
        return out
    def cmd_pull(self, args):
        rest = list(args)
        if "-r" in rest and "--rebase" not in rest:
            rest[rest.index("-r")] = "--rebase"
        autostash = "--autostash" in rest
        if autostash: rest.remove("--autostash")
        if "--ff-only" in rest:
            pos = [a for a in rest if not a.startswith("-")]
            tr = self.tracking.get(self.current) if not self.detached else None
            remote = pos[0] if pos else (tr[0] if tr else "origin")
            rb = pos[1] if len(pos) > 1 else (tr[1] if tr else self.current)
            rh = self.remote_branches.get(remote + "/" + rb)
            if rh and self.head and self.head not in self._ancestors(rh) and \
                    rh not in self._ancestors(self.head):
                return [("fatal: Not possible to fast-forward, aborting.", "err"),
                        ("your branch and '" + remote + "/" + rb +
                         "' have diverged — merge or rebase instead", "warn")]
        if autostash and not self._clean_for_switch():
            head_t = self.head_tree()
            self.stash.insert(0, {"index": dict(self.index), "working": dict(self.working),
                                  "base": self.head, "msg": "autostash"})
            keep = {f: v for f, v in self.working.items()
                    if f not in self.index and f not in head_t}
            self.working, self.index = dict(head_t), dict(head_t)
            out = [("Saved working directory (autostash).", "warn")]
            out += self._pull_core(rest)
            for f, v in self.stash[0]["working"].items(): self.working[f] = v
            for f, v in self.stash[0]["index"].items(): self.index[f] = v
            self.stash.pop(0)
            out.append(("Applied autostash ✔", "ok"))
            applied = self._rerere_autostep()
            return out
        res = self._pull_core(rest)
        applied = self._rerere_autostep()
        if applied:
            for f in applied:
                res.append(("Resolved '" + f + "' using previous resolution (rerere ✔)", "ok"))
            if self.merge_state and not self.merge_state["conflicts"]:
                res.append(("all conflicts auto-resolved — git commit to conclude", "warn"))
        return res
    def _pull_core(self, args):
        do_rebase = "--rebase" in args
        pos = [a for a in args if not a.startswith("-")]
        tr = self.tracking.get(self.current) if not self.detached else None
        remote = pos[0] if pos else (tr[0] if tr else "origin")
        rbranch = pos[1] if len(pos) > 1 else (tr[1] if tr else self.current)
        if remote not in self.remotes:
            return [("fatal: '" + remote + "' does not appear to be a git repository", "err"),
                    ("add one:  git remote add " + remote + " <url>", "out")]
        rkey = remote + "/" + rbranch
        out = self._fetch(remote)
        rh = self.remote_branches.get(rkey)
        if rh is None:
            out += [("There is no tracking information for the current branch.", "warn"),
                    ("publish first:  git push -u " + remote + " " + str(self.current), "out")]
            return out
        if rh == self.head or rh in self._ancestors(self.head):
            out.append(("Already up to date.", "ok")); return out
        if self.head in self._ancestors(rh):
            old = self.head
            self.head = rh
            if not self.detached: self.branches[self.current] = rh
            tree = self.commits[rh].tree
            self.working, self.index = dict(tree), dict(tree)
            self._reflog(rh, "pull", "fast-forward")
            out += [("Updating " + old[:9] + ".." + rh[:9], "out"), ("Fast-forward ⏩", "ok")]
            return out
        if not self._clean_for_switch():
            return out + [("error: your uncommitted changes would be lost —", "err"),
                          ("commit or stash first, then git pull", "warn")]
        if do_rebase:
            anc_rh = self._ancestors(rh)
            todo, h = [], self.head
            while h is not None and h not in anc_rh:
                todo.append(h); c = self.commits[h]
                h = c.parents[0] if c.parents else None
            todo.reverse()
            self.rebase_state = {"todo": [["pick", x, self.commits[x].message] for x in todo],
                                 "onto": rh, "saved": (self.current, self.head)}
            out += [("First, rewinding head to replay your work on top of it…", "out")]
            out += self._rebase_exec()
            return out
        base = self._merge_base(self.head, rh)
        base_t = self.commits[base].tree if base else {}
        ours = self.commits[self.head].tree
        theirs = self.commits[rh].tree
        merged, conflicts = dict(ours), []
        for f in sorted(set(ours) | set(theirs) | set(base_t)):
            b, o, t = base_t.get(f), ours.get(f), theirs.get(f)
            if o == t: continue
            if b == o:
                if t is None: merged.pop(f, None)
                else: merged[f] = t
            elif b != t: conflicts.append(f)
        if conflicts:
            for f in conflicts:
                self.working[f] = ("<<<<<<< HEAD\n" + (ours.get(f) or "") +
                                   "\n=======\n" + (theirs.get(f) or "") +
                                   "\n>>>>>>> " + rkey)
            self.index = dict(merged)
            for f in conflicts: self.index[f] = ours.get(f) or ""
            self.merge_state = {"branch": rkey, "head": rh,
                                "conflicts": list(conflicts), "theirs": dict(theirs)}
            out += [("CONFLICT (content): Merge conflict in " + f, "err") for f in conflicts]
            out += [("Automatic merge failed; fix conflicts and commit the result.", "err"),
                    ("1) cat <file>  2) resolve <file> ours|theirs  3) git add <file>  4) git commit", "warn")]
            return out
        msg = ("Merge branch '" + rbranch + "' of " + self.remotes[remote] +
               " into " + str(self.current))
        c = self._new_commit(msg, [self.head, rh], merged)
        self.branches[self.current] = c.hash; self.head = c.hash
        self.working, self.index = dict(merged), dict(merged)
        out += [("Merge made by the 'ort' strategy.", "ok"),
                ("[" + str(self.current) + " " + c.hash + "] " + msg, "ok")]
        return out
    def cmd_ls_files(self, args):
        cwd_pre = ("/".join(self.cwd) + "/") if self.cwd else ""
        if "-v" in args or "-t" in args:
            base = self._ls_files_core([a for a in args if a not in ("-v", "-t")])
            out = []
            for t, k in base:
                if k != "out": continue
                mark = "S" if t in self.sw_files else ("h" if t in self.au_files else "H")
                out.append((mark + " " + t, "out"))
            return out or [("(no tracked files)", "warn")]
        return self._ls_files_core(args)
    def _ls_files_core(self, args):
        cwd_pre = ("/".join(self.cwd) + "/") if self.cwd else ""
        if "-o" in args or "--others" in args:
            head = self.head_tree()
            files = [f for f in sorted(self.working)
                     if f not in self.index and f not in head and not self._is_ignored(f)]
        else: files = sorted(self.index)
        if cwd_pre:
            files = [f[len(cwd_pre):] for f in files if f.startswith(cwd_pre)]
        return [(f, "out") for f in files] or [("(no files matched)", "warn")]
    def cmd_ls_remote(self, args):
        pos = [a for a in args if not a.startswith("-")]
        dremote = "origin"
        if not self.detached and self.current in self.tracking:
            dremote = self.tracking[self.current][0]
        remote = pos[0] if pos else dremote
        if remote not in self.remotes:
            return [("fatal: '" + remote + "' does not appear to be a git repository", "err")]
        heads, tags_f = "--heads" in args, "--tags" in args
        out = [("From " + self.remotes[remote], "out")]
        for k in sorted(self.remote_branches):
            if k.startswith(remote + "/"):
                out.append((self.remote_branches[k] + "        refs/heads/" + k[len(remote) + 1:], "out"))
        for t in sorted(self.remote_tags):
            out.append((self.remote_tags[t] + "        refs/tags/" + t, "out"))
        if heads or tags_f:
            out = [(t, k) for t, k in out if k != "out" or
                   (("refs/heads/" in t) if heads and not tags_f else ("refs/tags/" in t))]
        return out or [("(the remote has no refs — push something!)", "warn")]
    # ---------------- plumbing ----------------
    def cmd_rev_parse(self, args):
        if "--git-dir" in args: return [(".git", "out")]
        if "--show-toplevel" in args: return [("~/project", "out")]
        if "--is-inside-work-tree" in args: return [("true", "out")]
        abbrev = "--abbrev-ref" in args
        toks = [a for a in args if not a.startswith("-")]
        out = []
        for t in toks:
            if abbrev:
                if t == "HEAD":
                    out.append(("HEAD" if self.detached else str(self.current), "out"))
                elif t in self.branches: out.append((t, "out"))
                else: return [("fatal: ambiguous argument '" + t + "'", "err")]
                continue
            h = self._resolve_ref(t)
            if h is None or h == "ambiguous":
                return [("fatal: ambiguous argument '" + t + "': unknown revision", "err")]
            out.append((h, "out"))
        return out or [("usage: git rev-parse [--abbrev-ref] <ref>...", "err")]
    def cmd_cat_file(self, args):
        toks = [a for a in args if not a.startswith("-")]
        mode = next((a for a in args if a in ("-t", "-p")), "-p")
        if not toks: return [("usage: git cat-file -t|-p <ref>[:<file>]", "err")]
        spec = toks[0]
        if mode == "-t":
            if ":" in spec: return [("blob", "out")]
            h = self._resolve_ref(spec)
            if not h or h == "ambiguous": return [("fatal: Not a valid object name " + spec, "err")]
            return [("commit", "out")]
        if ":" in spec:
            r, p = spec.split(":", 1)
            if p[:1].isdigit() and ":" in p: p = p.split(":", 1)[1]
            tree = self.index if r == "" else None
            src = "the index"
            if r:
                h = self._resolve_ref(r)
                if not h or h == "ambiguous": return [("fatal: bad revision '" + r + "'", "err")]
                tree, src = self.commits[h].tree, r
            if p not in tree:
                return [("fatal: path '" + p + "' does not exist in " + src, "err")]
            return [(l, "out") for l in (tree[p].splitlines() or [""])]
        return self.cmd_show([spec])
    def cmd_hash_object(self, args):
        files = [a for a in args if not a.startswith("-")]
        if not files: return [("usage: git hash-object <file>", "err")]
        key = self._resolve_path(files[0])
        if key not in self.working: return [("fatal: Cannot open '" + files[0] + "'", "err")]
        data = self.working[key]
        blob = b"blob " + str(len(data.encode())).encode() + b"\x00" + data.encode()
        return [(hashlib.sha1(blob).hexdigest(), "out"),
                ("(that's a real sha1: git hashes 'blob <size>\\0<content>')", "info")]
    def cmd_merge_base(self, args):
        pos = [a for a in args if not a.startswith("-")]
        if len(pos) < 2:
            return [("usage: git merge-base <commit1> <commit2>", "err")]
        hs = [self._resolve_ref(p) for p in pos[:2]]
        if any(h in (None, "ambiguous") for h in hs): return [("fatal: bad revision", "err")]
        b = self._merge_base(hs[0], hs[1])
        if not b: return [("fatal: no common ancestor", "err")]
        return [(b, "out"), ("(" + self.commits[b].message.splitlines()[0] + ")", "info")]
    def cmd_for_each_ref(self, args):
        out = []
        for b in sorted(self.branches):
            h = self.branches[b]
            if h: out.append((h + " commit  refs/heads/" + b, "out"))
        for r in sorted(self.rt): out.append((self.rt[r] + " commit  refs/remotes/" + r, "out"))
        for t, (th, _m) in sorted(self.tags.items()):
            out.append((th + " tag     refs/tags/" + t, "out"))
        return out or [("(no refs yet)", "warn")]
    def cmd_symbolic_ref(self, args):
        ref = next((a for a in args if not a.startswith("-")), "HEAD")
        if ref != "HEAD": return [("only HEAD is simulated", "warn")]
        if self.detached: return [("fatal: ref HEAD is not a symbolic ref", "err")]
        return [("refs/heads/" + str(self.current), "out")]
    def cmd_count_objects(self, args):
        n = len(self.commits)
        if "-v" in args:
            return [("count: " + str(n), "out"),
                    ("size: " + str(n * 120) + " bytes (simulated)", "out"),
                    ("in-pack: " + str(n), "out"), ("packs: 1", "out")]
        files = sum(len(c.tree) for c in self.commits.values())
        return [(str(n) + " objects, " + str(files) + " file versions", "out")]
    def cmd_ls_tree(self, args):
        name_only = bool({"--name-only", "--name-status"} & set(args))
        toks = [a for a in args if not a.startswith("-")]
        ref = toks[0] if toks else "HEAD"
        h = self._resolve_ref(ref)
        if h in (None, "ambiguous"): return [("fatal: Not a valid object name " + ref, "err")]
        tree = self.commits[h].tree
        if name_only: return [(f, "out") for f in sorted(tree)] or [("(empty tree)", "warn")]
        return [("100644 blob " + self._blob_sha(tree[f]) + "  " + f, "out")
                for f in sorted(tree)] or [("(empty tree)", "warn")]
    def cmd_update_ref(self, args):
        toks = [a for a in args if not a.startswith("-")]
        dele = "-d" in args
        if not toks:
            return [("usage: git update-ref [-d] refs/heads/<branch> [<newvalue>]", "err")]
        name = toks[0].split("refs/heads/")[-1]
        if dele:
            if name not in self.branches: return [("error: refname " + toks[0] + " not found", "err")]
            if name == self.current: return [("error: cannot delete the current branch", "err")]
            del self.branches[name]
            return [("Deleted ref refs/heads/" + name, "ok")]
        if len(toks) < 2: return [("fatal: <newvalue> required (or -d)", "err")]
        h = self._resolve_ref(toks[1])
        if h in (None, "ambiguous"): return [("fatal: " + toks[1] + ": not a valid SHA1", "err")]
        self.branches[name] = h
        return [("updated refs/heads/" + name + " → " + h[:7] + "  (" +
                 self.commits[h].message.splitlines()[0][:30] + ")", "ok"),
                ("(this is how reset/merge move branches under the hood)", "info")]
    def cmd_check_ignore(self, args):
        verbose = "-v" in args
        paths = [a for a in args if not a.startswith("-")]
        if not paths: return [("usage: git check-ignore [-v] <path>...", "err")]
        rules = []
        for i, raw in enumerate(self.working.get(".gitignore", "").splitlines(), 1):
            p = raw.strip()
            if p and not p.startswith(("#", "!")): rules.append((i, p.rstrip("/")))
        out, hit_any = [], False
        for a in paths:
            key = self._resolve_path(a)
            hit = None
            for ln, pat in rules:
                base = key.rsplit("/", 1)[-1]
                if fnmatch.fnmatch(key, pat) or key.startswith(pat + "/") or \
                        ("/" not in pat and fnmatch.fnmatch(base, pat)):
                    hit = (ln, pat)
            if hit:
                hit_any = True
                out.append(((".gitignore:" + str(hit[0]) + ":" + hit[1] + "\t" + key)
                            if verbose else key, "out"))
        self._status_forced = 0 if hit_any else 1
        if hit_any: return out
        return [("nothing ignored (exit status 1 — that's the real behaviour)", "warn")]
    def cmd_var(self, args):
        ident = (self.user_name + " <" + self.user_email + "> " +
                 str(int(time.time())) + " +0000")
        known = {"GIT_AUTHOR_IDENT": ident, "GIT_COMMITTER_IDENT": ident,
                 "GIT_EDITOR": self.env.get("EDITOR", "none"), "GIT_PAGER": "cat",
                 "GIT_DEFAULT_BRANCH": self.current or "main"}
        if not args: return [(k + "=" + v, "out") for k, v in sorted(known.items())]
        v = known.get(args[0])
        return [(v, "out")] if v else [("error: unknown variable: " + args[0], "err")]
    def cmd_update_index(self, args):
        out = []
        for flag, store in (("--assume-unchanged", self.au_files),
                            ("--skip-worktree", self.sw_files)):
            if flag in args:
                files = [a for a in args if not a.startswith("-")]
                if not files:
                    return [("usage: git update-index " + flag + " <file>...", "err")]
                for a in files:
                    k = self._resolve_path(a)
                    if k in self.index:
                        store.add(k); out.append(("marked '" + k + "' " + flag + " ✔", "ok"))
                    else: out.append(("error: not tracked: " + a, "err"))
                return out
            nof = "--no-" + flag[2:]
            if nof in args:
                for a in [a for a in args if not a.startswith("-")]:
                    store.discard(self._resolve_path(a))
                    out.append(("unmarked '" + a + "'", "ok"))
                return out
        return [("usage: git update-index [--assume-unchanged | --skip-worktree] <file>  (--no-<flag> to undo)", "err")]
    # ---------------- patch workflow ----------------
    def _parse_patch(self, text):
        files, cur = [], None
        for raw in text.splitlines():
            if raw.startswith("diff --git "):
                m = re.match(r'diff --git a/(.*) b/(.*)$', raw)
                cur = {"file": (m.group(2) if m else None), "hunks": [],
                       "new": False, "delete": False, "old_path": None}
                files.append(cur); continue
            if cur is None: continue
            if raw.startswith("-- "): cur = None; continue
            if raw.startswith("--- "):
                cur["old_path"] = raw[4:].split("\t")[0].strip()
            elif raw.startswith("+++ "):
                p = raw[4:].split("\t")[0].strip()
                if p == "/dev/null":
                    cur["delete"] = True
                    cur["file"] = re.sub(r'^a/', '', cur.get("old_path") or "")
                else:
                    cur["file"] = re.sub(r'^b/', '', p)
                    if cur.get("old_path") == "/dev/null": cur["new"] = True
            elif raw.startswith("@@"):
                m = re.match(r'@@ -\d+(?:,(\d+))? \+\d+(?:,(\d+))? @@', raw)
                ob = int(m.group(1)) if m and m.group(1) is not None else 1
                nb = int(m.group(2)) if m and m.group(2) is not None else 1
                cur["hunks"].append({"ob": ob, "nb": nb, "lines": []})
            elif cur["hunks"]:
                hh = cur["hunks"][-1]
                if hh["ob"] <= 0 and hh["nb"] <= 0: continue
                if raw.startswith("\\"): continue
                if raw.startswith(" ") or raw == "":
                    hh["lines"].append((" ", raw[1:] if raw else ""))
                    hh["ob"] -= 1; hh["nb"] -= 1
                elif raw.startswith("-"):
                    hh["lines"].append(("-", raw[1:])); hh["ob"] -= 1
                elif raw.startswith("+"):
                    hh["lines"].append(("+", raw[1:])); hh["nb"] -= 1
        return [f for f in files if f["file"] is not None or f["hunks"]]
    def _hunk_apply(self, base, hunks):
        lines = base.splitlines()
        res, pos = [], 0
        for hh in hunks:
            old = [t for o, t in hh["lines"] if o in (" ", "-")]
            if not old: start = pos
            else:
                start = None
                for s in range(pos, len(lines) - len(old) + 1):
                    if lines[s:s + len(old)] == old: start = s; break
                if start is None: return None
            res += lines[pos:start]
            res += [t for o, t in hh["lines"] if o == "+"]
            pos = start + len(old)
        res += lines[pos:]
        return ("\n".join(res) + "\n") if res else ""
    def _apply_patch_file(self, f, info, dry=False):
        if not f: return ("error: patch has no target file", "err")
        if info["delete"]:
            old = [t for h in info["hunks"] for o, t in h["lines"] if o in (" ", "-")]
            if self.working.get(f, "").splitlines() == old:
                if not dry: self.working.pop(f, None)
                return ("deleted " + f + ("  (dry run)" if dry else ""), "ok")
            return ("error: patch does not apply (delete mismatch): " + f, "err")
        base = self.working.get(f, self.index.get(f, ""))
        res = self._hunk_apply(base, info["hunks"])
        if res is None: return ("error: patch does not apply: " + f, "err")
        if not dry:
            if res == "" and not any(o == "+" for h in info["hunks"] for o, _t in h["lines"]):
                self.working.pop(f, None); return ("deleted " + f, "ok")
            self._ensure_parent(f); self.working[f] = res
        return ("patched " + f + ("  (dry run)" if dry else ""), "ok")
    def cmd_format_patch(self, args):
        toks = [a for a in args if not a.startswith("-")]
        limit = None
        for a in args:
            if re.fullmatch(r'-\d+', a): limit = int(a[1:])
        chain = []
        if toks:
            h = self._resolve_ref(toks[0])
            if h in (None, "ambiguous"): return [("fatal: bad revision '" + toks[0] + "'", "err")]
            excl, c = self._ancestors(h), self.head
            while c and c not in excl:
                chain.append(c); p = self.commits[c].parents
                c = p[0] if p else None
            chain.reverse()
        elif limit:
            c = self.head
            while c and len(chain) < limit:
                chain.append(c); p = self.commits[c].parents
                c = p[0] if p else None
            chain.reverse()
        else:
            return [("usage: git format-patch <since>  |  -<N>    e.g. format-patch -1", "err")]
        if not chain: return [("No commits in that range", "warn")]
        out, total = [], len(chain)
        for i, h in enumerate(chain, 1):
            c = self.commits[h]
            pt = self.commits[c.parents[0]].tree if c.parents else {}
            msg0 = c.message.splitlines()[0]
            slug = re.sub(r'[^a-z0-9]+', '-', msg0.lower()).strip('-')[:30] or "patch"
            fname = str(i).zfill(4) + "-" + slug + ".patch"
            stat = self._diff_lines(pt, c.tree, stat=True, patch=False)
            body = self._diff_lines(pt, c.tree, stat=False, patch=True)
            lines = ["From " + h + " Mon Sep 17 00:00:00 2001",
                     "From: " + c.author + " <" + self.user_email + ">",
                     "Date: " + self._ago(c.date),
                     "Subject: [PATCH " + str(i) + "/" + str(total) + "] " + msg0, "", "---"]
            lines += [t for t, _k in stat]
            lines += [""] + [t for t, _k in body]
            lines += ["-- ", "2.43.sandbox (GitLearn)", ""]
            self._ensure_parent(fname)
            self.working[fname] = "\n".join(lines)
            out.append((fname, "ok"))
        out.append(("email it (mentally) — then on any clone: git am " + fname, "info"))
        return out
    def cmd_apply(self, args):
        check = "--check" in args
        files = [a for a in args if not a.startswith("-")]
        if not files: return [("usage: git apply [--check] <patch>", "err")]
        key = self._resolve_path(files[0])
        if key not in self.working: return [("error: can't read patch file: " + files[0], "err")]
        parsed = self._parse_patch(self.working[key])
        if not parsed: return [("error: unrecognized patch format in " + files[0], "err")]
        out, ok = [], True
        for info in parsed:
            res = self._apply_patch_file(info["file"], info, dry=check)
            out.append(res)
            if res[1] == "err": ok = False
        if check:
            out.append(("--check: patch " + ("applies cleanly ✔" if ok else "DOES NOT apply ✘"),
                        "ok" if ok else "err"))
        else:
            out.append(("applied to the working tree (not staged) — git add to stage, or use git am", "info"))
        return out
    def cmd_am(self, args):
        files = [a for a in args if not a.startswith("-")]
        if not files: return [("usage: git am <patch>", "err")]
        if self.head is None: return [("error: am needs at least one existing commit", "err")]
        key = self._resolve_path(files[0])
        if key not in self.working: return [("error: can't read patch: " + files[0], "err")]
        text = self.working[key]
        author, subject = self.user_name, None
        for line in text.splitlines():
            if line.startswith("From: "):
                m = re.match(r'From:\s*(.*?)\s*<', line)
                if m: author = m.group(1)
            elif line.startswith("Subject: "):
                subject = re.sub(r'^(\[[^\]]*\]\s*)+', '', line[9:]).strip()
            elif line.strip() == "---": break
        if not subject:
            return [("error: no Subject: line — is this a format-patch file?", "err")]
        parsed = self._parse_patch(text)
        if not parsed: return [("error: no diff found in " + files[0], "err")]
        out = []
        for info in parsed:
            res = self._apply_patch_file(info["file"], info)
            out.append(res)
            if res[1] == "err": return out + [("am failed — nothing committed", "err")]
        for info in parsed:
            f = info["file"]
            if f in self.working: self.index[f] = self.working[f]
            else: self.index.pop(f, None)
        c = self._new_commit(subject, [self.head], self.index, author=author or self.user_name)
        self.branches[self.current] = c.hash; self.head = c.hash
        self.working = dict(self.index)
        out.append(("Applying: " + subject, "ok"))
        return out
    def cmd_request_pull(self, args):
        pos = [a for a in args if not a.startswith("-")]
        if len(pos) < 2: return [("usage: git request-pull <base> <url> [branch]", "err")]
        base = self._resolve_ref(pos[0])
        if base in (None, "ambiguous"): return [("fatal: bad base revision", "err")]
        branch = pos[2] if len(pos) > 2 else self.current
        excl, chain, h = self._ancestors(base), [], self.head
        while h and h not in excl:
            chain.append(h); p = self.commits[h].parents
            h = p[0] if p else None
        return [("The following changes since " + base[:7] + ":", "out"),
                ("  " + self.commits[base].message.splitlines()[0], "out"),
                ("are available in the Git repository at:", "out"),
                ("  " + pos[1] + "  " + str(branch), "info")] + \
            [("  " + x[:7] + " " + self.commits[x].message.splitlines()[0], "out")
             for x in reversed(chain)] + \
            [("(real life: email this, or open a pull request)", "warn")]
    # ---------------- notes / lfs / filter-repo / rerere / submodule -------------
    def cmd_notes(self, args):
        sub = args[0] if args else "list"
        rest_pos = [a for a in args[1:] if not a.startswith("-")] if args else []
        force = "-f" in args or "--force" in args
        msg = args[args.index("-m") + 1] if "-m" in args and \
            args.index("-m") + 1 < len(args) else None
        ref = rest_pos[0] if rest_pos else "HEAD"
        h = self._resolve_ref(ref)
        if sub == "add":
            if h in (None, "ambiguous"): return [("fatal: bad revision '" + str(ref) + "'", "err")]
            if msg is None: return [('usage: git notes add -m "text" [<commit>]', "err")]
            if h in self.notes and not force:
                return [("error: a note already exists on " + h[:7] + " — add -f to overwrite", "err")]
            self.notes[h] = msg
            return [("note attached to " + h[:7] + " ✔ (metadata only — no history rewritten)", "ok")]
        if sub == "append":
            if h in (None, "ambiguous"): return [("fatal: bad revision", "err")]
            if msg is None: return [('usage: git notes append -m "more" [<commit>]', "err")]
            self.notes[h] = (self.notes.get(h, "") + "\n" + msg).strip()
            return [("note appended ✔", "ok")]
        if sub in ("show", ""):
            if h in (None, "ambiguous"): return [("fatal: bad revision", "err")]
            if h not in self.notes: return [("(no note on " + h[:7] + ")", "warn")]
            return [(l, "out") for l in self.notes[h].splitlines()]
        if sub == "list":
            if not self.notes: return [('no notes yet — git notes add -m "JIRA-42"', "warn")]
            return [(x[:7] + "  " + t.splitlines()[0], "out") for x, t in sorted(self.notes.items())]
        if sub == "remove":
            if h in self.notes:
                del self.notes[h]; return [("note removed from " + h[:7], "ok")]
            return [("(no note on " + h[:7] + ")", "warn")]
        return [("usage: git notes [add | append | show | list | remove] [-m \"text\"] [<commit>]", "err")]
    def cmd_lfs(self, args):
        sub = args[0] if args else "env"
        if sub in ("install", "init", "env"):
            return [("Git LFS ready (simulated — always on here) ✔", "ok"),
                    ("big files → tiny pointer in git; real bytes in LFS storage", "info"),
                    ('start: git lfs track "*.psd"', "out")]
        if sub == "track":
            pats = [a for a in args[1:] if not a.startswith("-")]
            if not pats:
                if self.lfs_patterns:
                    return [("tracked: " + ", ".join(sorted(self.lfs_patterns)), "out")]
                return [('nothing tracked yet — git lfs track "*.psd"', "warn")]
            out = []
            for p in pats:
                self.lfs_patterns.add(p); out.append(("tracking " + p, "ok"))
            ga = self.working.get(".gitattributes", "")
            need = [p for p in pats if (p + " filter=lfs") not in ga]
            if need:
                self.working[".gitattributes"] = ga + "".join(
                    p + " filter=lfs diff=lfs merge=lfs -text\n" for p in need)
                out.append((".gitattributes updated — COMMIT it so teammates get LFS too", "warn"))
            return out
        if sub == "untrack":
            removed = [p for p in args[1:] if not p.startswith("-") and p in self.lfs_patterns]
            for p in removed: self.lfs_patterns.discard(p)
            return ([("untracked: " + ", ".join(removed), "ok")] if removed
                    else [("no such tracked pattern", "err")])
        if sub == "ls-files":
            files = sorted(set(self.index) | set(self.head_tree()))
            hit = [f for f in files if self._lfs_match(f)]
            return [(f + "  → pointer (" + str(len(self.index.get(f,
                        self.head_tree().get(f, "")))) + " bytes in git)", "out")
                    for f in hit] or [("no LFS-managed files staged/tracked yet", "warn")]
        if sub == "status":
            dirty = [f for f in sorted(self.working)
                     if self._lfs_match(f) and self.working[f] != self.index.get(f)]
            return [(f + "  (changed — git add stores a fresh pointer)", "out")
                    for f in dirty] or [("LFS files are in sync ✔", "ok")]
        if sub == "pointer":
            files = [a for a in args[1:] if not a.startswith("-")]
            if not files: return [("usage: git lfs pointer --file <f>", "err")]
            key = self._resolve_path(files[0])
            if key not in self.working: return [("no such file: " + files[0], "err")]
            return [("pointer git would store for " + key + ":", "info")] + \
                [(l, "out") for l in self._lfs_pointer(self.working[key]).splitlines()]
        return [("usage: git lfs [install | track | untrack | ls-files | status | pointer]", "err")]
    def cmd_filter_repo(self, args):
        paths, invert = [], "--invert-paths" in args
        i = 0
        while i < len(args):
            if args[i] == "--path" and i + 1 < len(args):
                paths.append(self._resolve_path(args[i + 1])); i += 2
            elif args[i].startswith("--path="):
                paths.append(self._resolve_path(args[i].split("=", 1)[1])); i += 1
            else: i += 1
        if not paths:
            return [("usage: git filter-repo --path <file-or-dir> [--invert-paths]", "err"),
                    ("keeps ONLY <path>; with --invert-paths it DELETES <path> from all history", "out")]
        if not self.commits: return [("fatal: nothing to rewrite — no commits", "err")]
        if not self._clean_for_switch():
            return [("error: commit or stash first — filter-repo rewrites everything", "err")]
        def wanted(f):
            hit = any(f == p or f.startswith(p + "/") for p in paths)
            return hit if not invert else (not hit)
        rewrite, n_rew = {}, 0
        for h in sorted(self.commits, key=lambda x: self.commits[x].seq):
            c = self.commits[h]
            nt = {f: v for f, v in c.tree.items() if wanted(f)}
            npar = [rewrite.get(p, p) for p in c.parents]
            if nt == c.tree and npar == c.parents:
                rewrite[h] = h; continue
            nc = Commit(c.message, npar, nt, c.branch)
            while nc.hash in self.commits:
                nc.hash = "".join(random.choice("0123456789abcdef") for _ in range(7))
            nc.seq = c.seq; nc.date = c.date; nc.author = c.author
            self.commits[nc.hash] = nc
            rewrite[h] = nc.hash; n_rew += 1
        if n_rew == 0: return [("nothing matched — history is unchanged", "warn")]
        for b in self.branches:
            if self.branches[b] in rewrite: self.branches[b] = rewrite[self.branches[b]]
        for t in self.tags:
            th, m = self.tags[t]
            if th in rewrite: self.tags[t] = (rewrite[th], m)
        if self.head in rewrite: self.head = rewrite[self.head]
        tree = self.head_tree()
        self.working, self.index = dict(tree), dict(tree)
        self._reflog(self.head, "filter-repo", "rewrote " + str(n_rew) +
                     " commit(s); old hashes still on disk")
        return [("⚠ filter-repo: " + str(n_rew) +
                 " commit(s) rewritten — every changed commit has a NEW hash", "warn"),
                ("branches & tags remapped ✔ — remotes are NOT touched (real repos: coordinated force-push)", "info"),
                ("the old commits still exist: git reflog → git reset --hard <old-hash> recovers everything", "out"),
                ("real-world last step: git gc prunes them for good", "info")]
    def cmd_rerere(self, args):
        sub = args[0] if args else "status"
        if sub in ("status", ""):
            if not self.rerere:
                return [("rerere: no recorded resolutions yet — resolve a conflict with "
                         "'resolve <file> ours|theirs' and it will be remembered", "warn")]
            out = [("recorded conflict signatures:", "info")]
            for sig in self.rerere:
                out.append(("  " + sig.splitlines()[0] + " …", "out"))
            return out + [("next identical conflict → auto-resolved ✔", "ok")]
        if sub == "diff":
            out = []
            for sig, res in self.rerere.items():
                out.append(("---- recorded resolution ----", "info"))
                out += [(l, "out") for l in (res.splitlines() or [""])]
            return out or [("nothing recorded", "warn")]
        if sub == "clear":
            n = len(self.rerere); self.rerere = {}
            return [("forgot " + str(n) + " recorded resolution(s)", "ok")]
        if sub == "forget":
            return [("forget <ref> isn't simulated — use 'git rerere clear'", "warn")]
        return [("usage: git rerere [status | diff | clear]", "err")]
    def cmd_submodule(self, args):
        sub = args[0] if args else "status"
        if sub == "add":
            rest = [a for a in args[1:] if not a.startswith("-")]
            if not rest: return [("usage: git submodule add <url> [path]", "err")]
            url = rest[0]
            path = rest[1] if len(rest) > 1 else url.rstrip("/").rsplit("/", 1)[-1]
            if path.endswith(".git"): path = path[:-4]
            if path in self.submodules:
                return [("fatal: '" + path + "' already exists in the index", "err")]
            self.submodules[path] = url
            self._ensure_parent(path + "/x")
            self.working[path + "/README.md"] = ("# submodule placeholder\nurl: " + url +
                                                 "\n(real git: an independent clone pinned to one commit)\n")
            gm = self.working.get(".gitmodules", "")
            gm += "[submodule \"" + path + "\"]\n\tpath = " + path + "\n\turl = " + url + "\n"
            self.working[".gitmodules"] = gm
            return [("Cloning into '" + path + "'… (simulated)", "out"),
                    ("added submodule '" + path + "' ← " + url, "ok"),
                    (".gitmodules written ✔ — git add . && git commit to record it", "warn")]
        if sub in ("status", ""):
            if not self.submodules:
                return [("no submodules — try: git submodule add <url> <path>", "warn")]
            return [(" " + "0" * 40 + " " + p + "  (pinned ← " + u + ")", "out")
                    for p, u in sorted(self.submodules.items())]
        if sub == "deinit" and len(args) > 1:
            p = args[1]
            if p in self.submodules:
                del self.submodules[p]
                return [("submodule '" + p + "' unregistered (files kept)", "ok")]
            return [("error: no submodule '" + p + "'", "err")]
        if sub in ("update", "init", "sync", "foreach"):
            return [("git submodule " + sub + " fetches real repositories — conceptual in this offline sandbox", "warn")]
        return [("usage: git submodule [add | status | update | deinit]", "err")]
    # ---------------- worktrees / bundles ----------------
    def _norm_wt_path(self, p):
        p = str(p).strip().rstrip("/")
        while p.startswith("./"): p = p[2:]
        if p.startswith("../"): p = p[3:]
        return p
    def cmd_worktree(self, args=None):
        args = args or []
        sub = args[0] if args else "list"
        if sub == "list":
            main = "(detached)" if self.detached else str(self.current)
            rows = [("~/project".ljust(26) + main.ljust(14) + "  [main working tree]", "out")]
            for p, w in sorted(self.worktrees.items()):
                h = w["head"]
                msg = self.commits[h].message.splitlines()[0][:28] if h in self.commits else ""
                rows.append((("~/project/" + p).ljust(26) + str(w["branch"]).ljust(14) +
                             h[:7] + " " + msg, "out"))
            return rows
        if sub == "add":
            toks = [a for a in args[1:] if not a.startswith("-")]
            newb = args[args.index("-b") + 1] if "-b" in args else None
            if not toks:
                return [("usage: git worktree add [-b <branch>] <path> [<start-point>]", "err")]
            path = self._norm_wt_path(toks[0])
            if not path or path in self.worktrees:
                return [("fatal: '" + toks[0] + "' is not a valid new path (or worktree exists)", "err")]
            start = toks[1] if len(toks) > 1 else None
            created = None
            if newb:
                if newb in self.branches:
                    return [("fatal: a branch named '" + newb + "' already exists", "err")]
                h = self._resolve_ref(start) if start else self.head
                if h in (None, "ambiguous"): return [("fatal: bad start point", "err")]
                self.branches[newb] = h
                branch, created = newb, newb
            else:
                cand = start or path.rsplit("/", 1)[-1]
                if cand in self.branches:
                    branch, h = cand, self.branches[cand]
                else:
                    h = self._resolve_ref(start) if start else self.head
                    if h in (None, "ambiguous"):
                        return [("fatal: invalid reference: " + cand, "err")]
                    self.branches[cand] = h
                    branch, created = cand, cand
            if h is None: return [("fatal: no commits yet — commit first", "err")]
            occupied = {None if self.detached else self.current} | \
                       {w["branch"] for w in self.worktrees.values()}
            if branch in occupied:
                return [("fatal: branch '" + branch + "' is already checked out " +
                         ("in the main working tree" if branch == self.current
                          else "in another worktree"), "err")]
            tree = self.commits[h].tree
            self.worktrees[path] = {"branch": branch, "head": h,
                                    "index": dict(tree), "working": dict(tree)}
            out = [("Preparing worktree (checking out '" + branch + "')", "out")]
            if created: out.append(("created branch '" + branch + "' at " + h[:7], "info"))
            out += [("worktree ready: ~/project/" + path + "  ← " + branch + " @ " + h[:7], "ok"),
                    ("drive it from here:  git -C " + path + " <any git command>", "info")]
            return out
        if sub == "remove":
            toks = [a for a in args[1:] if not a.startswith("-")]
            if not toks: return [("usage: git worktree remove <path>", "err")]
            p = self._norm_wt_path(toks[0])
            if p not in self.worktrees:
                return [("fatal: '" + toks[0] + "' is not a worktree (git worktree list)", "err")]
            b = self.worktrees[p]["branch"]
            del self.worktrees[p]
            return [("removed worktree '" + p + "' — branch '" + b + "' is free again (delete it: git branch -d " + b + ")", "ok")]
        if sub == "prune":
            return [("all " + str(len(self.worktrees)) + " worktree(s) healthy — nothing to prune", "ok")]
        return [("usage: git worktree [list | add | remove | prune]", "err")]
    def _bundle_read(self, fname):
        key = self._resolve_path(fname)
        if key not in self.working: return None
        refs = []
        for l in self.working[key].splitlines():
            if l and not l.startswith("#"):
                h, _, ref = l.partition(" ")
                refs.append((h, ref.strip()))
        return refs
    def cmd_bundle(self, args):
        sub = args[0] if args else "list-heads"
        if sub == "create":
            toks = [a for a in args[1:] if not a.startswith("-")]
            if not toks: return [("usage: git bundle create <file> <refs | --all>", "err")]
            fname = toks[0]
            want = toks[1:] or [self.current]
            refs = []
            for r in want:
                if r == "--all":
                    refs += [(b, self.branches[b]) for b in self.branches if self.branches[b]]
                    continue
                h = self._resolve_ref(r)
                if h in (None, "ambiguous"): return [("fatal: bad revision '" + r + "'", "err")]
                refs.append((r, h))
            lines = ["# GitLearn bundle v1 (simulated — a real bundle packs the objects too)"]
            lines += [h + " refs/heads/" + r for r, h in refs]
            key = self._resolve_path(fname)
            self._ensure_parent(key)
            self.working[key] = "\n".join(lines) + "\n"
            return [("wrote bundle '" + key + "' with " + str(len(refs)) + " ref(s):", "ok")] + \
                [("  " + h[:7] + " " + r, "out") for r, h in refs] + \
                [("copy it on a USB stick — the other side: git bundle unbundle " + fname, "info")]
        refs = self._bundle_read(args[1] if len(args) > 1 else "")
        if refs is None:
            return [("can't read bundle: " + (args[1] if len(args) > 1 else "?"), "err")]
        if sub in ("list-heads", "verify"):
            out = [(h[:7] + " " + ref, "out") for h, ref in refs]
            if sub == "verify":
                missing = [h for h, _r in refs if h not in self.commits]
                out.append(("bundle is " + ("VALID ✔ — all objects present" if not missing
                            else "INCOMPLETE ✘ — commits missing: " + ", ".join(missing[:3]),),
                            "ok" if not missing else "err"))
            return out
        if sub == "unbundle":
            for h, ref in refs:
                b = ref.rstrip("/").rsplit("/", 1)[-1]
                self.rt["bundle/" + b] = h
            return [("added remote-tracking refs:", "ok")] + \
                [("  bundle/" + ref.rsplit("/", 1)[-1] + " → " + h[:7], "out")
                 for h, ref in refs] + [("inspect: git log bundle/main", "info")]
        return [("usage: git bundle create | list-heads | verify | unbundle", "err")]
    # ---------------- help / dispatch ----------------
    def _list_git_commands(self):
        groups = [("porcelain (everyday)",
                   "init status add stage commit diff log show branch switch checkout merge rebase cherry-pick stash tag remote push pull fetch restore reset revert clean bisect grep blame shortlog describe mv rm config ls-files ls-remote worktree archive help version"),
                  ("plumbing (the engine room)",
                   "rev-parse cat-file hash-object ls-tree update-ref merge-base for-each-ref symbolic-ref count-objects check-ignore var apply am format-patch notes lfs filter-repo rerere bundle submodule")]
        out = []
        for name, cmds in groups:
            out.append((name + ":", "info"))
            line = "  "
            for w in cmds.split():
                if len(line) + len(w) > 62:
                    out.append((line.rstrip(), "out")); line = "  "
                line += w + " "
            if line.strip(): out.append((line.rstrip(), "out"))
        out.append(("all of the above work in this sandbox — try one!", "ok"))
        return out
    def _help(self):
        rows = [
            ("cmd1 | cmd2  |  cmd > file  |  a && b / a || b / a ; b", "pipes, redirection, chaining"),
            ("$(cmd) · echo $? · !! · !$ · time cmd · sh script.sh", "substitution, scripts"),
            ("cd <dir> | pwd | mkdir -p | cp -r | mv | tree | ls -laR | rmdir", "filesystem"),
            ("touch f / echo x > f / cat f / head / tail / wc / less", "files"),
            ("grep [-r -i -n -l -v -c] pat · find . -name · sort|uniq|cut|sed|tr|awk", "search & text tools"),
            ("export V=x · echo $V · env · tee f · xargs cmd · bc · base64", "env & pipelines"),
            ("alias name=\"cmd\" · type cmd · history · man git-x · tldr", "aliases & docs"),
            ("git status [-s]", "full/short (+ahead/behind)"),
            ("git add <f> | . | -A | -u | -p (y/n/a/q)", "stage (interactive -p!)"),
            ("git commit -m | -am | --amend | --allow-empty | --fixup=<ref> | -S", "commit variants"),
            ("git rm [--cached] f / git mv a b", "remove / move tracked"),
            ("git log [--oneline] [--graph] [--all] [-3] [--reverse]", "history — plus:"),
            ("", "  --author= --grep= --stat -p -S --since= --format= --name-only A..B"),
            ("git diff [--staged] [--stat] [-w] [--word-diff] [-U<n>] [A B] [-- f]", "compare anything"),
            ("git show <ref>[:file] / git blame [-L a,b] [--ignore-rev h] f", "details"),
            ("git branch [-a|-v|-d|-m new|--contains|--merged|--show-current]", "branches"),
            ("git switch <b> | -b new | -t origin/b | --detach | --orphan | -", "move around"),
            ("git checkout [-- <file>] / git restore [--staged] [--source <ref>] f", "restore files"),
            ("git reset [--soft|--mixed|--hard] <ref> | git reset HEAD <file>", "undo"),
            ("git merge <b> [--no-ff|--squash|--ff-only|-s ours|-X ours|theirs]", "merge flavours"),
            ("git rebase <b> | -i HEAD~<n> | --onto A B | --autosquash", "replay commits"),
            ("  pick|drop|squash|fixup|reword <n>   then: rebase --continue/--abort", "todo editing"),
            ("git cherry-pick [-x] [-n] <hash> | A..B", "copy commits"),
            ("git stash [-u] [-m] | list | show [-p] | pop | apply | branch | drop", "shelve"),
            ("git tag [-a v1.0 -m] [-s] [-v] [-f] [-l] [-d] [--contains]", "tags"),
            ("git revert <hash> | -m 1 <merge> | -n", "safe undo"),
            ("git reflog · git clean [-n] [-f] [-x] [-X]", "safety & cleanup"),
            ("git bisect start|good|bad|reset", "binary-search a bug"),
            ("git remote [-v | add | rename | remove | prune | show]", "remotes"),
            ("git push [-u] [--tags] [--force] [--force-with-lease] [--delete b]", "upload"),
            ("git fetch [--all] [--prune] [--tags] / git pull [--rebase] [--autostash]", "download"),
            ("teammate <msg> [file] | teammate -b <branch> <msg>", "🤝 fake colleague"),
            ("git ls-files [-o] [-v] / git ls-remote [--heads]", "list files/refs"),
            ("git rev-parse HEAD · cat-file -p · hash-object f · ls-tree HEAD", "plumbing"),
            ("git merge-base A B · for-each-ref · symbolic-ref HEAD · update-ref", "more plumbing"),
            ("git check-ignore [-v] p · update-index --skip-worktree f · var", "ignores & flags"),
            ("git format-patch -1 · apply [--check] f.patch · am f.patch", "patch workflow"),
            ("git request-pull <base> <url> · git notes add -m \"x\" <ref>", "meta"),
            ("git filter-repo --path f --invert-paths", "scrub history ⚠"),
            ("git lfs track \"*.psd\" | ls-files | status | pointer", "big files"),
            ("git worktree add <path> | list | remove · git -C <path> <cmd>", "worktrees"),
            ("git init --bare x.git · git bundle create f <ref> · submodule add", "server-less"),
            ("git rerere [status|diff|clear] · .githooks/pre-commit|pre-push", "automation"),
            ("git config user.name x / alias.x \"cmd\" · core.hooksPath <dir>", "configure"),
            ("git shortlog [-s] / describe [--abbrev=0] / gc / fsck / archive", "summaries"),
            ("git help -a · git version · gitk", "misc"),
            ("resolve <file> ours|theirs · fortune · cowsay · sudo", "special 😄"),
            ("clear", "clear the screen"),
        ]
        return [("Git Sandbox — available commands:", "info")] + \
            [("  " + c.ljust(48) + d, "out") for c, d in rows]
    def _git(self, args):
        if args and args[0] == "-C":
            if len(args) < 3: return [("usage: git -C <worktree-path> <command>", "err")]
            p = self._norm_wt_path(args[1])
            if p not in self.worktrees:
                return [("fatal: '" + args[1] + "' is not a worktree (git worktree list)", "err")]
            wt = self.worktrees[p]
            saved = (self.working, self.index, self.cwd, self.current, self.head, self.detached)
            self._main_current = saved[3]
            self._wt_context = p
            self.working, self.index = dict(wt["working"]), dict(wt["index"])
            self.cwd = []
            self.current, self.head, self.detached = wt["branch"], wt["head"], False
            try: res = self._git(args[2:])
            finally:
                wt["branch"], wt["head"] = self.current, self.head
                wt["working"], wt["index"] = dict(self.working), dict(self.index)
                (self.working, self.index, self.cwd, self.current,
                 self.head, self.detached) = saved
                self._wt_context = None
            return [("── git -C " + p + " ──", "info")] + res + \
                [("── back in the main working tree ──", "info")]
        if not args: return [("usage: git <command>   (try 'help')", "err")]
        cmd = args[0]; rest = args[1:]
        if cmd == "help" and rest in (["-a"], ["--all"]): return self._list_git_commands()
        if cmd == "stage": return self.cmd_add(rest)
        special = {
            "submodule": self.cmd_submodule, "rerere": self.cmd_rerere,
            "bundle": self.cmd_bundle, "update-index": self.cmd_update_index,
            "notes": self.cmd_notes, "lfs": self.cmd_lfs,
            "filter-repo": self.cmd_filter_repo, "ls-tree": self.cmd_ls_tree,
            "update-ref": self.cmd_update_ref, "check-ignore": self.cmd_check_ignore,
            "var": self.cmd_var, "format-patch": self.cmd_format_patch,
            "apply": self.cmd_apply, "am": self.cmd_am,
            "request-pull": self.cmd_request_pull, "rev-parse": self.cmd_rev_parse,
            "cat-file": self.cmd_cat_file, "hash-object": self.cmd_hash_object,
            "merge-base": self.cmd_merge_base, "for-each-ref": self.cmd_for_each_ref,
            "symbolic-ref": self.cmd_symbolic_ref, "count-objects": self.cmd_count_objects,
        }
        if cmd in ("verify-commit", "verify-tag"):
            g = self._guard()
            if g: return g
            if cmd == "verify-commit":
                ref = rest[0] if rest else "HEAD"
                h = self._resolve_ref(ref)
                if h in (None, "ambiguous"): return [("fatal: bad revision '" + str(ref) + "'", "err")]
                return [("gpg: Good signature from \"" + self.user_name + "\" 🔒", "ok"),
                        ("commit " + h + " — verified (simulated)", "out")]
            name = rest[0] if rest else None
            if name not in self.tags: return [("error: tag '" + str(name) + "' not found.", "err")]
            return [("gpg: Good signature from \"" + self.user_name + "\" 🔒", "ok"),
                    ("tag " + name + " — verified (simulated)", "out")]
        if cmd in special:
            g = self._guard()
            if g: return g
            return special[cmd](rest)
        table = {
            "init": lambda: self.cmd_init(rest),
            "status": lambda: self.cmd_status(rest),
            "add": lambda: self.cmd_add(rest),
            "commit": lambda: self.cmd_commit(rest),
            "log": lambda: self.cmd_log(rest),
            "whatchanged": lambda: self.cmd_log(rest + ["-p"]),
            "diff": lambda: self.cmd_diff(rest),
            "branch": lambda: self.cmd_branch(rest),
            "rm": lambda: self.cmd_rm(rest),
            "merge": lambda: self.cmd_merge(rest),
            "restore": lambda: self.cmd_restore(rest),
            "checkout": lambda: self.cmd_checkout(rest, "checkout"),
            "switch": lambda: self.cmd_checkout(rest, "switch"),
            "stash": lambda: self.cmd_stash(rest),
            "tag": lambda: self.cmd_tag(rest),
            "show": lambda: self.cmd_show(rest),
            "blame": lambda: self.cmd_blame(rest),
            "grep": lambda: self.cmd_grep(rest),
            "cherry-pick": lambda: self.cmd_cherry_pick(rest),
            "rebase": lambda: self.cmd_rebase(rest),
            "reflog": lambda: self.cmd_reflog(rest),
            "reset": lambda: self.cmd_reset(rest),
            "revert": lambda: self.cmd_revert(rest),
            "clean": lambda: self.cmd_clean(rest),
            "config": lambda: self.cmd_config(rest),
            "shortlog": lambda: self.cmd_shortlog(rest),
            "describe": lambda: self.cmd_describe(rest),
            "gc": lambda: self.cmd_gc(rest),
            "fsck": lambda: self.cmd_fsck(rest),
            "archive": lambda: self.cmd_archive(rest),
            "worktree": lambda: self.cmd_worktree(rest),
            "bisect": lambda: self.cmd_bisect(rest),
            "mv": lambda: self.cmd_mv(rest),
            "remote": lambda: self.cmd_remote(rest),
            "push": lambda: self.cmd_push(rest),
            "fetch": lambda: self.cmd_fetch(rest),
            "pull": lambda: self.cmd_pull(rest),
            "ls-files": lambda: self.cmd_ls_files(rest),
            "ls-remote": lambda: self.cmd_ls_remote(rest),
            "help": lambda: self._man(["git"] + rest),
            "version": lambda: [("git version 2.43.sandbox (GitLearn)", "out")],
        }
        if cmd == "diff" and "--no-index" in rest:
            return self._f_diff([a for a in rest if not a.startswith("-")])
        if cmd == "init" and "--bare" in rest: return self.cmd_init(rest)
        if cmd in ("clone",):
            return [("🌐 '" + cmd + "' isn't simulated — but push/pull/fetch ARE!", "warn"),
                    ("try:  git remote add origin <url>  →  git push -u origin " + str(self.current), "out")]
        if cmd in ("gitk", "gui"): return self._gitk()
        if cmd not in table:
            return [("git: '" + cmd + "' is not a sandbox command (type 'help')", "err")]
        if cmd not in ("init", "config", "version", "help"):
            g = self._guard()
            if g: return g
        return table[cmd]()

# ================================================================= graph =====
class CommitGraphWidget(QWidget):
    VSPACE, HSPACE, R = 58, 84, 8
    def __init__(self):
        super().__init__()
        self.commits, self.branches, self.cols = [], {}, {}
        self.current, self.head, self.tags = None, None, {}
        self.setMinimumSize(320, 480)
    def update_from_repo(self, repo):
        self.commits = sorted(repo.commits.values(), key=lambda c: c.seq, reverse=True)
        self.branches = dict(repo.branches)
        self.current, self.head = repo.current, repo.head
        self.tags = dict(getattr(repo, "tags", {}))
        cols, n = {}, 0
        for b in repo.branches: cols[b] = n; n += 1
        for c in self.commits:
            if c.branch not in cols: cols[c.branch] = n; n += 1
        self.cols = cols
        self.setMinimumSize(max(n, 1) * self.HSPACE + 200,
                            max(len(self.commits), 1) * self.VSPACE + 80)
        self.update()
    def _color(self, name):
        return QColor(BRANCH_PALETTE[self.cols.get(name, 0) % len(BRANCH_PALETTE)])
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(PANEL2))
        if not self.commits:
            p.setPen(QPen(QColor(MUTED)))
            p.drawText(self.rect(), Qt.AlignCenter,
                       "No commits yet.\nCreate files and commit in the Terminal —\nthe graph grows live!")
            p.end(); return
        pos = {}
        for i, c in enumerate(self.commits):
            pos[c.hash] = (46 + self.cols.get(c.branch, 0) * self.HSPACE, 40 + i * self.VSPACE)
        p.setPen(QPen(QColor("#565f89"), 2))
        p.setBrush(Qt.NoBrush)
        for c in self.commits:
            for ph in c.parents:
                if ph not in pos: continue
                x1, y1 = pos[c.hash]; x2, y2 = pos[ph]
                path = QPainterPath(QPointF(x1, y1))
                if abs(x1 - x2) < 1: path.lineTo(x2, y2)
                else:
                    my = (y1 + y2) / 2
                    path.cubicTo(QPointF(x1, my), QPointF(x2, my), QPointF(x2, y2))
                p.drawPath(path)
        font = p.font(); font.setPointSize(8); p.setFont(font)
        for c in self.commits:
            x, y = pos[c.hash]
            color = self._color(c.branch)
            p.setBrush(QBrush(color)); p.setPen(QPen(QColor(PANEL2), 2))
            p.drawEllipse(QPointF(x, y), self.R, self.R)
            p.setPen(QPen(QColor(FG)))
            msg = c.message if len(c.message) <= 36 else c.message[:35] + "…"
            p.drawText(QPointF(x + 14, y - 8), msg)
            if c.hash == self.head:
                p.setBrush(Qt.NoBrush); p.setPen(QPen(color, 2))
                p.drawEllipse(QPointF(x, y), self.R + 4, self.R + 4)
                p.setPen(QPen(QColor(ACCENT)))
                p.drawText(QPointF(x + 14, y + 5), "HEAD")
        offset = {}
        for b, bh in self.branches.items():
            if bh in pos and b != self.current:
                x, y = pos[bh]
                dy = offset.get(bh, 22); offset[bh] = dy + 16
                p.setPen(QPen(self._color(b)))
                p.drawText(QPointF(x + 14, y + dy), b)
        for t, (th, _ann) in self.tags.items():
            if th in pos:
                x, y = pos[th]
                dy = offset.get(th, 22); offset[th] = dy + 16
                p.setPen(QPen(QColor(YELLOW)))
                p.drawText(QPointF(x + 14, y + dy), "🏷 " + t)
        p.end()

def _prompt_html(repo):
    if not repo.initialized:
        return _span(GREEN, "sandbox") + _span(MUTED, " $")
    sub = ("/" + "/".join(repo.cwd)) if getattr(repo, "cwd", []) else ""
    if getattr(repo, "detached", False) and repo.head:
        return (_span(GREEN, "sandbox") + _span(MUTED, ":~/project" + sub) +
                _span(ORANGE, "(" + repo.head[:7] + "…)") + _span(MUTED, " $"))
    return (_span(GREEN, "sandbox") + _span(MUTED, ":~/project" + sub) +
            _span(PURPLE, "(" + str(repo.current or "") + ")") + _span(MUTED, " $"))

# ============================================ completion data / recipes ======
_SHELL_WORDS = set("""clear help exit history pwd cd ls tree cat touch echo grep
find head tail wc less more sort uniq cut sed nl rev tac tr bc awk tee xargs seq
stat cmp diff basename dirname column paste fold shuf md5sum sha1sum sha256sum
base64 strings file mktemp dos2unix unix2dos ln date whoami which type tldr
apropos id groups tty sleep yes ps top htop kill open xdg-open watch cmatrix
fortune cowsay sl export unset env alias unalias printf comm sudo uname hostname
uptime true false test read pushd popd dirs rmdir jobs fg bg umask nano vim vi
emacs code curl ping ssh python python3 node npm teammate sh bash zsh source
chmod chown df du gitk gui git""".split())
GIT_SUBCOMMANDS = """init status add stage commit log whatchanged diff show
branch switch checkout merge rebase cherry-pick stash tag remote push pull fetch
restore reset revert clean config shortlog describe mv rm ls-files ls-remote
bisect blame grep reflog rev-parse cat-file hash-object ls-tree update-ref
merge-base for-each-ref symbolic-ref count-objects check-ignore var format-patch
apply am request-pull notes lfs filter-repo worktree bundle submodule rerere
verify-commit verify-tag update-index archive gc fsck help version""".split()
_REF_CMDS = {"switch", "checkout", "merge", "rebase", "reset", "log", "diff",
             "show", "branch", "tag", "cherry-pick", "revert", "describe",
             "blame", "cat-file", "rev-parse", "merge-base", "for-each-ref"}
_GIT_FLAGS = {
    "status": ["-s", "-sb", "--short"], "add": [".", "-A", "-u", "-p"],
    "log": ["--oneline", "--graph", "--all", "--stat", "-p", "--author=", "--grep=",
            "-n", "--format=", "--reverse", "--name-only"],
    "diff": ["--staged", "--stat", "-w", "--word-diff", "--name-only"],
    "commit": ["-m", "-a", "-am", "--amend", "--allow-empty", "--no-verify", "-S"],
    "push": ["-u", "--tags", "--force", "--force-with-lease", "--delete"],
    "fetch": ["--all", "--tags", "--prune"],
    "pull": ["--rebase", "--ff-only", "--autostash"],
    "merge": ["--no-ff", "--squash", "--ff-only", "--abort", "-m",
              "--allow-unrelated-histories"],
    "reset": ["--soft", "--mixed", "--hard"],
    "restore": ["--staged", "--source="],
    "rebase": ["-i", "--continue", "--abort", "--onto", "--autosquash"],
    "tag": ["-a", "-m", "-d", "-l", "-s", "-v", "--contains", "-f"],
    "stash": ["-u", "-m"], "clean": ["-n", "-f", "-x", "-d"],
    "apply": ["--check"], "format-patch": ["-1", "-2", "-3"],
    "switch": ["-b", "-c", "-t", "--detach", "--orphan", "-"],
    "checkout": ["-b", "-c", "-t", "--detach", "--orphan", "-"],
    "worktree": ["add", "list", "remove", "prune", "-b"],
}
_FILE_CMD_WORDS = {"cd", "ls", "tree", "rm", "cat", "grep", "mv", "cp", "find",
                   "head", "tail", "wc", "less", "more", "mkdir", "rmdir",
                   "touch", "stat", "sh", "bash", "source", "sed", "sort", "uniq"}
def _common_prefix(strs):
    if not strs: return ""
    p = strs[0]
    for s in strs[1:]:
        while p and not s.startswith(p): p = p[:-1]
    return p

RECIPES = [
{"title": "Your first repository",
 "desc": "init → add → commit → log. The four-move dance everything else builds on.",
 "note": "Notice how status changed at each step — the three areas in action.",
 "cmds": ["git init", "touch hello.txt", 'echo "hello, git!" > hello.txt', "git status",
          "git add hello.txt", "git status", 'git commit -m "my first commit"',
          "git log --oneline"]},
{"title": "Branch, commit, merge",
 "desc": "The safest loop in Git: never work directly on main.",
 "note": "The merge was a fast-forward — main hadn't moved, so the pointer just slid.",
 "cmds": ["git init", 'echo "v1" > app.txt', 'git add . && git commit -m "initial version"',
          "git switch -c feature/fix", 'echo "v2 with fix" > app.txt',
          'git add . && git commit -m "fix applied on branch"', "git switch main",
          "git merge feature/fix", "git log --oneline --graph"]},
{"title": "Merge conflict, resolved",
 "desc": "Both branches edit the same line. Git asks; you decide.",
 "note": "rerere just recorded your resolution — a future identical conflict auto-resolves.",
 "cmds": ["git init", 'echo "color: blue" > theme.txt',
          'git add . && git commit -m "theme v1"', "git switch -c experiment",
          'echo "color: purple" > theme.txt', 'git add . && git commit -m "purple on experiment"',
          "git switch main", 'echo "color: teal" > theme.txt',
          'git add . && git commit -m "teal on main"', "git merge experiment",
          "cat theme.txt", "resolve theme.txt ours", "git add .",
          'git commit -m "merge experiment"', "git log --oneline --graph"]},
{"title": "The undo toolbox",
 "desc": "amend a typo, then uncommit with --soft and recommit properly.",
 "note": "--soft kept the changes staged — nothing was lost.",
 "cmds": ["git init", 'echo "one" > f.txt', 'git add . && git commit -m "add f"',
          'echo "two" > f2.txt', 'git add . && git commit -m "add f2 (typo mesage)"',
          'git commit --amend -m "add f2 (message fixed)"', "git log --oneline",
          "git reset --soft HEAD~1", "git status -s", 'git commit -m "add f2"',
          "git log --oneline"]},
{"title": "Stash — parking your work",
 "desc": "Mid-change but need a clean tree? Stash, hotfix, pop.",
 "note": "pop = apply + remove from the stack. Use apply to keep a copy.",
 "cmds": ["git init", 'echo "base" > w.txt', 'git add . && git commit -m "base"',
          'echo "half-finished idea" > w.txt', "git status -s",
          'git stash push -m "wip idea"', "git status -s", "git stash list",
          'echo "unrelated hotfix" > hotfix.txt',
          'git add . && git commit -m "urgent hotfix"', "git stash pop",
          "git status -s", "cat w.txt"]},
{"title": "Rebase onto main",
 "desc": "Replay your feature on top of main's new commits for a linear history.",
 "note": "After the rebase, merging back is a fast-forward — no merge bubble.",
 "cmds": ["git init", 'echo "core" > core.txt', 'git add . && git commit -m "core module"',
          "git switch -c feature", 'echo "feature work" > feat.txt',
          'git add . && git commit -m "feature work"', "git switch main",
          'echo "main moves on" > news.txt', 'git add . && git commit -m "main news"',
          "git switch feature", "git rebase main", "git log --oneline --graph",
          "git switch main", "git merge feature", "git log --oneline --graph"]},
{"title": "Interactive rebase: squash the wip",
 "desc": "Three messy commits → one clean one, using the sandbox todo commands.",
 "note": "The squashed messages joined with ' + '. Real git opens an editor.",
 "cmds": ["git init", 'echo "start" > code.py', 'git add . && git commit -m "add login form"',
          'echo "more" >> code.py', 'git add . && git commit -m "wip"',
          'echo "even more" >> code.py', 'git add . && git commit -m "fix typo"',
          "git log --oneline", "git rebase -i HEAD~3", "squash 2", "squash 3",
          "git rebase --continue", "git log --oneline"]},
{"title": "Tag a release",
 "desc": "Annotated tags mark milestones; describe names any commit relative to them.",
 "note": "git log v1.0.0..HEAD is literally your changelog, already written.",
 "cmds": ["git init", 'echo "1.0 code" > app.py',
          'git add . && git commit -m "feat: initial app"',
          'git tag -a v1.0.0 -m "first stable release"', 'echo "2.0 code" >> app.py',
          'git add . && git commit -m "feat: dark mode"',
          'git tag -a v1.1.0 -m "dark mode ships"', "git tag", "git describe",
          "git log --oneline", "git show v1.0.0 --stat"]},
{"title": "Remote round-trip with a teammate",
 "desc": "push → teammate pushes → fetch → pull --rebase → push. The daily rhythm.",
 "note": "status showed 'behind' after the teammate pushed — your cue to pull.",
 "cmds": ["git init", 'echo "shared" > doc.md', 'git add . && git commit -m "docs: start"',
          "git remote add origin https://github.com/you/team.git",
          "git push -u origin main", 'teammate "added a note on the server" doc.md',
          "git status -s", "git fetch", "git log origin/main --oneline",
          "git pull --rebase", "git log --oneline", "git push"]},
{"title": "Bisect: find the breaking commit",
 "desc": "Binary-search history: mark good and bad, Git walks you to the culprit.",
 "note": "Bisect checked out commits in detached HEAD — normal and safe.",
 "cmds": ["git init", 'echo "a" > lib.txt', 'git add . && git commit -m "v1 good"',
          'echo "b" >> lib.txt', 'git add . && git commit -m "v2 good"',
          'echo "c + BUG" >> lib.txt', 'git add . && git commit -m "v3 maybe"',
          'echo "d" >> lib.txt', 'git add . && git commit -m "v4 broken now"',
          "git bisect start", "git bisect bad", "git bisect good HEAD~3",
          "git bisect bad", "git bisect reset", "git log --oneline"]},
{"title": "Cherry-pick a hotfix",
 "desc": "Steal one commit from a branch without merging the rest.",
 "note": "exp.txt never arrived — only the fix commit was copied. A copy, not a move.",
 "cmds": ["git init", 'echo "base" > core.txt', 'git add . && git commit -m "base"',
          "git switch -c experiment", 'echo "experimental" > exp.txt',
          'git add . && git commit -m "risky experiment"',
          'echo "critical fix" > fix.txt', 'git add . && git commit -m "fix: critical patch"',
          "git switch main", "git log experiment --oneline", "ls",
          "git cherry-pick -x experiment", "git log --oneline", "ls"]},
{"title": "Hooks: a robot guards your commits",
 "desc": "A pre-commit hook that blocks commits until CHANGELOG.md exists.",
 "note": "--no-verify skips hooks once — genuine emergencies only.",
 "cmds": ["git init", 'echo "x" > f.txt', "git add .", "mkdir .githooks",
          "echo \"test -f CHANGELOG.md && echo 'changelog ok'\" > .githooks/pre-commit",
          'git commit -m "no changelog yet"', "touch CHANGELOG.md",
          'git commit -m "passes the gate"',
          'git commit --allow-empty -m "bypass" --no-verify']},
]

CHALLENGES = [
{"title": "Genesis", "desc": "Initialize a repository and make your first commit on any branch.",
 "hint": "git init → touch hello.txt → git add . → git commit -m \"first\"",
 "check": lambda r: bool(getattr(r, "initialized", False)) and bool(getattr(r, "head", None))},
{"title": "Triple crown", "desc": "Reach at least 3 commits reachable from your current HEAD.",
 "hint": "Loop: edit a file (echo x > f) → git add . → git commit -m \"...\"",
 "check": lambda r: bool(getattr(r, "head", None)) and len(r._ancestors(r.head)) >= 3},
{"title": "Fork in the road", "desc": "Have 3+ branches AND at least one merge commit (two parents) in history.",
 "hint": "git switch -c feat → commit → git switch main → git merge feat (then one more branch).",
 "check": lambda r: len(getattr(r, "branches", {})) >= 3 and
          any(len(c.parents) == 2 for c in r.commits.values())},
{"title": "Peacemaker", "desc": "Create a merge conflict, resolve it, and finish the merge commit.",
 "hint": "Two branches edit the same file → git merge → resolve <f> ours → git add . → git commit",
 "check": lambda r: (not getattr(r, "merge_state", None)) and bool(getattr(r, "rerere", {})) and
          any(len(c.parents) == 2 for c in r.commits.values())},
{"title": "Time capsule", "desc": "Put an ANNOTATED tag starting with 'v' on a commit that is NOT your HEAD.",
 "hint": "git log --oneline → git tag -a v0.9 -m \"retro tag\" HEAD~1",
 "check": lambda r: any(n.startswith("v") and m and h != getattr(r, "head", None)
                        for n, (h, m) in getattr(r, "tags", {}).items())},
{"title": "Plumber's licence", "desc": "Inspect the machinery: run git rev-parse, git cat-file and git hash-object.",
 "hint": "git rev-parse HEAD · git cat-file -t HEAD · git hash-object <file>",
 "check": lambda r: all(any(k in h for h in r.history)
                        for k in ("rev-parse", "cat-file", "hash-object"))},
{"title": "Full circle", "desc": "Add a remote, push, let a teammate push, and pull their commit into your branch.",
 "hint": "git remote add origin <url> → git push -u origin main → teammate \"hi\" → git pull --rebase",
 "check": lambda r: bool(getattr(r, "remotes", {})) and bool(getattr(r, "remote_branches", {})) and
          bool(getattr(r, "head", None)) and
          any(getattr(r.commits[h], "author", "").startswith("Teammate")
              for h in r._ancestors(r.head))},
{"title": "Safety net", "desc": "Park uncommitted work in the stash — a stash entry should exist right now.",
 "hint": "Edit a tracked file → git stash push -m \"wip\" → git stash list",
 "check": lambda r: len(getattr(r, "stash", [])) >= 1},
{"title": "Wordsmith", "desc": "Fix history politely: amend a commit message with --amend.",
 "hint": "git commit --amend -m \"a much better message\"",
 "check": lambda r: any("--amend" in h for h in r.history)},
{"title": "The detective", "desc": "Track down changes: use the pickaxe (git log -S …) AND git blame on a file.",
 "hint": "git log -S \"hello\" --oneline · git blame <file>",
 "check": lambda r: any("-S" in h for h in r.history) and
          any(h.startswith("git blame") for h in r.history)},
]

# ============================================================ lesson helper ==
def _strip_tags(html_text):
    txt = re.sub(r'<[^>]+>', ' ', html_text)
    txt = txt.replace('&nbsp;', ' ').replace('&amp;', '&') \
             .replace('&lt;', '<').replace('&gt;', '>')
    return re.sub(r'\s+', ' ', txt)

def _lesson_refs(q):
    q = q.strip().lower()
    if q.startswith("git "): q = q[4:]
    q = q.strip("-").strip()
    if not q: return None
    for i, l in enumerate(LESSONS):
        if q in l["title"].lower(): return i
        if re.search(r'\b' + re.escape(q) + r'\b', _strip_tags(l["body"]).lower()):
            return i
    return None

# ================================================================ UI =========
class _HistoryInput(QLineEdit):
    def __init__(self, page):
        super().__init__()
        self._page = page
    def keyPressEvent(self, e):
        p = self._page
        k = e.key()
        if k == Qt.Key_Tab: p.complete_command(); return
        if k == Qt.Key_Escape and getattr(p, "recipes_running", False):
            p.stop_recipe()
            p.write("⏹ recipe stopped — the sandbox is yours", "warn")
            return
        if k == Qt.Key_L and (e.modifiers() & Qt.ControlModifier):
            p.output.clear(); return
        if k == Qt.Key_Up and p.history:
            p.hpos = max(0, p.hpos - 1)
            self.setText(p.history[p.hpos])
            self.setCursorPosition(len(self.text()))
        elif k == Qt.Key_Down and p.history:
            p.hpos = min(len(p.history), p.hpos + 1)
            self.setText(p.history[p.hpos] if p.hpos < len(p.history) else "")
        else: super().keyPressEvent(e)

class TerminalPage(QWidget):
    stats_cb = None
    auto_check_cb = None
    recipes_running = False
    def __init__(self):
        super().__init__()
        self.repo = SimRepo()
        self.history, self.hpos = [], 0
        self._recipe_queue = []
        self._typing_text = ""
        self._typing_pos = 0
        self._type_timer = QTimer(self)
        self._type_timer.timeout.connect(self._type_tick)
        self._next_timer = QTimer(self)
        self._next_timer.setSingleShot(True)
        self._next_timer.timeout.connect(self._recipe_step)
        self._hs_active = False
        self._hs_query = ""
        self._hs_saved = ""
        self._hs_idx = 0
        split = QSplitter(Qt.Horizontal)
        root = QHBoxLayout(self)
        root.addWidget(split)
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 0, 0)
        hdr = QHBoxLayout()
        title = QLabel("⌨️  Sandbox Terminal")
        title.setObjectName("panelTitle")
        reset = QPushButton("Reset sandbox")
        reset.setObjectName("secondaryBtn")
        reset.setToolTip("Start over with an empty folder")
        hdr.addWidget(title); hdr.addStretch(); hdr.addWidget(reset)
        lv.addLayout(hdr)
        self.output = QTextBrowser()
        self.output.setObjectName("termOut")
        mono = QFont(_mono_family()); mono.setPointSize(10)
        self.output.setFont(mono)
        self.input = _HistoryInput(self)
        self.input.setFont(mono)
        self.input.setPlaceholderText("type a command…  Tab completes · Ctrl+R searches history · 'help' lists everything")
        self.prompt = QLabel()
        self.prompt.setFont(mono)
        self.prompt.setMinimumWidth(150)
        prow = QHBoxLayout()
        prow.addWidget(self.prompt); prow.addWidget(self.input, 1)
        lv.addWidget(self.output, 1)
        lv.addLayout(prow)
        split.addWidget(left)
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(0, 0, 0, 0)
        gtitle = QLabel("📈  Commit Graph (live)")
        gtitle.setObjectName("panelTitle")
        rv.addWidget(gtitle)
        self.graph = CommitGraphWidget()
        sa = QScrollArea()
        sa.setWidgetResizable(True)
        sa.setWidget(self.graph)
        sa.setStyleSheet("QScrollArea{border:1px solid " + BORDER +
                         "; border-radius:8px; background:" + PANEL2 + ";}")
        rv.addWidget(sa, 1)
        split.addWidget(right)
        split.setSizes([640, 480])
        split.setHandleWidth(8)
        reset.clicked.connect(self.reset_sandbox)
        self.input.returnPressed.connect(self.submit)
        self.input.installEventFilter(self)
        self._banner()
        self._refresh()
    # ---------- Ctrl+R history search ----------
    def hsearch_start(self):
        if self.recipes_running: return
        self._hs_active = True
        self._hs_saved = self.input.text()
        self._hs_query = self._hs_saved.strip()
        self._hs_idx = len(self.history)
        self._hs_find(self._hs_idx)
    def _hs_find(self, start):
        q = self._hs_query.lower()
        i = start - 1
        while i >= 0:
            if q in self.history[i].lower():
                self._hs_idx = i
                self.input.setText(self.history[i])
                self.input.setCursorPosition(len(self.history[i]))
                if self.stats_cb:
                    self.stats_cb('(reverse-i-search)`' + self._hs_query + "': " + self.history[i])
                return
            i -= 1
        if self.stats_cb:
            self.stats_cb("(failed reverse-i-search)`" + self._hs_query + "'")
    def hsearch_accept(self):
        self._hs_active = False
        self.input.setCursorPosition(len(self.input.text()))
        self._refresh()
    def hsearch_cancel(self):
        self._hs_active = False
        self.input.setText(self._hs_saved)
        self.input.setCursorPosition(len(self._hs_saved))
        self._refresh()
    def eventFilter(self, obj, ev):
        if obj is self.input and ev.type() == QEvent.KeyPress:
            k = ev.key(); mod = ev.modifiers()
            if k == Qt.Key_R and (mod & Qt.ControlModifier):
                if not self._hs_active: self.hsearch_start()
                else: self._hs_find(self._hs_idx)
                return True
            if self._hs_active:
                if k == Qt.Key_Escape: self.hsearch_cancel(); return True
                if k in (Qt.Key_Return, Qt.Key_Enter): self.hsearch_accept(); return True
                if k == Qt.Key_Backspace:
                    self._hs_query = self._hs_query[:-1]
                    self._hs_find(len(self.history)); return True
                t = ev.text()
                if t and t.isprintable():
                    self._hs_query += t
                    self._hs_find(len(self.history)); return True
                return True
        return super().eventFilter(obj, ev)
    # ---------- Tab completion ----------
    @staticmethod
    def _raw_split(text):
        parts, cur, q = [], "", None
        for ch in text:
            if q:
                cur += ch
                if ch == q: q = None
            elif ch in "\"'": q = ch; cur += ch
            elif ch.isspace():
                if cur: parts.append(cur)
                cur = ""
            else: cur += ch
        if cur: parts.append(cur)
        return parts
    @staticmethod
    def _token_at(text, pos):
        left = text[:pos]
        if not left or left[-1].isspace():
            return left.split(), "", pos
        b = len(left)
        while b > 0 and not left[b - 1].isspace(): b -= 1
        return left[:b].split(), left[b:len(left)], b
    def _file_tokens(self, token):
        repo = self.repo
        pre = "/".join(getattr(repo, "cwd", []))
        pre = (pre + "/") if pre else ""
        names = set()
        for f in getattr(repo, "working", {}):
            if not f.startswith(pre): continue
            rest = f[len(pre):]
            if "/" in rest: names.add(rest.split("/", 1)[0] + "/")
            names.add(rest)
        for d in getattr(repo, "dirs", set()):
            if d.startswith(pre) and d[len(pre):]: names.add(d[len(pre):] + "/")
        out = [n for n in names if n.startswith(token)] if token else sorted(names)
        return sorted(set(out))
    def _git_candidates(self, gargs, token):
        repo = self.repo
        if not gargs or gargs[0].startswith("-"):
            return sorted(set(GIT_SUBCOMMANDS))
        sub = gargs[0]
        cand = set(_GIT_FLAGS.get(sub, []))
        if sub in _REF_CMDS:
            cand |= set(getattr(repo, "branches", {}))
            cand |= set(getattr(repo, "tags", {}))
            cand |= set(getattr(repo, "rt", {}))
            if getattr(repo, "head", None): cand |= {"HEAD", "HEAD~1", "HEAD~2"}
        if sub in ("push", "pull", "fetch", "remote"):
            cand |= set(getattr(repo, "remotes", {}))
        if sub == "config":
            cand |= {"--global", "--list", "user.name", "user.email", "alias.", "core.hooksPath"}
        if sub in ("ls-files", "mv", "rm", "restore", "show", "blame", "add",
                   "archive", "hash-object", "check-ignore"):
            cand |= set(self._file_tokens(token))
        if sub == "stash":
            cand |= {"push", "pop", "apply", "list", "drop", "show", "branch", "clear"}
        if sub == "notes": cand |= {"add", "append", "show", "list", "remove"}
        if sub == "lfs": cand |= {"install", "track", "untrack", "ls-files", "status", "pointer"}
        if sub == "rerere": cand |= {"status", "diff", "clear"}
        if sub == "bisect": cand |= {"start", "good", "bad", "reset", "log"}
        if sub == "worktree": cand |= {"add", "list", "remove", "prune"}
        if sub == "bundle": cand |= {"create", "verify", "list-heads", "unbundle"}
        if sub == "submodule": cand |= {"add", "status", "update", "deinit"}
        return sorted(cand)
    def _context_candidates(self, pre, token):
        repo = self.repo
        if not pre: return sorted(set(_SHELL_WORDS))
        c0 = pre[0]
        if c0 in getattr(repo, "shell_aliases", {}):
            try: ex = shlex.split(repo.shell_aliases[c0])
            except ValueError: ex = repo.shell_aliases[c0].split()
            if ex:
                if ex[0] == "git": return self._git_candidates(ex[1:] + pre[1:], token)
                pre = ex + pre[1:]; c0 = pre[0]
        if c0 in getattr(repo, "aliases", {}):
            try: ex = shlex.split(repo.aliases[c0])
            except ValueError: ex = repo.aliases[c0].split()
            if ex and ex[0] == "git":
                return self._git_candidates(ex[1:] + pre[1:], token)
        if c0 == "git": return self._git_candidates(pre[1:], token)
        if c0 == "teammate": return ["-b"]
        if c0 == "man":
            return ["git-log", "git-commit", "git-branch", "git-rebase"]
        if c0 == "help": return []
        if c0 == "echo": return self._file_tokens(token)
        if c0 in _FILE_CMD_WORDS:
            extra = {"ls": ["-la", "-l", "-a", "-R"], "rm": ["-r", "-f"],
                     "mkdir": ["-p"], "cp": ["-r"],
                     "grep": ["-r", "-i", "-n", "-v", "-l", "-c"],
                     "head": ["-n"], "tail": ["-n"], "sort": ["-r", "-n", "-u"],
                     "uniq": ["-c"], "find": ["-name", "-type"]}.get(c0, [])
            return sorted(set(self._file_tokens(token) + extra))
        return []
    def complete_command(self):
        text = self.input.text()
        if not text.strip(): return
        pos = self.input.cursorPosition()
        pre, tok_raw, start = self._token_at(text, pos)
        token = tok_raw.strip("\"'")
        cand = self._context_candidates([t.strip("\"'") for t in pre], token)
        matches = [c for c in cand if c.startswith(token)]
        if not matches: return
        if len(matches) == 1: repl, final = matches[0], True
        else:
            common = _common_prefix(matches)
            if len(common) > len(token): repl, final = common, False
            else:
                self.write("  " + "   ".join(matches[:22]) +
                           ("   …" if len(matches) > 22 else ""), "info")
                self._scroll_end(); return
        if final and not repl.endswith("/"): repl += " "
        newtext = text[:start] + repl + text[pos:]
        self.input.setText(newtext)
        self.input.setCursorPosition(start + len(repl))
    # ---------- io / submit ----------
    def _scroll_end(self):
        bar = self.output.verticalScrollBar()
        bar.setValue(bar.maximum())
    def write(self, text, kind="out"):
        self.output.append(_span(KIND_COLORS.get(kind, FG), _ws(html_mod.escape(text))))
    def _banner(self):
        for text, kind in [("🟢 Git Sandbox — break things here, not in real repos", "ok"),
                           ("Try:", "out"), ("  git init", "info"),
                           ("  touch hello.txt", "info"), ("  git add hello.txt", "info"),
                           ('  git commit -m "my first commit"', "info"),
                           ("  git log --oneline", "info"), ("", "out")]:
            self.write(text, kind)
    def submit(self):
        line = self.input.text()
        if not line.strip(): return
        self.output.append(_prompt_html(self.repo) + " " + _span(FG, html_mod.escape(line)))
        if not self._hs_active:
            self.history.append(line)
        self.hpos = len(self.history)
        self.input.clear()
        if line.strip() == "clear":
            self.output.clear()
        else:
            try: results = self.repo.run(line)
            except Exception as exc: results = [("sandbox error: " + str(exc), "err")]
            for text, kind in results: self.write(text, kind)
        self._refresh()
    def _trim(self):
        doc = self.output.document()
        if doc.blockCount() > 1200:
            cur = QTextCursor(doc)
            cur.movePosition(QTextCursor.Start)
            cur.movePosition(QTextCursor.NextBlock, QTextCursor.KeepAnchor,
                             doc.blockCount() - 900)
            cur.removeSelectedText()
    def _refresh(self):
        self.graph.update_from_repo(self.repo)
        self.prompt.setText(_prompt_html(self.repo))
        bar = self.output.verticalScrollBar()
        bar.setValue(bar.maximum())
        self._trim()
        cb = self.stats_cb
        if cb:
            r = self.repo
            if not getattr(r, "initialized", False):
                cb("🌱 no repository yet — run git init")
            else:
                n_merge = sum(1 for c in r.commits.values() if len(c.parents) == 2)
                where = "detached" if r.detached else str(r.current)
                cb("🌿 " + where + "  ·  commits: " + str(len(r.commits)) +
                   "  ·  branches: " + str(len(r.branches)) +
                   "  ·  merges: " + str(n_merge) +
                   "  ·  tags: " + str(len(getattr(r, "tags", {}))) +
                   "  ·  stash: " + str(len(getattr(r, "stash", []))) +
                   "  ·  remotes: " + str(len(getattr(r, "remotes", {}))))
        cb2 = self.auto_check_cb
        if cb2:
            try: cb2()
            except Exception: pass
    # ---------- recipes ----------
    def run_recipe(self, recipe):
        self.stop_recipe()
        self._reset_sandbox_quiet()
        self.recipes_running = True
        self._recipe_queue = list(recipe["cmds"])
        self._recipe_note = recipe.get("note", "")
        self.write("▶ recipe: " + recipe["title"] + "   (Esc or Stop ■ to interrupt)", "info")
        self._recipe_step()
    def stop_recipe(self):
        self.recipes_running = False
        self._type_timer.stop()
        self._next_timer.stop()
    def _reset_sandbox_quiet(self):
        self.repo.reset()
        self.output.clear()
        self.write("🎬 sandbox reset — clean stage for the demo", "info")
        self._refresh()
    def _recipe_step(self):
        if not self.recipes_running: return
        if not self._recipe_queue:
            self.recipes_running = False
            if getattr(self, "_recipe_note", ""):
                self.write("💡 " + self._recipe_note, "info")
            self.write("✔ recipe finished — the sandbox is yours", "ok")
            return
        self._typing_text = self._recipe_queue.pop(0)
        self._typing_pos = 0
        self.input.clear()
        self._type_timer.start(22)
    def _type_tick(self):
        if not self.recipes_running:
            self._type_timer.stop(); return
        if self._typing_pos < len(self._typing_text):
            self._typing_pos += 1
            self.input.setText(self._typing_text[: self._typing_pos])
            return
        self._type_timer.stop()
        self.submit()
        if self.recipes_running: self._next_timer.start(430)
    def reset_sandbox(self):
        answer = QMessageBox.question(self, "Reset sandbox",
                                      "Start over with an empty sandbox?")
        if answer == QMessageBox.Yes:
            self.stop_recipe()
            self.repo.reset()
            self.output.clear()
            self._banner()
            self._refresh()

# ---------------------------------------------------------------- lessons ----
class LessonsPage(QWidget):
    open_terminal = Signal()
    progress_changed = Signal(int)
    def __init__(self):
        super().__init__()
        self.progress = self._load()
        self._building = True
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        side = QWidget()
        sv = QVBoxLayout(side)
        sv.setContentsMargins(0, 0, 0, 0)
        box = QLineEdit()
        box.setPlaceholderText("🔍  filter lessons — title or body text…")
        self.listw = QListWidget()
        self.listw.setObjectName("lessonList")
        self.listw.setFixedWidth(270)
        sv.addWidget(box)
        sv.addWidget(self.listw, 1)
        lay.addWidget(side)
        right = QWidget()
        rv = QVBoxLayout(right)
        self.title = QLabel()
        self.title.setObjectName("lessonTitle")
        self.title.setWordWrap(True)
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        btns = QHBoxLayout()
        prev = QPushButton("◀  Prev")
        prev.setObjectName("secondaryBtn")
        self.mark_btn = QPushButton()
        self.mark_btn.setObjectName("secondaryBtn")
        nxt = QPushButton("Next  ▶")
        nxt.setObjectName("secondaryBtn")
        open_btn = QPushButton("Practice in the Sandbox →")
        btns.addWidget(prev)
        btns.addWidget(self.mark_btn)
        btns.addWidget(nxt)
        btns.addWidget(open_btn)
        btns.addStretch()
        rv.addWidget(self.title)
        rv.addWidget(self.browser, 1)
        rv.addLayout(btns)
        lay.addWidget(right, 1)
        for i, lesson in enumerate(LESSONS):
            done = bool(self.progress.get(str(i)))
            item = QListWidgetItem(("✓  " if done else "") + str(i + 1) + ". " + lesson["title"])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if done else Qt.Unchecked)
            self.listw.addItem(item)
        self._building = False
        self.listw.currentRowChanged.connect(self.show_lesson)
        self.listw.itemChanged.connect(self._item_changed)
        self.mark_btn.clicked.connect(self._toggle_mark)
        open_btn.clicked.connect(self.open_terminal.emit)
        prev.clicked.connect(lambda: self._step(-1))
        nxt.clicked.connect(lambda: self._step(1))
        box.textChanged.connect(self._filter)
        self.listw.setCurrentRow(0)
        self._emit_progress()
    @staticmethod
    def _load():
        try: return json.loads(PROGRESS_FILE.read_text())
        except Exception: return {}
    def _save(self):
        try:
            data = {}
            try:
                if PROGRESS_FILE.exists(): data = json.loads(PROGRESS_FILE.read_text())
            except Exception: data = {}
            data.update(self.progress)
            PROGRESS_FILE.write_text(json.dumps(data))
        except Exception: pass
    def show_lesson(self, i):
        lesson = LESSONS[i]
        self.title.setText(str(i + 1) + ". " + lesson["title"])
        done = bool(self.progress.get(str(i)))
        self.mark_btn.setText("✓ Completed" if done else "○  Mark as complete")
        self.browser.setHtml(WRAP_OPEN + lesson["body"] + WRAP_CLOSE)
    def _step(self, d):
        n = self.listw.count()
        if n: self.listw.setCurrentRow((self.listw.currentRow() + d) % n)
    def _filter(self, q):
        q = q.strip().lower()
        for i, l in enumerate(LESSONS):
            hay = (l["title"] + " " + _strip_tags(l["body"])).lower()
            self.listw.setRowHidden(i, bool(q) and q not in hay)
    def _item_changed(self, item):
        if self._building: return
        i = self.listw.row(item)
        checked = item.checkState() == Qt.Checked
        self._building = True
        item.setText(("✓  " if checked else "") + str(i + 1) + ". " + LESSONS[i]["title"])
        self._building = False
        self.progress[str(i)] = checked
        self._save()
        if i == self.listw.currentRow():
            self.mark_btn.setText("✓ Completed" if checked else "○  Mark as complete")
        self._emit_progress()
    def _toggle_mark(self):
        item = self.listw.currentItem()
        if item:
            item.setCheckState(Qt.Unchecked if item.checkState() == Qt.Checked
                               else Qt.Checked)
    def _emit_progress(self):
        done = sum(1 for i in range(len(LESSONS)) if self.progress.get(str(i)))
        self.progress_changed.emit(round(100 * done / len(LESSONS)))

# ---------------------------------------------------------------- recipes ----
class RecipePage(QWidget):
    goto_sandbox = Signal()
    def __init__(self):
        super().__init__()
        self.terminal = None
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.listw = QListWidget()
        self.listw.setObjectName("lessonList")
        self.listw.setFixedWidth(290)
        lay.addWidget(self.listw)
        right = QWidget()
        rv = QVBoxLayout(right)
        self.title = QLabel()
        self.title.setObjectName("lessonTitle")
        self.title.setWordWrap(True)
        self.desc = QLabel()
        self.desc.setWordWrap(True)
        self.desc.setStyleSheet("color:" + MUTED + ";")
        self.preview = QTextBrowser()
        btns = QHBoxLayout()
        self.run_btn = QPushButton("▶  Run recipe")
        self.stop_btn = QPushButton("■  Stop")
        self.stop_btn.setObjectName("secondaryBtn")
        btns.addWidget(self.run_btn); btns.addWidget(self.stop_btn); btns.addStretch()
        rv.addWidget(self.title); rv.addWidget(self.desc)
        rv.addWidget(self.preview, 1)
        rv.addLayout(btns)
        lay.addWidget(right, 1)
        for i, r in enumerate(RECIPES):
            self.listw.addItem(str(i + 1) + ".  " + r["title"])
        self.listw.currentRowChanged.connect(self.show_recipe)
        self.run_btn.clicked.connect(self._run)
        self.stop_btn.clicked.connect(self._stop)
        self.listw.setCurrentRow(0)
    def set_terminal(self, t): self.terminal = t
    def show_recipe(self, i):
        r = RECIPES[i]
        self.title.setText("📺  " + r["title"])
        self.desc.setText(r["desc"])
        self.preview.setHtml(WRAP_OPEN + _code(*r["cmds"]) + WRAP_CLOSE)
    def _run(self):
        i = self.listw.currentRow()
        if self.terminal and 0 <= i < len(RECIPES):
            self.goto_sandbox.emit()
            self.terminal.run_recipe(RECIPES[i])
    def _stop(self):
        if self.terminal: self.terminal.stop_recipe()

# ------------------------------------------------------------- challenges ----
class ChallengePage(QWidget):
    status_cb = None
    def __init__(self):
        super().__init__()
        self.terminal = None
        self.done = self._load_done()
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.listw = QListWidget()
        self.listw.setObjectName("lessonList")
        self.listw.setFixedWidth(290)
        lay.addWidget(self.listw)
        right = QWidget()
        rv = QVBoxLayout(right)
        self.title = QLabel()
        self.title.setObjectName("lessonTitle")
        self.title.setWordWrap(True)
        self.score = QLabel()
        self.score.setStyleSheet("color:" + MUTED + ";")
        self.desc = QLabel()
        self.desc.setWordWrap(True)
        self.hint = QLabel()
        self.hint.setWordWrap(True)
        self.hint.setStyleSheet("color:" + CYAN + "; background:" + PANEL +
                                "; border-left:3px solid " + CYAN + "; padding:6px;")
        self.hint.hide()
        self.feedback = QLabel()
        self.feedback.setWordWrap(True)
        btns = QHBoxLayout()
        self.hint_btn = QPushButton("💡  Hint")
        self.hint_btn.setObjectName("secondaryBtn")
        self.check_btn = QPushButton("✔  Check")
        btns.addWidget(self.hint_btn); btns.addWidget(self.check_btn); btns.addStretch()
        rv.addWidget(self.title); rv.addWidget(self.score); rv.addWidget(self.desc)
        rv.addWidget(self.hint); rv.addWidget(self.feedback)
        rv.addLayout(btns); rv.addStretch()
        lay.addWidget(right, 1)
        for i, c in enumerate(CHALLENGES):
            self.listw.addItem(str(i + 1) + ". " + c["title"])
        self.listw.currentRowChanged.connect(self.show_challenge)
        self.hint_btn.clicked.connect(lambda: self.hint.show())
        self.check_btn.clicked.connect(self._check)
        self.listw.setCurrentRow(0)
        self._refresh_list()
    def set_terminal(self, t): self.terminal = t
    @staticmethod
    def _read_file():
        try: return json.loads(PROGRESS_FILE.read_text())
        except Exception: return {}
    def _load_done(self):
        d = self._read_file().get("challenges", [])
        return set(d) if isinstance(d, list) else set()
    def _persist(self):
        data = self._read_file()
        data["challenges"] = sorted(self.done)
        try: PROGRESS_FILE.write_text(json.dumps(data))
        except Exception: pass
    def _refresh_list(self):
        for i, c in enumerate(CHALLENGES):
            self.listw.item(i).setText(("✓  " if i in self.done else "") +
                                       str(i + 1) + ". " + c["title"])
        self.score.setText("Solved: " + str(len(self.done)) + " / " + str(len(CHALLENGES)))
    def show_challenge(self, i):
        c = CHALLENGES[i]
        self.title.setText(("✓ " if i in self.done else "☆ ") + c["title"])
        self.desc.setText(c["desc"])
        self.hint.setText("💡 " + c["hint"])
        self.feedback.setText("")
        self._refresh_list()
    def try_auto_check(self):
        i = self.listw.currentRow()
        if i < 0 or i in self.done or self.terminal is None: return
        try:
            if bool(CHALLENGES[i]["check"](self.terminal.repo)): self._check()
        except Exception: pass
    def _check(self):
        i = self.listw.currentRow()
        if i < 0 or self.terminal is None: return
        c = CHALLENGES[i]
        try: ok = bool(c["check"](self.terminal.repo))
        except Exception: ok = False
        if ok:
            first = i not in self.done
            self.done.add(i); self._persist(); self._refresh_list()
            self.title.setText("✓ " + c["title"])
            self.feedback.setText("🎉 solved — " + c["title"] + " complete!")
            self.feedback.setStyleSheet("color:" + GREEN + "; font-weight:600;")
            if first and self.status_cb:
                self.status_cb("🎯 challenge solved: " + c["title"] + "  (" +
                               str(len(self.done)) + "/" + str(len(CHALLENGES)) + ")")
        else:
            self.feedback.setText("✘ not yet — check the hint and try again. (The checker inspects the live sandbox.)")
            self.feedback.setStyleSheet("color:" + RED + ";")

# ------------------------------------------------------------------ quiz -----
class QuizPage(QWidget):
    def __init__(self):
        super().__init__()
        outer = QVBoxLayout(self)
        outer.addStretch()
        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setFixedWidth(640)
        cv = QVBoxLayout(self.card)
        cv.setContentsMargins(26, 22, 26, 22)
        cv.setSpacing(12)
        self.qcount = QLabel()
        self.qcount.setStyleSheet("color:" + MUTED + ";")
        self.qlabel = QLabel()
        self.qlabel.setObjectName("qtext")
        self.qlabel.setWordWrap(True)
        cv.addWidget(self.qcount); cv.addWidget(self.qlabel)
        self.opts = [QRadioButton() for _ in range(4)]
        for b in self.opts: cv.addWidget(b)
        self.feedback = QLabel()
        self.feedback.setWordWrap(True)
        cv.addWidget(self.feedback)
        row = QHBoxLayout()
        self.check_btn = QPushButton("Check answer")
        self.next_btn = QPushButton("Next →")
        self.next_btn.hide()
        row.addWidget(self.check_btn); row.addWidget(self.next_btn); row.addStretch()
        cv.addLayout(row)
        outer.addWidget(self.card, 0, Qt.AlignHCenter)
        self.result = QFrame()
        self.result.setObjectName("card")
        self.result.setFixedWidth(640)
        rv = QVBoxLayout(self.result)
        rv.setContentsMargins(26, 30, 26, 30)
        rv.setSpacing(14)
        self.score_label = QLabel()
        self.score_label.setObjectName("lessonTitle")
        self.score_label.setAlignment(Qt.AlignCenter)
        self.msg_label = QLabel()
        self.msg_label.setWordWrap(True)
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.msg_label.setStyleSheet("color:" + MUTED + "; font-size:15px;")
        restart = QPushButton("🔄  Restart quiz")
        restart.clicked.connect(self.start)
        rv.addWidget(self.score_label); rv.addWidget(self.msg_label)
        rv.addWidget(restart, 0, Qt.AlignHCenter)
        self.result.hide()
        outer.addWidget(self.result, 0, Qt.AlignHCenter)
        outer.addStretch()
        self.check_btn.clicked.connect(self._check)
        self.next_btn.clicked.connect(self._next)
        self.start()
    @staticmethod
    def _read_best():
        try:
            return int(json.loads(PROGRESS_FILE.read_text()).get("quiz_best", -1))
        except Exception: return -1
    def _save_best(self):
        try:
            data = json.loads(PROGRESS_FILE.read_text()) if PROGRESS_FILE.exists() else {}
            data["quiz_best"] = max(int(data.get("quiz_best", -1)), self.score)
            PROGRESS_FILE.write_text(json.dumps(data))
        except Exception: pass
    def start(self):
        self.order = list(range(len(QUIZ)))
        random.shuffle(self.order)
        self.idx, self.score = 0, 0
        self.result.hide(); self.card.show()
        self._show_q()
        best = self._read_best()
        if best >= 0:
            self.qcount.setText(self.qcount.text() + "     •     best: " +
                                str(best) + "/" + str(len(QUIZ)))
    def _show_q(self):
        self.qi = self.order[self.idx]
        q = QUIZ[self.qi]
        perm = list(range(len(q["o"])))
        random.shuffle(perm)
        self.perm = perm
        self.qcount.setText("Question " + str(self.idx + 1) + " of " + str(len(QUIZ)) +
                            "     •     Score: " + str(self.score))
        self.qlabel.setText(q["q"])
        for b, j in zip(self.opts, perm):
            b.setText(q["o"][j]); b.setChecked(False); b.setEnabled(True); b.setStyleSheet("")
        self.feedback.setText("")
        self.check_btn.show(); self.check_btn.setEnabled(True)
        self.next_btn.hide()
    def _check(self):
        sel = next((b for b in self.opts if b.isChecked()), None)
        if sel is None:
            self.feedback.setText("Select an answer first 🙂")
            self.feedback.setStyleSheet("color:" + YELLOW + ";")
            return
        q = QUIZ[self.qi]
        correct = self.perm.index(q["a"])
        self.check_btn.setEnabled(False)
        for i, b in enumerate(self.opts):
            b.setEnabled(False)
            if i == correct:
                b.setText("✔  " + b.text())
                b.setStyleSheet("color:" + GREEN + "; font-weight:600;")
            elif b is sel:
                b.setText("✘  " + b.text())
                b.setStyleSheet("color:" + RED + ";")
        if sel is self.opts[correct]:
            self.score += 1
            self.feedback.setText("✅ Correct!  " + q["e"])
            self.feedback.setStyleSheet("color:" + GREEN + ";")
        else:
            self.feedback.setText("❌ Not quite.  " + q["e"])
            self.feedback.setStyleSheet("color:" + RED + ";")
        self.check_btn.hide()
        self.next_btn.setText("See results 🏁" if self.idx == len(QUIZ) - 1 else "Next →")
        self.next_btn.show()
    def _next(self):
        if self.idx < len(QUIZ) - 1:
            self.idx += 1; self._show_q()
        else: self._finish()
    def _finish(self):
        self._save_best()
        n = len(QUIZ)
        pct = round(100 * self.score / n)
        if self.score == n: msg = "🏆 Perfect score — you could teach this course."
        elif pct >= 80: msg = "🎉 Great job! Your Git fundamentals are solid."
        elif pct >= 60: msg = "👍 Decent! Revisit the lessons on the ones you missed."
        else: msg = "💪 Keep going — walk through the Lessons and Sandbox once more."
        best = max(self._read_best(), self.score)
        self.score_label.setText("You scored " + str(self.score) + "/" + str(n) +
                                 "  (" + str(pct) + "%)")
        self.msg_label.setText(msg + "     ·     best so far: " + str(best) + "/" + str(n))
        self.card.hide(); self.result.show()

# ---------------------------------------------------------------- palette ----
class _PaletteEdit(QLineEdit):
    def __init__(self, dlg):
        super().__init__()
        self._dlg = dlg
    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Down, Qt.Key_Up):
            lw = self._dlg.listw
            row = lw.currentRow() + (1 if e.key() == Qt.Key_Down else -1)
            lw.setCurrentRow(max(0, min(lw.count() - 1, row)))
        else: super().keyPressEvent(e)

class _Palette(QDialog):
    def __init__(self, parent, actions):
        super().__init__(parent)
        self.setWindowTitle("Command palette — GitLearn  (Ctrl+K)")
        self.setModal(True)
        self.resize(580, 440)
        v = QVBoxLayout(self)
        self.edit = _PaletteEdit(self)
        self.edit.setPlaceholderText("Jump to a page, lesson, recipe or challenge…  (↑↓ · Enter · Esc)")
        self.listw = QListWidget()
        v.addWidget(self.edit); v.addWidget(self.listw)
        self.actions = actions
        self.edit.textChanged.connect(self._fill)
        self.edit.returnPressed.connect(self._go)
        self.listw.itemActivated.connect(lambda _i: self._go())
        self._fill("")
        self.edit.setFocus()
    def _fill(self, q):
        self.listw.clear()
        ql = q.lower()
        for label, _fn in self.actions:
            if ql in label.lower(): self.listw.addItem(label)
        if self.listw.count(): self.listw.setCurrentRow(0)
    def _go(self):
        it = self.listw.currentItem()
        if not it: return
        for label, fn in self.actions:
            if label == it.text():
                self.accept(); fn(); return

# ----------------------------------------------------------------- shell -----
STYLESHEET = """
* { font-family: 'Segoe UI', 'Ubuntu', 'Helvetica', sans-serif; font-size: 14px; }
QMainWindow, QWidget { background-color: %(BG)s; color: %(FG)s; }
QFrame#header { background: %(P2)s; border-bottom: 1px solid %(BR)s; }
QLabel#titleLabel { font-size: 22px; font-weight: 800; color: %(AC)s; }
QLabel#subtitleLabel { color: %(MU)s; font-size: 13px; }
QLabel#panelTitle { font-size: 15px; font-weight: 600; color: #a9b1d6; }
QLabel#lessonTitle { font-size: 20px; font-weight: 700; color: #e5e9f0; }
QLabel#qtext { font-size: 16px; font-weight: 600; }
QListWidget#navList { background: %(P2)s; border: none; padding: 10px 6px; outline: 0; }
QListWidget#navList::item { padding: 11px 14px; border-radius: 8px; margin: 2px 6px; color: #a9b1d6; }
QListWidget#navList::item:hover { background: %(PA)s; }
QListWidget#navList::item:selected { background: %(AC)s; color: %(P2)s; font-weight: 600; }
QListWidget#lessonList { background: transparent; border: none; }
QListWidget#lessonList::item { padding: 9px 10px; border-radius: 6px; margin: 2px 4px; }
QListWidget#lessonList::item:hover { background: %(PA)s; }
QListWidget#lessonList::item:selected { background: %(PA)s; color: %(AC)s; }
QTextBrowser { background: %(P2)s; border: 1px solid %(BR)s; border-radius: 8px; padding: 10px; }
QTextBrowser#termOut { background: #0f0f17; }
QLineEdit { background: %(P2)s; border: 1px solid %(BR)s; border-radius: 6px; padding: 7px; color: %(FG)s; }
QLineEdit:focus { border-color: %(AC)s; }
QPushButton { background-color: %(AC)s; color: %(P2)s; border: none; border-radius: 6px; padding: 8px 16px; font-weight: 600; }
QPushButton:hover { background-color: #89ddff; }
QPushButton:pressed { background-color: #565f89; }
QPushButton#secondaryBtn { background: %(PA)s; color: %(FG)s; border: 1px solid %(BR)s; }
QPushButton#secondaryBtn:hover { border-color: %(AC)s; }
QFrame#card { background: %(PA)s; border: 1px solid %(BR)s; border-radius: 12px; }
QProgressBar { background: %(P2)s; border: none; border-radius: 7px; min-height: 14px; max-height: 14px; }
QProgressBar::chunk { background-color: %(GR)s; border-radius: 7px; }
QRadioButton { spacing: 10px; padding: 5px; }
QRadioButton::indicator { width: 15px; height: 15px; border-radius: 8px; border: 1px solid #565f89; background: %(P2)s; }
QRadioButton::indicator:checked { background: %(AC)s; border-color: %(AC)s; }
QSplitter::handle { background: %(BG)s; }
QScrollBar:vertical { background: transparent; width: 10px; }
QScrollBar::handle:vertical { background: %(BR)s; border-radius: 5px; min-height: 30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: transparent; height: 10px; }
QScrollBar::handle:horizontal { background: %(BR)s; border-radius: 5px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QMessageBox { background: %(PA)s; }
QStatusBar { background: %(P2)s; color: %(MU)s; }
""" % {"BG": APP_BG, "PA": PANEL, "P2": PANEL2, "BR": BORDER, "FG": FG,
       "MU": MUTED, "AC": ACCENT, "GR": GREEN}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        app = QApplication.instance()
        app.setOrganizationName("GitLearn")
        app.setApplicationName("GitLearn")
        self.settings = QSettings()
        self.setWindowTitle("GitLearn — learn Git by doing")
        self.resize(1280, 800)
        geo = self.settings.value("geometry")
        if geo is not None:
            try: self.restoreGeometry(geo)
            except Exception: pass
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        header = QFrame()
        header.setObjectName("header")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 12, 20, 12)
        titles = QVBoxLayout()
        t1 = QLabel("GitLearn")
        t1.setObjectName("titleLabel")
        t2 = QLabel("lessons · sandbox · recipes · challenges · quiz  —  press Ctrl+K to jump anywhere")
        t2.setObjectName("subtitleLabel")
        titles.addWidget(t1); titles.addWidget(t2)
        hl.addLayout(titles); hl.addStretch()
        self.plabel = QLabel()
        self.plabel.setObjectName("subtitleLabel")
        self.pbar = QProgressBar()
        self.pbar.setFixedWidth(190)
        self.pbar.setTextVisible(False)
        hl.addWidget(self.plabel); hl.addWidget(self.pbar)
        root.addWidget(header)
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        self.nav = QListWidget()
        self.nav.setObjectName("navList")
        self.nav.setFixedWidth(200)
        for label in ["📘  Lessons", "⌨️  Sandbox", "📺  Recipes", "🎯  Challenges",
                      "🧠  Quiz", "📋  Cheat sheet"]:
            self.nav.addItem(label)
        self.stack = QStackedWidget()
        self.lessons = LessonsPage()
        self.terminal = TerminalPage()
        self.recipes = RecipePage()
        self.challenges = ChallengePage()
        self.quiz = QuizPage()
        self.cheat = QTextBrowser()
        self.cheat.setOpenExternalLinks(True)
        self.cheat.setHtml(_cheat_html())
        for w in (self.lessons, self.terminal, self.recipes, self.challenges,
                  self.quiz, self.cheat):
            self.stack.addWidget(w)
        body.addWidget(self.nav); body.addWidget(self.stack, 1)
        root.addLayout(body, 1)
        self.recipes.set_terminal(self.terminal)
        self.challenges.set_terminal(self.terminal)
        self.terminal.stats_cb = self._set_status
        self.challenges.status_cb = self._set_status
        self.terminal.auto_check_cb = self.challenges.try_auto_check
        self.recipes.goto_sandbox.connect(lambda: self.nav.setCurrentRow(1))
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.setCurrentRow(0)
        self.lessons.progress_changed.connect(self._on_progress)
        self.lessons.open_terminal.connect(lambda: self.nav.setCurrentRow(1))
        done = sum(1 for i in range(len(LESSONS)) if self.lessons.progress.get(str(i)))
        self._on_progress(round(100 * done / len(LESSONS)))
        self._set_status("🌱 no repository yet — Sandbox ▸ git init")
        sc = QShortcut(QKeySequence("Ctrl+K"), self)
        sc.activated.connect(self.open_palette)
        if not self.settings.value("welcomeSeen", False, bool):
            QTimer.singleShot(400, self._welcome)
    def closeEvent(self, e):
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(e)
    def _set_status(self, s): self.statusBar().showMessage(s)
    def _on_progress(self, pct):
        self.pbar.setValue(pct)
        self.plabel.setText(str(round(pct * len(LESSONS) / 100)) + "/" +
                            str(len(LESSONS)) + " lessons")
    def _goto(self, page, row):
        def f():
            self.nav.setCurrentRow(page)
            w = {0: self.lessons, 2: self.recipes, 3: self.challenges}.get(page)
            if w is not None and row is not None: w.listw.setCurrentRow(row)
        return f
    def _welcome(self):
        self.settings.setValue("welcomeSeen", True)
        QMessageBox.information(
            self, "Welcome to GitLearn 🎓",
            "1.  📘 Lessons — read a topic, then hit “Practice in the Sandbox”.\n"
            "2.  ⌨️  Sandbox — everything is simulated-for-real. Tab completes, ↑↓ "
            "history, Ctrl+R searches it, Ctrl+L clears.\n"
            "3.  📺 Recipes — watch complete workflows type themselves (Esc stops).\n"
            "4.  🎯 Challenges — solve tasks; success is detected automatically.\n\n"
            "Ctrl+K jumps anywhere. Break things here, not in real repos!")
    def _show_welcome_again(self):
        self.settings.setValue("welcomeSeen", False)
        self._welcome()
    def _export_report(self):
        done = [i for i in range(len(LESSONS)) if self.lessons.progress.get(str(i))]
        ch = sorted(self.challenges.done)
        try:
            best = int(json.loads(PROGRESS_FILE.read_text()).get("quiz_best", -1))
        except Exception: best = -1
        lines = ["# GitLearn progress report", "",
                 "generated: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "",
                 "## Lessons (" + str(len(done)) + "/" + str(len(LESSONS)) + ")"]
        lines += ["- [x] " + str(i + 1) + ". " + LESSONS[i]["title"] for i in done]
        lines += ["- [ ] " + str(i + 1) + ". " + LESSONS[i]["title"]
                  for i in range(len(LESSONS)) if i not in done]
        lines += ["", "## Challenges (" + str(len(ch)) + "/" + str(len(CHALLENGES)) + ")"]
        lines += ["- [x] " + CHALLENGES[i]["title"] for i in ch]
        lines += ["", "## Quiz best: " +
                  ((str(best) + "/" + str(len(QUIZ))) if best >= 0 else "not taken yet")]
        path = Path.home() / "gitlearn_report.md"
        try: path.write_text("\n".join(lines))
        except Exception as exc:
            QMessageBox.warning(self, "Export failed", str(exc)); return
        QMessageBox.information(self, "Report exported", "Written to:\n" + str(path))
    def open_palette(self):
        acts = [("Go · Lessons", self._goto(0, None)),
                ("Go · Sandbox terminal", self._goto(1, None)),
                ("Go · Recipe book", self._goto(2, None)),
                ("Go · Challenges", self._goto(3, None)),
                ("Go · Quiz", self._goto(4, None)),
                ("Go · Cheat sheet", self._goto(5, None))]
        for i, l in enumerate(LESSONS):
            acts.append(("Lesson " + str(i + 1) + " · " + l["title"], self._goto(0, i)))
        for i, r in enumerate(RECIPES):
            acts.append(("Recipe · " + r["title"], self._goto(2, i)))
        for i, c in enumerate(CHALLENGES):
            acts.append(("Challenge · " + c["title"], self._goto(3, i)))
        acts += [("Action · reset sandbox", self.terminal.reset_sandbox),
                 ("Action · stop running recipe", self.terminal.stop_recipe),
                 ("Action · export progress report (markdown)", self._export_report),
                 ("Action · show welcome", self._show_welcome_again)]
        _Palette(self, acts).exec()

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()