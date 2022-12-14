from enum import Enum
from pathlib import Path

import typer
import spacy
from srsly import read_jsonl
from wasabi import msg

Arg = typer.Argument
Opt = typer.Option

DEFAULT_PATTERNS_FILE = Path("patterns.jsonl")


class Location(str, Enum):
    before = "before"
    after = "after"


def attach_rules(
    # fmt: off
    base_model: Path = Arg(..., help="Path to the model to attach the rules onto."), 
    output_path: Path = Arg(..., help="Output path to save the model with rules."),
    patterns_file: Path = Opt(DEFAULT_PATTERNS_FILE, "-p", "--patterns", "--patterns-file", help="Path to the patterns file."),
    location: Location = Opt(Location.before, "-l", "--loc", "--location", help="Location in the pipeline (relative to ner) to put the span_ruler component."),
    validate: bool = Opt(False, "--validate", help="Validate the patterns file.")
    # fmt: on
):
    nlp = spacy.load(base_model)
    # Only save to doc.ents, not doc.spans. For a full list of
    # options, check: https://spacy.io/api/spanruler
    config = {
        "spans_key": None,
        "annotate_ents": True,
        "overwrite": False,
        "validate": validate,
    }
    kwargs = {location: "ner"}
    ruler = nlp.add_pipe("span_ruler", config=config, **kwargs)
    patterns = read_jsonl(patterns_file)
    ruler.add_patterns(patterns)

    # Save to disk
    nlp.to_disk(output_path)


if __name__ == "__main__":
    typer.run(attach_rules)
