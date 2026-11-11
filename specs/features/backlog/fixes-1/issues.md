# Issues: fixes-1

- [ ] **bug/medium** A unit with `factor=0` passes `Registry.register`, and converting to it makes `convert` raise `ZeroDivisionError` instead of `ConversionError`; the CLI does not catch it, so it prints a traceback — src/conv/core.py:50, src/conv/registry.py:38
- [ ] **gap/low** `Registry.register` does not check that `Quantity.base` names one of the quantity's units, or that `units` is not empty — src/conv/registry.py:38
- [ ] **gap/low** `Registry.register` accepts two quantities with the same name; `--list` would print both lines and the cross-quantity error message would be ambiguous — src/conv/registry.py:50
