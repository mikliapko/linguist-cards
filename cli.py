import argparse

from handlers import ask_and_translate


def parse_arguments():
    parser = argparse.ArgumentParser(description="A program for language cards creation")
    parser.add_argument("word", help="Word or phrase to create card for")
    parser.add_argument("-ot", "--only-translate", action="store_true", help="Only translate the word")
    return parser.parse_args()


def main():
    args = parse_arguments()
    word = args.word
    only_translate = args.only_translate

    translation = ask_and_translate(word, only_translate)
    print(translation)


if __name__ == "__main__":
    main()
