# Wasmer will let you easily run WebAssembly module in a Python host.
#
# This example illustrates the basics of using Wasmer through a “Hello
# World”-like project:
#
#   1. How to load a WebAssembly module as bytes,
#   2. How to compile the module,
#   3. How to create an instance of the module.
#
# You can run the example directly by executing in Wasmer root:
#
# ```shell
# $ python examples/instance.py
# ```
#
# Ready?

from wasmer import engine, wat2wasm, Store, Module, Instance
from wasmer_compiler_cranelift import Compiler

# Let's declare the Wasm module.
#
# We are using the text representation of the module here but you can
# also load `.wasm` files using the `open` function.
with open("/home/taruu/PycharmProjects/backrooms-scripts/utls/wikidot_normalize_bg.wasm", "rb") as file:
    wasm_bytes = file.read()
# Create a store. Engines and compilers are explained in other
# examples.
store = Store(engine.Universal(Compiler))

# Let's compile the Wasm module.
module = Module(store, wasm_bytes)

# Let's instantiate the module!
instance = Instance(module)