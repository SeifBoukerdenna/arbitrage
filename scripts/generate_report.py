import json
import argparse
from datetime import datetime


def format_combination(combination):
    """Format a single combination for output."""
    bets_info = "\n".join(
        [f"        - Name: {bet['name']}, Odds: {bet['odds']}, Confidence: {bet['confidence']}%" for bet in
         combination['bets']]
    )
    return (
        f"    Combined Odds: {combination['combined_odds']:.2f}\n"
        f"    Combined Probability: {combination['combined_prob']:.4f}\n"
        f"    Expected Value per Dollar: {combination['ev_per_dollar']:.2f}\n"
        f"    Stake Allocation: {combination['stake_allocation']:.2f}\n"
        f"    Potential Payout: {combination['potential_payout']:.2f}\n"
        f"    Bets:\n{bets_info}\n"
    )


def generate_report(json_file, output_file):
    """Generate a report from the JSON file and save it to a text file."""
    with open(json_file, 'r') as file:
        data = json.load(file)

    total_budget = data.get("total_budget", 0)
    total_stake = data.get("total_stake", 0)
    total_payout = data.get("total_potential_payout", 0)
    strategy_type = data.get("strategy_type", "Unknown")
    date = data.get("date", "Unknown")
    risk_preference = data.get("risk_preference", "Moderate")

    # Header
    report = (
        f"Betting Report\n"
        f"==============\n"
        f"Date: {date}\n"
        f"Total Budget: {total_budget}\n"
        f"Total Stake: {total_stake:.2f}\n"
        f"Total Potential Payout: {total_payout:.2f}\n"
        f"Strategy Type: {strategy_type}\n"
        f"Risk Preference: {risk_preference}\n"
        f"-----------------------------------\n\n"
    )

    # Format each combination
    combinations = data.get("combinations", [])
    combinations_with_stake = [comb for comb in combinations if comb.get("stake_allocation", 0) > 0]

    if not combinations_with_stake:
        report += "No combinations with stake allocation greater than zero.\n"
    else:
        for idx, combination in enumerate(combinations_with_stake, start=1):
            report += f"Combination {idx}:\n{format_combination(combination)}\n"

    # Save to file
    with open(output_file, 'w') as file:
        file.write(report)

    print(f"Report generated successfully: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Generate a betting report from a JSON file.")
    parser.add_argument('input_file', type=str, help="The input JSON file containing betting data")
    parser.add_argument('output_file', type=str, help="The output text file for the betting report")

    args = parser.parse_args()

    generate_report(args.input_file, args.output_file)


if __name__ == '__main__':
    main()
