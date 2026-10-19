import argparse
from src.pipeline import run

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic experimentation analytics.")
    parser.add_argument("--users", type=int, default=48000)
    parser.add_argument("--events", type=int, default=2400000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="outputs")
    args = parser.parse_args()
    if args.users < 100 or args.events < args.users:
        parser.error("--users must be >=100 and --events must be >= --users")
    run(args.users, args.events, args.seed, args.output)

if __name__ == "__main__":
    main()
