from anvil.js.window import Function

# We need to make sure the .then method doesn't return a Promise to avoid suspensions
PromiseLike = Function("""
class PromiseLike extends Promise {
    then(...args) {
        Promise.prototype.then.apply(this, args);
    }
}

return PromiseLike;
""")()
