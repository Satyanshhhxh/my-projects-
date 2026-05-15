import pandas as pd
import numpy as np
import sys
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

REQUIRED_COLUMNS = {"Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"}
FEATURE_COLUMNS = ["home_form_points", "away_form_points", "home_goals_scored", 
                   "home_goals_conceded", "away_goals_scored", "away_goals_conceded", "home_advantage"]

def load_data(filepath: str | Path) -> pd.DataFrame:
    """Load the CSV dataset, validate it, and sort it chronologically."""
    csv_path = Path(filepath)

    if not csv_path.exists():
        print(f"[ERROR] File not found: '{filepath}'")
        print("Make sure your CSV file is in the same folder as this script or pass the correct path.")
        sys.exit(1)

    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"[ERROR] File not found: '{filepath}'")
        print("Make sure your CSV file is in the same folder as this script or pass the correct path.")
        sys.exit(1)

    # Check that all required columns exist
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        print(f"[ERROR] Dataset is missing columns: {missing}")
        sys.exit(1)

    # Parse the Date column into proper datetime objects
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

    # Drop rows where date could not be parsed
    bad_dates = df["Date"].isna().sum()
    if bad_dates > 0:
        print(f"[WARNING] Dropped {bad_dates} rows with unparseable dates.")
        df = df.dropna(subset=["Date"])

    # Sort oldest to newest — critical to avoid data leakage
    df = df.sort_values("Date").reset_index(drop=True)

    # Validate FTR column only contains expected values
    valid_results = {"H", "D", "A"}
    invalid_ftr = ~df["FTR"].isin(valid_results)
    if invalid_ftr.any():
        print(f"[WARNING] Dropped {invalid_ftr.sum()} rows with invalid FTR values.")
        df = df[~invalid_ftr].reset_index(drop=True)

    print(f"[OK] Dataset loaded: {len(df)} matches from "
          f"{df['Date'].min().date()} to {df['Date'].max().date()}")

    return df


def get_all_teams(df: pd.DataFrame) -> list:
    """Return a sorted list of all unique teams in the dataset."""
    teams = set(df["HomeTeam"].unique()) | set(df["AwayTeam"].unique())
    return sorted(teams)


# ── FEATURE ENGINEERING ───────────────────────────────────────────────────

def get_last5_matches(df: pd.DataFrame, team: str, before_date: pd.Timestamp) -> pd.DataFrame:
    """Get the last 5 matches for a team strictly before a given date."""
    team_mask = (df["HomeTeam"] == team) | (df["AwayTeam"] == team)
    date_mask = df["Date"] < before_date
    past_matches = df[team_mask & date_mask]
    return past_matches.tail(5)


def compute_team_stats(matches: pd.DataFrame, team: str) -> dict:
    """Compute form string, points, goals scored/conceded for recent matches."""
    if matches.empty:
        return {
            "form_string": "N/A",
            "form_points": 0,
            "goals_scored": 0,
            "goals_conceded": 0,
            "num_matches": 0,
        }

    form_chars = []      # e.g., ['W', 'D', 'L']
    points = 0
    goals_scored = 0
    goals_conceded = 0

    for _, row in matches.iterrows():
        if row["HomeTeam"] == team:
            gf = row["FTHG"]   # Goals For
            ga = row["FTAG"]   # Goals Against
            result = row["FTR"]
            outcome = "W" if result == "H" else ("D" if result == "D" else "L")
            if result == "H": points += 3
            elif result == "D": points += 1
        else:
            gf = row["FTAG"]   # Away team's goals
            ga = row["FTHG"]
            result = row["FTR"]
            outcome = "W" if result == "A" else ("D" if result == "D" else "L")
            if result == "A": points += 3
            elif result == "D": points += 1
        goals_scored += gf
        goals_conceded += ga
        form_chars.append(outcome)

    return {
        "form_string": " ".join(form_chars),
        "form_points": points,
        "goals_scored": goals_scored,
        "goals_conceded": goals_conceded,
        "num_matches": len(matches),
    }


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build feature matrix for all matches (no data leakage)."""
    print("[INFO] Building features...")
    rows = []

    for idx, match in df.iterrows():
        date, home_team, away_team, result = match["Date"], match["HomeTeam"], match["AwayTeam"], match["FTR"]
        
        home_matches = get_last5_matches(df, home_team, before_date=date)
        away_matches = get_last5_matches(df, away_team, before_date=date)

        if home_matches.empty or away_matches.empty:
            continue

        home_stats = compute_team_stats(home_matches, home_team)
        away_stats = compute_team_stats(away_matches, away_team)

        rows.append({
            "home_form_points": home_stats["form_points"],
            "away_form_points": away_stats["form_points"],
            "home_goals_scored": home_stats["goals_scored"],
            "home_goals_conceded": home_stats["goals_conceded"],
            "away_goals_scored": away_stats["goals_scored"],
            "away_goals_conceded": away_stats["goals_conceded"],
            "home_advantage": 1,
            "result": result,
        })

    feature_df = pd.DataFrame(rows)
    print(f"[OK] Features built for {len(feature_df)} matches.")
    return feature_df
# ── MODEL TRAINING & EVALUATION ───────────────────────────────────────────

def train_model(feature_df: pd.DataFrame):
    """Train Logistic Regression and return model, encoder, test sets."""
    X = feature_df[FEATURE_COLUMNS].values
    y = feature_df["result"].values
    
    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(pd.Series(y).astype(str).to_numpy())
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )
    
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    
    print(f"[OK] Model trained on {len(X_train)} matches, tested on {len(X_test)} matches.")
    return model, encoder, X_test, y_test


def evaluate_model(model, encoder, X_test, y_test):
    """Print accuracy, classification report, and confusion matrix."""
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    accuracy = accuracy_score(y_test, y_pred)
    print("\n" + "=" * 50)
    print("MODEL EVALUATION")
    print("=" * 50)
    print(f"Overall Accuracy: {accuracy * 100:.1f}%\n")
    
    print(classification_report(y_test, y_pred, target_names=encoder.classes_, zero_division=0))
    
    cm = confusion_matrix(y_test, y_pred)
    classes = encoder.classes_
    print("Confusion Matrix:")
    print(f"{'':>10}", end="")
    for c in classes:
        print(f"  Pred {c}", end="")
    print()
    for i, actual_class in enumerate(classes):
        print(f"Actual {actual_class:>4}", end="")
        for val in cm[i]:
            print(f"  {val:>7}", end="")
        print()
    print("=" * 50)
# ── PREDICTION INTERFACE ──────────────────────────────────────────────────

def find_team(user_input: str, all_teams: list) -> str | None:
    """Match user input to team name, handling partial matches."""
    user_input = user_input.strip().lower()
    
    for team in all_teams:
        if team.lower() == user_input:
            return team
    
    matches = [team for team in all_teams if user_input in team.lower()]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        print(f"\nMultiple teams found matching '{user_input}':")
        for i, t in enumerate(matches, 1):
            print(f"  {i}. {t}")
        choice = input("Enter the number of the team: ").strip()
        try:
            return matches[int(choice) - 1]
        except (ValueError, IndexError):
            return None
    return None
def display_prediction(home_team: str, away_team: str, home_stats: dict, 
                       away_stats: dict, probabilities: dict):
    """Display match prediction and stats."""
    print("\n" + "=" * 55)
    print(f"Match: {home_team} (Home) vs {away_team} (Away)")
    print("=" * 55)
    
    home_max = home_stats["num_matches"] * 3
    print(f"\n{home_team} Last {home_stats['num_matches']}: {home_stats['form_string']}")
    print(f"Goals: {home_stats['goals_scored']} for, {home_stats['goals_conceded']} against")
    print(f"Form Points: {home_stats['form_points']}/{home_max}")
    
    away_max = away_stats["num_matches"] * 3
    print(f"\n{away_team} Last {away_stats['num_matches']}: {away_stats['form_string']}")
    print(f"Goals: {away_stats['goals_scored']} for, {away_stats['goals_conceded']} against")
    print(f"Form Points: {away_stats['form_points']}/{away_max}")
    
    print("\nWin Probabilities:")
    print(f"- {home_team} Win: {probabilities['H']:.0f}%")
    print(f"- Draw: {probabilities['D']:.0f}%")
    print(f"- {away_team} Win: {probabilities['A']:.0f}%")
    
    print("\nInsight:")
    insight = generate_insight(home_team, away_team, home_stats, away_stats, probabilities)
    print(f"{insight}")
    print("=" * 55)


def generate_insight(home_team: str, away_team: str, home_stats: dict, 
                     away_stats: dict, probabilities: dict) -> str:
    """Generate a plain-English explanation of the prediction."""
    lines = []
    
    home_pts = home_stats["form_points"]
    away_pts = away_stats["form_points"]
    home_gd = home_stats["goals_scored"] - home_stats["goals_conceded"]
    away_gd = away_stats["goals_scored"] - away_stats["goals_conceded"]
    
    if home_pts > away_pts:
        lines.append(f"{home_team} is in better form ({home_pts} vs {away_pts} pts), giving them the edge.")
    elif away_pts > home_pts:
        lines.append(f"{away_team} arrives in stronger form ({away_pts} vs {home_pts} pts), offsetting home advantage.")
    else:
        lines.append(f"Both teams are evenly matched on form ({home_pts} pts each).")
    
    if home_gd > away_gd:
        lines.append(f"{home_team}'s goal difference (+{home_gd}) outperforms {away_team}'s ({away_gd:+d}).")
    elif away_gd > home_gd:
        lines.append(f"{away_team}'s goal difference ({away_gd:+d}) is better than {home_team}'s ({home_gd:+d}).")
    
    lines.append("Home advantage is factored in.")
    
    if probabilities["H"] >= 50:
        lines.append(f"Model favors {home_team} win ({probabilities['H']:.0f}%).")
    elif probabilities["A"] >= 50:
        lines.append(f"Model favors {away_team} win ({probabilities['A']:.0f}%).")
    else:
        lines.append(f"Closely contested match — draw likely at {probabilities['D']:.0f}%.")
    
    return " ".join(lines)
            f"a draw is reasonably likely at {probabilities['D']:.0f}%."
        )

    return " ".join(lines)


def main():
    """Load data, train model, and run interactive predictor."""
    print("\n" + "=" * 55)
    print("Premier League Match Win Probability Predictor")
    print("=" * 55 + "\n")
    
    filepath = Path(__file__).parent / "epl_final001.csv"
    if not filepath.exists():
        print(f"[ERROR] CSV file not found at: {filepath}")
        sys.exit(1)
    
    df = load_data(filepath)
    all_teams = get_all_teams(df)
    
    feature_df = build_features(df)
    if len(feature_df) < 50:
        print("[WARNING] Very few samples; predictions may be unreliable.")
    
    model, encoder, X_test, y_test = train_model(feature_df)
    evaluate_model(model, encoder, X_test, y_test)
    
    last_date = df["Date"].max() + pd.Timedelta(days=1)
    
    while True:
        print("\nEnter team names (or 'quit' to exit).\n")
        
        home_input = input("Enter Home Team: ").strip()
        if home_input.lower() == "quit":
            break
        
        home_team = find_team(home_input, all_teams)
        if not home_team:
            print(f"[ERROR] Team '{home_input}' not found.")
            print(f"Available: {', '.join(all_teams)}")
            continue
        
        away_input = input("Enter Away Team: ").strip()
        if away_input.lower() == "quit":
            break
        
        away_team = find_team(away_input, all_teams)
        if not away_team:
            print(f"[ERROR] Team '{away_input}' not found.")
            print(f"Available: {', '.join(all_teams)}")
            continue
        
        if home_team == away_team:
            print("[ERROR] Home and Away teams must be different.")
            continue
        
        home_matches = get_last5_matches(df, home_team, before_date=last_date)
        away_matches = get_last5_matches(df, away_team, before_date=last_date)
        
        if home_matches.empty:
            print(f"[ERROR] No history for {home_team}.")
            continue
        if away_matches.empty:
            print(f"[ERROR] No history for {away_team}.")
            continue
        
        home_stats = compute_team_stats(home_matches, home_team)
        away_stats = compute_team_stats(away_matches, away_team)
        
        feature_vector = np.array([[
            home_stats["form_points"],
            away_stats["form_points"],
            home_stats["goals_scored"],
            home_stats["goals_conceded"],
            away_stats["goals_scored"],
            away_stats["goals_conceded"],
            1,
        ]])
        
        proba = model.predict_proba(feature_vector)[0]
        class_proba = {cls: round(prob * 100, 1) for cls, prob in zip(encoder.classes_, proba)}
        
        total = sum(class_proba.values())
        if total != 100.0:
            diff = 100.0 - total
            max_key = max(class_proba.items(), key=lambda kv: kv[1])[0]
            class_proba[max_key] = round(class_proba[max_key] + diff, 1)
        
        display_prediction(home_team, away_team, home_stats, away_stats, class_proba)
    
    print("\nThanks for using the predictor.")


if __name__ == "__main__":
    main()