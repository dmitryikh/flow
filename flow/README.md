## Overview

`flow` is a library to read heirarcial documents data into ORM models. It works by mean of so called _workflows_. workflows are the graph of actions that should be done on data in order to parse document and fill ORM models. Actions can be anything. Some primitive actions are already shipped along with `flow`:

1. `Debug` is simplest one. It just prints data to stdout
2. `GetField` to access dict's field
3. `ModelObjectCreate` to create and fill ORM model object from document's fields


## Install

```bash
[>] python setup.py install
[>] python setup.py test
```

## Project structure

`Action` base class and several general actions are written in [flow/action.py](flow/action.py). One can read comments in actions classes to get the idea.

[flow/session.py](flow/session.py) holds the wrapper of ORM session. `ORMSessionBase` makes it possible to abstract particular ORM framework.

Once created the workflows can be plotted as graph image by means of [flow/plot.py](flow/plot.py).


## Usage example

One can find some usage examples in `tests` folder.
