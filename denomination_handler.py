"""
Denomination Handler
---------------------
Adjusts the LLM system prompt and response framing based on the user's
selected Christian denomination (Catholic / Protestant / Orthodox / General).
"""

from dataclasses import dataclass


@dataclass
class DenominationProfile:
    name:           str
    short:          str
    emoji:          str
    description:    str
    prompt_context: str   # injected into system prompt
    scripture_note: str   # note about how this tradition uses scripture


DENOMINATIONS: dict[str, DenominationProfile] = {

    "General / Ecumenical": DenominationProfile(
        name="General / Ecumenical",
        short="General",
        emoji="✝️",
        description="Broad Christian perspective respecting all traditions.",
        prompt_context=(
            "Respond from a broad, ecumenical Christian perspective. "
            "Acknowledge that different denominations may have varying views. "
            "Prioritise what is common across mainstream Christianity. "
            "Be respectful of all Christian traditions."
        ),
        scripture_note="Uses the 66-book Protestant canon by default; may reference Deuterocanon where relevant.",
    ),

    "Catholic": DenominationProfile(
        name="Catholic",
        short="Catholic",
        emoji="🕊️",
        description="Roman Catholic tradition — Scripture, Tradition, and the Magisterium.",
        prompt_context=(
            "Respond from a Roman Catholic perspective. "
            "Honour the three pillars: Sacred Scripture, Sacred Tradition, and the Magisterium. "
            "Reference the Catechism of the Catholic Church where helpful. "
            "Acknowledge the Deuterocanonical books (Tobit, Judith, Maccabees, Sirach, Wisdom, Baruch) "
            "as part of the Old Testament canon. "
            "Reference Papal encyclicals, Church Fathers, and Saints where appropriate. "
            "Acknowledge the role of the Pope, bishops, and apostolic succession."
        ),
        scripture_note="Canon includes 73 books (includes Deuterocanon). Uses NAB or Douay-Rheims.",
    ),

    "Protestant": DenominationProfile(
        name="Protestant",
        short="Protestant",
        emoji="📖",
        description="Protestant tradition — Sola Scriptura, faith alone, grace alone.",
        prompt_context=(
            "Respond from a Protestant Christian perspective. "
            "Uphold Sola Scriptura — the Bible alone as the ultimate authority. "
            "Reference the five Reformation 'Solas': Scripture alone, Faith alone, Grace alone, "
            "Christ alone, Glory to God alone. "
            "Do not treat Tradition or Papal authority as equal to Scripture. "
            "Acknowledge diversity within Protestantism (Baptist, Methodist, Presbyterian, Lutheran, etc.)."
        ),
        scripture_note="Canon is 66 books. Uses NIV, ESV, KJV, or NASB.",
    ),

    "Eastern Orthodox": DenominationProfile(
        name="Eastern Orthodox",
        short="Orthodox",
        emoji="☦️",
        description="Eastern Orthodox tradition — Scripture, Holy Tradition, and the Church Fathers.",
        prompt_context=(
            "Respond from an Eastern Orthodox Christian perspective. "
            "Hold Scripture and Holy Tradition as equal witnesses to the Faith. "
            "Reference the Church Fathers (Chrysostom, Basil, Gregory, Athanasius, etc.) where helpful. "
            "Acknowledge the seven Ecumenical Councils as authoritative. "
            "Use theologically precise Orthodox terminology: Theosis, Theotokos, Philokalia, Hesychasm "
            "where relevant. "
            "Honour the liturgical life of the Church."
        ),
        scripture_note="Uses the Septuagint (LXX) as primary OT text. 79-book canon.",
    ),

    "Baptist": DenominationProfile(
        name="Baptist",
        short="Baptist",
        emoji="💧",
        description="Baptist tradition — believer's baptism, congregational polity, Scripture authority.",
        prompt_context=(
            "Respond from a Baptist Christian perspective. "
            "Affirm the authority of the Bible as God's Word. "
            "Emphasise personal faith, believer's baptism by immersion, "
            "the priesthood of all believers, and congregational church governance. "
            "Affirm salvation by grace through faith alone."
        ),
        scripture_note="66-book canon. Typically uses KJV or NKJV.",
    ),

    "Pentecostal / Charismatic": DenominationProfile(
        name="Pentecostal / Charismatic",
        short="Pentecostal",
        emoji="🔥",
        description="Spirit-filled tradition — gifts of the Spirit, healing, tongues.",
        prompt_context=(
            "Respond from a Pentecostal/Charismatic Christian perspective. "
            "Affirm the continuing gifts of the Holy Spirit: tongues, prophecy, healing, and miracles. "
            "Emphasise the baptism of the Holy Spirit as a distinct experience. "
            "Use vibrant, Spirit-led language appropriate to this tradition."
        ),
        scripture_note="66-book canon. Uses NKJV or NIV.",
    ),
}


def get_denomination(name: str) -> DenominationProfile:
    """Return denomination profile by name, falling back to General."""
    return DENOMINATIONS.get(name, DENOMINATIONS["General / Ecumenical"])


def list_denominations() -> list[str]:
    return list(DENOMINATIONS.keys())


def build_denomination_system_snippet(name: str) -> str:
    """Return the prompt snippet to inject for this denomination."""
    profile = get_denomination(name)
    return (
        f"DENOMINATION CONTEXT ({profile.name}):\n"
        f"{profile.prompt_context}\n"
        f"Scripture note: {profile.scripture_note}"
    )
