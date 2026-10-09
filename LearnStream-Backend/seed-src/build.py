"""
Builds the content packs the backend loads on startup (ContentSeeder):
  src/main/resources/seed/problems.json  <- seed-src/problems/*.py
  src/main/resources/seed/quizzes.json   <- seed-src/mcq/*.json

Each problems module defines PROBLEMS: a list of dicts with
  title, difficulty (EASY|MEDIUM|HARD), tags ("A,B"), description,
  input_format, output_format, constraints,
  solve: function(stdin_text) -> stdout_text   (the reference solution)
  tests: list of stdin strings; the first `samples` (default 2) are shown to students.
Expected outputs are computed by running solve(), so they are always consistent.

Run:  python seed-src/build.py
"""
import importlib.util, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT.parent / "src" / "main" / "resources" / "seed"
DIFFS = {"EASY", "MEDIUM", "HARD"}


def load_problems():
    problems, titles = [], set()
    for path in sorted((ROOT / "problems").glob("*.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for p in mod.PROBLEMS:
            where = f"{path.name}: {p.get('title')}"
            assert p["difficulty"] in DIFFS, where
            assert p["title"] not in titles, "duplicate title " + where
            assert len(p["title"]) <= 200 and len(p["tags"]) <= 255, where
            assert len(p["tests"]) >= 4, "need >= 4 tests " + where
            titles.add(p["title"])
            samples = p.get("samples", 2)
            tests = []
            for i, inp in enumerate(p["tests"]):
                inp = inp.strip("\n") + "\n"
                out = p["solve"](inp)
                assert out is not None and str(out).strip() != "", "empty output " + where
                tests.append({"input": inp, "expected": str(out).rstrip() + "\n", "sample": i < samples})
            problems.append({k: p[k] for k in ("title", "difficulty", "tags", "description",
                                                "input_format", "output_format", "constraints")} | {"tests": tests})
    return problems


def load_quizzes():
    quizzes = []
    for path in sorted((ROOT / "mcq").glob("*.json")):
        for qz in json.loads(path.read_text(encoding="utf-8")):
            where = f"{path.name}: {qz['title']}"
            assert qz["category"] and qz["questions"], where
            for q in qz["questions"]:
                assert q["answer"] in ("A", "B", "C", "D"), where + " " + q["q"]
                assert len(q["options"]) == 4 and len(set(q["options"])) == 4, where + " " + q["q"]
                assert all(len(o) <= 500 for o in q["options"]), where
            quizzes.append(qz)
    return quizzes


if __name__ == "__main__":
    sys.setrecursionlimit(100000)
    OUT.mkdir(parents=True, exist_ok=True)
    problems = load_problems()
    quizzes = load_quizzes()
    (OUT / "problems.json").write_text(json.dumps(problems, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "quizzes.json").write_text(json.dumps(quizzes, ensure_ascii=False, indent=1), encoding="utf-8")
    by = {d: sum(p["difficulty"] == d for p in problems) for d in DIFFS}
    print(f"{len(problems)} problems {by}; {len(quizzes)} quizzes, "
          f"{sum(len(q['questions']) for q in quizzes)} questions")
