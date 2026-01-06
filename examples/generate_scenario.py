#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example Usage: Generate and Export Scenario

Demonstrates how to use scenario_forge to generate a scenario,
print its narrative and risk summary, and export to JSON.
"""

import sys
from pathlib import Path

# Add scenario_forge package directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scenario_forge import (
    cross_chain_laundering,
    generate_narrative,
    export_json,
    export_csv_transactions,
    export_markdown_narrative
)


def main():
    """Generate a scenario and demonstrate usage"""
    print("=" * 80)
    print("scenario_forge: Example Usage")
    print("=" * 80)
    print()
    print("Generating cross-chain laundering scenario...")
    print()
    
    # Generate scenario
    scenario = cross_chain_laundering()
    
    # Validate
    is_valid, errors = scenario.validate()
    if not is_valid:
        print("⚠️  Validation errors:")
        for error in errors:
            print(f"   - {error}")
        print()
    
    # Print scenario info
    print("Scenario Information:")
    print(f"  ID: {scenario.scenario_id}")
    print(f"  Intent: {scenario.intent.value}")
    print(f"  Integrity Hash: {scenario.scenario_hash}")
    print(f"  Created: {scenario.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Print risk summary
    print("=" * 80)
    print("Risk Summary")
    print("=" * 80)
    risk_summary = scenario.get_risk_summary()
    print(f"  Total Transactions: {risk_summary['total_transactions']}")
    print(f"  Entities Involved: {risk_summary['entities_involved']}")
    print(f"  Time Span: {risk_summary['time_span_days']} days")
    print(f"  Total Amount: {risk_summary['total_amount']} {risk_summary['unique_assets'][0] if risk_summary['unique_assets'] else 'N/A'}")
    print(f"  Chains Used: {', '.join(risk_summary['unique_chains'])}")
    print(f"  AML Weaknesses: {risk_summary['aml_weaknesses_count']}")
    print(f"  Motifs Used: {', '.join(risk_summary['motifs_used'])}")
    print()
    
    # Print narrative
    print("=" * 80)
    print("Narrative")
    print("=" * 80)
    narrative = generate_narrative(scenario)
    print(narrative)
    print()
    
    # Export to files
    output_dir = Path("examples") / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = output_dir / f"scenario_{scenario.scenario_id[:8]}.json"
    csv_path = output_dir / f"scenario_{scenario.scenario_id[:8]}.csv"
    md_path = output_dir / f"scenario_{scenario.scenario_id[:8]}.md"
    
    print("=" * 80)
    print("Exporting Scenario")
    print("=" * 80)
    export_json(scenario, json_path)
    print(f"  ✅ JSON exported to: {json_path}")
    
    export_csv_transactions(scenario, csv_path)
    print(f"  ✅ CSV exported to: {csv_path}")
    
    export_markdown_narrative(scenario, md_path)
    print(f"  ✅ Markdown exported to: {md_path}")
    print()
    
    print("=" * 80)
    print("✅ Example Complete!")
    print("=" * 80)
    print()
    print("⚠️  REMINDER: This is ARTIFICIAL data for demos and evaluation only.")
    print("   Do not use for real cases or production monitoring.")
    print()


if __name__ == "__main__":
    main()

