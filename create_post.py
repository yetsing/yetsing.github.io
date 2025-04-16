#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo


script_dir = Path(__file__).parent.resolve()


def create_post(title, categories, directory="_posts"):
    # Ensure the posts directory exists
    post_directory = script_dir / directory

    # Generate the filename based on the current date and title
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_str}-{title.replace(' ', '-').lower()}.md"
    filepath = post_directory / filename

    # Update the date to Beijing time
    date_str = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S %z")
    post_content = f"""---
layout: post
title:  "{title}"
date:   {date_str}
categories: {" ".join(categories)}
---

"""
    # Write the content to the file
    with open(filepath, "w") as file:
        file.write(post_content)

    print(f"Post created: {filepath}")


def main():
    if len(sys.argv) < 3:
        print("Usage: create_post.py <title> <categories>")
        return
    title = sys.argv[1]
    create_post(title, sys.argv[2:])


if __name__ == "__main__":
    main()

