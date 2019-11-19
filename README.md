# Annotary

1) To integrate the plugin first clone this repository
2) Initialize submodules:

```
git submodule init
git submodule update
```

3) Install libraries
```
sudo apt-get install libssl-dev
```

4) Maybe if the installation does not successfully install requirement do it by:
```
cd mythril
pip3 install -r requirements.txt
```

5) Install mythril modified for annotary
```
cd mythril
python3 setup.py build
sudo python3 setup.py install
```

6) Copy plugin to Sublime's plugin Folder: e.g.
```
cp -R annotary ~/.config/sublime-text-3/Packages/
```
Run an analysis over the Annotary submenu when right-clicking inside a .sol file to open the context Menu.

Note:
It is also necessary to get the solidity compiler, install it:
```
sudo apt-get install solc
```
or get a specific version from https://github.com/ethereum/solidity/releases

Python version used: 3.6 the minimal version 3.5.3 should be sufficient

## Annotations

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






