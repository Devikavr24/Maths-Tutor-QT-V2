import pandas as pd
import os

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

def _load_logic_df() -> pd.DataFrame:
    """Load and normalise gamemode_logic.xlsx."""
    fp = os.path.join(os.getcwd(), "question", "gamemode_logic.xlsx")
    df = pd.read_excel(fp)
    if len(df) == 0:
        return df

    df["label"] = df["label"].astype(str).str.strip()
    df["forward"] = df["forward"].astype(str).str.strip()
    df["backward"] = df["backward"].astype(str).str.strip()
    df["warmup_order"] = pd.to_numeric(df["warmup_order"], errors="coerce")
    df["minimum_correct"] = pd.to_numeric(df["minimum_correct"], errors="coerce").fillna(2).astype(int)
    
    # Handle the spelling typo in excel 'maximun_wrong' gracefully
    if "maximun_wrong" in df.columns:
        df["maximum_wrong"] = pd.to_numeric(df["maximun_wrong"], errors="coerce").fillna(3).astype(int)
    else:
        df["maximum_wrong"] = pd.to_numeric(df.get("maximum_wrong", 3), errors="coerce").fillna(3).astype(int)
    return df

def _load_game_df() -> pd.DataFrame:
    """Load and normalise game_ques.xlsx. Always lower-cases 'type'."""
    fp = os.path.join(os.getcwd(), "question", "game_ques.xlsx")
    df = pd.read_excel(fp)
    df["type"]       = df["type"].astype(str).str.strip().str.lower()
    df["digits"]     = df["digits"].astype(str).str.strip().str.lower()
    df["label"]      = df["label"].astype(str).str.strip()
    df["difficulty"] = pd.to_numeric(df["difficulty"], errors="coerce").fillna(0).astype(int)
    return df


BUILTIN_WARMUP_ORDER = {
    "1D_addition": 1,
    "1D_subtraction": 2,
    "1D_multiplication": 3,
    "1D_division": 4,
    "2D_addition": 5,
    "2D_subtraction": 6,
    "2D_multiplication": 7,
    "2D_division": 8,
    "3D_addition": 9,
    "3D_subtraction": 10,
    "3D_multiplication": 11,
    "3D_division": 12,
    "4D_addition": 13,
    "4D_subtraction": 14,
    "4D_multiplication": 15,
    "4D_division": 16,
    "mixed_operation": 17
}

# ── Warmup sequence builder ───────────────────────────────────────────────────
def get_warmup_sequence(full_df):
    steps = []
    grouped = full_df.groupby("label").first().reset_index()
    
    for _, row in grouped.iterrows():
        lbl = str(row["label"]).strip()
        
        # Check game_ques.xlsx for warmup order first
        if "warmup_order" in row and pd.notna(row["warmup_order"]):
            order = int(row["warmup_order"])
        elif "warm_up" in row and pd.notna(row["warm_up"]):
            order = int(row["warm_up"])
        else:
            order = BUILTIN_WARMUP_ORDER.get(lbl, 999)

        if order == 999:
            continue

        steps.append({
            "label": lbl,
            "q_type": row["type"],
            "digits": row["digits"],
            "difficulty": 0,
            "warmup_order": order
        })

    steps.sort(key=lambda x: x["warmup_order"])
    print("[FINAL WARMUP]:", [(s["label"], s["warmup_order"]) for s in steps])
    return steps

# ── Dynamic Logic Generator ──────────────────────────────────────────────────
def generate_logic_from_warmup(ranked_results):
    try:
        logic_rows = []
        # Ensure all missing master labels are securely appended at the bottom
        ladder = list(ranked_results)
        existing = {item["label"] for item in ladder}
        
        # Sort internal built-in keys by their explicit order to maintain safe appended sequences
        master_sequence = sorted(BUILTIN_WARMUP_ORDER.keys(), key=lambda k: BUILTIN_WARMUP_ORDER[k])
        
        for lbl in master_sequence:
            if lbl not in existing:
                ladder.append({
                    "label": lbl,
                    "score": 0.0,
                    "q_type": "unknown",
                    "digits": "unknown",
                    "difficulty": 0,
                    "warmup_order": BUILTIN_WARMUP_ORDER[lbl]
                })
        
        for i, item in enumerate(ladder):
            label = item["label"]
            forward = ladder[i+1]["label"] if i + 1 < len(ladder) else "NaN"
            backward = ladder[i-1]["label"] if i - 1 >= 0 else "NaN"
            
            logic_rows.append({
                "label": label,
                "forward": forward,
                "backward": backward,
                "warmup_order": i + 1,
                "minimum_correct": 3,
                "maximum_wrong": 2
            })
            
        df = pd.DataFrame(logic_rows)
        fp = os.path.join(os.getcwd(), "question", "gamemode_logic.xlsx")
        df.to_excel(fp, index=False)
        print(f"[DEBUG] Generated dynamic logic to {fp} with {len(ladder)} steps.")
    except Exception as e:
        import traceback
        print(f"[ERROR] Failed to save gamemode logic: {e}")
        traceback.print_exc()



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
    session_time   = 90

    def __init__(self, ranked_list: list | None, saved_state: dict | None = None):
        self._full_df        = _load_game_df()
        self._logic_df       = _load_logic_df()
        self.warmup_sequence = get_warmup_sequence(self._full_df)
        self._seq_lookup     = {s["label"]: s for s in self.warmup_sequence}

        # Build node map from logic dataframe for safe lookups
        self.node_map = {}
        for _, row in self._logic_df.iterrows():
            lbl = str(row["label"]).strip()
            self.node_map[lbl] = {
                "forward": str(row.get("forward", "")).strip(),
                "backward": str(row.get("backward", "")).strip(),
                "minimum_correct": int(row.get("minimum_correct", 2)),
                "maximum_wrong": int(row.get("maximum_wrong", 3))
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
            self.questions_in_current_label = saved_state.get("questions_in_current_label", 0)
            self.used_question_ids = set(saved_state.get("used_question_ids", []))
        else:
            # Setup based directly on the first skill loaded in gamemode_logic.xlsx
            if not self._logic_df.empty:
                self.current_label = str(self._logic_df.iloc[0]["label"]).strip()
            else:
                self.current_label = self.warmup_sequence[0]["label"] if self.warmup_sequence else ""
            self.used_question_ids = set()

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
            "difficulty": 0
        }

    def build_processor(self, config: dict):
        from question.loader import QuestionProcessor
        lbl  = config.get("label", "").strip()

        # Primary filter by label
        filtered = self._full_df[self._full_df["label"] == lbl].copy().reset_index(drop=True)

        if not filtered.empty:
            valid_rows = filtered
            
            # 1. Filter out used IDs
            if "id" in valid_rows.columns:
                unused_rows = valid_rows[~valid_rows["id"].isin(self.used_question_ids)]
                if unused_rows.empty:
                    # They exhausted the pool! Reset just for this label
                    self.used_question_ids.clear()
                    unused_rows = valid_rows
                valid_rows = unused_rows

            # 2. Filter out immediate repeat by text gracefully
            if len(valid_rows) > 1 and self._last_question_text is not None and "question" in valid_rows.columns:
                non_repeat_rows = valid_rows[valid_rows["question"] != self._last_question_text]
                if not non_repeat_rows.empty:
                    valid_rows = non_repeat_rows
                    
            selected_row = valid_rows.sample(n=1)
            
            # Track it!
            if "id" in selected_row.columns:
                self.used_question_ids.add(selected_row.iloc[0]["id"])
            if "question" in selected_row.columns:
                self._last_question_text = selected_row.iloc[0]["question"]
                
            filtered = selected_row.copy().reset_index(drop=True)

            q_type = filtered.iloc[0]["type"]
        else:
            q_type = "addition"

        # Game mode no longer fetches via Excel difficulty level
        p = QuestionProcessor(q_type, 0, disable_dda=True, is_game_mode=True)
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
        node = self.node_map.get(self.current_label, {})
        min_correct = node.get("minimum_correct", 2)
        max_wrong = node.get("maximum_wrong", 3)

        if is_correct:
            self.consecutive_correct += 1
            self.consecutive_wrong = 0
            if self.consecutive_correct >= min_correct:
                self.consecutive_correct = 0
                self._move_forward()
        else:
            self.consecutive_wrong += 1
            self.consecutive_correct = 0
            if self.consecutive_wrong >= max_wrong:
                self.consecutive_wrong = 0
                self._move_backward()

    def _move_forward(self):
        node = self.node_map.get(self.current_label)
        if not node: return False
        nxt = node.get("forward", "")
        if nxt and str(nxt).lower() != "nan" and nxt in self.node_map:
            self.current_label = nxt
            self.questions_in_current_label = 0
            return True
        return False

    def _move_backward(self):
        node = self.node_map.get(self.current_label)
        if not node: return False
        prv = node.get("backward", "")
        if prv and str(prv).lower() != "nan" and prv in self.node_map:
            self.current_label = prv
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

    def save_state(self) -> dict:
        return {
            "current_label": self.current_label,
            "questions_in_current_label": getattr(self, "questions_in_current_label", 0),
            "used_question_ids": list(self.used_question_ids)
        }