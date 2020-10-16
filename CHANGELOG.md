# Changelog
All notable changes to this project will be documented in this file.


## [0.2.0] - 2020-10-11
* `jure` now tracks all changed cells and executes them
* add end-to-end test
## [0.2.1] - 2020-10-11
* fix bug with cells index
* less logs
## [0.2.2] - 2020-10-13
* simplify CellsIndex, do not skip first cell
## [0.3.0] - 2020-10-14
* Browser is no longer reloaded! Instead cell content is changed with JS
* Now parsing of notebooks is done with Jupytext
* jure now disables autosave of Jupyter Notebooks
## [0.3.1] - 2020-10-16
* Disable autosave after each page reload
* Try to reload page if content changed significantly
* Do not check notebook update timestamp