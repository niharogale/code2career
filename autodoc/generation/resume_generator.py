"""Resume bullet generation from git history and semantic changes."""

import subprocess
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import defaultdict

from autodoc.core.repository import Repository
from autodoc.analysis.semantic_changes import SemanticChangeAnalyzer, ChangeCategory


@dataclass
class GitCommit:
    """Represents a git commit."""
    hash: str
    author: str
    date: datetime
    message: str
    files_changed: List[str]
    insertions: int
    deletions: int


@dataclass
class ContributionStats:
    """Statistics about contributions to the project."""
    total_commits: int
    total_insertions: int
    total_deletions: int
    files_touched: int
    languages_used: List[str]
    breaking_changes: int
    additive_changes: int
    internal_changes: int
    docs_changes: int


@dataclass
class ResumeBullet:
    """A single resume bullet point."""
    text: str
    impact_score: float
    category: str
    evidence: List[str] = field(default_factory=list)


def get_git_commits(repo_root: Path, limit: int = 100, since: Optional[str] = None) -> List[GitCommit]:
    """
    Retrieve git commit history from the repository.
    """
    cmd = ["git", "log", f"--max-count={limit}", "--pretty=format:%H|%an|%at|%s", "--numstat"]
    
    if since:
        cmd.append(f"--since={since}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError:
        return []
    
    commits = []
    lines = result.stdout.strip().split("\n")
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        if "|" in line:
            parts = line.split("|", 3)
            if len(parts) < 4:
                i += 1
                continue
            
            commit_hash, author, timestamp, message = parts
            date = datetime.fromtimestamp(int(timestamp))
            
            files_changed = []
            insertions = 0
            deletions = 0
            i += 1
            
            while i < len(lines) and lines[i].strip() and "|" not in lines[i]:
                numstat_line = lines[i].strip()
                if numstat_line:
                    parts = numstat_line.split("\t")
                    if len(parts) >= 3:
                        ins, dels, filepath = parts[0], parts[1], parts[2]
                        files_changed.append(filepath)
                        try:
                            insertions += int(ins) if ins != "-" else 0
                            deletions += int(dels) if dels != "-" else 0
                        except ValueError:
                            pass
                i += 1
            
            commits.append(GitCommit(
                hash=commit_hash[:8],
                author=author,
                date=date,
                message=message,
                files_changed=files_changed,
                insertions=insertions,
                deletions=deletions
            ))
        else:
            i += 1
    
    return commits


def calculate_contribution_stats(
    commits: List[GitCommit],
    state: Dict[str, Any],
    author_filter: Optional[str] = None
) -> ContributionStats:
    """Calculate contribution statistics from commits."""
    filtered_commits = commits
    if author_filter:
        filtered_commits = [c for c in commits if author_filter.lower() in c.author.lower()]
    
    total_insertions = sum(c.insertions for c in filtered_commits)
    total_deletions = sum(c.deletions for c in filtered_commits)
    
    files_touched = set()
    for commit in filtered_commits:
        files_touched.update(commit.files_changed)
    
    files = state.get("files", {})
    languages_used = set()
    for path in files_touched:
        if path in files:
            lang = files[path].get("language")
            if lang:
                languages_used.add(lang)
    
    breaking_changes = 0
    additive_changes = 0
    internal_changes = 0
    docs_changes = 0
    
    for path, info in files.items():
        semantic_category = info.get("semantic_category")
        if not semantic_category:
            continue
        
        if semantic_category == "breaking":
            breaking_changes += 1
        elif semantic_category == "additive":
            additive_changes += 1
        elif semantic_category == "internal":
            internal_changes += 1
        elif semantic_category == "docs-only":
            docs_changes += 1
    
    return ContributionStats(
        total_commits=len(filtered_commits),
        total_insertions=total_insertions,
        total_deletions=total_deletions,
        files_touched=len(files_touched),
        languages_used=sorted(languages_used),
        breaking_changes=breaking_changes,
        additive_changes=additive_changes,
        internal_changes=internal_changes,
        docs_changes=docs_changes
    )


def extract_feature_commits(commits: List[GitCommit]) -> List[GitCommit]:
    """Extract commits that represent features or significant work."""
    feature_keywords = [
        r"\badd(ed|s)?\b",
        r"\bimplement(ed|s)?\b",
        r"\bcreate(d|s)?\b",
        r"\bbuild(s)?\b",
        r"\bdevelop(ed)?\b",
        r"\bintroduc(e|ed)\b",
        r"\bfeature\b",
        r"\bnew\b",
    ]
    
    exclude_keywords = [
        r"\bfix(ed|es)?\b",
        r"\brefactor(ed)?\b",
        r"\bdocs?\b",
        r"\btypo\b",
        r"\bupdate\b",
        r"\bcleanup\b",
    ]
    
    feature_pattern = re.compile("|".join(feature_keywords), re.IGNORECASE)
    exclude_pattern = re.compile("|".join(exclude_keywords), re.IGNORECASE)
    
    features = []
    for commit in commits:
        message = commit.message.lower()
        
        if feature_pattern.search(message) and not exclude_pattern.search(message):
            features.append(commit)
        elif len(commit.files_changed) >= 5 and commit.insertions >= 50:
            features.append(commit)
    
    return features


def generate_technical_bullets(
    stats: ContributionStats,
    commits: List[GitCommit],
    state: Dict[str, Any]
) -> List[ResumeBullet]:
    """Generate technical implementation bullets."""
    bullets = []
    repo_name = state.get("repo", {}).get("name", "project")
    files = state.get("files", {})
    
    if stats.languages_used:
        langs_str = ", ".join(stats.languages_used[:3])
        more_langs = f" and {len(stats.languages_used) - 3} more" if len(stats.languages_used) > 3 else ""
        
        bullets.append(ResumeBullet(
            text=f"Developed {repo_name}, a {langs_str}{more_langs} project with {stats.files_touched} source files and {stats.total_insertions:,} lines of code",
            impact_score=8.0,
            category="technical",
            evidence=[f"{len(commits)} commits", f"{stats.files_touched} files"]
        ))
    
    if stats.breaking_changes > 0 or stats.additive_changes > 5:
        design_terms = []
        if stats.additive_changes > 0:
            design_terms.append(f"{stats.additive_changes} new features")
        if stats.breaking_changes > 0:
            design_terms.append(f"{stats.breaking_changes} API redesigns")
        
        bullets.append(ResumeBullet(
            text=f"Architected and implemented {', '.join(design_terms)}, demonstrating strong software design and API development skills",
            impact_score=7.5,
            category="technical",
            evidence=[f"{stats.additive_changes} additive changes", f"{stats.breaking_changes} breaking changes"]
        ))
    
    if stats.internal_changes > 10:
        bullets.append(ResumeBullet(
            text=f"Improved code quality through {stats.internal_changes} internal refactorings, maintaining clean architecture without breaking public APIs",
            impact_score=6.5,
            category="technical",
            evidence=[f"{stats.internal_changes} internal changes"]
        ))
    
    feature_commits = extract_feature_commits(commits)
    if feature_commits:
        for commit in feature_commits[:3]:
            message = commit.message.strip()
            if message:
                message = message[0].upper() + message[1:]
                
                bullets.append(ResumeBullet(
                    text=f"Implemented {message}, touching {len(commit.files_changed)} files with {commit.insertions} additions",
                    impact_score=7.0,
                    category="technical",
                    evidence=[commit.hash]
                ))
    
    return bullets


def generate_impact_bullets(
    stats: ContributionStats,
    commits: List[GitCommit],
    state: Dict[str, Any]
) -> List[ResumeBullet]:
    """Generate impact-focused bullets."""
    bullets = []
    repo_name = state.get("repo", {}).get("name", "project")
    
    if stats.total_commits >= 10:
        bullets.append(ResumeBullet(
            text=f"Contributed {stats.total_commits} commits totaling {stats.total_insertions:,} additions and {stats.total_deletions:,} deletions across {stats.files_touched} files",
            impact_score=6.0,
            category="impact",
            evidence=[f"{stats.total_commits} commits"]
        ))
    
    files = state.get("files", {})
    if len(files) >= 20:
        bullets.append(ResumeBullet(
            text=f"Built comprehensive codebase with {len(files)} modules demonstrating full-stack development capabilities",
            impact_score=7.0,
            category="impact",
            evidence=[f"{len(files)} files total"]
        ))
    
    test_files = sum(1 for path in files if "test" in path.lower())
    if test_files >= 5:
        bullets.append(ResumeBullet(
            text=f"Established robust testing practices with {test_files} test files ensuring code quality and reliability",
            impact_score=6.5,
            category="impact",
            evidence=[f"{test_files} test files"]
        ))
    
    if stats.docs_changes >= 5:
        bullets.append(ResumeBullet(
            text=f"Maintained comprehensive documentation with {stats.docs_changes} documentation updates improving code maintainability",
            impact_score=5.5,
            category="impact",
            evidence=[f"{stats.docs_changes} doc changes"]
        ))
    
    return bullets


def generate_collaboration_bullets(
    commits: List[GitCommit],
    state: Dict[str, Any]
) -> List[ResumeBullet]:
    """Generate collaboration-focused bullets."""
    bullets = []
    
    good_messages = sum(1 for c in commits if len(c.message) >= 20 and c.message[0].isupper())
    if good_messages >= len(commits) * 0.7:
        bullets.append(ResumeBullet(
            text=f"Followed best practices with clear, descriptive commit messages and structured version control workflow",
            impact_score=5.0,
            category="collaboration",
            evidence=[f"{good_messages}/{len(commits)} quality commit messages"]
        ))
    
    avg_insertions = sum(c.insertions for c in commits) / len(commits) if commits else 0
    if avg_insertions < 100 and len(commits) >= 20:
        bullets.append(ResumeBullet(
            text=f"Practiced iterative development with {len(commits)} incremental commits, enabling easy code review and collaboration",
            impact_score=5.5,
            category="collaboration",
            evidence=[f"Average {int(avg_insertions)} LOC per commit"]
        ))
    
    return bullets


def generate_resume_bullets(
    state: Dict[str, Any],
    repo_root: Optional[Path] = None,
    author_filter: Optional[str] = None,
    limit: int = 50
) -> List[ResumeBullet]:
    """Generate resume bullets from project state and git history."""
    if repo_root is None:
        repo_root = Path.cwd()
    
    commits = get_git_commits(repo_root, limit=limit)
    if not commits:
        return []
    
    stats = calculate_contribution_stats(commits, state, author_filter)
    
    bullets = []
    bullets.extend(generate_technical_bullets(stats, commits, state))
    bullets.extend(generate_impact_bullets(stats, commits, state))
    bullets.extend(generate_collaboration_bullets(commits, state))
    
    bullets.sort(key=lambda b: b.impact_score, reverse=True)
    
    return bullets


def format_resume_bullets(
    bullets: List[ResumeBullet],
    style: str = "standard",
    max_bullets: int = 5
) -> str:
    """Format resume bullets for output."""
    lines = []
    
    for i, bullet in enumerate(bullets[:max_bullets], 1):
        if style == "standard":
            lines.append(f"• {bullet.text}")
        
        elif style == "detailed":
            lines.append(f"• {bullet.text}")
            lines.append(f"  Category: {bullet.category} | Impact: {bullet.impact_score}/10")
            if bullet.evidence:
                lines.append(f"  Evidence: {', '.join(bullet.evidence[:3])}")
            lines.append("")
        
        elif style == "concise":
            text = bullet.text
            if len(text) > 100:
                text = text[:97] + "..."
            lines.append(f"• {text}")
    
    return "\n".join(lines)


def export_resume_bullets_json(bullets: List[ResumeBullet]) -> Dict[str, Any]:
    """Export resume bullets to JSON-serializable format."""
    return {
        "bullets": [
            {
                "text": b.text,
                "impact_score": b.impact_score,
                "category": b.category,
                "evidence": b.evidence
            }
            for b in bullets
        ],
        "total_bullets": len(bullets),
        "categories": list(set(b.category for b in bullets))
    }
