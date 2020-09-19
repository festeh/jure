# Jupyter Browser Reload

Convenience tool around Jupytext to automatically reload browser
when source file is changed.

## Why Jure
Typical workflow while using external text editor: reload browser each time and exectute cells

![standard](assets/standard.gif)

Jure automatically reloads Selenium browser on each change, so it would actual notebook content (thanks to Jupytext!). Additionally it scrolls to last changed cell and executes it. 
 
 ![with jure](assets/with_jure.gif)


## Installation

```
pip install jure
```