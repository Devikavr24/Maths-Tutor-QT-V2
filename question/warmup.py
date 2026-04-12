import os
import random
import pandas as pd

def save_game_session(state):
    """Stub for saving game state. Implement disk writing here if needed later."""
    pass


# ── Constants ─────────────────────────────────────────────────────────────────
MAX_WRONG = MAX_SKIPS = 2
AUTO_SKIP_SECONDS      = 30
SCORE_FAST_THRESHOLD   = 4.0
SCORE_MEDIUM_THRESHOLD = 12.0
SCORE_INFO  = {1.0: ("🌟", "Very Fast"), 0.5: ("👍", "Good"),
               0.2: ("🐢", "Slow"),      0.0: ("✗",  "Missed")}
SCORE_COLOURS = {1.0: "#27AE60", 0.5: "#D4AC0D",
                 0.2: "#E67E22", 0.0: "#95A5A6"}

# ── Excel helper ──────────────────────────────────────────────────────────────

def _load_game_df() -> pd.DataFrame:
    """Load and normalise game_ques.xlsx. Always lower-cases 'type'."""
    fp = os.path.join(os.getcwd(), "question", "game_ques.xlsx")
    df = pd.read_excel(fp)
    df["type"]       = df["type"].astype(str).str.strip().str.lower()
    df["digits"]     = df["digits"].astype(str).str.strip().str.lower()
    df["label"]      = df["label"].astype(str).str.strip()
    df["forward"]    = df["forward"].astype(str).str.strip()
    df["backward"]   = df["backward"].astype(str).str.strip()
    df["difficulty"] = pd.to_numeric(df["difficulty"], errors="coerce").fillna(0).astype(int)
    return df


# ── Warmup sequence builder ───────────────────────────────────────────────────
def get_warmup_sequence(full_df):
    # STEP 1: group by LABEL (this is your real unit)
    grouped = full_df.groupby("label").first().reset_index()

    steps = []
    for _, row in grouped.iterrows():
        try:
            order = int(row.get("warmup_order", 999))
        except:
            order = 999

        # 🚫 skip junk (story/time/etc unless explicitly ordered)
        if order == 999:
            continue

        steps.append({
            "label": row["label"],
            "q_type": row["type"],
            "digits": row["digits"],
            "difficulty": 0,
            "warmup_order": order
        })

    # STEP 2: sort properly
    steps.sort(key=lambda x: x["warmup_order"])

    print("[FINAL WARMUP]:", [(s["label"], s["warmup_order"]) for s in steps])

    return steps


# ── WarmupSession ─────────────────────────────────────────────────────────────

class WarmupSession:
    """
    Drives the pre-game skill-assessment warmup.

    One question is drawn from each difficulty-0 label's pool in the Excel
    file. Labels are the atomic unit — no label appears twice, no cross-label
    overlap. Results live in memory only; nothing is written to disk.
    """

    def __init__(self):
        self.step_index  = 0
        self.wrong_count = 0
        self.skip_count  = 0
        self.consecutive_wrong = 0
        self.consecutive_skips = 0
        self.scores: dict[str, float] = {}
        self._full_df    = _load_game_df()

        self.warmup_sequence = get_warmup_sequence(self._full_df)
        print(f"[WARMUP] {len(self.warmup_sequence)} steps: "
              f"{[s['label'] for s in self.warmup_sequence]}")

    # ── Processor factory ─────────────────────────────────────────────────────

    def _build_processor(self, step: dict):
        from question.loader import QuestionProcessor

        q_type = step["q_type"].lower()
        lbl    = step["label"]
        diff   = step["difficulty"]

        # Primary: exact label + difficulty
        mask = (
            (self._full_df["label"] == lbl)
            & (self._full_df["difficulty"] == diff)
        )
        filtered = self._full_df[mask].copy().reset_index(drop=True)

        # Fallback: same label (ignore difficulty)
        if filtered.empty:
            mask2 = (self._full_df["label"] == lbl)
            filtered = self._full_df[mask2].copy().reset_index(drop=True)

        p = QuestionProcessor(q_type, diff, disable_dda=True, is_game_mode=True)
        p.df                 = filtered
        p._skip_process_file = True
        return p

    # ── Session interface ─────────────────────────────────────────────────────

    def total_steps(self) -> int:
        return len(self.warmup_sequence)

    def current_step(self) -> dict | None:
        if self.step_index < len(self.warmup_sequence):
            return self.warmup_sequence[self.step_index]
        return None

    def get_current_processor(self):
        s = self.current_step()
        return self._build_processor(s) if s else None

    def is_complete(self) -> bool:
        return (
            self.step_index >= len(self.warmup_sequence)
            or self.consecutive_wrong >= MAX_WRONG
            or self.consecutive_skips >= MAX_SKIPS
        )

    def completion_reason(self) -> str:
        if self.consecutive_wrong >= MAX_WRONG: return "wrong"
        if self.consecutive_skips >= MAX_SKIPS: return "skipped"
        return "complete"

    def submit_answer(self, is_correct: bool, elapsed: float) -> float:
        step = self.current_step()
        if step is None:
            return 0.0
        if not is_correct:
            score = 0.0
            self.wrong_count += 1
            self.consecutive_wrong += 1
            self.consecutive_skips = 0
        elif elapsed <= SCORE_FAST_THRESHOLD:
            score = 1.0
            self.consecutive_wrong = 0
            self.consecutive_skips = 0
        elif elapsed <= SCORE_MEDIUM_THRESHOLD:
            score = 0.5
            self.consecutive_wrong = 0
            self.consecutive_skips = 0
        else:
            score = 0.2
            self.consecutive_wrong = 0
            self.consecutive_skips = 0
        self.scores[step["label"]] = score
        self.step_index += 1
        return score

    def skip_question(self):
        step = self.current_step()
        if step:
            self.scores[step["label"]] = 0.0
            self.skip_count += 1
            self.consecutive_skips += 1
            self.consecutive_wrong = 0
            self.step_index += 1

    def get_ranked_results(self) -> list[dict]:
        seq_map = {s["label"]: s for s in self.warmup_sequence}
        result = []
        for label, score in self.scores.items():
            s = seq_map.get(label, {})
            result.append({
                "label":  label,
                "score":  score,
                "q_type": s.get("q_type", "addition"),
                "digits": s.get("digits", "1d"),
            })
        return sorted(result, key=lambda x: x["score"], reverse=True)

    def correct_count(self) -> int:
        return sum(1 for v in self.scores.values() if v > 0)


# ── GameModeSession ───────────────────────────────────────────────────────────

class GameModeSession:
    SUB_DIFF_NAMES = {0: "Easy", 1: "Medium", 2: "Hard"}
    session_time   = 90

    def __init__(self, ranked_list: list | None, saved_state: dict | None = None):
        self._full_df        = _load_game_df()
        self.warmup_sequence = get_warmup_sequence(self._full_df)
        self._seq_lookup     = {s["label"]: s for s in self.warmup_sequence}

        # Build node map from dataframe for safe lookups
        self.node_map = {}
        grouped = self._full_df.groupby("label").first().reset_index()
        for _, row in grouped.iterrows():
            lbl = str(row["label"]).strip()
            self.node_map[lbl] = {
                "forward": str(row.get("forward", "")).strip(),
                "backward": str(row.get("backward", "")).strip(),
            }

        # Keep ranked list around for stats
        ranked_scores = {e["label"]: e.get("score", 0.0) for e in (ranked_list or [])}
        self.ranked = []
        for seq in self.warmup_sequence:
            lbl = seq["label"]
            score = ranked_scores.get(lbl, 0.3)
            self.ranked.append({
                "label": lbl,
                "score": score,
                "q_type": seq.get("q_type", "addition"),
                "digits": seq.get("digits", "1d")
            })

        if saved_state and "current_label" in saved_state:
            self.current_label = saved_state["current_label"]
            self.current_sub_difficulty = saved_state.get("current_sub_difficulty", 0)
            self.questions_in_current_label = saved_state.get("questions_in_current_label", 0)
        else:
            # Setup based on warmup results
            last_success = None
            for s in self.warmup_sequence:
                lbl = s["label"]
                score = ranked_scores.get(lbl, 0.0)
                if score < 0.5:
                    if not last_success:
                        last_success = lbl
                    break
                last_success = lbl
            
            self.current_label = last_success or (self.warmup_sequence[0]["label"] if self.warmup_sequence else "")
            self.current_sub_difficulty = 0

        self.game_active = True
        self.consecutive_correct        = 0
        self.consecutive_wrong          = 0
        self.questions_in_current_label = getattr(self, "questions_in_current_label", 0)

        # Scoring
        self.accumulated_points    = {lbl: 0.0 for lbl in self.node_map.keys()}
        self.question_count        = 0
        self.correct_count         = 0
        self._last_question_text   = None

    def get_next_question_config(self) -> dict | None:
        if not self.current_label:
            return None
        return {
            "label": self.current_label,
            "difficulty": self.current_sub_difficulty
        }

    def build_processor(self, config: dict):
        from question.loader import QuestionProcessor
        lbl  = config.get("label", "").strip()
        diff = int(config.get("difficulty", 0))

        # Primary filter
        mask = (self._full_df["label"] == lbl) & (self._full_df["difficulty"] == diff)
        filtered = self._full_df[mask].copy().reset_index(drop=True)

        # Fallback 1: same label
        if filtered.empty:
            filtered = self._full_df[self._full_df["label"] == lbl].copy().reset_index(drop=True)

        if not filtered.empty:
            valid_rows = filtered
            if len(filtered) > 1 and self._last_question_text is not None and "question" in filtered.columns:
                valid_rows = filtered[filtered["question"] != self._last_question_text]
                if valid_rows.empty:
                    valid_rows = filtered
                    
            selected_row = valid_rows.sample(n=1)
            if "question" in selected_row.columns:
                self._last_question_text = selected_row.iloc[0]["question"]
            filtered = selected_row.copy().reset_index(drop=True)

        q_type = self._seq_lookup.get(lbl, {}).get("q_type", "addition")
        p = QuestionProcessor(q_type, diff, disable_dda=True, is_game_mode=True)
        p.df = filtered
        p._skip_process_file = True
        return p

    @staticmethod
    def calc_score(is_correct: bool, elapsed: float) -> float:
        if not is_correct:                    return 0.0
        if elapsed <= SCORE_FAST_THRESHOLD:   return 1.0
        if elapsed <= SCORE_MEDIUM_THRESHOLD: return 0.5
        return 0.2

    def submit_answer(self, config: dict, is_correct: bool, elapsed: float) -> float:
        score = self.calc_score(is_correct, elapsed)
        label = config.get("label", "")
        if label in self.accumulated_points:
            self.accumulated_points[label] += score
        self.question_count += 1
        if is_correct:
            self.correct_count += 1
        
        self._apply_progression(is_correct)
        return score

    def skip_question(self, config: dict):
        self.question_count += 1
        self._apply_progression(False)

    def _apply_progression(self, is_correct: bool):
        self.questions_in_current_label += 1

        if is_correct:
            self.consecutive_correct += 1
            self.consecutive_wrong = 0
            if self.consecutive_correct >= 2:
                self.consecutive_correct = 0
                if self.current_sub_difficulty < 2:
                    self.current_sub_difficulty += 1
                else:
                    self._move_forward()
        else:
            self.consecutive_wrong += 1
            self.consecutive_correct = 0
            if self.consecutive_wrong >= 3:
                self.consecutive_wrong = 0
                if self.current_sub_difficulty > 0:
                    self.current_sub_difficulty -= 1
                else:
                    self._move_backward()

        # Hard limit: force movement after 2 questions in same label
        if self.questions_in_current_label >= 2:
            moved = self._move_forward(force=True)
            if not moved:
                self._move_backward(force=True)
            self.questions_in_current_label = 0

    def _move_forward(self, force=False):
        node = self.node_map.get(self.current_label)
        if not node: return False
        nxt = node.get("forward", "")
        if nxt and str(nxt).lower() != "nan" and nxt in self.node_map:
            self.current_label = nxt
            self.current_sub_difficulty = 0
            self.questions_in_current_label = 0
            return True
        return False

    def _move_backward(self, force=False):
        node = self.node_map.get(self.current_label)
        if not node: return False
        prv = node.get("backward", "")
        if prv and str(prv).lower() != "nan" and prv in self.node_map:
            self.current_label = prv
            self.current_sub_difficulty = 2 if not force else 0
            self.questions_in_current_label = 0
            return True
        return False

    # ── Results & Formatters ──────────────────────────────────────────────────

    def get_ranked_results_updated(self) -> list[dict]:
        result = []
        for entry in self.ranked:
            lbl    = entry["label"]
            gained = self.accumulated_points.get(lbl, 0.0)
            result.append({
                **entry,
                "score":          entry.get("score", 0.0) + gained,
                "gained":         gained,
                "original_score": entry.get("score", 0.0),
            })
        return sorted(result, key=lambda x: x["score"], reverse=True)

    def accuracy_pct(self) -> int:
        return int((self.correct_count / max(self.question_count, 1)) * 100)

    def level_name(self) -> str:
        parts = self.current_label.split("_")
        return " ".join([p.capitalize() for p in parts])

    def sub_diff_name(self) -> str:
        return self.SUB_DIFF_NAMES.get(self.current_sub_difficulty, "Easy")

    def save_state(self) -> dict:
        return {
            "current_label": self.current_label,
            "current_sub_difficulty": self.current_sub_difficulty,
            "questions_in_current_label": getattr(self, "questions_in_current_label", 0)
        }