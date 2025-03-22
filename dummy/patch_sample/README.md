# Sample Patch Files

This directory contains sample files for demonstrating patch creation and application.

## Files Included

### Calculator Example (Feature Addition)
- `calculator_v1.py`: Original version of a simple calculator program
- `calculator_v2.py`: Enhanced version with additional features
- `calculator.patch`: A unified diff patch showing the changes from v1 to v2

### Greeting Example (Bug Fix)
- `greeting_v1.py`: Original version with a bug (misspelled "morning")
- `greeting_v2.py`: Fixed version with the bug corrected
- `greeting_bugfix.patch`: A small patch that fixes the bug

## Key Changes in the Patches

### Calculator Patch
The calculator patch demonstrates several types of changes typically seen in software development:

1. **Header Changes**: Updated the version comment
2. **New Imports**: Added `math` and `sys` modules
3. **New Functions**: Added `power()`, `square_root()`, and `show_help()`
4. **Major Logic Changes**: Rewrote the `main()` function to include a loop and improved UX
5. **Error Handling**: Added handling for `KeyboardInterrupt`
6. **Output Formatting**: Improved how results are displayed

### Greeting Bugfix Patch
The greeting patch demonstrates a simple bugfix:

1. **Comment Update**: Changed the header comment to indicate it's fixed
2. **Bug Fix**: Fixed the misspelled word "moring" to "morning"
3. **Comment Update**: Updated the inline comment to indicate the bug is fixed

## Using the Patches

### How to View a Patch

```bash
cat calculator.patch
cat greeting_bugfix.patch
```

### How to Apply a Patch

To apply a patch and transform the original file:

```bash
# For the calculator:
patch calculator_v1.py -i calculator.patch -o calculator_patched.py

# For the greeting program:
patch greeting_v1.py -i greeting_bugfix.patch -o greeting_patched.py
```

### How to Create a Patch

Patches were created using the `diff` command:

```bash
diff -u original_file.py modified_file.py > changes.patch
```

This type of unified diff format is commonly used in version control systems and is human-readable.

## Understanding Patch Format

In the patch file:
- Lines starting with `---` and `+++` show the original and new file
- Sections starting with `@@` show line numbers for each chunk of changes
- Lines starting with `-` are removed from the original
- Lines starting with `+` are added in the new version
- Lines without `+` or `-` are context (unchanged lines)

## Use Cases for Patches

1. **Sharing Bug Fixes**: Small patches are efficient for sharing fixes without sending entire files
2. **Code Reviews**: Patches clearly highlight changes for review purposes
3. **Open Source Contributions**: Contributors often submit patches rather than entire files
4. **Version Control**: Systems like Git use patch-like formats internally 