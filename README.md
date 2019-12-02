# Annotary

Annotary supports developers to write error-free Solidity smart contracts. It does so by adding a number of annotations (thus the name) which express conditions and invariants which must be fulfilled by the smart contract. An symbolic/concolic execution analysis engine based on a modified version of Mythril will then check if the contract code may violate any of the conditions.

This project is the plugin that brings error/warning highlighting and support for annotations to the Sublime Text editor. The actual symbolic execution engine is included as a submodule and hosted [here](https://github.com/konradweiss/mythril).

## Installation

1) To integrate the plugin first clone this repository including submodules:

```
git clone --recurse-submodules  git@github.com:Fraunhofer-AISEC/annotary-sublime-plugin.git
```

2) Install libraries
```
sudo apt-get install libssl-dev
```

3) If the installation did not succeed, you may need to install further Mythril dependencies:
```
cd mythril
pip3 install -r requirements.txt
```

4) Install the Annotary-compatible version of Mythril:
```
cd mythril
python3 setup.py build
sudo python3 setup.py install
```

4) Copy this plugin to Sublime's plugin folder: e.g.

```
cp -R annotary ~/.config/sublime-text-3/Packages/
```

Run an analysis over the Annotary submenu when right-clicking inside a .sol file to open the context Menu.

Note:
It is also necessary to get the solidity compiler. Install it with:

```
sudo apt-get install solc
```
or get a specific version from https://github.com/ethereum/solidity/releases

Python version used: 3.6, version 3.5.3 should also be sufficient

## Supported Annotations

The following annotations are supported by Annotary:

### @check
An annotation of the form `@check(<condition>)` can be inline to check whether or not the specific `condition` holds at that point in the program.
Example:
```
@check(address(this).balance > min_trans_value)
```

### @always, @never
An annotation of the form `@always` is an alias of `@check` and `@never(<condition>)` is equivalent to  `@check(!<condition>)`.

### @invariant
An annotation of the form `@invariant(<condition>)` is annotated at the contract level and defines a `condition` that is analyzed on whether it holds after any regular contract execution, i.e. end of inter-contract call or transaction.
Example:
```
@invariant(msg.sender == owner)
```
or
```
@invariant(managed_funds == address(this).balance)
```

### @set_restricted
Annotations of the form `@set_restricted("[var={[<contract>.]<member>[,]} ;][func=]{(constructor|<functionname>|<functionsignature>)[,]})` drives the analysis to find writed to member variables that are not in the list of allowed members, marking them as violations.

Examples:
```
@set_restricted(constructor)
address owner;
```
Or not directly at the member
```
@set_restricted(var=owner,max_tokens; constructor)
```
or
```
@set_restricted(constructor, setOwner(address))
address owner
```
## License
The Annotary plugin is released under the [Apache License, Version 2.0](https://opensource.org/licenses/Apache-2.0).

## Publication
This plugin is part of the publication: [Annotary: A Concolic Execution System for Developing Secure Smart Contracts](https://arxiv.org/pdf/1907.03868).

When refering to our work, please cite our ESORICS 2019 paper:

```
@inproceedings{Weiss2019,
author = {Konrad Weiss and Julian Sch{\"{u}}tte},
booktitle = {Computer Security -- ESORICS 2019},
editor = {Sako, Kazue and Schneider, Steve and Ryan, Peter Y A},
isbn = {978-3-030-29959-0},
pages = {747--766},
publisher = {Springer International Publishing},
title = {{Annotary: A Concolic Execution System for Developing Secure Smart Contracts}},
year = {2019}
}
```

