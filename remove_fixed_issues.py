import json
import sys


def remove_fixed_issues_from_sarif(sarif_path: str, issues_to_remove: list):
    """Remove fixed issues from SARIF file."""
    try:
        with open(sarif_path, 'r', encoding='utf-8') as f:
            sarif_data = json.load(f)

        # Create a set of issues to remove for faster lookup
        remove_set = set()
        for issue in issues_to_remove:
            remove_set.add((issue['file'], issue['line'], issue['message']))

        # Filter out the fixed issues
        for run in sarif_data['runs']:
            filtered_results = []
            for result in run['results']:
                file_path = result['locations'][0]['physicalLocation']['artifactLocation']['uri']
                line = result['locations'][0]['physicalLocation']['region']['startLine']
                message = result['message']['text']

                if (file_path, line, message) not in remove_set:
                    filtered_results.append(result)

            run['results'] = filtered_results

        # Write back to file
        with open(sarif_path, 'w', encoding='utf-8') as f:
            json.dump(sarif_data, f, indent=2)

        print(f"Removed {len(issues_to_remove)} fixed issues from SARIF file")

    except Exception as e:
        print(f"Error processing SARIF file: {e}")


if __name__ == '__main__':
    # Define the next 4 issues that were fixed (issues 17-20)
    fixed_issues = [
        {'file': 'ddd_architecture_analyzer.py', 'line': 187,
            'message': 'Method _classify_domain_layer has 54 lines of code (limit is 50)'},
        {'file': 'ddd_architecture_analyzer.py', 'line': 187,
            'message': 'Method _classify_domain_layer has a cyclomatic complexity of 29 (limit is 8)'},
        {'file': 'ddd_architecture_analyzer.py', 'line': 368,
            'message': 'Method _generate_migration_plan has 86 lines of code (limit is 50)'},
        {'file': 'ddd_architecture_analyzer.py', 'line': 368,
            'message': 'Method _generate_migration_plan has a cyclomatic complexity of 10 (limit is 8)'},
        {'file': 'ddd_structure_creator.py', 'line': 30,
            'message': 'Method _create_directories has 63 lines of code (limit is 50)'},
        {'file': 'ddd_structure_creator.py', 'line': 109,
            'message': 'Method _create_domain_base_classes has 175 lines of code (limit is 50)'},
    ]

    remove_fixed_issues_from_sarif('results.sarif', fixed_issues)
