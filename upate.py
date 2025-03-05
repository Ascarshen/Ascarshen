def update_readme(location, current_time):
    """更新 README 文件"""
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r"(<!-- START_SECTION:map -->)(.*?)(<!-- END_SECTION:map -->)"
    replacement = r"\1\n```\n" + location + r"\n```\n\3"
    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)


    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(updated_content)
