# -*- coding: utf-8 -*-
"""
Exporters

Export scenarios to JSON, CSV, and Markdown formats with governance metadata.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List

from .scenario import Scenario
from .narrative import generate_narrative


def export_json(scenario: Scenario, path: Path) -> None:
    """
    Export scenario to JSON format.
    
    Args:
        scenario: Scenario to export
        path: Output file path
    """
    scenario_dict = scenario.to_dict()
    
    # Add narrative to export
    from .narrative import generate_narrative
    scenario_dict['narrative'] = generate_narrative(scenario)
    
    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write JSON
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(scenario_dict, f, indent=2, ensure_ascii=False)
    
    # Prepend warning as comment (JSON doesn't support comments, so add to metadata)
    # The warning is already in the dictionary, so we're good


def export_csv_transactions(scenario: Scenario, path: Path) -> None:
    """
    Export transactions to CSV format.
    
    Args:
        scenario: Scenario to export
        path: Output file path
    """
    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Collect transactions
    transactions = []
    for from_addr, to_addr, data in scenario.transaction_graph.edges(data=True):
        tx = data['transaction']
        transactions.append({
            'tx_id': tx.tx_id,
            'from_address': from_addr,
            'to_address': to_addr,
            'asset_symbol': tx.asset.symbol,
            'amount': str(tx.amount),
            'fee': str(tx.fee),
            'timestamp': tx.timestamp.isoformat(),
            'block_number': tx.block_number,
            'from_role': scenario.entity_roles.get(from_addr, 'unknown'),
            'to_role': scenario.entity_roles.get(to_addr, 'unknown')
        })
    
    # Sort by timestamp
    transactions.sort(key=lambda x: x['timestamp'])
    
    # Write CSV
    with open(path, 'w', newline='', encoding='utf-8') as f:
        if not transactions:
            return
        
        fieldnames = [
            'tx_id', 'from_address', 'to_address', 'asset_symbol',
            'amount', 'fee', 'timestamp', 'block_number',
            'from_role', 'to_role'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # Write metadata as first data row (with special marker)
        writer.writerow({
            'tx_id': 'METADATA',
            'from_address': 'ARTIFICIAL_DATA_DO_NOT_USE_FOR_REAL_CASES',
            'to_address': f"Intent: {scenario.intent.value}",
            'asset_symbol': f"Scenario ID: {scenario.scenario_id}",
            'amount': f"Created: {scenario.created_at.isoformat()}",
            'fee': f"Hash: {scenario.scenario_hash}",
            'timestamp': '',
            'block_number': '',
            'from_role': '',
            'to_role': ''
        })
        
        writer.writerows(transactions)


def export_markdown_narrative(scenario: Scenario, path: Path) -> None:
    """
    Export narrative to Markdown format.
    
    Args:
        scenario: Scenario to export
        path: Output file path
    """
    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Generate narrative
    narrative = generate_narrative(scenario)
    
    # Write markdown
    with open(path, 'w', encoding='utf-8') as f:
        f.write(narrative)
        f.write('\n\n')
        f.write('---\n\n')
        f.write('## Export Metadata\n\n')
        f.write(f'- **Export Format:** Markdown Narrative\n')
        f.write(f'- **Scenario ID:** `{scenario.scenario_id}`\n')
        f.write(f'- **Integrity Hash:** `{scenario.scenario_hash}`\n')
        f.write(f'- **Export Timestamp:** {scenario.created_at.isoformat()}\n')
        f.write('\n')
        f.write('⚠️ **WARNING:** ARTIFICIAL_DATA_DO_NOT_USE_FOR_REAL_CASES\n')

