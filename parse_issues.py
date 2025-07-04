import csv
import io


def parse_issues(file_content):
    """
    Parses the content of the issues CSV file.

    Args:
        file_content (str): The string content of the CSV file.

    Returns:
        list: A list of dictionaries, where each dictionary represents an issue.
    """
    issues = []
    # Use io.StringIO to treat the string content as a file
    content_as_file = io.StringIO(file_content)

    # Find the start of the actual CSV data
    for line in content_as_file:
        if line.strip().startswith('---'):
            # The line after --- is a blank line, so we read one more line to get to the header.
            # but the actual data starts after some empty lines.
            break

    # Skip empty lines after '---'
    while True:
        pos = content_as_file.tell()
        line = content_as_file.readline()
        if line and line.strip():
            content_as_file.seek(pos)  # Go back to the beginning of the line
            break
        if not line:
            return []  # Reached end of file

    reader = csv.reader(content_as_file)
    for row in reader:
        # Skip empty rows
        if not any(field.strip() for field in row):
            continue

        try:
            # Based on the sample, the structure is:
            # ID, Severity, Description, Repo, Tool, Created, Updated, , Line, Path, Type
            issue_id = row[0]
            severity = row[1]
            description = row[2]
            repo = row[3]
            tool = row[4]
            created_at = row[5]
            updated_at = row[6]
            line = row[8]
            file_path = row[9]
            issue_type = row[10]

            if not file_path or not line:
                continue

            issues.append({
                'id': issue_id,
                'severity': severity,
                'description': description,
                'repository': repo,
                'tool': tool,
                'created_at': created_at,
                'updated_at': updated_at,
                'line': int(line),
                'file_path': file_path,
                'type': issue_type,
                'raw_row': row,
            })
        except (IndexError, ValueError) as e:
            # Ignore rows that don't parse correctly.
            # print(f"Skipping row: {row}. Error: {e}")
            pass

    return issues


if __name__ == '__main__':
    with open('5568.csv', 'r', encoding='utf-8') as f:
        content = f.read()

    all_issues = parse_issues(content)

    # Print first 20 issues
    for issue in all_issues[:20]:
        print(issue)

    print(f"\nTotal issues found: {len(all_issues)}")
