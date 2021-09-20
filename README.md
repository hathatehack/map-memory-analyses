# Map Memory Analysis

GCC map file memory analysis and report.  It's helpful for locating the large costs, optimizing and debugging.

## Workflow

1. Read sections from map file with scanner, a async-generator.
2. Classify section contents into certain modules dictionary.
3. Format module into DataFrame.
4. Render the DataFrame into html page.

## Required

The following python third-party libraries need to be installed first, e.g. `pip install lib_name`:
- pandas:     A powerful data processor.
- pyecharts: A expressive chart library. 
- pyyaml:      YAML is the data serialization language of the configuration file of this project.

## Start working

### Configuration:

The following configuration file is used for a more accurate analysis.

   ```yaml
   # Classify the objects of section into certain classification.
   # Three rule types are provided:
   # 1.[match_re. The re needs to have one group "()"],
   # 2.[match_re, classification],
   # 3.[match_str, classification]
   classification_rules:
     - match_re: ^\./sdk/(\w+)/[/\w]*\w+\.o
     - match_re: ^\.[/\w\-]+\.o
       classification: application
     - match_str: lib/gcc/arm-none-eabi
       classification: gcc
   
   # Group sections according to your lds file and count the group size.
   section_group_sizes:
     text: [ sections... ]
     data: [ sections... ]
   ```

### Generate:

Run the test case from command line

```bash
cd map-memory-analysis
python test/test.py
```

or add the following code to your own python project

   ```python
   from mapreport import Report
   
   Report(map_file_path, config_file_path, output_path).generate_report()
   ```

the report will be generated to *output_path/report*.

### Report:

This is a demo report [Report.html](https://hathatehack.github.io/map-memory-analysis/test/report/Report.html).

