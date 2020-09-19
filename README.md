# Jupyter Browser Reload

Convenience tool to automatically reload Jupyter Notebook in a browser
when its source .py file is changed.

It uses
* Jupytext
* Watchdog
* Selenium 

## Why Jure
Jupytext is a great tool that for instance allows one to benefit from static code analysis of Jupyter Notebooks. However I always struggled with this workflow: after each edit of .py file manually reload browser and execute changed cells.

![standard](assets/standard.gif)

Jure automatically reloads browser on each .py file change, so it would instantly show actual notebook content. Additionally it scrolls to last changed cell and executes it. 
 
 ![with jure](assets/with_jure.gif)


## Installation
The most non-trivial part is install ChromeDriver on you computer, here's [sample link for Ubuntu](https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/) for reference.
After that it's simply
```
pip install jure
```