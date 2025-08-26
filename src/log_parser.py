import re
import argparse
from typing import List, Tuple

def parse_log(log_text: str) -> Tuple[List[List], int]:
    """
    Parse the given log text and extract records for each processed file.

    Returns:
        entries: A list of lists in the format [filename, exact, duration, upper_bound, lower_bound, gap]
        exact_count: Number of entries where exact == True
    """
    # Regex patterns
    file_pattern = re.compile(r"Running cargo with argument: .*/(?P<file>\d+\.fjs)")
    exact_pattern = re.compile(r"Exact:\s*(?P<exact>true|false)", re.IGNORECASE)
    duration_pattern = re.compile(r"Duration:\s*(?P<duration>[0-9]+\.?[0-9]*) seconds")
    gap_pattern = re.compile(r"Gap:\s*(?P<gap>[0-9]+\.?[0-9]*)")
    # summary patterns
    upper_summary_pattern = re.compile(r"Upper Bnd:\s*(?P<upper>-?[0-9]+)")
    lower_summary_pattern = re.compile(r"Lower Bnd:\s*(?P<lower>-?[0-9]+)")
    # trace patterns
    trace_ub_pattern = re.compile(r"UB:\s*(?P<upper>[0-9]+)")
    trace_lb_pattern = re.compile(r"LB:\s*(?P<lower>[0-9]+)")

    entries = []
    lines = log_text.splitlines()
    i = 0
    while i < len(lines):
        file_match = file_pattern.search(lines[i])
        if not file_match:
            i += 1
            continue

        filename = file_match.group('file')
        snippet_lines = []
        j = i + 1
        # Collect until next separator or end
        while j < len(lines) and not lines[j].startswith('Running cargo'):
            snippet_lines.append(lines[j])
            j += 1

        snippet = '\n'.join(snippet_lines)
        # Extract required fields
        exact_match = exact_pattern.search(snippet)
        duration_match = duration_pattern.search(snippet)
        gap_match = gap_pattern.search(snippet)

        # Determine upper bound
        upper = None
        lower = None
        # Try summary
        sup = upper_summary_pattern.search(snippet)
        if sup:
            upper = int(sup.group('upper'))
        else:
            # fallback to last trace UB
            for line in snippet_lines:
                m = trace_ub_pattern.search(line)
                if m:
                    upper = int(m.group('upper'))

        slo = lower_summary_pattern.search(snippet)
        if slo:
            lower = int(slo.group('lower'))
        else:
            # fallback to last trace LB
            for line in snippet_lines:
                m = trace_lb_pattern.search(line)
                if m:
                    lower = int(m.group('lower'))

        # If any required missing, skip
        if not (exact_match and duration_match and upper is not None and lower is not None and gap_match):
            i = j
            continue

        exact_val = exact_match.group('exact').lower() == 'true'
        duration_val = float(duration_match.group('duration'))
        gap_val = float(gap_match.group('gap'))

        entries.append([filename,
                        exact_val,
                        duration_val,
                        upper,
                        lower,
                        gap_val])
        # Move to next block
        i = j

    # Sort entries by numeric part of filename
    entries.sort(key=lambda e: (int(e[0].split('h')[0].split('.')[0])))
    # Count exact solutions
    exact_count = sum(1 for e in entries if e[1])

    return entries, exact_count


def main():
    parser = argparse.ArgumentParser(description='Parse a log file for FJSP experiment results.')
    parser.add_argument('logfile', help='Path to the log file')
    args = parser.parse_args()

    # Read log file
    with open(args.logfile, 'r', encoding='utf-8') as f:
        log_content = f.read()

    results, count = parse_log(log_content)
    file = open("temp.csv", "+w")
    # print("Parsed entries:")
    for r in results:
        # print(r)
        # file.write(f"{r[0]}; {0 if r[1] == False and r[3] > 0 and r[3] == r[4] else (r[3] if r[3] > 0 else ' ')}; {r[4] if r[4] > 0 else ' '}; {str(r[2]).replace('.', ',')}\n")
        file.write(f"{r[3] if r[3] > 0 else ' '}; {r[4] if r[4] > 0 else ' '}; {str(r[2]).replace('.', ',')}\n")
    file.close()
    print(f"Number of exact solutions: {count}")

if __name__ == '__main__':
    main()
