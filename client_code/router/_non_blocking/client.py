# Copyright (c) 2024 Anvil
# SPDX-License-Identifier: MIT

from anvil.js.window import Function

# We need to make sure the .then method doesn't return a Promise to avoid suspensions
__version__ = "0.2.0"

PromiseLike = Function("""
class PromiseLike extends Promise {
    then(...args) {
        Promise.prototype.then.apply(this, args);
    }
}

return PromiseLike;
""")()
