# pandoc-mermaid-filter

## Requirements

This filter requires mmdc in $PATH

## Install

install by pip-git
```shell
$ pip3 install git+https://github.com/nocsi/pandoc-mermaid-filter.git
```

## Options

## Sample Markdown

```
--- 
# YAML frontmatter
mermaid:
  theme: "default"

[Example](mermaid.mmd){.mermaid}
```

## Usage

```
pandoc README.md --filter pandoc-mermaid-filter -o README.pdf
```
