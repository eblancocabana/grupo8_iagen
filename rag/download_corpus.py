from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

import requests

from app.config import settings


USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) CodexCorpusFetcher/1.0"
PUBMED_HOST = "eutils.ncbi.nlm.nih.gov"


@dataclass(frozen=True, slots=True)
class CorpusSource:
    doc_id: str
    title: str
    year: int
    language: str
    source_type: str
    topic: str
    inclusion_reason: str
    source_url: str
    filename: str
    fetch_kind: str


CURATED_SOURCES: tuple[CorpusSource, ...] = (
    CorpusSource(
        doc_id="who_physical_activity_2020",
        title="WHO Guidelines on Physical Activity and Sedentary Behaviour",
        year=2020,
        language="en",
        source_type="official_guideline",
        topic="general_health",
        inclusion_reason="Foundational public-health guideline for activity dose and general-health framing.",
        source_url="https://iris.who.int/server/api/core/bitstreams/faa83413-d89e-4be9-bb01-b24671aef7ca/content",
        filename="who_physical_activity_2020.pdf",
        fetch_kind="binary",
    ),
    CorpusSource(
        doc_id="nsca_professional_standards_2017",
        title="NSCA Strength and Conditioning Professional Standards and Guidelines",
        year=2017,
        language="en",
        source_type="professional_guideline",
        topic="beginner_safety",
        inclusion_reason="Conservative professional standard for progression, supervision, and safety constraints.",
        source_url="https://www.nsca.com/globalassets/education/nsca_strength_and_conditioning_professional_standards_and_guidelines.pdf",
        filename="nsca_professional_standards_2017.pdf",
        fetch_kind="binary",
    ),
    CorpusSource(
        doc_id="acsm_progression_models_2009",
        title="American College of Sports Medicine Position Stand. Progression Models in Resistance Training for Healthy Adults",
        year=2009,
        language="en",
        source_type="position_stand_abstract",
        topic="progression",
        inclusion_reason="Still canonical for progression logic, rep ranges, frequency, and rest recommendations.",
        source_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=19204579&rettype=abstract&retmode=text",
        filename="acsm_progression_models_2009.txt",
        fetch_kind="text",
    ),
    CorpusSource(
        doc_id="hypertrophy_umbrella_review_2022",
        title="Resistance Training Variables for Optimization of Muscle Hypertrophy: An Umbrella Review",
        year=2022,
        language="en",
        source_type="umbrella_review",
        topic="hypertrophy",
        inclusion_reason="Open umbrella review with broad coverage of hypertrophy variables and programming tradeoffs.",
        source_url="https://public-pages-files-2025.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2022.949021/pdf",
        filename="hypertrophy_umbrella_review_2022.pdf",
        fetch_kind="binary",
    ),
    CorpusSource(
        doc_id="low_vs_high_load_2017",
        title="Strength and Hypertrophy Adaptations Between Low- vs. High-Load Resistance Training: A Systematic Review and Meta-analysis",
        year=2017,
        language="en",
        source_type="systematic_review_abstract",
        topic="load_intensity",
        inclusion_reason="Core evidence for home/basic equipment viability and load-independent hypertrophy.",
        source_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=28834797&rettype=abstract&retmode=text",
        filename="low_vs_high_load_2017.txt",
        fetch_kind="text",
    ),
    CorpusSource(
        doc_id="training_frequency_hypertrophy_2019",
        title="How Many Times per Week Should a Muscle Be Trained to Maximize Muscle Hypertrophy? A Systematic Review and Meta-analysis",
        year=2019,
        language="en",
        source_type="systematic_review_abstract",
        topic="frequency",
        inclusion_reason="Strong evidence that weekly volume matters more than frequency when volume is equated.",
        source_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=30558493&rettype=abstract&retmode=text",
        filename="training_frequency_hypertrophy_2019.txt",
        fetch_kind="text",
    ),
)


def download_source(session: requests.Session, source: CorpusSource, target_dir: Path) -> dict[str, str | int]:
    if PUBMED_HOST in source.source_url:
        time.sleep(0.5)

    last_error: Exception | None = None
    for attempt in range(4):
        response = session.get(source.source_url, timeout=120)
        if response.status_code != 429:
            response.raise_for_status()
            break
        last_error = requests.HTTPError(f"429 while downloading {source.doc_id}")
        time.sleep(1.5 * (attempt + 1))
    else:
        raise last_error or RuntimeError(f"Unable to download {source.doc_id}")

    filepath = target_dir / source.filename
    if source.fetch_kind == "binary":
        filepath.write_bytes(response.content)
    else:
        filepath.write_text(response.text.strip() + "\n", encoding="utf-8")

    return {
        "doc_id": source.doc_id,
        "title": source.title,
        "year": source.year,
        "language": source.language,
        "source_type": source.source_type,
        "topic": source.topic,
        "filepath": str(filepath.relative_to(settings.project_root)),
        "inclusion_reason": source.inclusion_reason,
    }


def main() -> None:
    target_dir = settings.raw_docs_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    metadata = [download_source(session, source, target_dir) for source in CURATED_SOURCES]
    settings.seed_corpus_metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Downloaded {len(metadata)} curated corpus documents.")
    print(f"Metadata written to {settings.seed_corpus_metadata_path}")


if __name__ == "__main__":
    main()
