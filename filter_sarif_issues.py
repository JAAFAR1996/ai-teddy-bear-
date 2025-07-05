import json
import sys


def filter_complexity_issues(sarif_path):
    """Filter SARIF file to show only complexity and line count issues"""
    try:
        with open(sarif_path, 'r', encoding='utf-8') as f:
            sarif_data = json.load(f)

        complexity_issues = []
        for run in sarif_data['runs']:
            for result in run['results']:
                message = result['message']['text']
                # Check if it's a complexity or line count issue
                if ('lines of code (limit is' in message or
                        'cyclomatic complexity of' in message):
                    issue = {
                        'file': result['locations'][0]['physicalLocation']['artifactLocation']['uri'],
                        'line': result['locations'][0]['physicalLocation']['region']['startLine'],
                        'column': result['locations'][0]['physicalLocation']['region'].get('startColumn', 1),
                        'message': result['message']['text'],
                        'ruleId': result['ruleId'],
                        'level': result.get('level', 'warning')
                    }
                    complexity_issues.append(issue)

        print(f'Found {len(complexity_issues)} complexity/line count issues:')
        for i, issue in enumerate(complexity_issues):
            print(
                f'{i+1}. {issue["file"]}:{issue["line"]} - {issue["message"]}')

        return complexity_issues

    except Exception as e:
        print(f'Error filtering SARIF file: {e}')
        return []


if __name__ == '__main__':
    issues = filter_complexity_issues('results.sarif')
