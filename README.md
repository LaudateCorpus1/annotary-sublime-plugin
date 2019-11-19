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






