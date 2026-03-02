"""HR system example: generates a D2 diagram of templates and rules.

Run:
    uv run python examples/hr_system.py

Prints D2 text to stdout. If the `d2` CLI is installed, also renders
an SVG to examples/hr_system.svg.
"""

import sys
import os

# Allow running from the repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clipspyx import Environment
from clipspyx.dsl import Template, Rule, Multi


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

class Skill(Template):
    """A named skill with proficiency level."""
    name: str
    """Skill identifier, e.g. 'Python' or 'SQL'"""
    proficiency: int = 1
    """1 = beginner, 5 = expert"""


class Employee(Template):
    """An employee in the organization."""
    name: str
    """Full legal name"""
    title: str
    """Current job title"""
    years: int = 0
    """Years of service in the company"""


class Department(Template):
    """An organizational department."""
    name: str
    """Department name, e.g. 'Engineering'"""
    head: Employee
    """The department head (fact-address to Employee)"""


class Project(Template):
    """A project that requires certain skills."""
    name: str
    """Project codename"""
    required_skill: str
    """Skill name that team members must have"""
    min_proficiency: int = 1
    """Minimum proficiency level required"""


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------

class AssignProject(Rule):
    """Match employees to projects by skill."""
    e = Employee(name=name)
    Skill(name=skill, proficiency=prof)  # has_skill
    """Employee must hold the skill required by the project"""
    Project(name=proj, required_skill=skill, min_proficiency=min_prof)  # needs_skill
    """Project defines which skill is needed and the minimum proficiency bar"""
    prof >= min_prof  # qualified
    """Only assign if the employee's proficiency meets the project minimum"""

    def __action__(self):
        print(f"Assign {self.name} to project {self.proj}")


class PromoteEmployee(Rule):
    """Promote employees with enough experience."""
    __salience__ = 5
    e = Employee(name=name, years=years)
    years >= 10  # senior
    """Employees with 10+ years are candidates for promotion"""

    def __action__(self):
        print(f"Consider promoting {self.name} ({self.years} years)")


class SkillMatch(Rule):
    """Find department heads with relevant skills."""
    Department(name=dept, head=head_ref)  # in_dept
    """The department whose head we are evaluating"""
    e = Employee(name=name)
    Skill(name=skill, proficiency=prof)  # has_expertise
    """Skill record proving the employee's capability"""
    prof >= 3  # expert_level
    """Proficiency of 3 or above qualifies as expert"""

    def __action__(self):
        print(f"{self.name} has expert skill {self.skill} for dept {self.dept}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    env = Environment()

    # Define all templates
    env.define(Skill)
    env.define(Employee)
    env.define(Department)
    env.define(Project)

    # Define all rules
    env.define(AssignProject)
    env.define(PromoteEmployee)
    env.define(SkillMatch)

    # Generate D2 diagram
    d2_text = env.visualize(group_by_kind=True)
    print(d2_text)

    # Try rendering SVG if d2 is available
    svg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hr_system.svg')
    try:
        env.visualize(output=svg_path, group_by_kind=True)
        print(f"SVG rendered to {svg_path}", file=sys.stderr)
    except FileNotFoundError:
        print("d2 CLI not found; skipping SVG render", file=sys.stderr)


if __name__ == '__main__':
    main()
