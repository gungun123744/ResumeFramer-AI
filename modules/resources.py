
from urllib.parse import quote_plus


def get_learning_resources(skill, language="No preference"):
    skill = (skill or "").strip()

    if not skill:
        return []

    suffix = "" if language == "No preference" else f" {language}"
    query = quote_plus(skill)
    tutorial_query = quote_plus(f"{skill}{suffix} tutorial")

    return [
        {
            "type": "YouTube",
            "title": f"{skill} tutorials",
            "description": "Video explanations and practical walkthroughs.",
            "url": (
                "https://www.youtube.com/results?search_query="
                + tutorial_query
            ),
        },
        {
            "type": "Official documentation",
            "title": f"{skill} documentation",
            "description": "Find official concepts, APIs and examples.",
            "url": (
                "https://www.google.com/search?q="
                + quote_plus(f"{skill} official documentation")
            ),
        },
        {
            "type": "Articles and guides",
            "title": f"Learn {skill} step by step",
            "description": "Written guides and learning explanations.",
            "url": (
                "https://www.google.com/search?q="
                + quote_plus(f"{skill}{suffix} learning guide")
            ),
        },
        {
            "type": "GitHub projects",
            "title": f"{skill} example projects",
            "description": "Explore example repositories and implementations.",
            "url": (
                "https://github.com/search?q="
                + query
                + "&type=repositories"
            ),
        },
        {
            "type": "Practice",
            "title": f"{skill} practice exercises",
            "description": "Find exercises to test your understanding.",
            "url": (
                "https://www.google.com/search?q="
                + quote_plus(f"{skill}{suffix} practice exercises")
            ),
        },
    ]


def get_resources_for_skills(skills, language="No preference"):
    results = []
    seen = set()

    for skill in skills:
        if not isinstance(skill, str):
            continue

        skill = skill.strip()

        if not skill or skill.lower() in seen:
            continue

        seen.add(skill.lower())

        results.append({
            "skill": skill,
            "resources": get_learning_resources(skill, language),
        })

    return results
