# elevenplate

This is a template-based random text generation system with all the power of a context-sensitive grammar. It's more powerful than templates usually are, so I'm calling it elevenplate.

To use it from the command line, just point it at a file that has a context-sensitive grammar written in the elevenplate format, which I will now briefly describe.

## elevenplate context-sensitive grammar format

Any text after a pound sign is ignored, so put your comments there if comments are necessary.

The lines of the grammar file before any named tables are introduced are taken to be possible start sentences. One will be chosen at random to expand.

Any \[reference\] will be expanded by randomly selecting a line from the relavent table. All subsequent references to the same table will be filled in with the same line, unless an exclamation point is included, like so: \[!reference\]. If an exclamation mark is used, subsequent references will still match the original reference.

A \[?reference\] with a question mark will match a previous reference if one has been generated, but will not affect subsequent references if one has not.

_If the table has multiple columns_, this will result in an error unless the reference specifies which column to use, like so: \[reference.0\]. Specifying a column when the table does not have multiple columns will also result in an error.

To introduce a table, start the line with two semicolons and give the name (one alphanumeric word) of the table. If it is a table with multiple columns, provide the number of columns afterwards.

Columns are separated with the \& character.