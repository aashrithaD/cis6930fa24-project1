import glob
import sys
from redactor import (redact_names, redact_dates, redact_phones, redact_concepts, redact_address, parse_arguments, output_stats, process_file)

# Main Function
def main():
    args = parse_arguments()
    statistics = []

    for pattern in args.input:
        for file_path in glob.glob(pattern):
            try:
                stats = process_file(file_path, args)
                statistics.append(stats)
            except Exception as e:
                print(f"Error processing {file_path}: {e}", file=sys.stderr)

    if args.stats:
        output_stats(statistics, args.stats)

if __name__ == "__main__":
    main()
