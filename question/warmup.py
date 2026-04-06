"""question/warmup.py — Warmup session + adaptive Game Mode session logic."""

import os, json, pandas as pd

# ── Constants ─────────────────────────────────────────────────────────────────
WARMUP_PROFILE_FILE  = "warmup_profile.json"
GAME_SESSION_FILE    = "game_session.json"

WARMUP_SEQUENCE = [
    {"label": "1-digit Addition",          "q_type": "addition",       "digits": "1d",       "difficulty": 0},
    {"label": "2-digit Addition",          "q_type": "addition",       "digits": "2d",       "difficulty": 1},
    {"label": "1-digit Subtraction",       "q_type": "subtraction",    "digits": "1d",       "difficulty": 0},
    {"label": "2-digit Subtraction",       "q_type": "subtraction",    "digits": "2d",       "difficulty": 1},
    {"label": "1-digit Multiplication",    "q_type": "multiplication", "digits": "1d",       "difficulty": 0},
    {"label": "2×1-digit Multiplication",  "q_type": "multiplication", "digits": "2d",       "difficulty": 1},
    {"label": "2×2-digit Multiplication",  "q_type": "multiplication", "digits": "3d",       "difficulty": 2},
    {"label": "1-digit Division",          "q_type": "division",       "digits": "1d",       "difficulty": 0},
    {"label": "2÷1-digit Division",        "q_type": "division",       "digits": "2d+1d",    "difficulty": 1},
    {"label": "Word Problem",              "q_type": "story",          "digits": "1d",       "difficulty": 0},
    {"label": "Time Problem",              "q_type": "time",           "digits": "2d",       "difficulty": 1},
    {"label": "Currency Problem",          "q_type": "currency",       "digits": "2d",       "difficulty": 1},
    {"label": "Mixed Operations",          "q_type": "mixed",          "digits": "2d+2d+1d", "difficulty": 3},
]

MAX_WRONG = MAX_SKIPS = 2
AUTO_SKIP_SECONDS      = 30
SCORE_FAST_THRESHOLD   = 4.0
SCORE_MEDIUM_THRESHOLD = 12.0
SCORE_INFO = {1.0: ("🌟","Very Fast"), 0.5: ("👍","Good"), 0.2: ("🐢","Slow"), 0.0: ("✗","Missed")}
SCORE_COLOURS = {1.0:"#27AE60", 0.5:"#D4AC0D", 0.2:"#E67E22", 0.0:"#95A5A6"}

# ── Warmup persistence ────────────────────────────────────────────────────────

def has_completed_warmup():
    if not os.path.exists(WARMUP_PROFILE_FILE): return False
    try:
        with open(WARMUP_PROFILE_FILE, "r", encoding="utf-8") as f:
            return bool(json.load(f).get("completed", False))
    except Exception: return False

def save_warmup_profile(ranked):
    with open(WARMUP_PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump({"completed": True, "ranked": ranked}, f, indent=2, ensure_ascii=False)

def load_warmup_profile():
    if not os.path.exists(WARMUP_PROFILE_FILE): return None
    try:
        with open(WARMUP_PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("ranked")
    except Exception: return None

# ── Game session persistence ──────────────────────────────────────────────────

def save_game_session(state):
    with open(GAME_SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def load_game_session():
    if not os.path.exists(GAME_SESSION_FILE): return None
    try:
        with open(GAME_SESSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception: return None

def clear_game_session():
    if os.path.exists(GAME_SESSION_FILE):
        os.remove(GAME_SESSION_FILE)

# ── WarmupSession ─────────────────────────────────────────────────────────────

class WarmupSession:
    def __init__(self):
        self.step_index  = 0
        self.wrong_count = 0
        self.skip_count  = 0
        self.scores      = {}
        self._full_df    = None
        self._load_full_df()

    def _load_full_df(self):
        fp = os.path.join(os.getcwd(), "question", "game_ques.xlsx")
        df = pd.read_excel(fp)
        df["type_lower"] = df["type"].astype(str).str.lower().str.strip()
        df["digits_str"] = df["digits"].astype(str).str.lower().str.strip()
        df["difficulty"] = pd.to_numeric(df["difficulty"], errors="coerce")
        self._full_df = df

    def _build_processor(self, step):
        from question.loader import QuestionProcessor
        q, d, diff = step["q_type"].lower(), step["digits"].lower(), step["difficulty"]
        mask = (self._full_df["type_lower"]==q)&(self._full_df["digits_str"]==d)&(self._full_df["difficulty"]==diff)
        filtered = self._full_df[mask].copy().reset_index(drop=True)
        if filtered.empty:
            mask2 = (self._full_df["type_lower"]==q)&(self._full_df["difficulty"]==diff)
            filtered = self._full_df[mask2].copy().reset_index(drop=True)
        if filtered.empty:
            filtered = self._full_df[self._full_df["type_lower"]==q].copy().reset_index(drop=True)
        p = QuestionProcessor(q, diff, disable_dda=True, is_game_mode=True)
        p.df = filtered; p._skip_process_file = True
        return p

    def total_steps(self): return len(WARMUP_SEQUENCE)
    def current_step(self): return WARMUP_SEQUENCE[self.step_index] if self.step_index < len(WARMUP_SEQUENCE) else None
    def get_current_processor(self):
        s = self.current_step(); return self._build_processor(s) if s else None

    def is_complete(self):
        return self.step_index >= len(WARMUP_SEQUENCE) or self.wrong_count >= MAX_WRONG or self.skip_count >= MAX_SKIPS

    def completion_reason(self):
        if self.wrong_count >= MAX_WRONG: return "wrong"
        if self.skip_count >= MAX_SKIPS:  return "skipped"
        return "complete"

    def submit_answer(self, is_correct, elapsed):
        step = self.current_step()
        if step is None: return 0.0
        score = 0.0 if not is_correct else (1.0 if elapsed<=SCORE_FAST_THRESHOLD else (0.5 if elapsed<=SCORE_MEDIUM_THRESHOLD else 0.2))
        if not is_correct: self.wrong_count += 1
        self.scores[step["label"]] = score
        self.step_index += 1
        return score

    def skip_question(self):
        step = self.current_step()
        if step:
            self.scores[step["label"]] = 0.0
            self.skip_count += 1; self.step_index += 1

    def get_ranked_results(self):
        seq = {s["label"]: s for s in WARMUP_SEQUENCE}
        result = []
        for label, score in self.scores.items():
            s = seq.get(label, {})
            result.append({"label": label, "score": score,
                           "q_type": s.get("q_type","addition"), "digits": s.get("digits","1d")})
        return sorted(result, key=lambda x: x["score"], reverse=True)

    def correct_count(self): return sum(1 for s in self.scores.values() if s > 0)


# ── GameModeSession ───────────────────────────────────────────────────────────

class GameModeSession:
    SUB_DIFF_NAMES = {0: "Easy", 1: "Medium", 2: "Hard"}
    session_time = 90

    def __init__(self, ranked_list, saved_state=None):
        self.ranked  = ranked_list or []
        # Build label→WARMUP_SEQUENCE lookup for backward-compat (old profiles lack q_type)
        self._seq_lookup = {s["label"]: s for s in WARMUP_SEQUENCE}
        # Back-fill missing q_type / digits from WARMUP_SEQUENCE
        for entry in self.ranked:
            if not entry.get("q_type"):
                seq = self._seq_lookup.get(entry["label"], {})
                entry["q_type"] = seq.get("q_type", "addition")
                entry["digits"] = seq.get("digits", "1d")
        self.levels  = [self.ranked[i:i+2] for i in range(0, len(self.ranked), 2)]
        self.game_active = True

        # Progressive state
        self.current_level_index   = 0
        self.current_sub_difficulty = 0
        self.type_rotation          = 0
        self.phase                  = "normal"   # "normal" | "promotion_test"
        self.promotion_correct      = 0
        self.promotion_wrong        = 0
        self.consecutive_correct    = 0
        self.consecutive_wrong      = 0
        self.questions_at_sub_diff  = 0

        # Scoring
        self.accumulated_points  = {e["label"]: 0.0 for e in self.ranked}
        self.question_count      = 0
        self.correct_count       = 0
        self.highest_level_reached = 0

        # Shared DataFrame (loaded once, reused per question)
        self._full_df = None
        self._load_df()

        if saved_state:
            self._restore_state(saved_state)

    def _load_df(self):
        fp = os.path.join(os.getcwd(), "question", "game_ques.xlsx")
        df = pd.read_excel(fp)
        df["type_lower"] = df["type"].astype(str).str.lower().str.strip()
        df["digits_str"] = df["digits"].astype(str).str.lower().str.strip()
        df["difficulty"] = pd.to_numeric(df["difficulty"], errors="coerce")
        self._full_df = df

    # ── Question config ───────────────────────────────────────────────────────

    def _current_types(self):
        idx = min(self.current_level_index, len(self.levels)-1)
        return self.levels[idx] if self.levels else []

    def _next_level_types(self):
        idx = self.current_level_index + 1
        return self.levels[idx] if idx < len(self.levels) else []

    def get_next_question_config(self):
        if self.phase == "promotion_test":
            next_idx = self.current_level_index + 1
            if next_idx < len(self.levels):
                types = self.levels[next_idx]
                if types:
                    entry = types[self.type_rotation % len(types)]
                    q_type = entry.get("q_type") or self._seq_lookup.get(entry["label"],{}).get("q_type","addition")
                    digits = entry.get("digits") or self._seq_lookup.get(entry["label"],{}).get("digits","1d")
                    return {"q_type": q_type, "digits": digits, "difficulty": 0,
                            "label": entry["label"], "phase": self.phase}
            return None
        types = self._current_types()
        if not types: return None
        entry  = types[self.type_rotation % len(types)]
        q_type = entry.get("q_type") or self._seq_lookup.get(entry["label"],{}).get("q_type","addition")
        digits = entry.get("digits") or self._seq_lookup.get(entry["label"],{}).get("digits","1d")
        return {"q_type": q_type, "digits": digits,
                "difficulty": self.current_sub_difficulty,
                "label": entry["label"], "phase": self.phase}

    def build_processor(self, config):
        from question.loader import QuestionProcessor
        q_type = config["q_type"].lower()
        digits = config.get("digits", "").lower().strip()
        diff   = config["difficulty"]
        
        # Match EXACTLY by q_type and digits so "1-digit addition" never asks 2-digit questions
        mask = (self._full_df["type_lower"]==q_type) & (self._full_df["digits_str"]==digits)
        filtered = self._full_df[mask].copy().reset_index(drop=True)
        if filtered.empty:
            mask2 = (self._full_df["type_lower"]==q_type) & (self._full_df["difficulty"]==diff)
            filtered = self._full_df[mask2].copy().reset_index(drop=True)
            if filtered.empty:
                filtered = self._full_df[self._full_df["type_lower"]==q_type].copy().reset_index(drop=True)
                
        p = QuestionProcessor(q_type, diff, disable_dda=True, is_game_mode=True)
        p.df = filtered; p._skip_process_file = True
        return p

    # ── Scoring ───────────────────────────────────────────────────────────────

    @staticmethod
    def calc_score(is_correct, elapsed):
        if not is_correct: return 0.0
        if elapsed <= SCORE_FAST_THRESHOLD:   return 1.0
        if elapsed <= SCORE_MEDIUM_THRESHOLD: return 0.5
        return 0.2

    def _advance_rotation(self, types):
        if types: self.type_rotation = (self.type_rotation + 1) % len(types)

    def submit_answer(self, config, is_correct, elapsed):
        score = self.calc_score(is_correct, elapsed)
        label = config.get("label","")
        if label in self.accumulated_points: self.accumulated_points[label] += score
        self.question_count += 1
        if is_correct: self.correct_count += 1
        types = self._next_level_types() if self.phase=="promotion_test" else self._current_types()
        self._advance_rotation(types)
        self.questions_at_sub_diff += 1
        self._apply_progression(is_correct)
        return score

    def skip_question(self, config):
        label = config.get("label","")
        # skip = 0 pts (no accumulation)
        self.question_count += 1
        self._advance_rotation(self._current_types())
        self.questions_at_sub_diff += 1
        self._apply_progression(False)

    # ── Progression ───────────────────────────────────────────────────────────

    def _apply_progression(self, is_correct):
        if self.phase == "promotion_test":
            self._handle_promotion(is_correct); return
        if is_correct:
            self.consecutive_correct += 1; self.consecutive_wrong = 0
            if self.consecutive_correct >= 2 and self.questions_at_sub_diff >= 3:
                self._advance_sub_diff()
        else:
            self.consecutive_wrong += 1; self.consecutive_correct = 0
            if self.consecutive_wrong >= 3: self._demote()

    def _advance_sub_diff(self):
        self.consecutive_correct = 0; self.questions_at_sub_diff = 0
        if self.current_sub_difficulty < 2:
            self.current_sub_difficulty += 1
        else:
            if self._next_level_types():
                self.phase = "promotion_test"
                self.promotion_correct = self.promotion_wrong = 0
                self.type_rotation = 0

    def _handle_promotion(self, is_correct):
        if is_correct: self.promotion_correct += 1
        else:          self.promotion_wrong   += 1
        total = self.promotion_correct + self.promotion_wrong
        if self.promotion_correct >= 2:  self._promote()
        elif self.promotion_wrong >= 2:   self._fail_promotion()
        elif total >= 3:                  self._fail_promotion()

    def _promote(self):
        self.current_level_index   += 1
        self.current_sub_difficulty = 0
        self.phase = "normal"
        self.promotion_correct = self.promotion_wrong = 0
        self.consecutive_correct = self.consecutive_wrong = 0
        self.questions_at_sub_diff = self.type_rotation = 0
        if self.current_level_index > self.highest_level_reached:
            self.highest_level_reached = self.current_level_index

    def _fail_promotion(self):
        self.current_sub_difficulty = 2; self.phase = "normal"
        self.promotion_correct = self.promotion_wrong = 0
        self.consecutive_correct = self.questions_at_sub_diff = self.type_rotation = 0

    def _demote(self):
        self.consecutive_wrong = self.consecutive_correct = 0
        self.questions_at_sub_diff = self.type_rotation = 0; self.phase = "normal"
        if self.current_level_index > 0:
            self.current_level_index  -= 1; self.current_sub_difficulty = 2
        else:
            self.current_sub_difficulty = 0

    # ── Results ───────────────────────────────────────────────────────────────

    def get_ranked_results_updated(self):
        result = []
        for entry in self.ranked:
            lbl    = entry["label"]
            gained = self.accumulated_points.get(lbl, 0.0)
            result.append({**entry, "score": entry.get("score",0.0)+gained, "gained": gained,
                           "original_score": entry.get("score",0.0)})
        return sorted(result, key=lambda x: x["score"], reverse=True)

    def accuracy_pct(self):
        return int((self.correct_count / max(self.question_count,1)) * 100)

    def level_name(self): return f"Level {self.current_level_index + 1}"
    def sub_diff_name(self): return self.SUB_DIFF_NAMES.get(self.current_sub_difficulty, "Easy")

    # ── State persistence ─────────────────────────────────────────────────────

    def save_state(self):
        return {k: getattr(self,k) for k in (
            "current_level_index","current_sub_difficulty","type_rotation",
            "phase","promotion_correct","promotion_wrong",
            "consecutive_correct","consecutive_wrong","questions_at_sub_diff",
            "accumulated_points","question_count","correct_count","highest_level_reached"
        )}

    def _restore_state(self, state):
        for k, v in state.items():
            if hasattr(self, k): setattr(self, k, v)
