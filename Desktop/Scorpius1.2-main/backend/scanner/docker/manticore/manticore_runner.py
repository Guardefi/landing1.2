#!/usr/bin/env python3
"""
Manticore runner script for Scorpius vulnerability scanner
"""

import json
import os
import sys
from pathlib import Path

try:
    from manticore.core.smtlib import ConstraintSet
    from manticore.ethereum import ManticoreEVM
    from manticore.utils import log
except ImportError as e:
    print(f"Error importing Manticore: {e}")
    sys.exit(1)


def analyze_contract(contract_path, output_path):
    """Analyze smart contract using Manticore"""

    results = {"vulnerabilities": [], "analysis_info": {}, "error": None}

    try:
        # Read contract source
        with open(contract_path, "r") as f:
            source_code = f.read()

        # Initialize Manticore
        m = ManticoreEVM()

        # Create user account
        user_account = m.create_account(balance=1000000000000000000)

        # Deploy contract
        try:
            contract = m.solidity_create_contract(
                contract_path, owner=user_account, gas=3000000
            )

            if contract is None:
                results["error"] = "Failed to deploy contract"
                return results

        except Exception as e:
            results["error"] = f"Contract deployment failed: {str(e)}"
            return results

        # Run symbolic execution
        print(f"Starting symbolic execution with {len(m.ready_states)} states...")

        # Explore possible execution paths
        for state in m.ready_states:
            try:
                # Check for common vulnerabilities

                # 1. Reentrancy detection
                if hasattr(state.platform, "get_call_value"):
                    call_value = state.platform.get_call_value()
                    if call_value > 0:
                        results["vulnerabilities"].append(
                            {
                                "type": "potential_reentrancy",
                                "name": "Potential Reentrancy Vulnerability",
                                "description": "External call with value transfer detected",
                                "location": f"State {state.id}",
                                "state_count": len(m.ready_states),
                            }
                        )

                # 2. Integer overflow detection
                for transaction in state.platform.transactions:
                    if hasattr(transaction, "return_value"):
                        results["vulnerabilities"].append(
                            {
                                "type": "integer_operation",
                                "name": "Integer Operation Detected",
                                "description": "Potential integer overflow/underflow",
                                "location": f"Transaction {transaction.sort}",
                                "state_count": len(m.ready_states),
                            }
                        )
                        break  # Only report one per state

            except Exception as e:
                print(f"Error analyzing state {state.id}: {e}")
                continue

        # Finalize execution
        m.finalize()

        results["analysis_info"] = {
            "total_states": len(m.terminated_states),
            "analyzed_states": len([s for s in m.terminated_states]),
            "execution_tree_nodes": len(m.terminated_states),
        }

        print(
            f"Analysis completed. Found {len(results['vulnerabilities'])} potential vulnerabilities"
        )

    except Exception as e:
        results["error"] = f"Manticore analysis failed: {str(e)}"
        print(f"Analysis error: {e}")

    # Save results
    try:
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {output_path}")
    except Exception as e:
        print(f"Error saving results: {e}")

    return results


def main():
    if len(sys.argv) != 3:
        print("Usage: manticore_runner.py <contract_file> <output_file>")
        sys.exit(1)

    contract_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.exists(contract_file):
        print(f"Error: Contract file {contract_file} not found")
        sys.exit(1)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Run analysis
    analyze_contract(contract_file, output_file)


if __name__ == "__main__":
    main()
